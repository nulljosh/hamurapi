"""Draws every sprite and copies the story into the app and the web game. Run: python3 art/build.py
Sprites go to app/App/Sprites, and as one sheet to web/play/sprites.png. story.json goes beside them."""
import json, os, shutil
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAL = {
    "k": "#23262d", "w": "#ffffff", "g": "#e4e7eb", "G": "#b9bfc8", "s": "#7a8494", "S": "#4d5561",
    "r": "#b5502c", "R": "#8a3a1f", "o": "#dd7d52", "b": "#3b7bc6", "B": "#a6cbee",
    "n": "#58993b", "N": "#33692a", "y": "#e8b02e", "Y": "#b98717", "t": "#a8744f", "m": "#8a6b55",
    "z": "#8cb447", "Z": "#5f7f2c", "e": "#d04a4a",
    # skin and hair, so the city is not one face repeated
    "1": "#f6d9bd", "2": "#e6b98c", "3": "#c68d5c", "4": "#8f5e3c", "5": "#5e3d28",
    "H": "#5a3b24", "L": "#d2a84a", "A": "#9c4a26", "W": "#c9ccd2",
}

def rgba(ch):
    h = PAL[ch].lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)

class Sprite:
    def __init__(self, w, h): self.w, self.h, self.px = w, h, {}
    def put(self, x, y, ch):
        if 0 <= x < self.w and 0 <= y < self.h:
            if ch == ".": self.px.pop((x, y), None)
            else: self.px[(x, y)] = ch
    def rect(self, x, y, w, h, ch):
        for j in range(h):
            for i in range(w): self.put(x + i, y + j, ch)
    def rows(self, rows, sub=None, ox=0, oy=0):
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch != ".": self.put(ox + i, oy + j, (sub or {}).get(ch, ch))
        return self
    def image(self, soft=False):
        """Flat pixels in, shaded pixels out. Light comes from the top left and leans warm, shade leans cool,
        and the outline takes a dark version of the colour it wraps instead of flat black."""
        im = Image.new("RGBA", (self.w + 2, self.h + 2), (0, 0, 0, 0))
        solid = set(self.px)
        for (x, y), ch in self.px.items():
            r, g, b, a = rgba(ch)
            lit = (x, y - 1) not in solid or (x - 1, y) not in solid
            dark = (x, y + 1) not in solid or (x + 1, y) not in solid
            if lit and not dark: r, g, b = r * 1.10 + 8, g * 1.08 + 4, b * 1.02
            elif dark and not lit: r, g, b = r * 0.80, g * 0.82, b * 0.90 + 6
            elif self.px.get((x, y - 1)) not in (None, ch): r, g, b = r * 0.94, g * 0.94, b * 0.96  # a soft step under each colour change
            im.putpixel((x + 1, y + 1), (min(255, int(r)), min(255, int(g)), min(255, int(b)), a))
        if not soft:
            for (x, y), ch in self.px.items():
                r, g, b, _ = rgba(ch)
                edge = (int(r * 0.32 + 8), int(g * 0.32 + 10), int(b * 0.36 + 18), 240)
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    if (x + dx, y + dy) not in solid: im.putpixel((x + dx + 1, y + dy + 1), edge)
        return im

def from_rows(rows, sub=None):
    w = len(rows[0]); assert all(len(r) == w for r in rows), rows
    return Sprite(w, len(rows)).rows(rows, sub)

OUT = {}
SOFT = {"cloud_a", "cloud_b", "ghost", "plague", "grain", "spark", "bird_0", "bird_1", "skull", "rat_0", "rat_1",
        "flame_0", "flame_1", "fish", "sun_0", "sun_1"} | {f"wheat_{a}_{b}" for a in ("0", "1", "2", "dry") for b in (0, 1)}  # no outline

# villagers: a 4-frame walk and a 2-frame cheer, in a dozen outfits, plus the sick green set
BODY = {"swing_a": [".cccccc.", "tcccccc.", "t.eeeet.", "..cccc.t", "..cccc.."],
        "rest":    [".cccccc.", "tcccccct", "t.eeee.t", "..cccc..", "..cccc.."],
        "swing_b": [".cccccc.", ".cccccct", ".teeee.t", "t.cccc..", "..cccc.."],
        "cheer":   [".cccccc.", "..cccc..", "..eeee..", "..cccc..", "..cccc.."]}
