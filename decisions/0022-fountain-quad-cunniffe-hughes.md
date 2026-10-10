# D-0022: The fountain quad: Cunniffe House, Hughes Hall and the Cunniffe Fountain

| | |
|---|---|
| **Status** | Approved, all parts Option A (2026-10-10). You asked me to write this up, tick every box, and build it |
| **Raised** | 2026-10-10. You asked to update the area between Cunniffe House, Hughes Hall and Dealy Hall from your new photos, with the fountain in the centre between the three buildings |
| **Affects** | The map between Edgar Allan Poeway, Rose Hill Manor Drive and the walkway past Dealy; Cunniffe House and Hughes Hall become drawn buildings; the fountain becomes a drawn landmark; two new colors; building cards |
| **Built?** | Yes, the same day (see "What was built" at the end) |

**Photos used:** `Cunniffe_House,_2017.jpg`, `Carolyn_Dursi_Cunniffe_fountain,_Fordham.png`, `hughes_gabelli_hall.jpg`, `gabelli_hughes.jpeg` and `gabelli_hughes_2.jpg`, all in `research/images/`.

## What the photos show

| | |
|---|---|
| **Cunniffe House** | A three-storey centre block in gray stucco: cream stone surrounds on the windows, a white cornice and top storey, and a **white octagonal cupola with a cross**. Its arched front door has an iron grille, with lanterns either side. Lower **pink-brick wings** on both sides have white trim and arched ground-floor windows. Hedges and a lawn sit in front |
| **The Carolyn Dursi Cunniffe Fountain** | A tall, **tiered dark-bronze fountain** in a round stone basin, on a paved plaza **right in front of Cunniffe House**. Clipped hedges, yellow mums, benches and lamp bollards surround it |
| **Hughes Hall** | Home of the **Gabelli School of Business** (the name is on the doors). Five storeys of **dark fieldstone with white-trimmed arched windows**, a white cornice and a **sloped glass roof**. A modern **glass entrance under a teal glass canopy** has "HUGHES HALL" in metal letters. The **Ram statue** stands on the lawn out front |

## Today in the game

Cunniffe is a tall, narrow tile building west of a small 2 × 2 pond (the fountain), Hughes is a tile building to the north-east, and Dealy (drawn, D-0021) is to the south. The fountain isn't really in the middle, and nothing makes the space feel like the plaza in the photo.

---

# Part 1: A fountain plaza at the centre of the three buildings

### A. Rebuild the quad around a paved fountain plaza (recommended)

```
        Edgar Allan Poeway (road)
   :                         :  [ HUGHES HALL ]  =
   :                         :  [====door=====]  =  Rose
   : : : : : : : : : : : : : , , RAM , , , , ,   =  Hill
   :  [ CUNNIFFE  ]   , bench , ( FOUNTAIN ) bench  Manor
   :  [  HOUSE    ]   , , , , , (  basin   ) , = Drive
   :  [===door====]   , , , , , , , , , , , ,    =
   :  , , , , , , , , mums , , , , mums , ,      =
   :            [        DEALY HALL         ]    =
```

*Revised 2026-10-10 at your request:* Cunniffe House sits on the **left (west)**, centred between **Hughes Hall on top** and **Dealy Hall below**, with the fountain in the middle. Doors still face south (D-0021). Cunniffe's door opens onto a strip of paving along its front that joins the fountain plaza.

- **Cunniffe House** (5 × 4 tiles) is on the left, centred on the fountain. **Hughes Hall** (5 × 5) is on top. Both front doors open south onto the paving.
- **The plaza** is 7 × 6 tiles of stone paving between the three buildings, plus a strip along Cunniffe's front. The fountain is in the middle, level with Cunniffe's centre and lined up with Hughes and Dealy. Benches stand either side of the fountain, with mums by Dealy.
- **The Ram statue** stands in front of Hughes, as in the photo.
- **Dealy** is unchanged. It sits on the south side of the plaza, and its own door still faces south (D-0021).
- **Walkways:** a walkway between Cunniffe and Hughes joins the plaza to Edgar Allan Poeway. The existing path past Cunniffe's west side leads down to Dealy's door.

### B. Keep the buildings where they are; only move the pond to the middle

- **Pros:** Smallest change.
- **Cons:** It doesn't feel like the plaza in the photo, and Cunniffe still faces away from the fountain.

## Your decision (Part 1)

- [x] **Approve**: go with Option A
- [ ] **Not approve**: say which option you'd prefer, or why
- [ ] **Other**: describe below

---

# Part 2: Cunniffe House as a drawn building

### A. Draw it in the house style (recommended)

