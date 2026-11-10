# Hamurapi loop handoff (2026-11-10, 02:26)

## What the loop is

Ship Hamurapi to the App Store on iPhone and Mac, then make it playable inside Joshua Tree, then work through the rest of the fleet apps queued for the OS.

## Where things stand

The game was Hamurabi until 2026-10-04. That name is taken on the App Store, so it is Hamurapi everywhere: this repo, the folder, the site (now hamurapi.jaybulb.com; heyitsmejosh.com has lapsed, so its old address is dead) and the store listing. The bundle ID stays `com.nulljosh.hamurabi`.

SUBMITTED on 2026-10-05 at 00:19 PDT. The App Store record is 6819131590. iPhone and Mac 1.0.0 both show Waiting for Review (submission ids cbdc649d and 9debfa8c), with build 202610042011.

The Joshua Tree version is merged (Joshua Tree 2.7.0) and playable in the OS.

The sprites are redrawn in `art/build.py` (f4bda7d): real legs and faces on the camel, ox, cat, sheep and rat, two-stalk wheat so fields read as fields, and a sun with rays. The trailer is a 29-second `web/trailer.mp4`, cut by `art/trailer.mjs` from frames of the web game in headless Chrome (ae5c408), and it replaces `art/trailer.sh`. Its music has not been listened to by anyone yet. The Mac and iPhone apps only get the new sprites with the next store build; nothing has been submitted. Higgsfield was not used (4.25 credits; the cheapest clip costs 5). The web deploy to hamurapi.jaybulb.com was reported done at checkpoint time, not yet verified live.

## Next, in order

1. Watch the review: `asc status --app 6819131590`. If Apple rejects it, read the reason with `asc web review show --app 6819131590` before changing anything. Do not resubmit into a spam-wave rejection; appeal in Resolution Center.
2. The day Apple approves it: the game is free for its first week. Schedule the $0.99 price for seven days later (command in `docs/MONEY.md`). Anyone who got it free keeps it free.
3. After approval, add the App Store link to the README and the landing page.
4. Landing and trailer: the night hero, the redrawn sprites and the new trailer are on `main`. Check the live site once, and listen to the trailer's music before using it anywhere. Next store version carries the new sprites to the apps; it is not submitted.
5. Joshua Tree: Hamurapi has no sound or difficulty setting in the OS yet.

## Restart prompt

```
/loop until all platforms including Joshua tree are supported. Ship to App Store.
```
