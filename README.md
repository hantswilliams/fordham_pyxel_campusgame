# Fordham Campus Quest

A Pokémon-style, top-down pixel game where new Fordham students explore campus and find its resources. It's built with [Pyxel](https://github.com/kitao/pyxel).

**Status:** Milestone 1 (Walk) prototype. You can walk around Edwards Parade, talk to NPCs and read signs. All art is placeholder art drawn in code.

## Run it

You need [uv](https://docs.astral.sh/uv/) installed (`brew install uv` on macOS). uv installs Python 3.12 and Pyxel for you.

```bash
uv sync                          # first time only: creates .venv with Python + Pyxel
uv run python main.py            # play
uv run pyxel watch . main.py     # play with auto-reload when files change
uv run pytest                    # run tests (also validates map content)
uv run python tools/capture.py   # headless run, saves screenshots to build/screenshots/
```

**Controls:**
- Arrows or WASD move.
- **Z**, Space or Enter talks to people and reads signs.
- **X** skips text.
- Esc quits.

## Where things live

| Path | What |
|---|---|
| `ARCHITECTURE.md` | The overall plan: layers, gameplay loop, milestones |
| `decisions/` | **Decisions for review.** Each one has options, a recommendation, and Approve / Not approve / Other boxes |
| `content/maps/*.txt` | Maps as text grids (see the legend in `game/world/tiles.py`) |
| `content/maps/*.json` | What signs say, who the NPCs are and what they say. Edit these to change the game's text |
| `game/` | Engine code: `scenes/` (title, overworld, dialogue), `world/` (map, movement, camera), `systems/` (input), `gfx/` (placeholder art) |
| `tests/` | Unit tests plus content checks (every map loads, every NPC is reachable) |
| `tools/capture.py` | Scripted headless playthrough that saves screenshots |

## Editing a map

Each character in `content/maps/edwards_parade.txt` is one 16×16 tile:

- **Ground:** `.` grass, `:` path, `*` flowers
- **Buildings:** `R` roof, `W` wall, `w` window, `B` banner
- **Obstacles:** `T` tree, `h` hedge, `b` bench, `L` lamp, `~` water
- **Player start:** `@`
- **Signs, NPCs and doors:** digits. Each digit is defined under `"objects"` in the matching `.json`

Run `uv run pytest` after editing. It catches ragged rows, unknown characters and unreachable NPCs.
