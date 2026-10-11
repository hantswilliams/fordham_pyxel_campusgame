# D-0033: What's outside the fence

| | |
|---|---|
| **Status** | Decided 2026-10-11: plain tan-grey |
| **Raised** | 2026-10-11. You asked to replace the navy squares around the campus with what Google Maps shows around it |

## What happened

**First try: painted scenery.** The first version painted the neighbourhood over the off-campus squares:
- Webster Ave and the Metro-North tracks, with Fordham Prep
- Southern Blvd and the Botanical Garden, with the Haupt Conservatory
- E Fordham Rd with shops
- green street-name signs

You didn't like it, so it has been taken out.

**Decision:** everything outside the university boundary is now a **plain tan-grey** (the palette's stone colour, `#c6bdae`), with no grid lines or detail.

- It's the `offcampus` tile in `game/gfx/placeholder_art.py`. The campus map (M) uses the same colour for off-campus.
- Off-campus squares are still blocked, as before.

## Your decision

- [x] **Approve**: plain tan-grey outside the boundary
- [ ] **Other**: describe below

**Your notes:**

> Didn't like the painted neighbourhood; make everything outside the university boundaries a tan grey.
