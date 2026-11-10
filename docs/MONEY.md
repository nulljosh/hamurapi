# Hamurapi Money

How Hamurapi makes money. The company plan is `REVENUE.md` in the Code root; the ledger is `GTM.md`.

## Price and rail

Free on iPhone and Mac (ASC 6819131590), and free on the web. The store price is free today. The plan was a free week after Apple approved the app, then $0.99 once. That step is not in place (see Next). A $0.99 sale would pay $0.84 after Apple's 15%.

## What is actually sold

Nothing yet. The game is Hamurabi (1968) played as a game you can watch. The rules come from a 1968 game, and the name Hamurabi was taken on the store, so the product is Hamurapi. The credit to the original stays. The name risk is already handled.

## Who pays and why

A player who wants the 1968 resource game with a drawn city and a story, once, with no ads and nothing to unlock.

## Cost to serve

No paid API and no server. The site is static files on Cloudflare, with no accounts. Hosting is Cloudflare's free tier.

## Where we are

- 2026-10-04: Joshua set the plan: free for a week after Apple approves it, then $0.99 once.
- 2026-11-02: the store price is still free in App Store Connect.
- Revenue: no verified number (the App Store Connect key cannot read sales yet).

## Role in the company plan

Catalogue. GTM.md lists it that way. It serves Stage 0 as one more game a stranger can try free and then buy for a dollar. Under Stage 2 it stays on the grid or is retired.

## Next

Joshua decides whether the free week ends. If yes, start the $0.99 price seven days after that day, with the command below. Until then it stays free.

## Million, billion, trillion

**A million.** Hamurapi is the resource game people play on the train, paid once, with the story intact.

**A billion.** Hamurapi is one of the first games a person finds on a Jaybulb device, the one that teaches a city's economy.

**A trillion.** Hamurapi would be one of thousands of games on a Joshua Tree store, which is a platform, not one game.

## Change it

`asc pricing schedule create --app 6819131590 --price 0.99 --base-territory USA --start-date YYYY-MM-DD`, with the start date seven days after Joshua says yes. `--free` reverts it. No build, no review.

Anyone who got Hamurapi while it was free keeps it free.

*ASC 6819131590. Verified 2026-11-02.*
