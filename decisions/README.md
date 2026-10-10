# Decisions

This folder records the choices that shape the game. I'll add a new file here whenever a decision needs your input.

## How to review

1. Open a decision file. Each one says what's being decided, lists the options with pros and cons, and gives my recommendation and why.
2. At the bottom, tick **one** box by changing `[ ]` to `[x]`:
   - **Approve** means go with my recommendation.
   - **Not approve** means don't. Say which option you'd prefer instead, or why.
   - **Other** means something else. Describe it.
3. Add anything you like under **Your notes**.
4. Tell me "I've reviewed the decisions." I'll read your answers, make any code changes, and update the status here and in the file.

**Status values:**
- *Awaiting review:* I need your input.
- *Approved*
- *Changed:* you picked something else.
- *Superseded:* replaced by a later decision.
- *Deferred:* parked on purpose, with the options recorded for later.

**"Built provisionally"** means I already built it the recommended way so work could continue. The file says how much it would cost to change.

## Index

| # | Decision | My recommendation | Built provisionally? | Status |
|---|---|---|---|---|
| [0001](0001-audience-and-first-campus.md) | Who the game is for, and which campus first | First-years, Rose Hill only | Yes (content only) | Approved |
| [0002](0002-primary-platform.md) | How students will play it | Web first, desktop for development | No | Approved |
| [0003](0003-core-gameplay-loop.md) | What players actually do | Explore + Campus Guide + checklist + trivia, no combat | No | Approved |
| [0004](0004-screen-and-tile-size.md) | Screen resolution and tile size | 256×192, 16px tiles, 30 fps | Yes | Approved |
| [0005](0005-map-authoring.md) | How maps are made | Text maps now, Tiled editor from M3 | Yes | Approved |
| [0006](0006-content-as-data.md) | Where game text and campus facts live | JSON files in `content/` | Yes | Approved |
| [0007](0007-dev-environment.md) | Python setup and tooling | uv + Python 3.12 + pytest | Yes | Approved |
| [0008](0008-art-source.md) | Where the pixel art comes from | Placeholder now, original art later | Yes (placeholder) | Approved |
| [0009](0009-branding-and-ip.md) | Fordham branding and Pokémon IP | Use Fordham name/maroon, get Marketing sign-off before launch; no Pokémon assets | Yes | Approved |
| [0010](0010-campus-map-accuracy.md) | How faithful the map is to the real campus | Recognizable layout, compressed distances | No (current map is illustrative) | Approved |
| [0011](0011-git-hosting.md) | Where the code is hosted | Private GitHub repo now | No (git is local only) | Approved |
| [0012](0012-building-interiors.md) | Going inside buildings | Defer, outdoors only with building cards; revisit after playtest | Building cards: yes | Approved, deferred until after playtest |
| [0013](0013-campus-map-structure.md) | One big campus map, or zones | One continuous compressed Rose Hill map | No | Approved |
| [0014](0014-v1-locations-and-checklist.md) | Places in v1 and the First Week Checklist | 7-step checklist, about 20 Campus Guide entries | No | Approved |
| [0015](0015-starting-point.md) | Where the player starts | Main Entrance at Matteo Ricci Circle | Replaced | Superseded by 0016 Part 2 |
| [0016](0016-roads-vs-walkways.md) | Part 1: roads vs. walkways. Part 2: opening sequence arriving by train | 1: asphalt roads with sidewalks and crosswalks, walkable. 2: animated train arrival ending at the Webster Ave gate (replaces 0015) | Yes, both | Approved |
| [0017](0017-in-game-campus-map.md) | In-game campus map | Whole campus visible from the start, pins you can browse, no fast travel; visited/unvisited pins in M3 | Yes | Approved |
| [0018](0018-readable-text.md) | Readable, Pokémon-style text | PixelMplus 12 pixel font, black on white, 3 lines per box | Yes | Awaiting review |
| [0019](0019-southwest-corner-and-intro-characters.md) | 1: bigger intro characters. 2: detailed southwest corner (library entrance north, Campbell, Archer Dr). 3: Walsh Library look | 1: 2x characters in all intro scenes. 2: rebuild the corner from the close-up map. 3: custom north-facing library tiles | Yes | Approved |

New decision? Copy [`TEMPLATE.md`](TEMPLATE.md).
