# D-0040: Keys in the top bar, people who walk about, and the bike rack

| | |
|---|---|
| **Status** | Built 2026-10-13 on branch `campus-life`, for your review |
| **Raised** | 2026-10-13. Tell players about Tab and M in the top bar; have some people walk back and forth like in Pokémon; move the bike rack to the west side of Walsh Library and make it look more like a bike rack |
| **Affects** | The web page's top bar, the people on the campus map, and the bike rack by Walsh Library |
| **Built?** | Yes, all three, on branch `campus-life` |

**Pictures** (in `decisions/images/0040/`):
- `top_bar.png`: the bar while playing
- `bike_rack.png`: the rack today and proposed, close up

---

# Part 1: Tab and M in the top bar

The bar now reads:

> **Accessible version: Rose Hill Campus Guide** (opens in a new tab) · Tab: missions · M: map · Esc: leave the game · Playing · [Play with the keyboard]

"Playing" changes to the yellow "Game paused: click the game to keep playing." when the game doesn't have the keyboard (see the follow-up in decision 0039). On a narrow window the bar wraps onto more lines, and the game moves down to fit.

## Your decision (Part 1)

- [ ] **Approve**
- [ ] **Not approve**: say why
- [ ] **Other**: describe below

**Your notes:**

>

---

# Part 2: People who walk about

### A. Six students stroll near their spot (recommended; built)

**Who walks:**
- the Junior by McShane
- the Senior by O'Hare
- the Sophomore by Walsh Library
- the Sophomore at the shuttle stop (1 tile, so they stay by the sign)
- the Commuter by the Webster Avenue gate
- the First-Year on Martyrs' Lawn

Each stays within 2 tiles of where they start.

**Who stays put:** the Orientation Leaders, Bert at the gate, the Public Safety staff member, and anyone who gives you a mission. You need to find them reliably, and some start talking when you walk up.

**How they move:**
- Every 1½ to 5 seconds a person takes a step at half your walking pace, or just turns to look around.
- They only step onto lawns and walkways: never roads, crosswalks or parking, never in front of a door, and never into you.
- You can talk to someone mid-step. They stand still while a text box or menu is open.
- When you reload the game, everyone is back at their starting spot.

**Pros:** campus feels alive, and nobody can block your way for long.

**Cons:**
- A walking person can briefly stand in your path. They move on within a few seconds.
- The screenshot tool keeps people still, because its walks are planned ahead of time.

### B. Everyone except Bert walks about
- **Pros:** livelier still.
- **Cons:** the Orientation Leaders' welcome at the gate depends on standing next to them, and mission givers are harder to find when they move.

## Your decision (Part 2)

- [ ] **Approve**: A
- [ ] **Not approve**: say which option you'd prefer, or who should or shouldn't walk
- [ ] **Other**: describe below

**Your notes:**

>

---

# Part 3: The bike rack

**Moved:** the rack is now on the lawn on the west side of Walsh Library, where your screenshot had the player, beside the walkway and the shuttle-stop sign.

**Redrawn:** each of the two rack tiles shows:
- a light metal hoop (an upside-down U) on a concrete pad
- a maroon bike parked against it, seen side on, with two wheels, a frame, a seat and handlebars

Side by side they read as a rack of two bikes. Before, the bikes were seen from above, which made them hard to make out.

**Unchanged:** it still says "A bike rack outside Walsh Library", and the Bike Courier mission's hint still fits.

## Your decision (Part 3)

- [ ] **Approve**
- [ ] **Not approve**: say why
- [ ] **Other**: describe below, for example a different spot, or changes to the drawing

**Your notes:**

>

---

## What was built (2026-10-13, branch `campus-life`)

- **`tools/build_web.py`:** "Tab: missions · M: map · Esc: leave the game" in the bar, plus a short "Playing" / "Game paused" status.
- **`game/world/wander.py` (new):**
  - people with `"wander": n` in the map take a step now and then, within n tiles of home
  - while stepping they hold both cells, so you can't walk into them
  - each has its own random generator seeded from their spot, so every run plays the same way
- **`game/world/mapdata.py`:** the `wander` field, plus `begin_move` / `end_move`.
- **`game/scenes/overworld.py`:** moves the walkers each frame and draws them mid-step with walking legs, and their "!" bubbles follow them.
- **`content/maps/rose_hill.json`:**
  - `"wander"` on the six people above
  - the two rack tiles moved from (20, 71) and (21, 71) to (3, 68) and (4, 68)
- **`game/gfx/placeholder_art.py`:** the new rack drawing.
- **Tests:** 273 pass. The new `tests/test_wander.py` checks that walkers:
  - stay near home on open ground
  - never block a door
  - never walk into the player
  - hold both cells mid-step
  - play out the same way every run

  The rack test now allows the library's west side.
- **Speed:** about 4 ms a frame on campus, the same as before.
