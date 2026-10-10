# Fordham Campus Quest

A Pokémon-style, top-down pixel game where new Fordham students explore campus and find its resources. It's built with [Pyxel](https://github.com/kitao/pyxel).

**Status:** Milestone 2 (Real Rose Hill). The whole Rose Hill campus is one walkable map, laid out from the official campus map. The game opens with a short, skippable intro: you ride Metro-North to Fordham station, walk to the Third / Webster Avenue gate, learn the controls, then walk up to the gate, where Bert the guard checks your Fordham ID (tap your card, or your phone with Apple Wallet or Google Wallet). An Orientation Leader greets you inside. Area names pop up as you walk, and you can talk to students and open a card for any building, landmark, shuttle stop or gate. Art is placeholder art drawn in code. Building interiors are deferred (decision 0012).

## Run it

You need [uv](https://docs.astral.sh/uv/) installed (`brew install uv` on macOS). uv installs Python 3.12 and Pyxel for you.

```bash
uv sync                          # first time only: creates .venv with Python + Pyxel
uv run python main.py            # play
uv run pyxel watch . main.py     # play with auto-reload when files change
uv run pytest                    # run tests (also validates map content)
uv run python tools/capture.py   # headless run, saves screenshots to build/screenshots/
uv run python tools/render_map.py  # whole map as one picture: build/map_rose_hill.png
```

**Controls:**
- Arrows or WASD move.
- **Z**, Space or Enter talks to people and reads signs.
- **X** skips text, closes a card, or skips the intro.
- **M** opens the campus map. Arrow keys jump between places, Z shows a place's card, and M or X closes it.
- Up and Down scroll a long card.
- Esc quits.

## Where things live

| Path | What |
|---|---|
| `ARCHITECTURE.md` | The overall plan: layers, gameplay loop, milestones |
| `decisions/` | **Decisions for review.** Each one has options, a recommendation, and Approve / Not approve / Other boxes |
| `content/maps/*.txt` | Maps as text grids (see the legend in `game/world/tiles.py`) |
| `content/maps/*.json` | Area names, plus everything placed on the map: NPCs and what they say, signs, landmarks, doors |
| `content/intro.json` | The opening sequence: captions, how long each stays up, and the controls card. Edit the text here |
| `content/locations.json` | Building cards: name, type, description, what's inside. Will feed the Campus Guide in M3 |
| `assets/fonts/` | The reading font (PixelMplus 12, free M+ license, decision 0018) |
| `research/` | The official Rose Hill campus map and notes taken from it |
| `game/` | Engine code: `scenes/` (title, overworld, dialogue), `world/` (map, movement, camera), `systems/` (input), `gfx/` (placeholder art) |
| `tests/` | Unit tests plus content checks (`test_content.py`: every map loads, everything is reachable, every door has a building card) |
| `tools/capture.py` | Scripted headless playthrough that saves screenshots |
| `tools/render_map.py` | Draws a whole map as one picture, to compare with the real campus map |

## Editing the map

`content/maps/rose_hill.txt` is the map. Each character is one 16×16 tile:

- **Ground:** `.` grass, `:` walkway or sidewalk, `*` flowers, `P` parking
- **Roads** (decision 0016): `=` road, `X` crosswalk on a left-right road, `Y` crosswalk on an up-down road
- **Buildings:**
  - Roofs show the building type: `R` academic (slate), `O` residence hall (orange), `G` other campus building (gray), `M` Admission (maroon)
  - Walls: `W` wall, `w` window, `B` banner, `D` door
  - Walsh Library (faces north): `S` stone, `A` glass-arch entrance, `s` upper windows, `t` tower
  - Campbell Hall (modern): `Q` flat roof, `q` dark brick wall, `g` glass stair tower, `J` glass entrance
  - Entrances (`D`, `A`, `J`) each need a door object in the `.json`
- **Outdoors:** `T` tree, `h` hedge, `b` bench, `L` lamp, `~` water, `F` athletic field, `d` infield dirt, `+` graves
- **Edges:** `|` campus fence, `I` gate pillar, `K` guard booth, `#` off campus
- **Player start:** `@`

Everything you can talk to or inspect goes in `content/maps/rose_hill.json` under `"objects"`, placed by `"at": [x, y]` tile coordinates. Column 0 is the left edge and row 0 is the top. An object can be:

- **A door:** sits on a `D` tile and has a `"location"`.
- **A sign or landmark:** has a `"tile"` to draw, plus a `"location"` or some `"lines"`.
- **An NPC:** has a `"name"`, a `"sprite"`, a `"facing"` and `"lines"`.

`"location"` ids refer to entries in `content/locations.json`, which is where the text of every building card lives. `"areas"` are the named rectangles that trigger the banner when you walk into them. When several overlap, the first one listed wins.

Run `uv run pytest` after editing. It catches ragged rows, unknown characters, unreachable NPCs, doors without a card, and typos in location ids.
