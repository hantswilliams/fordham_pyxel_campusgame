# Drawn buildings

Important buildings can be drawn as **one picture** instead of being built from 16×16 tiles (decisions/0020). Each one gets its own folder here. Walsh Library is the pilot. Buildings without a folder keep using tiles.

```
assets/buildings/
  README.md           this file
  palette.hex         the game's exact colors, for any drawing app
  <building_id>/
    building.json     where it is, its footprint, entrances, status
    map.png           the drawing on the map
    map_fine.png      the same drawing at twice the detail, for the finer world (decisions/0045)
    card.png          the picture on its building card (228 x 88 px)
    card_fine.png     the same picture at twice the detail (decisions/0045)
    notes.md          sources, simplifications, open questions
    options/          mockups and earlier versions
```

## building.json

```json
{
  "id": "walsh_library",
  "name": "William D. Walsh Family Library",
  "map": "rose_hill",
  "location": "walsh_library",
  "faces": "north",
  "status": "in review",
  "origin": [8, 64],
  "sprite_offset": [0, -4],
  "footprint": ["AAAA::::::", "GGGGAAAAAA", "..."]
}
```

| Field | Meaning |
|---|---|
| `map` | Which map the building is on (`content/maps/<map>.txt`) |
| `location` | Its building card in `content/locations.json` |
| `origin` | Map tile `[x, y]` of the footprint's top-left cell |
| `footprint` | One string per row, using the **map legend** (`game/world/tiles.py`). A space leaves the map's own cell alone. Solid tiles (`G` roof, `S` stone…) are what you bump into. Every **entrance** tile (`A` glass arch, `D` door, `J` glass door) opens the building card, and the game adds those doors itself. Walkable tiles (`:` path) can be part of a footprint too, for a forecourt |
| `sprite_offset` | Where `map.png`'s top-left goes, in pixels from the footprint's top-left. A negative y lets a tower or roofline rise above the footprint |
| `faces` | Which way the main entrance faces. Always `south` since decision 0021 |
| `nameplate` | Where the name plaque goes, in pixels from the footprint's top-left: `[centre x, top y]`. The game draws the plaque, using the building's `short_name` in `content/locations.json` |
| `status` | `draft`, `in review` or `approved` |
| `landmark` | `true` for a statue, fountain or similar with no entrance (decision 0022). It needs a `sign` object on one of its cells in the map's `.json` to open its card |

**`map.png` must be exactly** (footprint width × 16 − offset x) by (footprint height × 16 − offset y) pixels. The tests check this.

## Drawing rules

**The house style (decision 0021, from `research/images/inspiration1-4.png`):**
- A roof on top and a front wall at the bottom, facing south. Tall, narrow buildings show their front almost all the way up.
- The entrance goes in the bottom row of the front wall. Leave room above it for the plaque.
- A 1 px navy outline round the building, and a dark eave line where the roof meets the wall.
- Two-pane windows: white frame, light blue glass.
- Its own materials and one signature feature. Simple outlines.
- Don't draw the plaque or the door mat: the game adds both, so they match on every building. See `_style/` for the mockups and the drafts.

**The basics:**

- **Use only the colors in `palette.hex`**: the game's 16 plus 10 extra colors: four stone shades, two roof grays, two charcoal bricks and two pink bricks. Load it in Aseprite, LibreSprite or Piskel (all can import a `.hex` palette). The tests flag any other color.
- **Pure black is transparent.** Leave everything outside the building transparent (or pure black). For dark lines, use navy (`2b335f`).
- **1 pixel = 1 game pixel.** Draw at actual size and don't scale up.
- **Characters can't walk on solid footprint cells**, so they're always drawn in front of the building. Keep anything that rises above the footprint (towers, pier caps) small.
- Photos are references to trace from. Don't paste or convert a photo into the drawing unless we have permission to use it.

## Adding or updating a building

1. Make the folder and `building.json`, copying the library's. Start with `"status": "draft"`.
2. Draw `map.png` and `card.png`, or ask Claude for a first draft in code. The batch scripts in `_style/` draw most buildings with the shared kit `_style/kit.py`: `draw_athletics.py`, `draw_residence.py` and `draw_academic.py`.
3. If the footprint changed, run `uv run python tools/stamp_buildings.py` to copy it into the map file. The tests tell you if they differ.
4. Make its pictures at twice the detail: `uv run python assets/buildings/_style/fine.py <id>`. This runs the building's drawing script again with finer stone, roofs, windows and doors (decisions/0045). A new building needs a line in `SOURCES` in `fine.py`, and in `CARDS` if it has a card picture. The game draws `map_fine.png` and `card_fine.png`; the tests check that they're there, twice the size, in the game's colors.
5. Run the tests: `uv run pytest`.
6. Build the review page: `uv run python tools/building_gallery.py`, then open `build/building_gallery.html`.
7. When it looks right, set `"status": "approved"`.

## Photos found online (decisions 0023–0025)

The buildings drawn in the photo pass were traced from photos found online.
- **Wikimedia Commons** photos have free licenses, which are listed in each building's `building.json` and `notes.md`.
- **Image-search** screenshots are for reference only.

The screenshots are kept in `research/images/web/`, listed in its `SOURCES.md`. Faculty Memorial Hall and the Regional Parking Facility are still tiles, because no reliable photos turned up.

## A place drawn as several buildings

One place can be split across more than one folder, as long as each folder has the same `location`. Martyrs' Court is the example: `martyrs_court` is the main block and `martyrs_court_west` is the west wing.
- Each block needs its own `nameplate`.
- Exactly one block should have a `card.png`. The tests check both.