LEGS = {"wide": ["..p..p..", ".p....p.", "kk....kk"], "apart": ["..p..p..", "..p..p..", ".kk..kk."], "together": ["...pp...", "...pp...", "..kkkk.."]}
ROBE = {"wide": ["..cccc..", ".cccccc.", "kk....kk"], "apart": ["..cccc..", "..cccc..", ".kk..kk."], "together": ["..cccc..", "..cccc..", "..kkkk.."]}
WALK = [("swing_a", "wide"), ("rest", "apart"), ("swing_b", "together"), ("rest", "apart")]
HATS = {None: ("........", "..hhhh.."), "bald": ("........", "..tttt.."), "straw": ("..YYYY..", "yyyyyyyy"),
        "wrap": ("..bbbb..", ".bbbbbb."), "band": ("..hhhh..", "..bbbb.."), "hood": ("..cccc..", ".cccccc.")}

def person(look, body, legs, arms=None):
    """One villager frame. look = (tunic, skin, hair, hat, hat colour, robe, belt, trousers)."""
    tunic, skin, hair, hat, hatc, robe, belt, trousers = look
    side = "c" if hat == "hood" else "."
    rows = list(HATS[hat]) + [f".{side}tttt{side}.", f".{side}tttt{side}.", "...tt..."] + BODY[body] + (ROBE if robe else LEGS)[legs]
    if arms is not None:  # arms up beside the head; the second frame reaches higher
        for y, cols in ((2, (0, 7)), (3, (0, 7)), (4, (1, 6) if arms == 0 else (0, 1, 6, 7))) + (((1, (0, 7)),) if arms == 0 else ()):
            rows[y] = "".join("t" if x in cols and ch == "." else ch for x, ch in enumerate(rows[y]))
    return from_rows(rows, {"c": tunic, "t": skin, "h": hair, "b": hatc, "e": belt or tunic, "p": trousers})

#            tunic skin hair  hat      hat colour  robe   belt  trousers
LOOKS = dict(a=("r", "1", "H", None,    "w",        False, None, "k"),
             b=("b", "4", "k", "wrap",  "w",        False, "y",  "S"),
             c=("n", "2", "L", "straw", "y",        False, None, "m"),
             d=("s", "5", "k", "hood",  "s",        True,  "m",  "k"),
             e=("o", "3", "A", "band",  "b",        False, None, "k"),
             f=("b", "1", "A", None,    "w",        True,  "y",  "k"),
             g=("r", "3", "k", "straw", "y",        False, "k",  "S"),
             h=("n", "5", "W", None,    "w",        True,  "y",  "k"),
             i=("G", "2", "k", "wrap",  "r",        False, "r",  "m"),
             j=("y", "4", "k", "bald",  "w",        False, "m",  "S"),
             k=("m", "1", "L", "band",  "r",        False, None, "k"),
             l=("o", "2", "H", "wrap",  "b",        True,  "b",  "k"),
             sick=("z", "2", "k", None, "w",        False, None, "Z"))
for name, look in LOOKS.items():
    for f, (body, legs) in enumerate(WALK): OUT[f"villager_{name}_{f}"] = person(look, body, legs)
    if name != "sick":
        OUT[f"cheer_{name}_0"] = person(look, "cheer", "apart", 0)
        OUT[f"cheer_{name}_1"] = person(look, "cheer", "wide", 1)

