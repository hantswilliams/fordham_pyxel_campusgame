# Campbell Hall: notes

**Status:** in review (v2, house style). Second drawn building, after Walsh Library (decisions/0020).

## Sources

- `research/images/campbell_dorms_facingWest.png`: the east side from Mill River Road, looking west. It shows:
  - six storeys of charcoal brick, with tall paired windows in white frames and light trim bands between the bays
  - a stepped roofline and glass shopfronts on the ground floor
  - a tall glass stair tower rising above the roof, and a second glass strip on the building set back to the right
  - the dining entrance under a wood canopy, with a stepped plaza, birch trees, tables and chairs in front

  **We don't know who owns this screenshot**, so it's a tracing reference only and is never shipped in the game.
- `research/images/zoomin_southwest.png`: the official map's outline. Campbell sits between Archer Drive (west) and Mill River Road (east). Its north part is wider, its south part narrower and slightly further east, and the dining entrance is at the step between them on the east side.

## What the drawings show

- `map.png` (48 × 160 px): the building from above.
  - The north part is three tiles wide; the south part is two tiles wide, with the Archer Drive sidewalk beside it.
  - The east façade is a strip of window bays along the east edge, with the north part set back 2 px.
  - The flat roof is drawn in stepped segments with rooftop units, and the exposed south walls show the windows.
  - Two glass stair towers rise above the roof.
  - The dining entrance has glass doors under the wood canopy, facing Mill River Road.
- `card.png` (228 × 88 px): the view from the plaza, as in the photo. It has the closer south part with the tall glass tower, the entrance canopy, the set-back north part, birch trees, the wide steps, tables, and students outside the dining hall.

## Simplifications (open for review)

- **The east side can't really be seen from above.** The camera looks north, so an east-facing front shows only as a strip along the building's east edge. The card picture shows the real view.
- **The stepped plaza and birches** in front of the entrance don't fit between the building and Mill River Road on the map, so they appear only on the card.
- **Width.** The real building is about 2–2.5 tiles wide at the map's scale; it's drawn as 3 (north) and 2 (south).

## Open questions

- Is the building on the right of the photo part of Campbell, or Salice / Conley Halls next door? The card treats it as Campbell's north part.
- Does Campbell have other entrances students use (residents' entrances) besides the dining entrance?

## v2: house style (decision 0021)

- **Entrance now faces south.** Campbell is one 3 × 10 block (the step between its north and south parts is gone), with glass doors at the south end under the wood canopy.
  - The real dining entrance faces east onto Mill River Road; the card says so under **IN REAL LIFE**.
- **Tall and narrow**, so the front shows almost all the way up, like the dark tower in `inspiration3`: storeys of paired windows in charcoal brick, the glass stair tower, and the glass ground floor.
- **The game adds** the plaque (CAMPBELL) and the mat.
- v1's map drawing is kept in `options/map_v1.png`. The card picture is unchanged.

## History

- v1, 2026-10-09: first drafts drawn in code (`options/draft_v1.py`). Added two charcoal brick colors to the palette for it.
- v2, 2026-10-10: house style and south-facing entrance (decision 0021), drawn by `../_style/draw_v2.py`.
