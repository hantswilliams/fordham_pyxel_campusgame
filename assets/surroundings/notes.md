# Outside the fence (decisions/0033)

`rose_hill.png` is the scenery around Rose Hill: a picture the size of the map
(1600 × 1216), clear on every campus cell. The game draws it over the
off-campus (`#`) cells, which stay blocked. `rose_hill_labels.json` holds the
green street-name signs drawn on top.

Redraw it after changing the map's outline:

    python3 assets/surroundings/draw_surroundings.py

Laid out by eye from `research/images/google_map_view.png`. That image is a
reference only; nothing is traced or copied from it.

| Side | What's there |
|---|---|
| North-west | Metro-North's Harlem Line in a gravel cutting, with a train. Webster Avenue runs up beside it. Apartment blocks with water towers beyond. Fordham Prep and Prep Field between Webster Avenue and the fence |
| North and east | Southern Boulevard hugging the fence, with the main-gate link onto it. Beyond it, the New York Botanical Garden: woods, lawns, winding paths, a pond, and the Enid A. Haupt Conservatory with its Palm Dome and reflecting pool |
| East edge | Bronx Park woods |
| South | East Fordham Road, four lanes with traffic and a Select Bus. A wide sidewalk with street trees along the campus side, shops with awnings, and the street from the south-east gate. Shops and apartment houses across the road |
| West edge | Webster Avenue down to the Webster Avenue gate |

The map is a grid, so the roads are straightened and the distances squeezed
to fit the space outside the fence. It's a likeness, not a survey.
