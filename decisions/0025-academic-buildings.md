# D-0025: Academic and other buildings, drawn from photos found online

| | |
|---|---|
| **Status** | Approved, all parts Option A (2026-10-10). You asked me to find photos online, tick the boxes myself and keep going batch by batch; you'll review at the end |
| **Raised** | 2026-10-10, batch 3 of 3 (athletics, residence halls, then academic and other buildings) |
| **Affects** | Eight new drawn buildings; card pictures and card text; three places left as they are for want of good photos |
| **Built?** | Yes, the same day |

## How the photos were found

The method was the same as D-0023 and D-0024:
- **Wikimedia Commons categories** covered University Church, Collins Auditorium, Thebaud, Freeman, Spellman, Larkin, Mulcahy, Duane Library, the William Spain Seismic Observatory and the cemetery.
- **Facts** came from Wikipedia ("Campuses of Fordham University").
- **Image search** found nothing reliable for Faculty Memorial Hall or the Regional Parking Facility: the results showed other buildings.

The screenshots I traced from are in `research/images/web/` (`academic_*.jpg`).

## What I learned

| Building | What it looks like | Facts |
|---|---|---|
| **University Church** | Gray fieldstone Gothic Revival. A square bell tower with pinnacles stands over the pointed-arch door, and an octagonal lantern sits over the crossing | 1845. Its altar came from Old St. Patrick's Cathedral, and some of its glass was a gift from King Louis Philippe |
| **Collins Hall** | Red brick with a white limestone classical front: columns, a pediment and three arched doors | 1904. Collins Auditorium, theatre, philosophy |
| **Thebaud Hall** | Cream stone, green copper mansard roof with white dormers, beside the tall old smokestack | 1886, the first science building |
| **Freeman Hall** | Gray Collegiate Gothic fieldstone | 1930, built for physics |
| **Larkin Hall** | Gray Collegiate Gothic with a central tower | 1927, built for biology |
| **Spellman Hall** | Red brick with stone trim, three storeys | 1946, Jesuit residence with St. Robert Bellarmine Chapel |
| **Mulcahy Hall** | Brown brick between white concrete piers, tall window strips | 1969, chemistry |
| **Duane Library (Admission)** | Gray Collegiate Gothic, central tower with a tall tracery window | 1926. The library until 1998; now Admission and theology |
| **Seismic Observatory** | A small, flat-roofed gray stone block (not a dome) | 1931 |

---

# Part 1: Draw eight academic buildings on their existing footprints

### A. New art, same footprints and doors (recommended)

These are University Church, Collins, Thebaud, Freeman, Larkin, Spellman, Mulcahy and Duane Library.
- **Thebaud's smokestack** and **Duane's tower** rise just above their roof lines.
- **Duane (Admission) stays maroon on the campus map**, so it still stands out as the place to start a tour, even though the building itself is gray stone.

## Your decision (Part 1)

- [x] **Approve**: go with Option A
- [ ] **Not approve**
- [ ] **Other**

---

# Part 2: Places without good photos

These are Faculty Memorial Hall, the Regional Parking Facility, and the Seismic Observatory's small sign tile.

### A. Leave them as they are for now (recommended)

I'd rather not invent how they look. They keep the restyled tile look (D-0021).
- If you drop photos of Faculty Memorial Hall and the parking garage into `research/images/`, I'll draw them the same way.
- The observatory photo shows a flat-roofed stone block, so its map tile should change from a dome. That's a one-tile change, best done with the next landmark pass (statues, the Victory Bell, the cemetery).

### B. Draw them from my best guess

- **Cons:** They might not look like the real buildings.

## Your decision (Part 2)

- [x] **Approve**: go with Option A
- [ ] **Not approve**
- [ ] **Other**

---

# Part 3: Card pictures and text

### A. A card picture for each of the eight, and new text with the facts above (recommended)

## Your decision (Part 3)

- [x] **Approve**: go with Option A
- [ ] **Not approve**
- [ ] **Other**

---

## What was built (2026-10-10)

- **Drawn buildings:** 8 new folders in `assets/buildings/`: `university_church`, `collins_hall`, `thebaud_hall`, `freeman_hall`, `larkin_hall`, `spellman_hall`, `mulcahy_hall` and `admissions`.
  - They're drawn by `assets/buildings/_style/draw_academic.py`.
  - Each has a card picture.
- **Map:** the tiles are unchanged. The door objects now come from the building files.
- **Cards:** new text for all eight.
  - The Admission card now says it's "marked in maroon on the campus map", instead of calling it "the maroon building".
- **Tests:** the minimap test now looks up Admission's door rather than its first object.

## To confirm with Fordham

- The Public Safety Office's location (the card puts it in Thebaud Hall).
- Collins Hall's departments (theatre, philosophy).
- Mulcahy's use (chemistry).
