# D-0033: What's outside the fence

| | |
|---|---|
| **Status** | Built 2026-10-11 at your request. Review the boxes below |
| **Raised** | 2026-10-11. You asked to replace the blue squares around the campus with what Google Maps shows to the north, south, east and west: buildings, roads, trees and so on, so play feels more real |
| **Affects** | What you see beyond the campus fence, in the game and on the campus map (M). Nothing you can walk on has changed |

## What changed

Everything outside the fence used to be navy squares. It is now painted with the neighbourhood, laid out by eye from `research/images/google_map_view.png`.

**North-west**
- Metro-North's Harlem Line in its gravel cutting, with a silver train.
- **Webster Avenue** running up beside it.
- Apartment blocks with NYC water towers beyond.
- Between Webster Avenue and the fence: **Fordham Prep** and **Prep Field**.

**North and east**
- **Southern Boulevard** runs right along the fence, with traffic and a bus. The main gate on Xavier Way joins it.
- Beyond it is the **New York Botanical Garden**: woods with a few autumn trees, lawns, winding paths and a pond.
- Across from the stadium is the **Enid A. Haupt Conservatory**, with its glass Palm Dome, wings and reflecting pool.

**East edge**
- Bronx Park woods.

**South**
- **East Fordham Road**: four lanes with a double yellow line, traffic and a Select Bus.
- A wide sidewalk with street trees and people along the campus side, and shops with coloured awnings.
- The street from the south-east gate down to the road.
- Shops and apartment houses on the far side.

**West edge**
- Webster Avenue, down to the Webster Avenue gate.

**Street signs:** green street-name signs, like NYC's, label Webster Ave, Metro-North, Fordham Prep, Southern Blvd, the Haupt Conservatory, the NY Botanical Garden and E Fordham Rd.

**How it's made**
- It is one picture the size of the map, drawn by `assets/surroundings/draw_surroundings.py`, the same way the drawn buildings are made.
- It's painted only over off-campus cells. A test checks that it never covers a campus cell and that every off-campus cell is covered.
- The game draws it under the buildings and characters. The campus map (M) and `tools/render_map.py` include it too.

**Limits:** the map is a grid with little room outside the fence, so roads are straightened and distances squeezed. It's a likeness, not a survey.

---

# Part 1: How the outside is shown

### A. A painted backdrop you can't walk into (recommended, built)
- **Pros:** Looks like the real neighbourhood, with diagonal roads, woods and the conservatory. Nothing about walking, missions or the gates changes.
- **Cons:** You can see the streets but can't go out onto them.

### B. Real tiles, so you can walk out through the gates onto the streets
- **Pros:** More to explore.
- **Cons:** It's a much bigger job. The map has no room beyond its edge, so the streets would stop after a tile or two. It also needs rules for leaving campus, and onboarding is about the campus.

### C. Keep the navy squares
- **Pros:** Nothing to maintain.
- **Cons:** The edges look empty, which is what prompted this.

## Your decision (Part 1)

- [ ] **Approve**: go with Option A
- [ ] **Not approve**: say which option you'd prefer, or why
- [ ] **Other**: describe below

**Your notes:**

>

---

# Part 2: Street-name signs

### A. Green NYC-style signs on the streets and places (built)
### B. No signs, just the scenery

## Your decision (Part 2)

- [ ] **Approve**: keep the signs (A)
- [ ] **Not approve**: take them out (B)
- [ ] **Other**: e.g. different names or places to label

**Your notes:**

>

---

## What was built

- `assets/surroundings/draw_surroundings.py` draws `rose_hill.png`. `notes.md` lists what's on each side.
- `assets/surroundings/rose_hill_labels.json` holds the street-name signs.
- `game/gfx/surroundings.py` loads and draws the scenery and the signs. It's used by the overworld and `map_render.py`.
- `tests/test_surroundings.py`: the scenery stays off campus and covers every off-campus cell, and the signs sit off campus.

**Still to confirm:** whether the Fordham Prep buildings and Prep Field should count as campus (and be walkable) rather than scenery.
