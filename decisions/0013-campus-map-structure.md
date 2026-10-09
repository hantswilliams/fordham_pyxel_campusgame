# D-0013: One big campus map, or connected zones?

| | |
|---|---|
| **Status** | Approved, Option A (2026-10-09). Built in M2. |
| **Raised** | 2026-10-09 |
| **Affects** | The next milestone (building the real Rose Hill), the camera, map files |
| **Built provisionally?** | No |

## What's being decided

Now that we're building a recognizable Rose Hill (D-0010, approved) from the official map, how do we split it up? Pokémon games use towns and routes joined at their edges. A campus is one connected place.

Pyxel's limit: one tilemap holds 256×256 small tiles, which is **128×128 of our 16px tiles**.

## Options

### A. One continuous map of all of Rose Hill, compressed (recommended)
- About **100×75 tiles**. Walking corner to corner takes around 25–30 seconds.
- Edwards Parade becomes roughly 12×9 tiles, and the athletic fields become big decorative areas you walk around.
- **Pros:**
  - No loading screens.
  - Players see how places connect, which is the onboarding goal (D-0010).
  - Matches the official map one-to-one, so a staff reviewer can check it at a glance.
  - Fits Pyxel's limit with room to spare.
- **Cons:**
  - One large text file (100 characters wide). Still readable and editable, and tests check it.
  - Tiled (D-0005) becomes more attractive sooner.

### B. Zones joined at their edges
- For example: Central (Edwards Parade), West (residential), Southwest (library), North (athletics) and East (O'Hare).
- **Pros:**
  - Each map is small and easy to edit.
  - Feels like Pokémon routes.
  - Each zone can have its own music and name banner.
- **Cons:**
  - Edge transitions break the sense of one campus.
  - Players can't see neighboring areas.
  - More code (zone links, spawn points per entrance).

### C. Small hub map plus a "travel" menu
- **Pros:** The least map work.
- **Cons:** Teaches nothing about how to get from A to B, which defeats D-0010.

## My recommendation

**Option A.** The real value is the spatial layout: "the library is southwest, past Martyrs' Lawn." One continuous map teaches that best, and the engine already handles a scrolling camera. We still show **area name banners** as you walk between zones (for example "Edwards Parade" or "Walsh Lawn"), which gives the Pokémon "new area" feeling without loading screens. Athletics fields can be simplified to save space.

## Your decision

- [x] **Approve**: go with Option A
- [ ] **Not approve**: say which option you'd prefer, or why
- [ ] **Other**: describe below

**Your notes:**

>
