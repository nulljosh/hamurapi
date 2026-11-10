// Cuts the trailer from the web game in headless Chrome. No screen recording: frames are grabbed from the
// page as it plays, so nothing from the desktop or a saved game can leak in.
// Usage: node art/trailer.mjs [base url]   (needs Chrome, ffmpeg and a server for web/: python3 -m http.server 8765 --directory web)
import { spawn } from "node:child_process";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const BASE = process.argv[2] || "http://localhost:8765", ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", PORT = 9334, FPS = 30, W = 1280, H = 800, SCALE = 1.5;
//               page                seconds  caption
const SCENES = [["play/?shot=title",  3.5, ""],
                ["play/?shot=orders", 5,   "Feed your people."],
                ["play/?shot=report", 4,   "Fill the barn."],
                ["play/?shot=plague", 4.5, "Things go wrong."],
                ["play/?shot=card",   4,   "Make hard choices."],
                ["play/?shot=over",   4.5, "Keep your crown."]];
const END = 3.5, LEN = SCENES.reduce((n, s) => n + s[1], 0) + END;
const CAPTION = text => `(() => { const d = document.createElement("div"); d.textContent = ${JSON.stringify(text)};
  d.style.cssText = "position:fixed;z-index:99;top:96px;left:50%;transform:translateX(-50%);padding:14px 36px;border-radius:40px;background:rgba(255,255,255,.9);box-shadow:0 10px 30px rgba(0,0,0,.12);font:700 40px -apple-system,system-ui,sans-serif;letter-spacing:-.5px;color:#23262d;white-space:nowrap";
  document.body.append(d); })()`;
const ENDCARD = `(() => { const d = document.createElement("div");
  d.style.cssText = "position:fixed;z-index:100;inset:0;background:#f6f6f4;display:grid;place-content:center;justify-items:center;gap:18px;font-family:-apple-system,system-ui,sans-serif;color:#23262d;animation:endin .5s ease-out";
  d.innerHTML = '<style>@keyframes endin{from{opacity:0}}</style><img src="../icon.png" width="200" height="200" style="image-rendering:pixelated;border-radius:45px">' +
    '<div style="font-size:96px;font-weight:800;letter-spacing:-2px">Hamurapi</div><div style="font-size:32px;color:#666b75">Play free at hamurapi.jaybulb.com</div>';
  document.body.append(d); })()`;

const chrome = spawn(CHROME, ["--headless=new", `--remote-debugging-port=${PORT}`, "--hide-scrollbars", "--mute-audio",
  `--user-data-dir=${mkdtempSync(join(tmpdir(), "hamurapi-trailer-"))}`, "about:blank"], { stdio: "ignore" });
const film = spawn("ffmpeg", ["-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", FPS, "-c:v", "mjpeg", "-i", "-",
  "-stream_loop", "-1", "-i", join(ROOT, "web/play/audio/music.mp3"), "-t", LEN, "-af", `afade=t=in:d=0.5,afade=t=out:st=${LEN - 2}:d=2`,
  "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "23", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", join(ROOT, "web/trailer.mp4")],
  { stdio: ["pipe", "inherit", "inherit"] });
const sleep = ms => new Promise(r => setTimeout(r, ms));

try {
  for (let i = 0; i < 50; i++) { try { await fetch(`http://localhost:${PORT}/json/version`); break; } catch { await sleep(200); } }
  const tab = await (await fetch(`http://localhost:${PORT}/json/new?about:blank`, { method: "PUT" })).json();
  const ws = new WebSocket(tab.webSocketDebuggerUrl);
  await new Promise(r => ws.addEventListener("open", r));
  let id = 0; const waiting = new Map(), events = new Map();
  ws.addEventListener("message", m => {
    const msg = JSON.parse(m.data);
    if (msg.id) { waiting.get(msg.id)?.(msg); waiting.delete(msg.id); }
    else if (msg.method === "Runtime.exceptionThrown") throw new Error(msg.params.exceptionDetails.exception?.description || msg.params.exceptionDetails.text);
    else { events.get(msg.method)?.(); events.delete(msg.method); }
  });
  const send = (method, params = {}) => new Promise(r => { waiting.set(++id, r); ws.send(JSON.stringify({ id, method, params })); });
  const frames = async seconds => {  // grab as fast as Chrome gives them, and repeat a frame to hold 30 a second
    const start = Date.now(), want = Math.round(seconds * FPS);
    for (let done = 0; done < want;) {
      const shot = await send("Page.captureScreenshot", { format: "jpeg", quality: 90, optimizeForSpeed: true }), jpg = Buffer.from(shot.result.data, "base64");
      for (const due = Math.min(want, Math.max(done + 1, Math.round((Date.now() - start) / 1000 * FPS))); done < due; done++)
        if (!film.stdin.write(jpg)) await new Promise(r => film.stdin.once("drain", r));
    }
  };
  await send("Runtime.enable"); await send("Page.enable");
  await send("Emulation.setDeviceMetricsOverride", { width: W, height: H, deviceScaleFactor: SCALE, mobile: false });
  for (const [path, seconds, caption] of SCENES) {
    await send("Page.navigate", { url: `${BASE}/${path}` }); await sleep(1800);
    if (caption) await send("Runtime.evaluate", { expression: CAPTION(caption) });
    await frames(seconds); console.log(`  ${path}: ${seconds} s`);
  }
  await send("Runtime.evaluate", { expression: ENDCARD }); await frames(END);
  film.stdin.end(); await new Promise(r => film.on("close", r));
  console.log(`web/trailer.mp4: ${LEN} s`);
} finally { chrome.kill(); }
