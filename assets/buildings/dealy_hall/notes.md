# Dealy Hall: notes

**Status:** in review (first drafts, v1). Third drawn building, after Walsh Library and Campbell Hall (decisions/0020).

## Sources

- `research/images/dealey_hall_facingEast.png`: the west façade, looking east. It shows:
  - dark fieldstone walls with white stone quoins around every window
  - arched windows on the ground and third floors, and a light top storey
  - white trim bands framing the centre bays
  - a columned portico with "DEALY HALL" over an arched wooden door, wide steps, hedges and lamp posts

  **We don't know who owns this screenshot**, so it's a tracing reference only and is never shipped in the game.
- `research/images/fasting_east_cunniffee(1stbuilding)_dealey(2ndbuilding-back).png`: Dealy behind Cunniffe House, with its portico facing the lawn between them.
- `research/Rose-Hill-Campus-Map.pdf`: the outline. A north-south wing on the west and a main block running east toward Rose Hill Manor Drive. There's a dining icon by the south part of the wing and a Ram Van stop on the drive at the east end.

## A correction

Earlier notes (D-0019) said Dealy's entrance faces west "onto Rose Hill Manor Drive". The campus map shows the drive on Dealy's **east** side. The portico faces **west**, toward Cunniffe House and the lawn, away from the drive. The game now has it that way, with a short walkway from Cunniffe's path to the portico steps.

## What the drawings show

- `map.png` (102 × 128 px): the building from above.
  - The shape is a T: a north-south wing (2 tiles wide) and the main block running east (6 tiles).
  - It has a flat roof with the light top storey as a rim.
  - The dark stone south walls have white-trimmed windows, arched on the ground floor.
  - The west façade is a strip of window bays along the wing's west edge.
  - The columned portico has steps down to the walkway; they reach 6 px past the footprint, on the walkway.
  - A small dining entrance is on the east side of the wing.
- `card.png` (228 × 88 px): the west façade, as in the photo. It has the light top storey, the dark fieldstone with quoined windows, the centre bays framed in white, the portico with columns and the arched door, steps, hedges, lamp posts and overhanging trees.

## Simplifications (open for review)

- **The west side can't really be seen from above.** The camera looks north, so the main façade shows only as a strip along the wing's west edge, with the portico sticking out. The card shows the real view.
- **Proportions.** The wing and main block are drawn from the campus map at the game's compressed scale.

## Open questions

- Where exactly is the dining entrance? The campus map's dining icon is by the south part of the wing. It's placed on the wing's east side, reached by a walkway from Rose Hill Manor Drive.
- Is the accessible entrance (at the north end of the wing on the campus map) worth adding as a second way in?

## History

- v1, 2026-10-10: first drafts drawn in code (`options/draft_v1.py`). No new colors: it uses the charcoal bricks added for Campbell plus white and the stone shades.
