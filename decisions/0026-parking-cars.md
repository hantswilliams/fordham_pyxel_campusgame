# D-0026: Cars in the parking lot and on the garage

| | |
|---|---|
| **Status** | Built 2026-10-10 at your request. Review the boxes below |
| **Raised** | 2026-10-10. You asked for cars in the flat parking lot, cars on the garage roof, and visuals for the garage's ramps and stairwells |
| **Affects** | The surface lot by the Main Entrance; the Regional Parking Facility; a new map tile; a new place card |

---

# Part 1: Parked cars you can't walk through

### A. A new `c` "parked car" tile (recommended, built)

- **The lot:** the cars are solid, so you walk round them down the drive aisles. Empty stalls stay walkable.
- **The tile:** its stand-in art is a red car on asphalt, and it shows gray on the campus map like the rest of the lot.
- **The drawing:** `assets/buildings/parking_lot/` paints the cars over the tiles in a dozen colors, facing their aisles. It also adds stall lines, aisle arrows and a blue **P** sign by the entrance.

### B. Cars as decoration only

- **Cons:** You would walk straight over them.

## Your decision (Part 1)

- [x] **Approve**: go with Option A
- [ ] **Not approve**
- [ ] **Other**

---

# Part 2: The garage as a drawn building

### A. Draw the Regional Parking Facility (recommended, built)

**The top deck has:**
- parked cars in four rows, with a few empty stalls
- light poles
- a striped **down ramp** with arrows along the east side
- a **stair / elevator tower** in the north-west corner

**The front has:**
- two open parking levels with cars inside
- a **glass stair tower** at the corner
- the pedestrian doors, the old door positions
- the **car entrance** with its striped barrier arm and a **P** sign

I found no photo of this garage (D-0025), so it's drawn from the campus map and the usual look of a parking garage. Swap in a photo any time.

## Your decision (Part 2)

- [x] **Approve**: go with Option A
- [ ] **Not approve**
- [ ] **Other**

---

# Part 3: A card for the lot

### A. Add a "Parking Lot" place (recommended, built)

- The lot is a landmark with a sign by its entrance, so it gets its own card.
- The card says parking needs a Fordham permit and visitors check in at the gate. **Fordham should confirm this.**
- It's a transit pin on the campus map.

## Your decision (Part 3)

- [x] **Approve**: go with Option A
- [ ] **Not approve**
- [ ] **Other**

---

## What was built

- **Tile:** `game/world/tiles.py` (tile 42), `game/gfx/placeholder_art.py` and `game/world/minimap.py`.
- **Drawings:**
  - `assets/buildings/parking_lot/`: a landmark, with no card picture.
  - `assets/buildings/regional_parking/`: has a card picture with the Ram Van out front.
  - `assets/buildings/_style/draw_parking.py`, with the new `car()` and `p_sign()` helpers in `kit.py`.
- **Map:** the lot's car cells, and the lot's sign at (82, 34). The garage's doors now come from its building file.
- **Cards:** the new `parking_lot` place in `content/locations.json`.
