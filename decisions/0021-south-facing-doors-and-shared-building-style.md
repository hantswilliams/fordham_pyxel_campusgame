# D-0021: Every door faces south, and one building style for the whole campus

| | |
|---|---|
| **Status** | Awaiting review (four parts, each with its own decision box) |
| **Raised** | 2026-10-10. You asked that building doors always face the same direction, to make the game easier to walk through, even though it's less true to life. You also added `research/images/inspiration1.png` to `inspiration4.png` as a style reference: "some buildings still look very unique, but they all have the same general trend" |
| **Affects** | Every building's entrance and look, the signs by buildings, the building cards. Changes parts of D-0019 (north-facing library) and D-0020 (the three drawn buildings) |
| **Built provisionally?** | No. Only mockups, in `assets/buildings/_style/` (see `style_mockups.png`) |

## What the inspiration images show

All four are towns from Pokémon Gold/Silver.

1. **One recipe for every building.**
   - A big roof on top, a short front wall at the bottom, and a thin dark outline.
   - The front wall is about 1 to 1½ tiles tall and always faces the camera (south).
2. **The door is always in the bottom row of the front wall**, usually near the middle, with a doormat or step outside. Paths lead straight to it.
3. **Windows** are small two-pane squares, the same on every house.
4. **A gray signpost stands beside the door**, on the path. Special buildings also have their name on the wall (MART, POKÉ, GYM).
5. **Buildings still look different** through:
   - roof color and texture: brown slats, orange, olive
   - wall material: cream plaster, pink brick
   - size
   - one signature feature: the Radio Tower's glass column and plaza (`inspiration1`), the dark tower with lit windows (`inspiration3`)
6. **Tall buildings show their front almost all the way up**, with only a thin roof strip on top (the Radio Tower, and the dark tower in `inspiration3`).
7. **Outlines are simple rectangles.** Even big buildings avoid complicated shapes.

## Which of our buildings face the wrong way today

The game was checked door by door. Every building already opens south **except four**:

| Building | Today | Why |
|---|---|---|
| Walsh Library | North, onto Walsh Lawn | D-0019, true to life |
| Larkin Hall | North | D-0019, true to life |
| Campbell Hall | East, onto Mill River Road | D-0019, true to life |
| Dealy Hall | West, toward Cunniffe House | Yesterday, true to life |

## The mockups (all in `assets/buildings/_style/`)

| File | What it is |
|---|---|
| `style_mockups.png` | **Today vs proposed, side by side** for the library, Campbell, Dealy and a typical tile hall (Hughes). Start here |
| `proposed_walsh.png`, `proposed_campbell.png`, `proposed_dealy.png`, `proposed_hughes.png` | Each proposed version on its own |
| `mockups_v1.py` | The code that drew them |

In each mockup, the player stands on the mat at the front door, with the gray signpost to the left of the door.

---

# Part 1: Every door faces south

## What's being decided

You've decided that all doors face the same way. The questions are which way, and what to do about the real-world direction.

## Options

### A. All doors face south (toward the camera); each building's card says where the real entrance is (recommended)

- **South**, because it's the only side the camera can see, it's how all four inspiration images work, and 27 of our 31 buildings with doors already do it.
- **One main entrance per building**, one or two tiles wide. The library's other glass arches become windows.
- **The four buildings that change:**
  - **Walsh Library:** the entrance moves to the south wall. The library becomes one row shorter, so a walkway runs between it and the fence, joined to Mill River Road and the lawn. (D-0019 removed that walkway because the real campus has lawn there. It comes back so you can reach the door.)
  - **Larkin Hall:** the door moves to its south wall, on the same walkway.
  - **Campbell Hall:** the door moves to its south end, by the Archer Drive / Mill River Road sidewalk.
  - **Dealy Hall:** the portico moves to the main block's south wall, facing the walkway that runs past Dealy to Thebaud.
- **Real life still gets a mention.** The building card adds one line, for example: *"In real life: the entrance is on the north side, facing Walsh Lawn."* That's useful when a student walks there for real.

### B. All doors face south, with no real-world note

- **Pros:** Simplest.
- **Cons:** Students may look for the library entrance on the wrong side in real life.

### C. Keep the real directions (as now)

- **Cons:** It's what you asked to move away from. It's harder to find doors while walking around.

## My recommendation (Part 1)

**Option A.** You get the easy, consistent walk-through, and the card still tells students the truth. That matters most for the library, whose real entrance is on the far side.

## Your decision (Part 1)

- [ ] **Approve**: go with Option A
- [ ] **Not approve**: say which option you'd prefer, or why
- [ ] **Other**: describe below

**Your notes:**

>

---

# Part 2: One shared building style ("house style")

## What's being decided

These are the rules every building follows, so the campus reads as one game while each building still looks like itself.

## The proposed rules