g = from_rows(["..BBBB..", ".BBBBBB.", ".BkBBkB.", ".BBBBBB.", ".BBBBBB.", ".BBBBBB.", ".BBBBBB.", ".BBBBBB.", ".BB.BB.B", ".B..B..."])
OUT["ghost"] = g
OUT["tombstone"] = from_rows([".ssss.", "sGGGGs", "sGsGGs", "sGGGGs", "sGGGGs", "sGGGGs", "SSSSSS", "SSSSSS"])
OUT["skull"] = from_rows([".kkkkk.", "kwwwwwk", "kwkwkwk", "kwwwwwk", ".kwwwk.", ".kwkwk.", "..kkk.."])
OUT["grain"] = from_rows([".y.", "yYy", ".y."])
OUT["flag_0"] = from_rows(["krrrr.", "krrrrR", "krrrR.", "k.....", "k.....", "k.....", "k.....", "k.....", "k.....", "kk...."])
OUT["flag_1"] = from_rows(["krrr..", "krrrrr", "k.rrrR", "k.....", "k.....", "k.....", "k.....", "k.....", "k.....", "kk...."])
# a fight: a dust cloud with fists, feet and stars flying out of it
OUT["scuffle_0"] = from_rows(["..y..ggg....y..", ".2ggggggggg....", "2ggwgggggggk...", ".ggggggwggggkk.", "gggggggggggGG..", ".GgwggggggggG2.", "..GGggggggGG22.", ".kkGGGGGGGG....", "..k...GG...y..."])
OUT["scuffle_1"] = from_rows(["..ggg.....y....", ".gggggggggg22..", "kggggwggggg2...", "kkgggggggggg.y.", ".ggwgggggggGG..", "2GgggggggggGGk.", "22GGgggwggGGkk.", "..y.GGGGGGG....", ".....GGG......."])
def sheep(frame):  # frame 1 has its head down in the grass
    return from_rows(["...ww.ww....", ".wwwwwwwww..", "wwwGwwwwwSSS", "wwwwwwGwwSwS", "wGwwwwwwwwSS", ".wwwwGwwww..", "..SS...SS...", "..SS...SS..."] if frame == 0 else
                     ["...ww.ww....", ".wwwwwwwww..", "wwwGwwwwww..", "wwwwwwGwwww.", "wGwwwwwwwSSS", ".wwwwGwwwSwS", "...SS.SS..SS", "...SS.SS...."])
OUT["sheep_0"], OUT["sheep_1"] = sheep(0), sheep(1)
OUT["fish"] = from_rows(["s..bbbb.", "ssbbbbkb", "ssbBBBb.", "s..bb..."])
# a ginger cat: ears, a tail that flicks, white socks
OUT["cat_0"] = from_rows(["........o..o", "........oooo", "o.......ooko", "o..ooooooooo", ".oooroorooo.", "..oooooooo..", "..o.o..o.o..", "..w.w..w.w.."])
OUT["cat_1"] = from_rows(["........o..o", ".o......oooo", ".o......ooko", ".o.ooooooooo", ".oooroorooo.", "..oooooooo..", "...oo..oo...", "...ww..ww..."])

def house(roof, shade, w=18, h=14):
    """A mudbrick house: flat roof with a coloured awning, a door to one side, one window, roof beams poking out."""
    s = Sprite(w, h)
    s.rect(0, 0, w, 3, shade); s.rect(1, 0, w - 2, 2, roof)
    s.rect(1, 3, w - 2, h - 3, "g"); s.rect(w - 5, 3, 4, h - 3, "G"); s.rect(1, h - 2, w - 2, 2, "s")
    for x in range(3, w - 3, 4): s.put(x, 4, "m")                       # beam ends under the roof
    s.rect(3, h - 8, 4, 6, "m"); s.rect(3, h - 8, 4, 1, "S"); s.put(6, h - 5, "y")  # wooden door with a latch
    s.rect(w - 9, 6, 4, 4, "S"); s.rect(w - 8, 7, 2, 2, "B"); s.rect(w - 10, 10, 6, 1, "s")  # window and sill
    return s
OUT["house_a"] = house("r", "R")
OUT["house_b"] = house("b", "S", 16, 12)
OUT["house_c"] = house("n", "N", 14, 13)

z = Sprite(56, 40)
for (x, y, w, h) in ((0, 26, 56, 14), (6, 16, 44, 10), (14, 8, 28, 8)):
    z.rect(x, y, w, h, "s"); z.rect(x, y, w, 1, "G"); z.rect(x, y + h - 2, w, 2, "S")
    for yy in range(y + 3, y + h - 2, 3):
        for xx in range(x + (yy % 2) * 2, x + w, 5): z.put(xx, yy, "S")
for i, y in enumerate(range(8, 40)):
    z.rect(25, y, 6, 1, "r" if i % 2 == 0 else "R")
z.rect(26, 0, 12, 3, "r"); z.rect(26, 0, 12, 1, "o"); z.rect(27, 3, 10, 5, "g"); z.rect(30, 4, 4, 4, "k")
OUT["ziggurat"] = z

