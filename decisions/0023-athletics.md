# D-0023: Athletics: the fields, the stadium, the gym, McShane and Lombardi

| | |
|---|---|
| **Status** | Approved, all parts Option A (2026-10-10). You asked me to find photos online, tick the boxes myself and keep going batch by batch; you'll review at the end |
| **Raised** | 2026-10-10, batch 1 of 3 (athletics, then residence halls, then academic and other buildings) |
| **Affects** | The north side of campus between Murphy Field and Jack Coffey Field; nine new drawn assets; new building cards |
| **Built?** | Yes, the same day |

## How the photos were found

This workspace can't download images, so I used the browser in the Claude app on your Mac:
- **Wikimedia Commons**, through its API: the categories for Jack Coffey Field, Murphy Field, Rose Hill Gymnasium, the McGinley Center and Fordham Rams baseball. These photos have free licenses, recorded per photo in each building's notes.
- **Image search** for buildings Commons doesn't cover well (the 2021 McShane Campus Center, Lombardi's expansion, the softball complex).
- **Facts** from Wikipedia (Coffey Field, Houlihan Park, Rose Hill Gymnasium), Fordham news (the McShane dedication, the Murphy Field renovation), the field builder's project page and Fordham Prep's facilities page.

Screenshots of the photos I traced from are in `research/images/web/`, listed in `SOURCES.md`.

## What I learned

| Place | What it's like |
|---|---|
| **Jack Coffey Field** | The football and soccer field, FieldTurf since 2005. **Moglia Stadium** is its 7,000-seat grandstand, with the press box (FORDHAM in maroon) along the north sideline. **Houlihan Park**, the baseball field (about 1,000 seats), is on the far side |
| **Murphy Field** | A lit turf field for soccer and football practice, side by side with **Bahoshy Softball Field**. You enter through a stone **MURPHY FIELD archway** with iron gates and a bust of Cornelius Murphy. The six **Hawthorn/Rooney tennis courts** are beside it |
| **Rose Hill Gymnasium** | Home of Fordham basketball since 1925, with about 3,200 seats: the oldest on-campus arena still used by a Division I team. It has a light fieldstone Gothic front, a crenellated parapet, and a tall pointed-arch window with a stone cross above three wooden doors. Behind it is a big arched roof with clerestory glass. The **Victory Bell** stands outside |
| **McShane Campus Center** | **Rebuilt in 2021** where the beige, arched McGinley Center stood. Your 2013 photo shows the old building. The new one has tall limestone walls with vertical fins and windows, plus a glass atrium tower. The Marketplace inside is the main dining hall |
| **Lombardi Memorial Center** | Named for Vince Lombardi. It has the pool and a fieldhouse with an **indoor 220 m track** (so the campus track is indoors). The expansion is in gray ribbed metal |

---

# Part 1: Fields and the stadium as drawn landmarks

### A. Draw them, re-laid around Jack Coffey Field (recommended)

- **Moglia Stadium** becomes the grandstand along the north side of the field, instead of a small building beside it. **Houlihan Park** is now its own place, just south of the field, with a walkway between the two.
- **Murphy Field** (with its archway), **Bahoshy** and **the tennis courts** stay where they were, now drawn.
- All six are landmarks: no door; a sign on the edge of each opens its card.

### B. Keep plain green field tiles

- **Cons:** Every field looks the same.

## Your decision (Part 1)

- [x] **Approve**: go with Option A
- [ ] **Not approve**
- [ ] **Other**

---

# Part 2: Rose Hill Gym, McShane and Lombardi as drawn buildings

### A. Draw all three in the house style, McShane as the 2021 building (recommended)

Same places and doors as now, south-facing.

### B. Draw McShane as the old McGinley Center (your 2013 photo)

- **Cons:** That building no longer looks like that.

## Your decision (Part 2)

- [x] **Approve**: go with Option A
- [ ] **Not approve**
- [ ] **Other**

---

# Part 3: Building cards

### A. New and updated cards (recommended)

- New cards: Houlihan Park, Murphy Field, Bahoshy Softball Field, the tennis courts.
- Updated text: Jack Coffey Field, Moglia Stadium, the gym, McShane and Lombardi.
- Card pictures: the field, the press box, the Murphy archway, the gym, McShane and Lombardi.

## Your decision (Part 3)

- [x] **Approve**: go with Option A
- [ ] **Not approve**
- [ ] **Other**

---

## What was built (2026-10-10)

- `assets/buildings/` has nine new folders: `lombardi_center`, `mcshane_center`, `rose_hill_gym`, `moglia_stadium`, `jack_coffey_field`, `houlihan_park`, `murphy_field`, `bahoshy_field` and `tennis_courts`. They're drawn by `assets/buildings/_style/draw_athletics.py`, using the shared `_style/kit.py`.
- Map:
  - Moglia's old building and the plain field tiles are gone.
  - A walkway runs between Jack Coffey Field and Houlihan Park.
  - A path leads from Murphy Field's archway to the walkway past Lombardi.
- `content/locations.json` has 4 new places and 5 updated ones.

## To confirm with Fordham

- The press box sideline and Houlihan Park's position relative to the football field.
- That the tennis courts are the six Hawthorn/Rooney courts next to Murphy Field.
