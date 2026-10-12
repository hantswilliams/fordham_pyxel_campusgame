# Fordham Campus Quest: Architecture & Approach

*A Pokémon-style, top-down pixel game built with [Pyxel](https://github.com/kitao/pyxel) that new students walk around to learn the campus and its resources.*

> Choices that refine or change this plan are recorded in [`decisions/`](decisions/README.md). Where a decision and this document disagree, the decision wins.

---

## 1. Review of `scratch.goals.md`

**What's there:** use Pyxel, a "welcome to Fordham" onboarding game, Pokémon-like feel, explore campus, see what's available.

**What's good:** the scope is right. A small, explorable world is easy to build and it's a good use of Pyxel.

**What's missing (decide these before writing much code):**

| Open question | Recommendation |
|---|---|
| Who is the player? | Incoming first-years first. Transfers and grad students can come later as alternate "quest lines." |
| Which campus? | Start with **Rose Hill** only. Add Lincoln Center later as a second "region." |
| How do students get it? | **Web build** (`pyxel app2html`) linked from orientation emails or the portal. Nobody installs Python. A desktop build is optional. |
| What does "explore" mean in gameplay? | Discover locations to fill a **Campus Guide**, a Pokédex-style collection of buildings and offices, plus an **Orientation Checklist** quest. |
| What replaces battles? | Friendly **trivia "challenges"** from student-guide NPCs (RAs, orientation leaders) that award badges. No combat. |
| How long is a playthrough? | 15–25 minutes to finish the checklist. You can keep exploring after that. |
| Who keeps the content accurate? | Store all content (descriptions, URLs, offices) in **data files**, not code, so orientation staff can edit it. Link to official pages and don't hard-code office hours. |
| How do we know it worked? | Track completion rate and a 3-question post-game survey ("Do you know where to go for X?"). |

**IP and brand notes:**
- Make it *feel* like Pokémon (grid movement, text boxes, a collection index) with original art and names. Don't use Pokémon creatures, sprites, music or names. For example, call it "Campus Guide" or "Ram-dex," not "Pokédex."
- Fordham's name, logo, maroon and the Ram are university marks. Get sign-off from Fordham Marketing/Communications before the game ships publicly.

---

## 2. Tech baseline (Pyxel 2.9.x, current as of Oct 2026)

- **Python 3.11+ is required.** Use `uv` to create a 3.12 environment: `uv venv --python 3.12 && uv pip install pyxel`.
- **Constraints to design around:** a 16-color palette that you can redefine via `pyxel.colors` (so you can add Fordham maroon), 8×8 base tiles, 3 image banks of 256×256, 8 tilemaps, and 4 sound channels.
- **APIs you'll use:**
  - `pyxel.init` / `pyxel.run(update, draw)` for the game loop
  - `pyxel.bltm` for drawing the map, `pyxel.blt` for sprites
  - `pyxel.camera` for scrolling
  - `pyxel.Font` (BDF/TTF) for readable dialogue text
  - `pyxel.Tilemap.from_tmx` to load maps made in **Tiled**
  - `pyxel.user_data_dir` for save files
  - `pyxel.btn` / `btnp` for keyboard and gamepad input
- **CLI:**
  - `pyxel edit` edits sprites, tiles and sounds
  - `pyxel watch` hot-reloads while you develop
  - `pyxel package` produces a `.pyxapp`
  - `pyxel app2html` produces the web build
  - `pyxel app2exe` produces a desktop build
- **Screen:** 256×192 at 30 fps, with **16×16 "meta-tiles"** (each is 2×2 Pyxel tiles) for the classic Pokémon proportions. That shows 16×12 tiles on screen.

---

## 3. High-level architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                         main.py  →  App                          │
│              pyxel.init / pyxel.run(update, draw)                │
└──────────────────────────────┬───────────────────────────────────┘
                               │
                 ┌─────────────▼─────────────┐
                 │       SceneManager        │  stack of scenes;
                 │  push / pop / replace     │  the top one gets input
                 └─────────────┬─────────────┘
     ┌──────────────┬──────────┼──────────────┬────────────────┐
     ▼              ▼          ▼              ▼                ▼
 TitleScene   OverworldScene  InteriorScene  DialogueOverlay  GuideMenu /
                  │                │          (text box)      QuestLog /
                  └──────┬─────────┘                          QuizOverlay
                         ▼
                 ┌───────────────┐        ┌──────────────────────────┐
                 │    World      │        │        Systems           │
                 │  Map (layers, │◄──────►│  Input  (actions, not    │
                 │  collision,   │        │          raw keys)       │
                 │  triggers)    │        │  Dialogue (data-driven)  │
                 │  Entities:    │        │  Progress (flags, quests,│
                 │   Player, NPC,│        │            discoveries)  │
                 │   Sign, Door  │        │  Save   (JSON)           │
                 │  Camera       │        │  Audio                   │
                 └──────┬────────┘        └────────────┬─────────────┘
                        │                              │
          ┌─────────────▼──────────────────────────────▼──────────┐
          │                   Content & Assets                    │
          │  assets/maps/*.tmx (Tiled)    content/locations.json  │
          │  assets/game.pyxres (sprites, │content/npcs.json      │
          │    tiles, sfx, music)         │content/dialogue/*.json│
          │  assets/fonts/*.bdf           │content/quests.json    │
          └───────────────────────────────────────────────────────┘
```

### Layer responsibilities

**1. App and SceneManager.** These own the Pyxel loop. Scenes form a stack, so a dialogue box or menu is pushed *on top of* the overworld. The world freezes underneath and is still drawn. Each scene implements `update()`, `draw()`, `on_enter()` and `on_exit()`.

**2. World.**
- `Map` loads the tile layers (ground, buildings, overhead/roofs) from Tiled via `Tilemap.from_tmx`.
- A small XML reader parses Tiled **object layers** for doors/warps, NPC spawns, signs, and "discovery zones."
- Collision is a boolean grid built from a dedicated collision layer.
- `Entity` is the base class. `Player`, `NPC`, `Sign` and `Door` extend it.
- **Movement is grid-based.** Input picks a target tile, and the sprite animates over about 8 frames. That's the Pokémon feel and it makes collision trivial.
- `Camera` follows the player and clamps to the map edges via `pyxel.camera()`.

**3. Systems.**
- **Input** maps keys, gamepad and the web virtual pad to actions (`UP`, `CONFIRM`, `CANCEL`, `MENU`), so scenes never check raw keys.
- **Dialogue** plays scripted lines from JSON:
  - typewriter text and pagination
  - simple choices
  - side effects such as `set_flag`, `discover`, `start_quiz` and `open_url`
- **Progress** is a single source of truth for:
  - discovered locations
  - quest steps
  - badges
  - flags
- **Save** serializes Progress to JSON in `pyxel.user_data_dir(...)`. Test persistence in the web build early.
- **Audio** holds thin wrappers over `pyxel.play` and `pyxel.playm` for bgm per area and sfx for steps, confirm and discovery.

**4. Content (data, not code).** This is the most important decision for an onboarding game. The *code* is a generic tile-RPG engine, and *Fordham* lives entirely in data files:

```jsonc
// content/locations.json
{
  "walsh_library": {
    "name": "Walsh Library",
    "category": "Academics",
    "blurb": "Main library at Rose Hill: study spaces, research help, printing.",
    "url": "https://www.fordham.edu/libraries",   // verify all URLs
    "map": "rose_hill", "discover_zone": "walsh_entrance",
    "sprite": [0, 64]
  }
}
```

```jsonc
// content/dialogue/ra_maria.json
[
  {"say": "Welcome to Rose Hill! Have you found Walsh Library yet?"},
  {"choice": ["Not yet", "Yep!"], "branches": ["hint_walsh", "nice"]},
  {"id": "hint_walsh", "say": "It's past Edwards Parade.", "do": ["set_flag:hint_walsh"]}
]
```

**5. Drawn buildings (decision 0020).** Most buildings are built from 16×16 tiles. An important building can instead get a folder in `assets/buildings/<id>/`:
- `building.json` gives its footprint in map-legend characters. It decides what you bump into, and every entrance cell opens the building card.
- `map.png` is drawn over the map.
- `card.png` appears on its building card.

`load_map` stamps the footprint onto the grid and adds the entrance doors. The overworld draws `map.png` after the tiles and before the characters. The palette is the 16 Pyxel colors (four swapped) plus ten extra colors for stone, roofs and brick (`config.EXTRA_COLORS`, mirrored in `assets/buildings/palette.hex`). `tools/building_gallery.py` builds a review page per building.

**6. House style (decision 0021).** Every building follows one look: a roof over a south-facing front wall, the door in the bottom row, two-pane windows, a name plaque and a gray signpost by the door. Tile buildings get it from their tiles plus `game/gfx/building_overlay.py`, which draws outlines, eaves, door mats and plaques once into a map-sized image when the map loads. Drawn buildings carry their own outline and get mats and plaques from the same overlay. Walsh Library was the pilot. Next came Campbell, Dealy, Keating and Hughes Halls and Cunniffe House, plus the Cunniffe Fountain as the first drawn landmark (no entrance, decision 0022).

**6b. Outside the fence (decision 0033).** Off-campus cells (`#`) are blocked and drawn plain tan-grey (`Col.STONE`), on the map and in the campus map view.

**6c. Web build (decision 0034).** `tools/build_web.py` packs `main.py`, `game/`, `assets/` and `content/` into a Pyxel app and one HTML page (`build/web/index.html`) that runs in the browser with Pyodide, pinned to Pyxel 2.9.9. GitHub Actions (`.github/workflows/web.yml`) publishes it to Pages on every push to `main`. In the browser, `SaveFile` writes to `localStorage` (`browser_storage()` in `game/systems/progress.py`) instead of `save.json`. The campus map's `ctypes` pixel copy has a pure-Python fallback in case the browser lacks it.
- The photo pass (decisions 0023–0025) then drew the athletics fields and buildings, every residence hall and eight academic buildings from photos found online, using the shared kit in `assets/buildings/_style/kit.py`.
- Only Faculty Memorial Hall, the parking garage and the small landmarks (statues, the Victory Bell, the observatory and the cemetery) still use tiles.
- A place can span several drawn buildings, such as Martyrs' Court's two blocks. The overlay matches each plaque to its block, and the card uses the block that has a picture.

**7. Missions and saving (decision 0031).** `content/missions/*.json` holds one mission per file: who offers it, its steps and its reward. The First Week Checklist is one of them, the only required one.
- `game/systems/missions.py` is a pure-logic engine. The overworld tells it what the player did (talked to someone, opened a card, stood by a door, picked something up, answered a question) and shows the Reactions it returns.
- Givers and items are added to the map at runtime from the mission files.
- `game/systems/progress.py` keeps everything worth remembering (position, gate, bike, visited places, missions, stamps, badges, unlocks). It saves it as JSON in `pyxel.user_data_dir`, which on the web build is the browser's storage.
- Headless runs (tests, screenshots) never touch a real save.

A `tests/test_content.py` check validates the data: every NPC's dialogue exists, every quest references real locations, and every URL is well-formed. Content edits then can't break the game.

---

## 4. Gameplay loop (Pokémon mechanics → onboarding)

| Pokémon mechanic | Campus Quest equivalent | Onboarding goal |
|---|---|---|
| Pokédex | **Campus Guide** fills in when you walk into a location's zone | Know *what* exists |
| Gym badges | **Orientation badges**: Academics, Wellness, Community, Career, Dining | Know *where to go for help* |
| Trainer battles | **Trivia challenges** with RAs and orientation leaders (3 questions each) | Retain key facts |
| Professor Oak | Opening guide character gives you a "Ram Card" and the checklist | Clear first goal |
| Town map | Fly-free **campus map** with discovered pins | Spatial memory |
| Signs and NPCs | Real tips: "Shuttle to Lincoln Center leaves from…" | Practical knowledge |

**Starter quest, "First Week Checklist":** the proposed steps and locations are in [D-0014](decisions/0014-v1-locations-and-checklist.md). Real places are taken from the official campus map ([research notes](research/rose-hill-map-notes.md)).

Finishing the checklist unlocks an end card that links to the real orientation page.

**Outdoors only for v1.** Doors open a *building card* (name, what's inside, official link) instead of an interior. Interiors are deferred, see [D-0012](decisions/0012-building-interiors.md). *Have someone from Fordham check which offices sit in which buildings before the dialogue is final.*

---

## 5. Project layout

```
fordham_pyxel_campusgame/
├── main.py                  # entry point: App().run()
├── pyproject.toml           # pyxel dependency, python >=3.11
├── game/
│   ├── app.py               # init, SceneManager, global systems
│   ├── config.py            # screen size, tile size, palette, fps
│   ├── scenes/              # base.py, title.py, overworld.py,
│   │                        # dialogue.py, guide_menu.py, quiz.py, quest_log.py
│   ├── world/               # map.py (tmx + objects), entity.py, player.py,
│   │                        # npc.py, camera.py, triggers.py
│   ├── systems/             # input.py, dialogue.py, progress.py, save.py, audio.py
│   └── ui/                  # textbox.py, menu.py, hud.py
├── content/                 # locations.json, npcs.json, quests.json, dialogue/
├── assets/                  # game.pyxres, maps/*.tmx, tilesets/*.png, fonts/,
│                            # buildings/<id>/ (drawn buildings, D-0020)
├── tests/                   # content validation + pure-logic unit tests
└── tools/build.sh           # pyxel package → app2html (+ app2exe)
```

---

## 6. Build and distribution

```
pyxel package . main.py        → fordham_pyxel_campusgame.pyxapp
pyxel app2html *.pyxapp        → single .html (host on GitHub Pages / Fordham site)
pyxel app2exe  *.pyxapp        → optional desktop build
```

The web build is what students will actually use. Test it on a phone early (touch controls, screen scaling) and on whatever page will host it.

---

## 7. Milestones

| # | Milestone | Done when… |
|---|---|---|
| M0 | Setup | `uv` env with Python 3.12 + Pyxel, git repo, decisions log. **Done** |
| M1 | **Walk** | Grid movement, collision, camera, NPCs, signs, dialogue box on a test map. **Done** (text maps, D-0005) |
| M2 | **Real Rose Hill** | One continuous, compressed map of Rose Hill built from the official campus map (D-0010, D-0013), with area-name banners as you cross zones, building cards on doors, and the start at the Main Entrance (D-0015). **Done** (draft content pending staff review). Later additions: roads vs. walkways, and the train-arrival intro that starts the game at the Webster Ave gate (D-0016) |
| M3 | **Collect** | `locations.json` drives the Campus Guide menu, discovery zones and save/load |
| M4 | **Quest** | First Week Checklist (D-0014), trivia challenges, badges, end card |
| M5 | **Ship** | Title screen, music/sfx, web build, playtest with 5–10 students, content review by orientation staff |
| (deferred) | Enter | Building interiors, see D-0012 |

Get M2 and M3 working with placeholder art before investing in real pixel art (D-0008).

---

## 8. Risks and mitigations

- **Art is the bottleneck.** Start with colored-rectangle placeholders. Then draw a small, reusable tileset of about 30 tiles for paths, grass, gothic stone walls, windows, doors and trees. 16×16 meta-tiles keep the art manageable.
- **Content goes stale.** Keep content in data files with a `last_verified` field, and link to official pages instead of copying hours or policies.
- **Text readability at low resolution.** Use a proper pixel BDF font and a 2–3 line text box, and let the player advance text at their own pace.
- **Accessibility.**
  - Support keyboard, gamepad and touch.
  - Don't rely on color alone.
  - Offer a "skip to map / list view" so every resource is reachable without playing.
- **Scope creep.** No battles, inventory or overworld randomness in v1.
