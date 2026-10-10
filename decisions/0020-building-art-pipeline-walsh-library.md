# D-0020: A better way to draw buildings, piloted on Walsh Library

| | |
|---|---|
| **Status** | Approved, all four parts Option A (2026-10-09). Built the same day; the library's drawings are v1, **in review** |
| **Raised** | 2026-10-09. You felt the tile-built library doesn't look like the real one, and asked for more options and an asset folder to store and review buildings |
| **Affects** | How buildings are drawn and stored, the building cards, the color palette. Walsh Library first, then other buildings one at a time |
| **Built?** | Yes. `assets/buildings/` (README, `palette.hex`, `walsh_library/`), `game/world/buildings.py` (footprints), `game/gfx/building_art.py` (pictures), card pictures in `game/scenes/card.py`, extra colors in `game/config.py`, review page `tools/building_gallery.py` |

## Why the library doesn't look right yet (I agree it doesn't)

1. **It's made of repeating 16×16 tiles.**
   - Tiles work for grass, paths and simple buildings.
   - A distinctive building like Walsh Library needs one *drawing* of the whole thing: its real outline (a tower block at the northwest plus a long wing with an angled east end), a façade that reads as one piece, and the tower as a proper landmark.
   - From tiles you get a grid of identical squares.
2. **The camera looks north, but the library's front faces north.**
   - In Pokémon-style maps you always see a building's *south* wall.
   - Walsh Library's real entrance faces north onto Walsh Lawn, so on the map its best side points away from the camera.
   - We can hint at the façade along the building's north edge, but the map alone can never show the view in your photo.
   - The fix is to also show that view somewhere else: a **picture on the building card** (Part 2).
3. **The 16-color palette has one gray** for stone, roofs and roads.
   - The library's warm light stone, darker trim and flat roof all end up the same gray.

## The mockups (all in `assets/buildings/walsh_library/options/`)

| File | What it is |
|---|---|
| `review_sheet.png` | **All options side by side with the reference photo.** Start here |
| `1_now_tiles.png` | What's in the game today |
| `A_whole_building_sprite.png` | **Part 1, option A:** one drawing of the whole library, real outline |
| `B_bold_landmark_sprite.png` | **Part 1, option B:** simple, bold "Pokémon landmark" drawing |
| `C_card_picture_drawn.png` | **Part 2, option A:** hand-drawn picture of the front, as in the photo |
| `D_card_picture_from_photo.png` | **Part 2, option B:** the photo shrunk and snapped to the game's colors |

These are quick mockups to compare *directions*, not finished art. On the review sheet, panels A and B are the two map options (Part 1), and panels C and D are the two picture options (Part 2).

---

# Part 1: How the library looks on the map

## Options

### A. One whole-building drawing with the real outline and extra stone colors (recommended)
- A single drawing (`A_whole_building_sprite.png`) covering:
  - the tower block and the long wing with its angled east end, matching the campus map
  - a two-story stone façade along the north edge: piers, upper windows, glass arches, steps down to the walkway
  - a flat roof with stone rim and skylights
  - the slatted tower standing on the roof, with its shadow
- **Pros:**
  - Clearly "that building", in its real shape.
  - Fits the Pokémon look.
  - The same method works for any building later.
- **Cons:**
  - Somebody has to draw (or refine) each building.
  - The façade is still only a strip on the north edge (the camera problem above). Part 2 covers the true view.

### B. A bold, simplified "landmark" drawing
- `B_bold_landmark_sprite.png`: a rectangle, three big glass arches, an oversized tower, thick outline. Only the existing 16 colors.
- **Pros:** Instantly readable at a glance, very Pokémon-like, quickest to draw.
- **Cons:**
  - Doesn't match the real outline.
  - The tower covers part of the façade.
  - Less "that's our library."

### C. Keep the tile approach, with more tile types
- **Pros:** No new system.
- **Cons:** Still looks like a grid of identical squares. Your screenshot shows the limit.

## My recommendation (Part 1)

**Option A.** It's the only one that captures the library's real shape, and it sets up a method that works for every important building.

## Your decision (Part 1)

- [x] **Approve**: go with Option A
- [ ] **Not approve**: say which option you'd prefer, or why
- [ ] **Other**: describe below

**Your notes:**

>

---

# Part 2: A picture of the building on its building card

## What's being decided

Because the map can't show the library's front (see "why" above), the place to show students what the building really looks like is its **building card**: a picture of the façade as you'd see it walking up. This also helps orientation: "this is what you're looking for."

