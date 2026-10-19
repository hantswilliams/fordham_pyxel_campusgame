# Fordham Campus Quest

A Pokémon-style, top-down pixel game where new Fordham students explore campus and find its resources. It's built with [Pyxel](https://github.com/kitao/pyxel).

**Status:** Milestone 2 (Real Rose Hill). The whole Rose Hill campus is one walkable map, laid out from the official campus map. The game opens with a short, skippable intro: you ride Metro-North to Fordham station, walk to the Third / Webster Avenue gate, learn the controls, then walk up to the gate, where Bert the guard checks your Fordham ID (tap your card, or your phone with Apple Wallet or Google Wallet). An Orientation Leader greets you inside. Area names pop up as you walk, and you can talk to students and open a card for any building, landmark, shuttle stop or gate. Most art is placeholder art drawn in code. Every building follows one house style taken from Pokémon Gold/Silver towns (decision 0021). Each has a roof over a front wall, with its door on the south side, a name plaque and a gray signpost. Walsh Library, Campbell, Dealy, Keating, Hughes Hall and Cunniffe House are drawn as whole pictures, as is the Cunniffe Fountain at the centre of its plaza (decision 0022), and each has a picture on its card (decision 0020). Building interiors are deferred (decision 0012). The art is being redrawn at twice the detail for a cleaner, less pixelated look (decision 0045); so far the campus (ground, trees, buildings, signs), the people, the bike and the vans, and the screens (boxes, cards, menus, the campus map, the title and the intro).

## Run it

