# D-0041: Easier-to-find mission items

| | |
|---|---|
| **Status** | Built 2026-10-13 on branch `mission-items`, for your review |
| **Raised** | 2026-10-13. The lost ID is hard to spot on the walkway, and the package should be at McShane's front door |
| **Affects** | The Lost and Found and Bike Courier missions, and how mission items are drawn |
| **Built?** | Yes |

**Picture:** `decisions/images/0041/items.png` shows the package at McShane's door and the ID card on the road, each with a "!".

## What changed

**The lost ID (Lost and Found)**
- It now lies on the dark grey road between McShane and Edwards Parade, at (47, 31), where the white card stands out. It used to be on the walkway at (47, 33).
- The hint now says to look along the road and to watch for the "!".
- Finding it now says "You found a Fordham ID card lying in the road!"

**The package (Bike Courier)**
- It now waits on the walkway just to the left of McShane's front door, at (48, 27). It used to be beside the Mail Room Staffer at (42, 28).
- The staffer and the hint now point you to McShane's front door.
- It sits beside the door rather than on its mat, so McShane's door still works while the package is there.

**A "!" over every mission item.** While an item is waiting to be picked up, a bobbing "!" floats above it, like the one over people with a mission for you.

## Your decision

- [ ] **Approve**
- [ ] **Not approve**: say why
- [ ] **Other**: for example a different spot on the road, or the "!" only on the ID card

**Your notes:**

>

## What was built

- **`content/missions/lost_and_found.json`** and **`bike_courier.json`:** the new spots and wording.
- **New tile `item_card_road`:** the ID card drawn on road instead of walkway. It's in `game/world/tiles.py` and `game/gfx/placeholder_art.py`, and is allowed as a mission item in `game/systems/missions.py`.
- **`game/scenes/overworld.py`:** draws the "!" over mission items.
- **Tests:** 273 pass, with the item spots updated in `tests/test_missions.py` and `tests/test_save_continue.py`.