- **Map:** the gray stucco centre has cream window surrounds, a white cornice and the arched iron-grille door with lanterns. The white octagonal cupola and cross rise above the roof, its signature. Pink-brick wings either side have white trim and arched ground-floor windows.
- **Card:** the front as in the photo, with hedges, a lamp post and bare trees.
- **"In real life":** the front door faces east, onto the fountain.

### B. Keep the tile version, restyled

- **Cons:** Loses the cupola and the pink wings, which are what make it recognizable.

## Your decision (Part 2)

- [x] **Approve**: go with Option A
- [ ] **Not approve**
- [ ] **Other**

---

# Part 3: Hughes Hall as a drawn building

### A. Draw it in the house style (recommended)

- **Map:** tall, so the front shows almost all the way up. It has dark fieldstone with white-trimmed arched windows and a white cornice. The sloped glass roof shows as a teal strip at the top. The glass entrance sits under the teal canopy, its signature.
- **Card:** the front with the canopy, the arched windows, the glass roof and the Ram statue.
- **Text:** the card says it's home to the **Gabelli School of Business**.

### B. Keep the tile version, restyled

- **Cons:** Hughes would look like a generic hall, though it's one of the most photographed buildings on campus.

## Your decision (Part 3)

- [x] **Approve**: go with Option A
- [ ] **Not approve**
- [ ] **Other**

---

# Part 4: The fountain as a drawn landmark

### A. A drawn fountain, plus a picture on its card (recommended)

- **Map:** the round stone basin with water fills 2 × 2 tiles. The tiered bronze fountain rises above it with its spray. You can't walk through it; reading it opens its card.
- **Card:** the fountain in front of Cunniffe House, with hedges and benches.
- **Code:** drawn "buildings" can now be **landmarks** with no entrance, so the same asset folder, loader and gallery work for statues and fountains later too.

### B. Keep the plain 2 × 2 water tiles

- **Cons:** It doesn't read as a fountain.

## Your decision (Part 4)

- [x] **Approve**: go with Option A
- [ ] **Not approve**
- [ ] **Other**

---

# Part 5: Two more colors, for Cunniffe's pink brick

D-0021 noted that any further colors need a small decision. Cunniffe's wings are a soft salmon-pink brick. The closest existing colors are a bright pink and a light peach, and both look wrong.

### A. Add a pink brick and its shadow, bringing the extra colors from 8 to 10 (recommended)

- `c98a7c` pink brick
- `a5675e` pink brick shadow

They go in `palette.hex`, and the test limit rises to 10.

### B. Use the existing peach/orange

- **Cons:** Reads as orange plaster, not Cunniffe's brick.

## Your decision (Part 5)

- [x] **Approve**: go with Option A
- [ ] **Not approve**
- [ ] **Other**

---

## Facts to confirm with Fordham

- Cunniffe House is the original Rose Hill manor house and the oldest building on campus, and it holds administration offices. (The "Administration" sign by the fountain supports the last part.)
- Hughes Hall is home to the Gabelli School of Business (shown on its doors).
- The Ram statue's position in front of Hughes.

## What was built (2026-10-10)

- **Part 1: the plaza** (revised the same day so Cunniffe sits on the left, between Hughes and Dealy).
  - Hughes Hall (5 × 5) is on top and Dealy below. Cunniffe House (5 × 4) is on the left, centred on the fountain.
  - The fountain is in the middle of a 7 × 6 stone-paved plaza, with a strip along Cunniffe's front. A new **plaza** tile (`,` in the map legend) does the paving.
  - Benches flank the fountain, with mums by Dealy.
  - A walkway runs north of Cunniffe from the west walkway, and another runs beside Hughes up to Edgar Allan Poeway.
  - The Ram statue moved to the plaza in front of Hughes. Each building's signpost stands beside its door.
  - A new crosswalk leads east across Rose Hill Manor Drive to Edwards Parade. The path past Cunniffe's west side leads down to the walkway and Dealy's door.
- **Parts 2–4:** `assets/buildings/cunniffe_house/`, `hughes_hall/` and `cunniffe_fountain/`, each with a map drawing, a card picture and notes. They're drawn by `assets/buildings/_style/draw_fountain_quad.py`.
  - `building.json` now accepts `"landmark": true`, for an asset with no entrance; the fountain is the first.
  - Cunniffe's card has an **IN REAL LIFE** note: its front door faces east, onto the fountain.
- **Part 5:** two pink-brick colors were added (10 extra colors in all), plus `palette.hex`, with the test limit at 10.
- **Cards:** new text for Cunniffe House (the original manor house, now administration), Hughes Hall (home of the Gabelli School of Business), the fountain and the Ram statue.
- **Tests:** landmarks need no entrance but do need a sign on their cell.