def king(frame):
    rows = [".y.yy.y.y.", "..yyyyyy..", "..tttttt..", "..tkttkt..", "..tttttt..", "..HHHHHH..", "...HHHH...",
            ".bbbbbbbb.", "tbbbbbbbbt", "tbbyyyybbt", ".bbbbbbbb.", ".bbbbbbbb.", ".bbbbbbbb.", ".bbbbbbbb.", "..kk..kk..", "..kk..kk.."]
    if frame == 2:  # head down, crown slipping, hands over his face
        rows[:7] = ["..........", "y.yy.y.y..", ".yyyyyy...", "..tttttt..", "..tttttt..", ".tHHHHHHt.", ".ttHHHHtt."]
        rows[8], rows[9] = ".bbbbbbbb.", ".bbyyyybb."
    s = from_rows(rows, {"t": "2"})
    if frame == 1:  # arm raised, waving
        for y in (7, 8, 9): s.put(0, y, ".")
        for y in (2, 3, 4, 5, 6): s.put(0, y, "2")
    return s
OUT["king_0"], OUT["king_1"], OUT["king_2"] = king(0), king(1), king(2)

def wheat(stage, sway, dry=False):
    """Two stalks to a tile, one tall and one short, so a field reads as a field and not as a row of pins."""
    s = Sprite(7, 12); dx = 1 if sway else 0
    leaf, dk = ("t", "Y") if dry else ("n", "N")
    for cx, top in ((1, 0), (4, 3)):
        if stage == 0:
            s.rect(cx, 10, 1, 2, dk); s.put(cx + dx, 9, leaf)
            if top: s.put(cx + 1, 10, leaf)
        elif stage == 1:
            s.rect(cx, top + 4, 1, 8 - top, dk); s.put(cx - 1, top + 6, leaf); s.put(cx + 1, top + 5, leaf)
            if dry: s.put(cx + 1, top + 4, dk)           # the tip hangs over
            else: s.put(cx + dx, top + 3, leaf)
        else:
            s.rect(cx, top + 5, 1, 7 - top, "N"); s.put(cx + 1, top + 7, "n"); s.put(cx - 1, top + 8, "n")
            s.rows([".y.", "yYy", "yyy", "yYy", ".y."], ox=cx - 1 + dx, oy=top)  # the ear
    return s
for st in range(3):
    for sw in range(2): OUT[f"wheat_{st}_{sw}"] = wheat(st, sw)
for sw in range(2): OUT[f"wheat_dry_{sw}"] = wheat(1, sw, True)

def palm(sway):
    s = Sprite(16, 24)
    for y in range(7, 24): s.rect(7 if y < 17 else 6, y, 2, 1, "m")
    for y in range(11, 24, 3): s.put(8 if y < 17 else 7, y, "H")       # rings up the trunk
    s.rect(5, 23, 4, 1, "m")
    s.rows(["....nnn..nnn....", "..nnnnnnnnnnnn..", ".nnNnnnnnnnnNnn.", "nnN.nnnnnnnn.Nnn", "nN..nNnnnnNn..Nn", "n..nnN.nn.Nnn..n"], ox=sway, oy=1)
    s.rows(["...nN..mm..Nn...", "..nN..HmmH..Nn..", "..n....mm....n.."], oy=7)  # the low fronds and two coconuts
    return s
OUT["palm_0"], OUT["palm_1"] = palm(0), palm(1)

