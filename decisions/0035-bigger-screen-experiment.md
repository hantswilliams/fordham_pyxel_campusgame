# D-0035: A bigger screen (experiment on the `hi-res-screen` branch)

| | |
|---|---|
| **Status** | Built on branch `hi-res-screen`, for you to try. `main` is unchanged |
| **Raised** | 2026-10-11. You asked for a branch with a slightly higher resolution, to see how it looks |
| **Affects** | Screen size, plus the few screens that were laid out for the old size (title, intro, building cards) |
| **Built provisionally?** | Yes, on the branch only. To undo, switch back to `main` |

## What's being decided

You picked "bigger screen, same art" over redrawing the art at twice the detail or running it through an upscaler. On the branch, the game screen goes from **256 × 192 to 384 × 288**: the same 4:3 shape, 1.5× the pixels each way.

In the same window, everything is drawn with smaller, finer pixels, and you see **1.5× as much campus across and down** (24 × 18 tiles instead of 16 × 12). The art itself is unchanged.

Most of the game adapted on its own, because it's laid out from the screen size: the overworld, dialogue boxes, menus, the campus map, the mission log and the passport. Three places needed changes:

- **Title screen:** centred vertically on the taller screen.
- **Intro (train, station, street, controls):** these scenes are hand-placed for 256 px. They're now drawn at that size and **scaled up 1.5×** to fill the width, with the caption box underneath at full resolution. People in the intro were already drawn at 2×, so they come out at an even 3×. A few 1-pixel lines come out slightly uneven, which you'd only spot up close.
- **Building cards:** the picture (228 × 88) is **centred** on the wider card instead of sitting at the left.

**Try it:**
```bash
git checkout hi-res-screen
uv run python main.py
git checkout main          # back to 256 x 192
```
The web build works on the branch too (`uv run python tools/build_web.py`). Only `main` publishes to GitHub Pages.

Side by side, at the same window size: `build/hi_res_compare.png` (sent in chat).

## Options

### A. Keep 256 × 192 (main as it is)
- **Pros:** Chunkier, more classic Game Boy Advance look. Characters and text are bigger in the window. Nothing to merge.
- **Cons:** You see less of campus at once.

### B. Merge 384 × 288 into main
- **Pros:**
  - You see more of campus, so finding your way is easier.
  - Finer look, and more room for menus, cards and the map.
- **Cons:**
  - Characters and text are smaller in the same window, though Pyxel can make the window bigger.
  - The intro is scaled up 1.5×, so it's slightly less crisp than the rest.
  - Drawing new intro scenes natively at the bigger size would be a later job.

### C. Something in between, e.g. 320 × 240
- **Pros:** 1.25× the view, with a smaller jump in pixel size.
- **Cons:** The intro would scale by 1.25×, which looks less even than 1.5×. I'd try it on the same branch first.

## My recommendation

**Try the branch for a session and see how it feels.** If seeing more campus helps more than the bigger characters, go with **B**. If the smaller text or characters bother you, stay with **A**.

## Your decision

- [ ] **A**: keep 256 × 192
- [ ] **B**: merge 384 × 288 into main
- [ ] **Other**: e.g. try 320 × 240

**Your notes:**

>
