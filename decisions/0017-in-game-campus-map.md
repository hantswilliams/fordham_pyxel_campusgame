# D-0017: In-game campus map

| | |
|---|---|
| **Status** | Approved, Option A (2026-10-09). You approved it in chat and asked me to tick the box for you. Built the same day |
| **Raised** | 2026-10-09 |
| **Affects** | Controls (new **M** key), a new map screen, the controls card in the intro, and the Campus Guide later (M3) |
| **Built?** | Yes: `game/scenes/campus_map.py`, `game/world/minimap.py` |

## What's being decided

Players can get lost on a 100×76-tile campus, and the only help so far is the area banner. Pokémon games have a town map you can pull up at any time. Should we add one, and how should it work?

The whole campus fits on one screen at 2 pixels per tile (200×152 of the 256×192 screen), so no scrolling is needed.

### What the map shows (all options)

- **The whole campus shrunk down, in the same colors as the game:**
  - gray roads, tan walkways, green lawns
  - roofs colored by building type: slate = academic, orange = residence hall, light = other campus building, maroon = Admission
- **A blinking "you are here" marker** and the name of your current area.
- **Pins** for the important places:
  - the gates: Webster Ave, Main Entrance, Bathgate, Clavius Way
  - the Ram Van stops
  - the buildings and landmarks in the Campus Guide (D-0014)
- **Arrow keys jump between pins.** The selected pin's name shows at the bottom, and **Z opens its building card**, so the map also works as a directory.
- **A small legend** explains the colors.
- **M or X closes it.** Tab stays reserved for the Campus Guide.

## Options

### A. Whole campus visible from the start, no fast travel (recommended)
- **Pros:**
  - Works like a real campus map: students can plan a route right away.
  - Walking the real routes is what teaches the campus, so no teleporting.
  - Simple: no exploration state needed yet.
- **Cons:** Less sense of discovery. The M3 tweak below fixes that.

### B. The map fills in as you explore ("fog of war")
- **Pros:** Strong incentive to explore, very game-like.
- **Cons:**
  - A new student can't use it to find the library before walking there, which works against onboarding.
  - Needs saved exploration state.

### C. Option A plus fast travel to places you've visited
- **Pros:** Convenient on return visits.
- **Cons:** Skips the walking that teaches routes. Better left out of an onboarding game.

## My recommendation

**Option A, with one addition in M3:** once the Campus Guide exists, pins you haven't *visited* yet show as hollow outlines and visited ones as filled. The map stays fully useful for navigation, but players can see what's left to discover and what remains on the First Week Checklist.

## Your decision

- [x] **Approve**: go with Option A (hollow and filled pins added in M3)
- [ ] **Not approve**: say which option you'd prefer, or why
- [ ] **Other**: describe below

**Your notes:**

> Approved in chat on 2026-10-09 ("please write it up, and then select approve").