You need [uv](https://docs.astral.sh/uv/) installed (`brew install uv` on macOS). uv installs Python 3.12 and Pyxel for you.

```bash
uv sync                          # first time only: creates .venv with Python + Pyxel
uv run python main.py            # play
uv run pyxel watch . main.py     # play with auto-reload when files change
uv run pytest                    # run tests (also validates map content)
uv run python tools/capture.py   # headless run, saves screenshots to build/screenshots/
uv run python tools/render_map.py  # whole map as one picture: build/map_rose_hill.png
uv run python tools/building_gallery.py  # review page for drawn buildings: build/building_gallery.html
uv run python tools/build_web.py   # web version for testing: build/web/index.html (decision 0034)
```

**In a browser (decision 0034):**
- `tools/build_web.py` packs the game into one HTML page that runs with Pyodide, using Pyxel's web runtime pinned to 2.9.9.
- Open `build/web/index.html`, or run `cd build/web && python -m http.server 8000` and visit http://localhost:8000.
- The first load needs internet and takes a few seconds.
- In the browser the game saves to that browser's local storage, so CONTINUE works after a reload, but only in that browser on that device.
- Every push to `main` rebuilds the page and publishes it to GitHub Pages (`.github/workflows/web.yml`). Turn that on once: in the repo's Settings, open Pages and set Source to "GitHub Actions".

**Accessibility (decision 0037):**
- The game's accessible version is the **Rose Hill Campus Guide**, built from the same content by `tools/build_guide.py` (`tools/build_web.py` runs it too). It goes into `build/web/guide/` and is published at `/guide/`. It covers:
  - every place, with directions from both entrances worked out from the map
  - the missions as checklists
  - the Ram Passport
  - the story and how to play
- The game page puts a link to the guide first.
- The game only takes the keyboard once you click it or press "Play with the keyboard". **Esc** hands it back to the page.
- Every push runs the tests and `node tools/check_accessibility.cjs build/web` (axe-core, WCAG 2.2 AA rules). A failure stops the publish.
- Before a release, also run the manual checklist in `docs/accessibility-checklist.md`.
- The accessibility statement's contact lives in `content/guide.json`.

**Controls:**
- Arrows or WASD move.
- **Z**, Space or Enter talks to people and reads signs.
- **X** skips text, closes a card, or skips the intro. Once you've borrowed a bike from the rack outside Walsh Library, X also hops you on or off it (decision 0030). Riding is twice as fast.
- **M** opens the campus map. Arrow keys jump between places, Z shows a place's card, and M or X closes it. A "!" pin marks where your current mission wants you.
- **TAB** opens the Mission Log and the Ram Passport (decision 0031). Left/Right switch tabs, Z opens a mission's full page (summary, checklist, hint, reward; Z there tracks or drops it), and M pins the mission bar on. By default the bar stays hidden for a clean screen: it pops up for a few seconds when your next step changes, and stays up during a timed ride.
- People with a **!** over their head have an optional mission for you. A **?** means a mission you're doing is waiting on them.
- The game saves as you go. With a save, the title screen offers **CONTINUE** or **NEW GAME**.
- Up and Down scroll a long card.
- Esc quits.

## Where things live

| Path | What |
|---|---|
| `ARCHITECTURE.md` | The overall plan: layers, gameplay loop, milestones |
| `decisions/` | **Decisions for review.** Each one has options, a recommendation, and Approve / Not approve / Other boxes |
| `content/maps/*.txt` | Maps as text grids (see the legend in `game/world/tiles.py`) |
| `content/maps/*.json` | Area names, plus everything placed on the map: NPCs and what they say, signs, landmarks, doors |
| `content/missions/` | **Missions** (decision 0031): one JSON file per mission, plus `_TEMPLATE.json` to copy and a README on how to write one. The First Week Checklist is `first_week.json` |
| `content/intro.json` | The opening sequence: captions, how long each stays up, and the controls card. Edit the text here |
| `content/locations.json` | Building cards: name, type, description, what's inside. Will feed the Campus Guide in M3 |
| `assets/buildings/` | **Drawn buildings** (decision 0020): one folder per building with its map drawing, card picture, footprint and notes. See its README for how to add one |
| `assets/fonts/` | Fonts, all free: M PLUS 1 Code (the reading font, decision 0038), DotGothic16 (the pixel reading font, decision 0036) and PixelMplus (map plaques) |
| `research/` | The official Rose Hill campus map and notes taken from it |
| `game/` | Engine code: `scenes/` (title, overworld, dialogue), `world/` (map, movement, camera, the ground under each cell), `systems/` (input, bike, missions, saved progress), `gfx/` (the campus drawn at twice the detail in `world_art.py`, decision 0045, and placeholder art) |
| `tests/` | Unit tests plus content checks (`test_content.py`: every map loads, everything is reachable, every door has a building card) |
| `tools/capture.py` | Scripted headless playthrough that saves screenshots |
| `tools/render_map.py` | Draws a whole map as one picture, to compare with the real campus map |
| `tools/building_gallery.py` | Builds one review page comparing each drawn building with its photo and its tile version |
| `tools/stamp_buildings.py` | Copies drawn buildings' footprints into the map file after a footprint changes |

## Editing the map

`content/maps/rose_hill.txt` is the map. Each character is one 16×16 tile:

- **Ground:** `.` grass, `:` walkway or sidewalk, `,` stone-paved plaza, `*` flowers, `P` parking, `c` a parked car (solid; decision 0026)
- **Roads** (decision 0016): `=` road, `X` crosswalk on a left-right road, `Y` crosswalk on an up-down road
- **Buildings:**
  - Roofs show the building type: `R` academic (slate), `O` residence hall (orange), `G` other campus building (gray), `M` Admission (maroon)
  - Walls: `W` wall, `w` window, `B` banner, `D` door
  - Walsh Library: `S` stone, `A` glass-arch entrance, `s` upper windows, `t` tower. The library is a drawn building: its cells come from `assets/buildings/walsh_library/building.json`, and the game adds its entrance doors itself
  - Campbell Hall (modern): `Q` flat roof, `q` dark brick wall, `g` glass stair tower, `J` glass entrance. Campbell is a drawn building too, from `assets/buildings/campbell_hall/building.json`
  - Entrances (`D`, `A`, `J`) each need a door object in the `.json`. Every entrance goes in the bottom row of the building's front wall and opens **south** (decision 0021); the tests check this
  - Each building's name plaque uses its `short_name` in `content/locations.json`. Its gray signpost is a `sign` object placed beside the door
- **Outdoors:** `T` tree, `V` copper beech (purple leaves; decision 0027), `h` hedge, `b` bench, `L` lamp, `~` water, `F` athletic field, `d` infield dirt, `+` graves
- **Edges:** `|` campus fence, `I` gate pillar, `K` guard booth, `#` off campus
- **Player start:** `@`

Everything you can talk to or inspect goes in `content/maps/rose_hill.json` under `"objects"`, placed by `"at": [x, y]` tile coordinates. Column 0 is the left edge and row 0 is the top. An object can be:

- **A door:** sits on a `D` tile and has a `"location"`.
- **A sign or landmark:** has a `"tile"` to draw, plus a `"location"` or some `"lines"`.
- **An NPC:** has a `"name"`, a `"sprite"`, a `"facing"` and `"lines"`.

`"location"` ids refer to entries in `content/locations.json`, which is where the text of every building card lives. `"areas"` are the named rectangles that trigger the banner when you walk into them. When several overlap, the first one listed wins.

Run `uv run pytest` after editing. It catches ragged rows, unknown characters, unreachable NPCs, doors without a card, and typos in location ids.