## Options

### A. A hand-drawn pixel picture, using the photo as reference (recommended)
- `C_card_picture_drawn.png`: the stone wings, the centre block with tall glass arches, the slatted tower, the lawn in front, and a student for scale. Drawn in the game's own style.
- **Pros:**
  - Looks like part of the game.
  - Clearly the real building.
  - No rights questions, since it's our own drawing.
- **Cons:** Someone draws one picture per building (about 30–60 minutes each to refine).

### B. The photo, shrunk and snapped to the game's colors
- `D_card_picture_from_photo.png`.
- **Pros:** Very accurate, and instant.
- **Cons:**
  - Looks like a photo, not like the game.
  - Pulls in unrelated things (for example, the domed building behind the library is off campus).
  - **We don't know who owns that photo.** We can't ship a converted copy without permission.
  - Best used only as a *tracing guide* for option A.

### C. No pictures: cards stay text-only
- **Pros:** No work.
- **Cons:** Students never see what the real entrance looks like.

## My recommendation (Part 2)

**Option A, with B used only as a private tracing guide.** We get the accuracy of the photo and the look of the game, with no rights issues. Once the Campus Guide exists (M3), the same picture appears there too.

## Your decision (Part 2)

- [x] **Approve**: go with Option A (photo conversions used only as tracing guides)
- [ ] **Not approve**: say which option you'd prefer, or why
- [ ] **Other**: describe below

**Your notes:**

>

---

# Part 3: An asset folder to store and review each building

## What's being decided

You asked for a place to keep individual buildings and review them. Today buildings exist only as letters in the map file plus art drawn in code, which is hard to see or review.

## Options

### A. One folder per building, plus a review gallery (recommended)

```
assets/buildings/
  README.md                   how to add or update a building
  palette.hex                 the game's exact colors, for any drawing app
  walsh_library/
    building.json             name, card id, position and size in tiles,
                              which tiles are solid, where the entrances are,
                              which way it faces, status: draft / in review / approved
    map.png                   the map drawing (Part 1)
    card.png                  the card picture (Part 2)
    notes.md                  sources (which photos, map), open questions
    options/                  mockups and earlier versions under review
```

- **The game loads `map.png` at start-up** and draws it over the map.
  - `building.json` sets what you bump into and which spots open the building card.
  - So a building can be redrawn without touching code or the map grid.
- **A gallery tool** (`tools/building_gallery.py`) builds one review page with a row per building:
  - the reference photo
  - the map drawing
  - the card picture
  - an in-game screenshot
  - its status
- I can also publish that page as a private link, so you (or Fordham staff) can review on any device and leave comments.
- **Drawing tools:**
  - **Piskel** (free, in the browser) or **LibreSprite** (free).
  - **Aseprite** (about $20, the standard pixel-art editor).
  - Or I draw first drafts in code, as with the mockups.
  - `palette.hex` keeps every app on the game's exact colors.
- **Pros:**
  - Each building is self-contained and easy to find.
  - It's easy to review side by side with photos.
  - It works for both human artists and me.
  - Changes show clearly in git.
- **Cons:** A small loader and the gallery tool to build (about half a day, once).

### B. Pyxel's built-in resource file (`pyxel edit` → `game.pyxres`)
- **Pros:** Pyxel's own editor, with no extra tools.
- **Cons:**
  - Everything lives in one binary file, so changes can't be reviewed in git.
  - There are only three 256×256 image banks, too small for many full building drawings.
  - No place for notes or status.

### C. Keep drawing buildings in code
- **Pros:** No new structure.
- **Cons:** Nobody but a programmer can change a building, and there's nothing to review except screenshots.

## My recommendation (Part 3)

**Option A, piloted on Walsh Library only.** Once the library looks right and the review flow feels good to you, we move other buildings over one at a time (Keating, Campbell, Dealy, McShane…). Buildings without an asset folder keep using tiles, so nothing breaks in the meantime.

## Your decision (Part 3)

- [x] **Approve**: go with Option A (library first)
- [ ] **Not approve**: say which option you'd prefer, or why
- [ ] **Other**: describe below

**Your notes:**

>

---

# Part 4: A few more colors for stone, brick and roofs

## What's being decided

Pyxel starts with 16 colors, but I tested that it **can use more**. Options A (Part 1) and A (Part 2) use **6 extra colors**:
- 4 warm stone shades: highlight, stone, shadow, dark trim
- 2 roof grays