| Rule | Detail |
|---|---|
| **Roof on top, front wall at the bottom** | The front wall is 1–2 tiles tall (taller for big buildings like the library). Tall, narrow buildings (Campbell) show their front almost all the way up, like the dark tower in `inspiration3` |
| **Thin navy outline** | Around every building, and around tall features like towers |
| **Door in the bottom row** | With a maroon mat outside. Glass for modern buildings, wood for older ones |
| **Two-pane windows** | White frame, light blue glass. Older stone buildings add their own trim (Dealy's white quoins) |
| **Own materials, from the palette** | Fordham stone (library, typical halls), charcoal brick (Campbell), dark fieldstone (Dealy), slate, gray or orange roofs |
| **One signature feature each** | Library: the slatted tower and glass arches. Campbell: the glass stair tower. Dealy: the white-columned portico. Keating (later): its gothic tower |
| **Simple outlines** | Rectangles, or two joined rectangles at most. Dealy's T becomes one block facing south (see the mockup) |

## Options

### A. The rules apply to every building, drawn or built from tiles; outlines simplified (recommended)

- The three drawn buildings are redrawn to the rules.
- The tile buildings' wall, window, door and roof tiles are restyled to match, so all 28 tile buildings change in one go.
- **Pros:**
  - The whole campus looks like one game.
  - Buildings are easy to read at a glance.
  - Every future drawing has a clear brief.
- **Cons:**
  - Some real shapes are lost, such as Dealy's T and the library's stepped front.
  - The three v1 drawings are redone.

### B. The same rules, but keep real outlines (T and L shapes)

- **Pros:** Closer to the campus map.
- **Cons:**
  - Odd shapes fight the "roof on top, wall at the bottom" look.
  - It's harder to see where the front is.

### C. Only drawn buildings follow the rules; tile buildings stay as they are

- **Pros:** Less work now.
- **Cons:** Two visibly different styles side by side until every building is drawn.

## My recommendation (Part 2)

**Option A.** It's the "same general trend" you described, and restyling the tiles gets the whole campus there at once, not one building at a time.

## Your decision (Part 2)

- [ ] **Approve**: go with Option A
- [ ] **Not approve**: say which option you'd prefer, or why
- [ ] **Other**: describe below

**Your notes:**

>

---

# Part 3: Signs outside buildings

## What's being decided

The inspiration images have a small gray signpost by almost every door, and the important buildings have their name on the wall. Today our buildings have neither. Only landmarks have a sign: the brown wooden board.

## Options

### A. A gray signpost beside every building's door, and a nameplate on the wall of every building (recommended)

- **The signpost** stands one tile to the left of the door, on the path. Reading it shows the building's name and opens its card, the same card as the door.
- **The nameplate** is a small plaque above the door with the short name (WALSH LIBRARY, CAMPBELL, DEALY HALL). It uses the game's built-in small font, so it stays readable at 1×.
- **Landmarks and Ram Van stops keep their own signs.** Landmarks change to the same gray signpost style; Ram Van stops stay maroon, so they stand out.
- **Pros:** You can tell what a building is from across the lawn, and from up close.
- **Cons:** Short names are needed for long ones ("WILLIAM D. WALSH FAMILY LIBRARY" becomes "WALSH LIBRARY").

### B. Signposts only

- **Pros:** Less clutter on small buildings.
- **Cons:** You have to walk up to every building to learn what it is.

### C. Nameplates only

- **Pros:** Cleanest look.
- **Cons:** It loses the signpost, the most recognizable detail in your inspiration images.

## My recommendation (Part 3)

**Option A.**

## Your decision (Part 3)

- [ ] **Approve**: go with Option A
- [ ] **Not approve**: say which option you'd prefer, or why
- [ ] **Other**: describe below

**Your notes:**

>

---

# Part 4: How to roll it out

## Options

### A. Everything in one pass (recommended)

1. Turn the four doors south, re-route the walkways to them, and add the real-entrance line to the cards.
2. Redraw the library, Campbell and Dealy to the rules, refining the mockups. They go back to "in review" in the gallery.
3. Restyle the tile buildings' tiles to the rules.
4. Add signposts and nameplates everywhere. The nameplate text lives in `content/locations.json` as a new `short_name`.
5. Update the tests:
   - every door opens south
   - every building has a signpost
   - every nameplate fits its building

### B. Doors and signposts now, the style later

- **Pros:** The walk-through improvement lands first.
- **Cons:** The three drawn buildings are touched twice.

### C. Pilot on the library first, then the rest

- **Pros:** You see one finished building before committing.
- **Cons:** Slower, and the mockups already show the direction.

## My recommendation (Part 4)

**Option A.** The mockups already show the direction for every kind of building, and doing it in one pass avoids redrawing the same buildings twice.

## Your decision (Part 4)

- [ ] **Approve**: go with Option A
- [ ] **Not approve**: say which option you'd prefer, or why
- [ ] **Other**: describe below

**Your notes:**

>

---

## What stays the same

- The asset folder per building, the review gallery and the palette (D-0020). No new colors are needed.
- Building cards, the campus map, Bert's gate and the Orientation Leader.
- The intro.
