# Missions (decisions/0031)

Each `.json` file here is one mission. The game loads every file except ones that start with `_`.

## Add a mission

1. Copy `_TEMPLATE.json` to `your_mission_id.json`. The file name must match `"id"`.
2. Fill it in. Delete the step examples you don't need.
3. Run the tests: `uv run pytest`. `tests/test_missions.py` checks every mission. It catches:
   - places that don't exist
   - people who aren't on the map
   - items or givers placed on a wall
   - questions without a right answer
   - stamps used twice
4. Play it, or run `uv run python tools/capture.py` for screenshots.

## The fields

| Field | What it is |
|---|---|
| `optional` | `false` only for the First Week Checklist, the one required mission. It starts by itself and has no giver |
| `order` | `"in_order"` (the default): steps one at a time. `"any"`: all steps open at once (the checklist) |
| `requires` | `"bike"` (you've borrowed one) or `"mission:<id>"` (another mission is done). Until then the giver says `requires_say` |
| `giver` | The person who offers the mission. The game puts them on the map at `at` (a free walkway or lawn tile) with a **!** over their head. `sprite` 0–5 picks their look |
| `steps` | What the player does, in order (see below). Each step can have `say` (lines shown when it's done), `hint` (shown in the Mission Log), `label` (the tracker text) and `badge` |
| `reward` | `stamp` (a Ram Passport stamp, one per mission), `badge` (academics, wellness, community, career or dining), and `unlock` (`maroon_bike`) |
| `done_say` | Lines when the mission is finished |

## Step types

| `do` | The player… | Fields |
|---|---|---|
| `talk` | talks to someone | `npc` |
| `go_to` | walks up to a place's door or sign | `location` (an id in `content/locations.json`) |
| `read` | opens a place's card | `location` |
| `find` | picks up an item that appears on the map while this step is current | `item`, `name`, `at`, `tile` (`item_card` or `item_package`) |
| `answer` | answers someone's question (talk to them to be asked) | `npc`, `question`, `options`, `correct` (0 = first option), `ask_say`, `wrong_say` |
| `ride` | gets to a place, against the clock if `seconds` is set. When time runs out, it goes back to step `restart_from` (0 = first step) | `location`, `seconds`, `restart_from`, `fail_say` |
| `collect` | does `need` of the `targets` in any order. Each target is a place to `read` (the default) or `go_to` | `need`, `targets`, `label` |
