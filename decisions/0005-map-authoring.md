# D-0005: How maps are made

| | |
|---|---|
| **Status** | Approved, Option A (2026-10-09) |
| **Raised** | 2026-10-08 |
| **Affects** | `content/maps/`, `game/world/mapdata.py`, who can edit maps |
| **Built provisionally?** | Yes: text maps. This deviates from ARCHITECTURE.md, which assumed Tiled from M1. Switching to Tiled later is about a day of work, and the rest of the engine doesn't change. |

## What's being decided

What tool do we use to draw the campus maps?

## Options

### A. Text maps now, switch to the Tiled editor around M3 (recommended, already built)
- Today each map is a `.txt` grid (one character per tile) plus a `.json` file for signs, NPCs and doors.
- **Pros:**
  - Zero tools to install.
  - You can read and edit a map in any text editor.
  - Changes show up clearly in git diffs.
  - Tests already check every map for mistakes.
- **Cons:**
  - Only one layer, so we can't yet draw a roof *over* the player or decorations on top of paths.
  - Awkward for large or detailed maps.

### B. Tiled (free map editor) right now
- **Pros:**
  - A proper visual editor with layers and object placement.
  - Pyxel can load Tiled files directly (`Tilemap.from_tmx`).
- **Cons:**
  - Needs real tile art to be useful, and we only have placeholders.
  - Another tool to learn.
  - We'd write an object-layer reader before it's needed.

### C. Text maps forever
- **Pros:** Simplest.
- **Cons:** Painful once maps have multiple layers or interiors with furniture.

### D. Pyxel's built-in tilemap editor (`pyxel edit`)
- **Pros:** Built in, and the art and the map live in one file.
- **Cons:**
  - No object placement for NPCs and doors.
  - A binary file format, so changes are hard to review in git.
  - A small editor that's tiring to use for big maps.

## My recommendation

**Option A.** Text maps got us walking around today, and they're easy for both of us to review. Once real art exists and we need layers (M3, interiors), Tiled earns its keep. The rest of the engine only sees a `MapData` object, so the switch is contained to one loader file.

## Your decision

- [x] **Approve**: go with Option A
- [ ] **Not approve**: say which option you'd prefer, or why
- [ ] **Other**: describe below

**Your notes:**

>
