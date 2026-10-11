# D-0027: The southwest corner: real tree cover, and the Old Elm Road loop round Martyrs' Court

| | |
|---|---|
| **Status** | Built 2026-10-10 at your request. Review the boxes below |
| **Raised** | 2026-10-10, from `research/images/southwest_trees.png` (satellite view) and `research/images/southwest_maincar_rode_wider_gray.png` (street map) |
| **Affects** | The map between Mill River Road, Edgar Allan Poeway, Rose Hill Manor Drive and the Webster Avenue fence; one new tile |

## What the pictures show

- **Old Elm Road loops round Martyrs' Court and its lawn.** Along the north side it runs past Martyrs' Court; in the game that's Edgar Allan Poeway. Down the east side it passes the Archbishop Hughes statue. Along the south side it curves back west to Mill River Road by Campbell. Mill River Road closes the loop on the west.
- **Trees:**
  - Martyrs' Lawn is open, but it's lined with trees.
  - The south half of the loop is heavily wooded.
  - Walsh Lawn is open in the middle, with woods along the road and to the east.
  - Dense trees surround Duane Library and Larkin Hall.
  - Several dark purple **copper beeches** stand among the green trees.

---

# Part 1: Close the road loop

### A. Add the east side of Old Elm Road (recommended, built)

- **The new road:** two lanes, running from Edgar Allan Poeway down past the statue to the south side of the loop. That closes the circle.
- **Crosswalks:** walkways crossing the new road get full-width crosswalks.
- **The junction:** where it meets the south side, it's plain road.

## Your decision (Part 1)

- [x] **Approve**: go with Option A
- [ ] **Not approve**
- [ ] **Other**

---

# Part 2: Plant the southwest from the aerial photo

### A. Zones of woods and open lawn (recommended, built)

The trees here are no longer scattered at random. The map generator now uses zones taken from the photo:
- **Open lawns:** Martyrs' Lawn and the middle of Walsh Lawn.
- **Dense woods:**
  - along both sides of the loop's south side
  - between Martyrs' Lawn and the loop's east side
  - round Duane Library, and between the library and Larkin
- **Lighter woods:** by the Hughes statue and below Larkin.

**Safeguards:**
- A tree is never placed if it would cut off a patch of lawn or a path.
- Signposts and the space round every object stay clear.
- The rest of the campus keeps its trees exactly as before.

## Your decision (Part 2)

- [x] **Approve**: go with Option A
- [ ] **Not approve**
- [ ] **Other**

---

# Part 3: Copper beeches

### A. A purple-leaved tree tile, `V` (recommended, built)

About one tree in six in the southwest is a copper beech, as in the photo. It's solid like any tree, and it shows green on the campus map.

## Your decision (Part 3)

- [x] **Approve**: go with Option A
- [ ] **Not approve**
- [ ] **Other**

---

## What was built

- **Map:** `content/maps/rose_hill.txt` was regenerated. Nothing outside the southwest changed.
- **New tile:** `tree_purple` (`V`) in `game/world/tiles.py`, `game/gfx/placeholder_art.py` and `game/world/minimap.py`.

## Later

- If you want the loop to curve the way the real road does, a road drawing in the style of the building drawings would do it. Tile roads can only go straight or in steps.
