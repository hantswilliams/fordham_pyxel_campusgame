# D-0019: Bigger intro characters, a detailed southwest corner, and a realistic Walsh Library

| | |
|---|---|
| **Status** | Approved, all three parts Option A (2026-10-09). Built the same day |
| **Raised** | 2026-10-09, from your new photos in `research/images/` (added 7:52–8:35pm) |
| **Affects** | Part 1: the intro scenes. Part 2: the map around the Webster Ave gate, Campbell, Walsh Library, Larkin, Ram Van stops. Part 3: Walsh Library's art |
| **Built?** | Yes. Part 1: `game/gfx/intro_art.py`. Part 2: `content/maps/rose_hill.*`, `content/locations.json`. Part 3: new tiles in `game/world/tiles.py` and `game/gfx/placeholder_art.py` |

**Source images used:**

| Image | What it shows |
|---|---|
| `person_shouldbe_bigger.png`, `person_shouldbe_bigger_intrain.png` | Screenshots of the station and train scenes: characters look tiny next to the doors and seats |
| `zoomin_southwest.png` | Close-up of the official map's southwest corner |
| `Walsh-1078_lookingSouth.jpg` | Walsh Library seen from Walsh Lawn, looking south |
| `campbell_dorms_facingWest.png` | Campbell Hall (new residence hall), looking west |
| `dealey_hall_facingEast.png`, `rosehill_manor_drive_facingNorth.png` | Dealy Hall and Rose Hill Manor Drive (notes for later, see the end) |

---

# Part 1: Bigger characters in the intro

## What's being decided

In the train and station scenes, people are drawn with the same 16×16-pixel sprites as the top-down campus. On a 256×192 side-view scene they look like toys next to the train doors and seats (your two screenshots). How should we make them bigger?

## Options

### A. Draw intro characters at 2× in all three intro scenes, and re-proportion the scenery (recommended)
- People become 32×32 pixels: about the height of the train door's windows, and filling a seat properly.
- Seats, doors, the platform and the gate are resized to match.
- Applies to the **train, station and Webster Avenue street** scenes, so the player is the same size throughout the intro, including standing next to Bert.
- **Pros:**
  - Fixes the problem everywhere at once.
  - Keeps the chunky pixel look.
  - Small change (about an hour or two).
- **Cons:** The 2× sprites are a bit blocky up close. Option C polishes that later.

### B. 2× only in the train and station scenes (exactly the two screenshots)
- **Pros:** The smallest change.
- **Cons:** The player shrinks again on Webster Avenue, which looks like a bug.

### C. New, larger hand-drawn side-view character art for cutscenes (for example 24×40 pixels)
- **Pros:** The best-looking result, with room for faces, a backpack, Bert's uniform and cap.
- **Cons:** New art for every character in the intro. Fits the art pass (D-0008) better than now.

## My recommendation (Part 1)

**Option A now, C at the art pass.** It's a quick fix that makes the intro read properly, and A's scene re-proportioning carries over unchanged if we later swap in C's sprites.

## Your decision (Part 1)

- [x] **Approve**: go with Option A (Option C later, at the art pass)
- [ ] **Not approve**: say which option you'd prefer, or why
- [ ] **Other**: describe below

**Your notes:**

>

---

# Part 2: A more detailed, accurate southwest corner

## What's being decided

The southwest corner is the first part of campus every player sees, so it should be the most accurate. Comparing the game with `zoomin_southwest.png` turned up these differences:

