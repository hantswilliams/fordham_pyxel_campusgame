# Drawn buildings

Important buildings can be drawn as **one picture** instead of being built from 16×16 tiles (decisions/0020). Each one gets its own folder here. Walsh Library is the pilot. Buildings without a folder keep using tiles.

```
assets/buildings/
  README.md           this file
  palette.hex         the game's exact colors, for any drawing app
  <building_id>/
    building.json     where it is, its footprint, entrances, status
    map.png           the drawing on the map
    card.png          the picture on its building card (228 x 88 px)
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
| `faces` | Which way the main entrance faces: `north`, `south`, `east` or `west` |
| `status` | `draft`, `in review` or `approved` |

**`map.png` must be exactly** (footprint width × 16 − offset x) by (footprint height × 16 − offset y) pixels. The tests check this.

## Drawing rules

- **Use only the colors in `palette.hex`**: the game's 16 plus the 6 "Fordham stone" colors. Load it in Aseprite, LibreSprite or Piskel (all can import a `.hex` palette). The tests flag any other color.
- **Pure black is transparent.** Leave everything outside the building transparent (or pure black). For dark lines, use navy (`2b335f`).
- **1 pixel = 1 game pixel.** Draw at actual size and don't scale up.
- **Characters can't walk on solid footprint cells**, so they're always drawn in front of the building. Keep anything that rises above the footprint (towers, pier caps) small.
- Photos are references to trace from. Don't paste or convert a photo into the drawing unless we have permission to use it.

## Adding or updating a building

1. Make the folder and `building.json`, copying the library's. Start with `"status": "draft"`.
2. Draw `map.png` and `card.png` (or ask Claude for a first draft in code; see `walsh_library/options/draft_v1.py`).
3. If the footprint changed, run `uv run python tools/stamp_buildings.py` to copy it into the map file. The tests tell you if they differ.
4. Run the tests: `uv run pytest`.
5. Build the review page: `uv run python tools/building_gallery.py`, then open `build/building_gallery.html`.
6. When it looks right, set `"status": "approved"`.