gr = Sprite(24, 22)
gr.rect(2, 8, 20, 14, "g"); gr.rect(15, 8, 7, 14, "G"); gr.rect(2, 20, 20, 2, "s")
for i, w in enumerate((18, 14, 10, 6)): gr.rect(12 - w // 2, 7 - i * 2 + 1, w, 2, "r" if i % 2 == 0 else "R")
gr.rect(10, 13, 5, 9, "S"); gr.rect(10, 13, 5, 1, "k"); gr.rect(11, 0, 2, 2, "k")
OUT["granary"] = gr
OUT["sack"] = from_rows([".kkk..", "yyyyyy", "yyyYyy", "yyyyYy", "yYyyyy", ".YYYY."])

OUT["rat_0"] = from_rows(["......SS..", "....SSSSS.", "oo.SSSSSwS", "..oSSSSSSo", "....k..k.."])
OUT["rat_1"] = from_rows(["......SS..", "....SSSSS.", "..oSSSSSwS", "oo.SSSSSSo", ".....k..k."])

c = Sprite(28, 11)
c.rect(3, 5, 22, 6, "g"); c.rect(8, 2, 9, 4, "g"); c.rect(15, 3, 8, 3, "g"); c.rect(4, 4, 6, 1, "g")
c.rect(9, 2, 6, 1, "w"); c.rect(5, 5, 4, 1, "w"); c.rect(3, 10, 22, 1, "G")
OUT["cloud_a"] = c
c2 = Sprite(20, 8); c2.rect(2, 4, 16, 4, "g"); c2.rect(6, 1, 7, 4, "g"); c2.rect(7, 1, 4, 1, "w"); c2.rect(2, 7, 16, 1, "G")
OUT["cloud_b"] = c2

def sun(frame):
    """A disc with a bright side and a shaded rim, and rays that pulse: long up and across, then long on the slant."""
    s = Sprite(20, 20)
    for y in range(20):
        for x in range(20):
            dx, dy = x - 9.5, y - 9.5; d = dx * dx + dy * dy
            if d <= 38: s.put(x, y, "y" if (dx + 2) ** 2 + (dy + 2) ** 2 <= 9 else "r" if d > 24 and dx + dy > 2 else "o")
    n = 3 if frame == 0 else 2
    s.rect(9, 3 - n, 2, n, "o"); s.rect(9, 17, 2, n, "o"); s.rect(3 - n, 9, n, 2, "o"); s.rect(17, 9, n, 2, "o")
    for k in range(1 if frame == 0 else 3):
        for x, y in ((4 - k, 4 - k), (15 + k, 4 - k), (4 - k, 15 + k), (15 + k, 15 + k)): s.put(x, y, "o")
    return s
OUT["sun_0"], OUT["sun_1"] = sun(0), sun(1)

OUT["bird_0"] = from_rows(["k.....k", ".k...k.", "..kkk.."])
OUT["bird_1"] = from_rows(["..kkk..", ".k...k.", "k.....k"])

def camel(frame):
    """One hump, a long neck, a red saddle blanket. The far legs are darker and step opposite the near ones."""
    s = Sprite(24, 18)
    for x in ((8, 12) if frame == 0 else (4, 13)): s.rect(x, 12, 2, 5, "m"); s.rect(x, 17, 2, 1, "S")
    s.rows(["...................t.t..", "..................ttttt.", "..................ttkttt", "..................tttttt",
            "........tttt......ttt...", ".......tttttt....ttt....", "......tttttttt..tttt....", "....tttttttttttttttt....",
            "...ttttttttttttttttt....", "..t.tttttttttttttt......", "..t.tttttttttttttt......", "..m.tttttttttttttt......"])
    s.rect(8, 5, 4, 4, "r"); s.rect(8, 9, 4, 1, "y")
    for x in ((5, 15) if frame == 0 else (7, 16)): s.rect(x, 12, 2, 5, "t"); s.rect(x, 17, 2, 1, "S")
    return s
OUT["camel_0"], OUT["camel_1"] = camel(0), camel(1)

p = Sprite(32, 14)  # the sickness: a low cloud of round puffs, dark underneath, with spores in it
for y in range(14):
    for x in range(32):
        if any((x - cx) ** 2 + (y - cy) ** 2 <= r * r + 1 for cx, cy, r in ((3, 10, 2), (8, 8, 4), (15, 6, 5), (22, 7, 5), (28, 9, 3))) and y < 13:
            p.put(x, y, "Z" if y >= 11 else "z")
for x, y in ((7, 7), (14, 4), (17, 8), (23, 6), (27, 9), (11, 10)): p.put(x, y, "Z")
for x in (6, 13, 20, 26): p.put(x, 13, "Z")
OUT["plague"] = p
OUT["spark"] = from_rows([".y.", "yyy", ".y."])

def ox(frame):
    """Heavy shoulders, a low head, horns like a lyre."""
    s = Sprite(18, 12)
    for x in ((6, 9) if frame == 0 else (2, 11)): s.rect(x, 8, 2, 3, "H"); s.rect(x, 11, 2, 1, "k")
    s.rows([".............w...w", "........mmmm..w.w.", "..mmmmmmmmmmm.mmm.", ".mmmmmmmmmmmmmmmmm", "H.mmmmmmmmmmmmmkmm", "H.mmmmmmmmmmmmmmm1", "H.mmmmmmmmmmm.mm11", "..mmmmmmmmmmm....."])
    for x in ((3, 11) if frame == 0 else (5, 9)): s.rect(x, 8, 2, 3, "m"); s.rect(x, 11, 2, 1, "k")
    return s
OUT["ox_0"], OUT["ox_1"] = ox(0), ox(1)

bt = Sprite(22, 12)
bt.rect(2, 9, 18, 2, "m"); bt.rect(4, 11, 14, 1, "S"); bt.put(1, 8, "m"); bt.put(20, 8, "m"); bt.put(0, 7, "m"); bt.put(21, 7, "m")
bt.rect(10, 0, 1, 9, "S"); bt.rect(11, 1, 6, 5, "w"); bt.rect(11, 3, 6, 1, "r"); bt.rect(5, 6, 2, 3, "b"); bt.rect(5, 5, 2, 1, "t")
OUT["boat"] = bt

OUT["flame_0"] = from_rows(["..o..", ".oy..", ".oyo.", "oyyo.", ".oo..", "..S..", "..S.."])
OUT["flame_1"] = from_rows(["...o.", "..yo.", ".oyo.", ".oyyo", "..oo.", "..S..", "..S.."])

def icon():
    """The app icon as a 64x64 grid: night sky, golden sun, the ziggurat, wheat. One source for every size."""
    px = {}
    def box(x, y, w, h, c):
        for j in range(h):
            for i in range(w): px[(x + i, y + j)] = c
    for y in range(64):
        k = y / 63
        for x in range(64): px[(x, y)] = (int(13 + 20 * k), int(18 + 26 * k), int(32 + 44 * k))
    for i in range(22):  # stars
        x, y = (i * 37 + 11) % 64, (i * 23 + 5) % 30
        px[(x, y)] = (200, 210, 230) if i % 3 else (255, 255, 255)
    for y in range(64):  # the sun and its glow
        for x in range(64):
            d = ((x - 31.5) ** 2 + (y - 27.5) ** 2) ** 0.5
            if d <= 15: px[(x, y)] = (247, 208, 104) if d <= 11 and x + y < 62 else (232, 176, 46)
            elif d <= 27:
                a = (1 - (d - 15) / 12) ** 2 * 0.55; r, g, b = px[(x, y)]
                px[(x, y)] = (int(r + (232 - r) * a), int(g + (150 - g) * a), int(b + (60 - b) * a))
    lit, face, shade, deep = (221, 125, 82), (181, 80, 44), (138, 58, 31), (96, 40, 22)
    for x, y, w, h in ((7, 44, 50, 10), (14, 34, 36, 10), (21, 24, 22, 10)):
        box(x, y, w, h, face); box(x, y, w, 2, lit); box(x + w - 7, y + 2, 7, h - 2, shade); box(x, y + h - 1, w, 1, deep)
        for bx in range(x + 3, x + w - 8, 6): box(bx, y + 4, 2, 2, shade)
    for i, y in enumerate(range(24, 54)): box(29, y, 6, 1, (245, 190, 150) if i % 2 == 0 else lit)
    box(26, 14, 12, 2, lit); box(27, 16, 10, 8, face); box(34, 16, 3, 8, shade); box(30, 18, 4, 6, (255, 211, 107)); box(31, 19, 2, 5, (255, 240, 190))
    box(0, 54, 64, 10, (9, 13, 20)); box(0, 54, 64, 1, (30, 42, 62))
    for i, x in enumerate(range(2, 63, 4)):
        hgt = 5 + (i * 7) % 3
        box(x, 62 - hgt, 1, hgt + 2, (150, 110, 24)); box(x - 1, 61 - hgt, 3, 2, (232, 176, 46)); px[(x, 60 - hgt)] = (247, 208, 104)
    return px

def write_icon():
    px = icon()
    rows = []
    for y in range(64):  # runs of one colour become one rect each
        x = 0
        while x < 64:
            c = px[(x, y)]; n = 1
            while x + n < 64 and px[(x + n, y)] == c: n += 1
            rows.append(f'<rect x="{x}" y="{y}" width="{n}" height="1" fill="#{c[0]:02x}{c[1]:02x}{c[2]:02x}"/>')
            x += n
    with open(os.path.join(ROOT, "icon.svg"), "w") as f:
        f.write('<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 64 64" shape-rendering="crispEdges">'
                '<clipPath id="r"><rect width="64" height="64" rx="13"/></clipPath><g clip-path="url(#r)">' + "".join(rows) + "</g></svg>\n")
    im = Image.new("RGB", (64, 64))
    for (x, y), c in px.items(): im.putpixel((x, y), c)
    im.resize((1024, 1024), Image.NEAREST).save(os.path.join(ROOT, "web/icon.png"))
    im.resize((192, 192), Image.NEAREST).save(os.path.join(ROOT, "web/icon-192.png"))  # home screen icon for the web game
    # Icon Composer bundle for the app: the same picture split into layers, so the system can light each one.
    # Xcode builds every icon size from it.
    layers = {"Sun": lambda x, y: y < 54 and not zig(x, y) and px[(x, y)] != sky(y),
              "Ziggurat": lambda x, y: y < 54 and zig(x, y), "Wheat": lambda x, y: y >= 54}
    def sky(y): k = y / 63; return (int(13 + 20 * k), int(18 + 26 * k), int(32 + 44 * k))
    def zig(x, y): return any(a <= x < a + w and b <= y < b + h for a, b, w, h in ((7, 44, 50, 10), (14, 34, 36, 10), (21, 24, 22, 10), (26, 14, 12, 10)))
    bundle = os.path.join(ROOT, "app/Hamurapi.icon"); shutil.rmtree(bundle, ignore_errors=True); os.makedirs(os.path.join(bundle, "Assets"))
    for name, keep in layers.items():
        layer = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        for (x, y), c in px.items():
            if keep(x, y): layer.putpixel((x, y), c + (255,))
        layer.resize((1024, 1024), Image.NEAREST).save(os.path.join(bundle, "Assets", name.lower() + ".png"))
    group = lambda name, glass, shadow: {"layers": [{"glass": glass, "image-name": name.lower() + ".png", "name": name}], "lighting": "individual",
                                         "name": name, "shadow": {"kind": "neutral", "opacity": shadow}, "specular": glass}
    with open(os.path.join(bundle, "icon.json"), "w") as f:
        json.dump({"fill": {"linear-gradient": ["extended-srgb:0.051,0.071,0.125,1.0", "extended-srgb:0.129,0.173,0.298,1.0"],
                            "orientation": {"start": {"x": 0.5, "y": 0}, "stop": {"x": 0.5, "y": 1}}},
                   "groups": [group("Wheat", False, 0.4), group("Ziggurat", True, 0.5), group("Sun", False, 0.0)],
                   "supported-platforms": {"squares": "shared"}}, f, indent=2)

if __name__ == "__main__":
    images = {name: sp.image(name in SOFT) for name, sp in OUT.items()}
    app = os.path.join(ROOT, "app/App/Sprites")
    shutil.rmtree(app, ignore_errors=True); os.makedirs(app)
    for name, im in images.items(): im.save(os.path.join(app, name + ".png"))
    # The web game gets one sheet and a map of where each sprite sits: one request, all or nothing.
    x = y = rowh = 0; where = {}
    for name, im in images.items():
        if x + im.width > 256: x, y, rowh = 0, y + rowh + 1, 0
        where[name] = [x, y, im.width, im.height]; x += im.width + 1; rowh = max(rowh, im.height)
    atlas = Image.new("RGBA", (256, y + rowh), (0, 0, 0, 0))
    for name, im in images.items(): atlas.paste(im, tuple(where[name][:2]))
    atlas.save(os.path.join(ROOT, "web/play/sprites.png"))
    for d in ("app/App", "web/play"): shutil.copy(os.path.join(ROOT, "art/story.json"), os.path.join(ROOT, d, "story.json"))
    with open(os.path.join(ROOT, "web/play/sprites.json"), "w") as f: json.dump(where, f)
    sheet = Image.new("RGBA", (760, 2000), (246, 246, 244, 255)); x = y = 4; rowh = 0  # contact sheet for eyeballing
    for name, sp in OUT.items():
        im = sp.image(name in SOFT)
        if x + im.width * 3 > 756: x, y, rowh = 4, y + rowh + 6, 0
        sheet.alpha_composite(im.resize((im.width * 3, im.height * 3), Image.NEAREST), (x, y))
        x += im.width * 3 + 6; rowh = max(rowh, im.height * 3)
    sheet.crop((0, 0, 760, y + rowh + 4)).save(os.path.join(ROOT, "art/sheet.png"))
    write_icon()
    print(len(OUT), "sprites, icon written")
