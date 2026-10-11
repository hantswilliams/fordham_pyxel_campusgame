# D-0032: A detailed, painted-looking campus map

| | |
|---|---|
| **Status** | Built 2026-10-11 at your request. Review the boxes below |
| **Raised** | 2026-10-11. You asked for the in-game map (M) to be more detailed and less pixelated, like the picture `tools/render_map.py` makes |
| **Affects** | The campus map screen (D-0017). The pins, arrow keys, cards and closing it work as before |

## What changed

The old map coloured every tile as one flat block, 2 pixels to a tile, with one colour per building type.

**Now:**
- **Same art as the game.** The map is made from the same picture `render_map.py` saves: the real tiles, the drawn buildings, the outlines and the name plaques.
- **Shrunk smoothly.** That picture is shrunk to **4 pixels per tile**. Each 4 × 4 block is averaged and snapped to the nearest game colour, which is why it looks painted rather than blocky. You can pick out every building, field, car park and tree line.
- **Scrolling view.** At that size the campus doesn't fit on the screen, so the view **glides to follow** the place you pick with the arrow keys. It opens centred on you.
- **Overview.** A **small overview of the whole campus** sits in the top-right corner, with a yellow box showing what the main view is looking at, and your dot.
- **Selected place:** it gets a map pin and a **name tag**.
- **Other places:** small coloured markers, so they don't cover the buildings.
- **Footer:** the pin key is in the footer, replacing the old colour legend, since the map now shows real buildings instead of colour codes.

**Cost:** the picture is made once, the first time you open the map, in about a quarter of a second, then reused.

---

# Part 1: The detailed map

### A. Real art at 4 px per tile, scrolling, with an overview (recommended, built)

### B. The whole campus on one screen at about 2.5 px per tile

- **Pros:** No scrolling.
- **Cons:** At that size buildings blur together and it looks nearly as pixelated as before.

### C. Two zoom levels you switch between

- **Pros:** You get both views full-size.
- **Cons:** It needs another button, and the corner overview already gives the whole-campus view.

## Your decision (Part 1)

- [ ] **Approve**: go with Option A
- [ ] **Not approve**: say which option you'd prefer, or why
- [ ] **Other**: describe below

**Your notes:**

>

---

## What was built

- `game/gfx/map_render.py`: draws a whole map at full size, shared by the game and `tools/render_map.py`, so the two always match.
- `game/world/minimap.py`: a new `downsample()` does the colour-averaging shrink. It's pure Python and has a test.
- `game/scenes/campus_map.py`: the scrolling view, the overview, the pin tags and the new footer.
