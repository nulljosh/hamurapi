# Hamurapi loop handoff (2026-11-10, 13:30)

## What the loop is

Keep Hamurapi moving across every platform, starting with Joshua Tree, then work through the rest of the fleet apps queued for the OS.

## Where things stand

The game was Hamurabi until 2026-10-04. That name is taken on the App Store, so it is Hamurapi everywhere: this repo, the folder, the site (hamurapi.jaybulb.com; heyitsmejosh.com has lapsed, so its old address is dead) and the store listing. The bundle ID stays `com.nulljosh.hamurabi`.

The App Store record is 6819131590. `asc` shows both iOS and Mac 1.0.0 at READY_FOR_SALE (build 202610042011), so the 2026-10-05 spam-wave rejection was answered and the app is approved. The approval date is not recorded in this repo.

The Joshua Tree version is merged (Joshua Tree 2.7.0) and playable in the OS.

The sprites are redrawn in `art/build.py` (f4bda7d): real legs and faces on the camel, ox, cat, sheep and rat, two-stalk wheat so fields read as fields, and a sun with rays. The trailer is a 29-second `web/trailer.mp4`, cut by `art/trailer.mjs` from frames of the web game in headless Chrome (ae5c408), and it replaces `art/trailer.sh`. Its music has not been listened to by anyone yet. The Mac and iPhone apps still carry the old sprites until the next store build; nothing new has been submitted. Higgsfield was not used (4.25 credits; the cheapest clip costs 5). The web deploy to hamurapi.jaybulb.com was reported done at checkpoint time, not yet verified live.

## Next, in order

1. Check whether the $0.99 price change is scheduled. The plan was free for the first week, then $0.99 once (command in `docs/MONEY.md`). Anyone who got it free keeps it free.
2. Add the App Store link to the README and the landing page.
3. Landing and trailer: the night hero, the redrawn sprites and the new trailer are on `main`. Check the live site once, and listen to the trailer's music before using it anywhere. The next store version carries the new sprites to the apps; it is not submitted.
4. Joshua Tree: Hamurapi has no sound or difficulty setting in the OS yet.

## Restart prompt

```
/loop until all platforms including Joshua Tree are supported.
```
