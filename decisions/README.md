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

**"Built provisionally"** means I already built it the recommended way so work could continue. The file says how much it would cost to change.

## Index

| # | Decision | My recommendation | Built provisionally? | Status |
|---|---|---|---|---|
| [0001](0001-audience-and-first-campus.md) | Who the game is for, and which campus first | First-years, Rose Hill only | Yes (content only) | Awaiting review |
| [0002](0002-primary-platform.md) | How students will play it | Web first, desktop for development | No | Awaiting review |
| [0003](0003-core-gameplay-loop.md) | What players actually do | Explore + Campus Guide + checklist + trivia, no combat | No | Awaiting review |
| [0004](0004-screen-and-tile-size.md) | Screen resolution and tile size | 256×192, 16px tiles, 30 fps | Yes | Awaiting review |
| [0005](0005-map-authoring.md) | How maps are made | Text maps now, Tiled editor from M3 | Yes | Awaiting review |
| [0006](0006-content-as-data.md) | Where game text and campus facts live | JSON files in `content/` | Yes | Awaiting review |
| [0007](0007-dev-environment.md) | Python setup and tooling | uv + Python 3.12 + pytest | Yes | Awaiting review |
| [0008](0008-art-source.md) | Where the pixel art comes from | Placeholder now, original art later | Yes (placeholder) | Awaiting review |
| [0009](0009-branding-and-ip.md) | Fordham branding and Pokémon IP | Use Fordham name/maroon, get Marketing sign-off before launch; no Pokémon assets | Yes | Awaiting review |
| [0010](0010-campus-map-accuracy.md) | How faithful the map is to the real campus | Recognizable layout, compressed distances | No (current map is illustrative) | Awaiting review |
| [0011](0011-git-hosting.md) | Where the code is hosted | Private GitHub repo now | No (git is local only) | Awaiting review |

New decision? Copy [`TEMPLATE.md`](TEMPLATE.md).
