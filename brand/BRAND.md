# Hamurapi brand kit and design system

a ziggurat

## The mark
The icon is pixel art, drawn by `art/build.py` like every sprite: the ziggurat at night, the sun behind it, wheat in front.

- `../app/Hamurapi.icon` is the Icon Composer bundle the app ships. `../icon.svg` is the flat copy for READMEs (80 px). `icon-1024.png` is the App Store icon, no alpha. All three come out of `python3 art/build.py`; never edit them by hand.
- `mark.svg` is the ziggurat as a flat glyph in `currentColor`, for one colour jobs.
- Smallest size 16 px.

## Colour
| Role | Value |
|---|---|
| Accent | `#b5502c` |
| Gradient top | `#dd7d52` |
| Text | `#1d1d1f` light, `#f5f5f7` dark |
| Background | `#ffffff` light, `#000000` dark |
| Surface | `#f5f5f7` light, `#1c1c1e` dark |

The accent is for actions, links and the icon. Never brown, beige, purple or teal.

## Type
The system font: `-apple-system, BlinkMacSystemFont, "SF Pro Text", Lato, "Helvetica Neue", Helvetica, Arial, sans-serif`. Scale 34/41 bold, 22/28, 17/24, 15/20, 13/18.

## Space and shape
- Space on the 8 point grid: 4, 8, 12, 16, 24, 32, 48. Side margin 20. Reading column 680.
- Radii: cards 28, grouped lists 20, controls fully round, icon 22 percent.
- Controls are 48 points tall capsules, one height in a row. Focus is a 4 point ring at 30 percent accent.
- Motion is 0.2 s ease and honours reduced motion.

`tokens.css` holds the app's accent. Everything else comes from the shared token file.
