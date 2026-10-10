# D-0024: Residence halls, drawn from photos found online

| | |
|---|---|
| **Status** | Approved, all parts Option A (2026-10-10). You asked me to find photos online, tick the boxes myself and keep going batch by batch; you'll review at the end |
| **Raised** | 2026-10-10, batch 2 of 3 (athletics, then residence halls, then academic and other buildings) |
| **Affects** | Twelve new drawn buildings for eleven residence halls; card pictures and card text; two small code changes for places drawn as more than one building |
| **Built?** | Yes, the same day |

Campbell Hall was drawn already (D-0020), so it isn't part of this batch.

## How the photos were found

The method was the same as D-0023:
- **Wikimedia Commons**, through its API: the categories for Loschert, Faber, Loyola, Queen's Court, Martyrs' Court, Conley, Salice, Finlay and Tierney. A file search covered O'Hare and Walsh Hall. Licenses are recorded per photo in each building's notes.
- **Image search** for the halls Commons barely covers: Alumni Court South, Finlay, Walsh Hall and Tierney.
- **Facts** from Wikipedia ("Campuses of Fordham University") and The Fordham Ram's guide to first-year halls.

The screenshots I traced from are in `research/images/web/` (`residence_*.jpg`), listed in `SOURCES.md`.

## What I learned

| Hall | What it looks like | Facts |
|---|---|---|
| **Loschert** and **Alumni Court South** | Twin buildings in pinkish-tan brick. Each has a tall glass entrance bay under a pointed stone gable | Loschert was formally Alumni Court North (1987). Both are first-year halls |
| **Queen's Court** | Collegiate Gothic in golden fieldstone with brown window trim and battlements, round a garden courtyard with a white statue | Three halls (Bishops', St. John's, St. Robert's) joined in 1940. Home to a first-year wellness community |
| **Loyola** | Gray Gothic stone, a taller entrance bay with a pointed arch | 1936, built for Jesuit faculty. First-year (Manresa) |
| **Faber** | Pale tan brick in horizontal bands, seven storeys | 1963 addition to Loyola. First-year |
| **Martyrs' Court** | Long tan-brick blocks, four storeys, a white-stone **clock tower** with a cross over the entrance steps | 1950. First-year; its steps are a popular hangout |
| **Conley & Salice** | Charcoal brick with glass stair towers, like Campbell | 2009, upperclass |
| **O'Hare** | Dark fieldstone with limestone piers, big gridded windows, three wings | 2000, up to 560 upperclass students |
| **Tierney** | White panels, dark brick end wall, three storeys | 1986 (built as Sesquicentennial Hall) |
| **Finlay** | Dark fieldstone, **green copper mansard roof** with dormers, Gothic limestone entrance | 1913, built for the medical school. Mostly sophomores |
| **Walsh Hall** | A **thirteen-storey** brown-brick tower with vertical piers | 1972 (once "the 555"), upperclass apartments |

---

# Part 1: Draw every residence hall on the footprint it already has

### A. New art, same footprints and doors (recommended)

- Each hall keeps its size, place and south-facing door, so walkways, signposts and the minimap don't change.
- Halls with more storeys show a taller front and less roof: Walsh Hall's front fills most of its footprint.
- Martyrs' Court's clock tower rises just above its roof line.

### B. Re-lay out the west side to match the real shapes

Queen's Court's quad, Martyrs' Court's U, and the Alumni Court circle.

- **Cons:** It's a much bigger change to paths and signposts, so I'd rather do it only if you want it.

## Your decision (Part 1)

- [x] **Approve**: go with Option A
- [ ] **Not approve**
- [ ] **Other**

---

# Part 2: Places drawn as more than one building

Martyrs' Court is two blocks on the map: the long main block and the west wing.

### A. Two drawn buildings sharing one place (recommended)

- Each block gets its own name plaque.
- The card uses the main block's picture.
- Two small code changes support this: plaques are matched to the block whose door they belong to, and the card picks the block that has a picture.
- A new test checks it.

## Your decision (Part 2)

- [x] **Approve**: go with Option A
- [ ] **Not approve**
- [ ] **Other**

---

# Part 3: Card pictures and text

### A. A card picture for every hall, and new text with the facts above (recommended)

## Your decision (Part 3)

- [x] **Approve**: go with Option A
- [ ] **Not approve**
- [ ] **Other**

---

## What was built (2026-10-10)

- **Drawn buildings:** 12 new folders in `assets/buildings/`: `loschert_hall`, `alumni_court_south`, `queens_court`, `faber_hall`, `loyola_hall`, `martyrs_court`, `martyrs_court_west`, `conley_salice`, `ohare_hall`, `tierney_hall`, `finlay_hall` and `walsh_hall`.
  - They're drawn by `assets/buildings/_style/draw_residence.py`, using the shared kit.
  - Every hall except Martyrs' Court's west wing has a card picture.
- **Map:** the tiles are unchanged. The door objects now come from the building files.
- **Code:**
  - `game/gfx/building_overlay.py` matches each plaque to its block.
  - `game/app.py` gives each card the picture from the block that has one.
  - New test: `test_a_place_drawn_as_several_buildings_has_one_card_picture`.
- **Cards:** new text for all eleven halls.

## To confirm with Fordham

- Which halls are first-year and which are upperclass this year (this changes from year to year).
- Martyrs' Court's wing names (Jogues, Lalande, Goupil), and which wing the clock tower is on.
- Loyola Hall's program (Manresa).
- Whether O'Hare still houses the student services listed on its card.
