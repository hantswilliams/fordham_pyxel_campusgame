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

**Starter quest, "First Week Checklist":**
1. Get your ID card.
2. Find Walsh Library.
3. Eat at the student center (McGinley).
4. Visit a wellness or counseling resource.
5. Visit career services.
6. Find University Church.
7. Talk to 3 student-club NPCs on Edwards Parade.

Finishing the checklist unlocks an end card that links to the real orientation page.

**Suggested Rose Hill zones for v1:** Edwards Parade (hub), Keating Hall, Walsh Library, McGinley Center, University Church, Dealy Hall, Hughes Hall (Gabelli), Rose Hill Gym, and a residence hall. *Have someone from Fordham check which offices sit in which buildings before you write the dialogue.*

---

## 5. Project layout

```
fordham_pyxel_campusgame/
├── main.py                  # entry point: App().run()
├── pyproject.toml           # pyxel dependency, python >=3.11
├── game/
│   ├── app.py               # init, SceneManager, global systems
│   ├── config.py            # screen size, tile size, palette, fps
│   ├── scenes/              # base.py, title.py, overworld.py, interior.py,
│   │                        # dialogue.py, guide_menu.py, quiz.py, quest_log.py
│   ├── world/               # map.py (tmx + objects), entity.py, player.py,
│   │                        # npc.py, camera.py, triggers.py
│   ├── systems/             # input.py, dialogue.py, progress.py, save.py, audio.py
│   └── ui/                  # textbox.py, menu.py, hud.py
├── content/                 # locations.json, npcs.json, quests.json, dialogue/
├── assets/                  # game.pyxres, maps/*.tmx, tilesets/*.png, fonts/
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
| M0 | Setup | `uv` env with Python 3.12 + Pyxel, `pyxel watch` running "hello world," git repo |
| M1 | **Walk** | One outdoor map (Edwards Parade), grid movement, collision, camera follow. **Prototype done** (text map instead of Tiled, see D-0005; basic dialogue pulled forward from M2) |
| M2 | **Talk** | NPCs and signs, dialogue box with BDF font, choices |
| M3 | **Enter** | Door warps into 2–3 interiors (Walsh, McGinley), fade transitions |
| M4 | **Collect** | `locations.json` drives the Campus Guide menu, discovery zones, save/load |
| M5 | **Quest** | First Week Checklist, trivia challenges, badges, end card |
| M6 | **Ship** | Title screen, music/sfx, web build, playtest with 5–10 students, content review by orientation staff |

Get M1 → M2 → M3 working end to end with placeholder art before investing in real pixel art.

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