Should we add a small set of extra colors to the game's palette?

## Options

### A. Add a small "Fordham stone" set: about 6–8 extra colors (recommended)
- Stone and roof shades now, perhaps a dark brick for Campbell and a pink for Cunniffe later.
- Recorded in `assets/buildings/palette.hex`.
- **Pros:**
  - Buildings look like real stone and brick.
  - Still a small, consistent palette, so it keeps the retro look.
- **Cons:** Slightly less "pure" retro than strictly 16 colors.

### B. Stay at 16 colors
- **Pros:** Strictly retro.
- **Cons:** Stone, roof and road stay the same gray. Fordham's stone buildings are hard to tell apart.

### C. Use any colors freely
- **Pros:** Maximum realism.
- **Cons:** Art gets inconsistent quickly and loses the pixel-game look.

## My recommendation (Part 4)

**Option A.** A handful of extra colors makes the biggest visual difference for Fordham's stone buildings, and keeping it to a short, recorded list keeps everything consistent.

## Your decision (Part 4)

- [x] **Approve**: go with Option A
- [ ] **Not approve**: say which option you'd prefer, or why
- [ ] **Other**: describe below

**Your notes:**

>

---

## What was built (2026-10-09)

- **Part 3: the folder and loader.**
  - `assets/buildings/walsh_library/building.json` holds the library's footprint, written in map-legend characters. `load_map` stamps it onto the map and adds a door for every glass arch (10 entrances), so the library's door objects were removed from `rose_hill.json`.
  - `tools/stamp_buildings.py` copies a changed footprint into the map file. The tests check that the two match.
- **Part 4: palette.** There are 6 extra colors: four stone shades and two roof grays. They live in `config.EXTRA_COLORS` and `assets/buildings/palette.hex`. Tests check that every drawing uses only palette colors and that the extra list stays at 8 or fewer.
- **Part 1: map drawing.**
  - `map.png` (160 × 148 px) is refined from mockup A. It has the tower block and wing with stone façades on the lawn side, one glass arch per tile, pier caps above the roofline, a flat roof with parapet, skylights and rooftop units, the slatted tower with its shadow, and the angled SE end.
  - A small paved forecourt in front of the wing lets you reach its entrances.
- **Part 2: card picture.** `card.png` (228 × 88 px) is refined from mockup C. On the building card, the picture sits at the top and scrolls away with the text; the building type tag sits on the lawn in the picture. Cards without a picture are unchanged.
- **Review page.** `uv run python tools/building_gallery.py` writes `build/building_gallery.html`. It shows the reference photo, the building in the game, the tile version, the map drawing, the card picture, the footprint, and the notes. A copy is published as a private link for review.
- **Simplifications to review** are listed in `assets/buildings/walsh_library/notes.md`. The main one: the real lawn-side façade is curved, and here it's two straight steps.

**Campbell Hall (second building, 2026-10-09, at your request).**
- It's converted the same way: `assets/buildings/campbell_hall/`. The footprint is a wider north part, a narrower south part, and the dining entrance at the step on the east side.
- Two charcoal brick colors were added for it, bringing the extra colors to 8. That's the top of the "about 6–8" approved in Part 4.
- Its drawings are v1, **in review**. Open questions are in its `notes.md`.

**Dealy Hall (third building, 2026-10-10, at your request).**
- It's converted the same way: `assets/buildings/dealy_hall/`. The footprint is a T from the campus map: a north-south wing and a main block running east toward Rose Hill Manor Drive.
- The columned entrance now faces **west**, toward Cunniffe House, reached by a short new walkway. The dining entrance is on the wing's east side.
- This corrects an earlier note that put the drive on Dealy's west side.
- No new colors. Its drawings are v1, **in review**.

## Next steps

1. Review the library, Campbell and Dealy in the gallery. Once each one looks right, set its status to `approved` in its `building.json` (or tell me what to change).
2. Pick the next building to convert (Keating, McShane or Cunniffe).
3. The palette is now at 8 extra colors. Any further colors (for example a pink for Cunniffe) would need a small follow-up decision.

## Original plan (if all four were approved)

1. Set up `assets/buildings/` with the palette, the loader, and `building.json` for Walsh Library.
2. Refine option A into the library's real `map.png`, and option C into `card.png`. You review both in the gallery before they go in the game.
3. Add the extra stone colors.
4. Show pictures on building cards (the library first; other cards stay text-only until they get a picture).
5. After you sign off on the library, pick the next building to convert.