| # | Today in the game | What the map and photos show | Proposed change |
|---|---|---|---|
| 1 | **Walsh Library** faces south, with its doors on the south wall | The entrances face **north, onto Walsh Lawn**, the inner part of campus | Move the library's entrances to its **north side** (see Part 3 for how it looks) |
| 2 | A **walkway runs along the south side of the library**, between it and the fence | **No walkway there**: just lawn between the building and the fence | Remove it. The south side becomes lawn and trees up to the fence |
| 3 | The library is a plain rectangle | A tower block at the northwest plus a long wing toward the southeast | Reshape the footprint to match (tower block and wing) |
| 4 | No path to the library's front | Walkways reach the north entrance from Old Elm Road and Walsh Lawn, and from the library's east end toward Larkin | Add a walkway along the north façade, joined to Old Elm Road, Mill River Road and the Walsh Lawn paths |
| 5 | **Larkin Hall** faces south, onto the walkway being removed | Paths reach Larkin from the **north** | Move Larkin's entrance to its north side, on the same walkway |
| 6 | **Campbell Hall** is a generic orange-roof hall with a door on the south | **New residence hall:** a long building between **Archer Drive** (west) and **Mill River Road** (east). The dining entrance faces **east** across Mill River Road. The photo shows modern dark brick, a glass stair tower, and a stepped plaza with birch trees | Campbell gets its **entrance on the east side**, facing Mill River Road, with a crosswalk to the lawn paths. It's drawn as a modern dorm (dark brick, a glass-tower strip), so it doesn't look like the older halls |
| 7 | No **Archer Drive** | Archer Drive runs down the west side of Campbell and curves east to meet Mill River Road near the Webster gate | Add Archer Drive as a road, with its curve into Mill River Road |
| 8 | Ram Van stops by Dealy, Cunniffe, Alumni Court and the parking garage | The close-up also shows stops at the **Mill River Rd / Old Elm Rd junction** and on **Mill River Road by the Webster gate** | Add those two stops (and confirm with Fordham, since the full PDF map didn't show them) |
| 9 | The Admission card says "Office of Undergraduate Admission" | The building is labeled **Duane** (Duane Library), with Admission inside | Rename the card to **"Duane Library: Office of Undergraduate Admission"** |

**Rough sketch of the proposed layout** (north is up, not to scale):

```
 fence  Archer  Campbell (new)   Mill River        Walsh Lawn                 Duane /
   |     Dr.    [modern dorm]E <-> Rd.  V   Old Elm Rd  ------------------->  Admission
   |      =     [  glass  ]        =   /
   |      =     [ tower   ]        =  /
   |       \                       = :: walkway along the library's north façade ::::: [Larkin]
   |        \=======>  V           =  [ ENTRANCES | ENTRANCES | ENTRANCES ]             entrance
   |                               =  [        WALSH LIBRARY      (tower)  ]            on north
   |                               =  [ lawn behind it, no walkway         ]
   |-------------------- I [gate] I ----------------------------------------------- fence
                          Bert
```

**What stays the same:** you still start outside the Webster Ave gate, Bert still checks your ID, and the Orientation Leader still greets you just inside. From there, the walk to the library is up Mill River Road and east along the library's front, which is how you'd really do it.

## Options

### A. Rebuild the southwest corner with all nine changes above (recommended)
- **Pros:** The opening area matches what students will actually see when they walk in from the train.
- **Cons:**
  - About half a day.
  - Ram Van stops 8 and the "Duane" name (9) should be confirmed with Fordham.

### B. Only fix the library: entrance on the north, no south walkway (changes 1–4)
- **Pros:** Smallest change.
- **Cons:** Larkin would be left facing a walkway that no longer exists, and Campbell and Archer Drive stay inaccurate.

### C. Option A, and also apply "entrances face where they really are" to every building now
- For example, your photos show **Dealy's** columned entrance faces **west** onto Rose Hill Manor Drive, and **Cunniffe House** faces **east**.
- **Pros:** The most accurate campus.
- **Cons:** Needs a photo or map check for every building, and much more work. Better done gradually as photos come in.

## My recommendation (Part 2)

**Option A now, and C gradually.** Each time you add photos of a building, I'll put its entrance on the right side, starting with Dealy and Cunniffe, which your photos already cover.

**About the top-down view:** in Pokémon-style maps, buildings usually show their *south* wall. A building whose front faces north (like the library) is drawn with its **façade on its north edge**. When you stand on the lawn north of it, *facing south*, you see the entrances, as you described. It looks slightly different from the other buildings on purpose: it tells players "this side is the front."

## Your decision (Part 2)

- [x] **Approve**: go with Option A (and C gradually, as photos come in)
- [ ] **Not approve**: say which option you'd prefer, or why
- [ ] **Other**: describe below

**Your notes:**

>

---

# Part 3: Make Walsh Library look like the real building

## What's being decided

`Walsh-1078_lookingSouth.jpg` shows the library from Walsh Lawn:
- a wide **light gray stone façade** with square stone piers
- a row of **tall, dark glass entrance arches** at ground level
- windows above
- a **tall slatted stone tower** rising above the middle

Today the library is a generic gray-roofed building. How closely should it match the photo?

## Options

### A. Custom library tiles that face north (recommended)
- New tiles:
  - **Stone façade:** light gray stone with piers.
  - **Glass-arch entrance:** tall dark glass framed in stone, used for the doors, so every arch is a way in.
  - **Upper windows.**
  - **Slatted tower:** drawn rising from the middle of the roof, the library's landmark.
- **Pros:**
  - Instantly recognizable from the lawn.
  - Only about 4 new tiles.
  - Combines with Part 2 (the north-facing entrance).
- **Cons:** Still a simplified, placeholder-quality version of a complex building.

### B. Keep the generic building, just move the door to the north side
- **Pros:** No art work.
- **Cons:** Doesn't look like Walsh Library, which you asked for.

### C. One large hand-drawn library picture (a multi-tile sprite) based on the photo
- **Pros:** The most faithful look.
- **Cons:**
  - Much more art.
  - Harder to change.
  - A bigger job that fits the art pass (D-0008).

## My recommendation (Part 3)

**Option A.** Matching the library is worth a few custom tiles because it's the first big building players reach and one they'll use all year. The same approach can later give other landmarks (Keating's tower, Campbell's glass stair tower) their own look.

## Your decision (Part 3)

- [x] **Approve**: go with Option A
- [ ] **Not approve**: say which option you'd prefer, or why
- [ ] **Other**: describe below

**Your notes:**

>

---

### Noted for later (no decision needed now)

- **Dealy Hall** (`dealey_hall_facingEast.png`): dark stone with white trim around arched windows, and a columned portico entrance that faces **west**, onto Rose Hill Manor Drive.
- **Rose Hill Manor Drive** (`rosehill_manor_drive_facingNorth.png`): tree-lined, with sidewalks on both sides and a **low post-and-rail fence** along Edwards Parade. A good detail for the art pass.
- **Campbell's plaza**: steps, birch trees and outdoor tables in front of the entrance. It can be suggested with a few tiles if Part 2 is approved.
