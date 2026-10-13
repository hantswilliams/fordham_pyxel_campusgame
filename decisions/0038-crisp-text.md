# D-0038: Crisp text, and the bar covering the game

| | |
|---|---|
| **Status** | Approved 2026-10-13 (all three parts). Browser check passed. Part 1 on `main`; Part 2 merged from branch `crisp-text` |
| **Raised** | 2026-10-12. Text in the browser looks too pixelated and hard to read, some strokes look thicker and darker than others, and the new accessibility bar hides the top of the game |
| **Affects** | The web page wrapper, the game's screen size, and the reading font everywhere (dialogue, menus, cards, map, HUD, title) |
| **Built?** | Yes, both parts |

## What's being decided

Two problems from your screenshots:
1. **Uneven, blocky text.** The game draws a 384 × 288 picture, and the browser stretches it to fill the window by an uneven amount, about 2.3× to 2.7× on a laptop. A pixel can't be 2.65 screen pixels wide, so some become 2 wide and some 3. That's why one stroke of a letter looks heavier than its neighbour. The font is also a pixel font, so even evenly scaled it stays blocky.
2. **The bar hides the game.** The accessibility bar (decision 0037) floats over the game, which still fills the whole window behind it. It covers the top rows: the HOW TO PLAY title, the area banner and the mission bar.

**Pictures** (in `decisions/images/0038/`, all at a laptop's size):
- `compare_dialogue.png`, `compare_controls.png`, `compare_mission_page.png`, `compare_card.png`: today and `crisp-text`, the same screen
- `font_options.png`: three fonts for Part 3
- `crisp_*.png`: full `crisp-text` screens (title, overworld, campus map, a mission offer)
- `text_options.png`: the first sketch of the options from our conversation

---

# Part 1: Keep the game below the bar (built on `main`)

The bar now has its own strip at the top, and the game fills the space below it, so nothing is covered. The page measures the bar's height, since it wraps onto two or three lines on a narrow window or phone. It's a change to the web page only (`tools/build_web.py`); the game is untouched.

**Checked:**
- With a stand-in for Pyxel's runtime at 1440 × 900, 800 × 600 and 320 × 640, the game starts exactly at the bar's bottom edge every time.
- The accessibility check still passes: 60 pages, 0 problems.

**Needs a look in a real browser.** Pyxel's runtime can't be downloaded here, so the stand-in has Pyxel's own page layout without the game itself.

## Your decision (Part 1)

- [x] **Approve**: keep it on `main`
- [ ] **Not approve**: say why
- [ ] **Other**: describe below

**Your notes:**

>

---

# Part 2: Crisp text (built on branch `crisp-text`)

### A. Draw the text at twice the detail (recommended; built)

**How it works:**
- The game's screen becomes **768 × 576**. Everything is still laid out and drawn at 384 × 288, then doubled, so the art looks exactly as it does now.
- Only the text uses the extra pixels. Each letter gets four times as many, in a smooth font (Part 3).
- Each letter still takes 8 layout pixels, so every box, menu and card keeps its current layout. Nothing was resized.

**In the browser:**
- The page keeps the game's canvas at exactly 768 × 576, so Pyxel draws it pixel for pixel (2:1 on a Retina screen).
- The browser then scales it smoothly to fit the window below the bar.
- Because the art is already doubled, smooth scaling leaves it sharp, and every stroke comes out even.
- If Pyxel's runtime ever sized its drawing to the window instead, the page notices and falls back to Pyxel's own layout, so the picture is never squashed.

**On the desktop:** the window is 768 × 576 with the same crisp text.

**Pros:**
- Text reads like a modern game's: smooth, even and easier on the eyes.
- Same art, same layout, same content.
- It also fixes the uneven strokes in the art.

**Cons:**
- **Speed.** Doubling the picture costs about 4 ms per layer (overworld, plus a menu or card on top), against about 0.6 ms for everything else. That's fine on a computer, but it needs checking on the web and on a phone (see "Before merging").
- The text no longer looks like pixel art. Signs, plaques and the small built-in font stay pixel art.
- A finger tapping the game canvas would land in the wrong spot. The game is played with keys and Pyxel's touch buttons (which aren't affected), so nothing uses taps today.

### B. Whole-number scaling only
Scale the 384 × 288 picture by exactly 2× or 3× with hard edges.

- **Pros:** Even strokes. A small change.
- **Cons:**
  - Still blocky pixel text.
  - The game shows smaller than the window: 768 × 576 on most laptops, with borders.

### C. Real web text over the game
- **Pros:**
  - The smoothest possible text.
  - Screen readers could read dialogue as it appears.
- **Cons:**
  - Browser only.
  - A big rework: every text box would need its own web element kept in sync with the game.
  - Could come later on top of A if the accessibility office wants it.

## Your decision (Part 2)

- [x] **Approve**: A, merge `crisp-text` once it passes the browser check
- [ ] **Not approve**: say which option you'd prefer, or why
- [ ] **Other**: describe below

**Your notes:**

>

---

# Part 3: Which font (see `font_options.png`)

All three are free (SIL Open Font License) and fit the same 8-pixel grid.

### A. M PLUS 1 Code, Medium (recommended; built)
- From the M+ family, the same family behind the PixelMplus font the game used before. In effect it's the smooth version of the game's original letters.
- Letters are the same size and shape as today's, so text keeps its size on screen.
- Clean and friendly. A cut-down copy (Latin letters only, 25 KB) is in `assets/fonts/`.

### B. Atkinson Hyperlegible Mono
- Designed by the Braille Institute for readers with low vision, with letters that are hard to confuse (I, l, 1; O, 0).
- A good story for the accessibility office.
- Its letters are about 20% smaller than today's in the same space, because it's a wider design.

### C. DotGothic16 at full detail
Today's pixel font drawn with twice the pixels. It's even, but it still looks dotted and pixelated, which is what you wanted to move away from.

## Your decision (Part 3)

- [x] **Approve**: A, M PLUS 1 Code
- [ ] **Not approve**: say which font you'd prefer
- [ ] **Other**: describe below

**Your notes:**

>

---

## Before merging `crisp-text`

**Done 2026-10-13:** you checked it in your browser and it looks good.

I can't run Pyxel's web runtime here, so this needs your browser. About 5 minutes:

1. `git checkout crisp-text`
2. `uv run python tools/build_web.py`
3. `python3 -m http.server -d build/web 8000`, then open http://localhost:8000

Check:
- [x] Text looks smooth and even, and the art still looks sharp.
- [x] The game sits below the bar and fills the space without being squashed.
- [x] Walking and opening the TAB menu feel as smooth as on `main`. If it stutters, tell me; there are ways to make the doubling cheaper.
- [ ] Optional: the same on a phone.

`uv run python main.py` shows the desktop version.

## What was built

**On `main`:** the bar strip (Part 1), in `tools/build_web.py`.

**On `crisp-text`:**
- **`game/gfx/display.py` (new):**
  - doubles each layer of the picture onto a 768 × 576 image
  - draws that layer's text over it at full size
  - with a menu or card on top, the text beneath is covered properly, dimmed with the world
  - skips the extra doubling when the layer beneath has no text
- **`game/ui/font.py`:**
  - text goes to the crisp display, M PLUS 1 Code at 32 px, one letter per 16 pixels
  - with `DISPLAY_SCALE = 1`, it draws DotGothic16 as before
- **`game/config.py`:** `DISPLAY_SCALE = 2`.
- **`game/app.py`:** starts Pyxel at 768 × 576 and runs the display each frame.
- **`game/scenes/base.py`:** each scene in the stack is a layer.
- **Camera and clipping** now go through `display.camera` and `display.clip`, so text under the overworld camera ("!" bubbles) and inside scrolling cards lands and clips in the right place.
- **The title** is drawn in the crisp font at double size.
- **`tools/build_web.py`:** keeps the canvas at the game's size and scales it smoothly, with the fallback above.
- **`tools/capture.py`:** saves 768 × 576 screenshots.
- **Tests:** all 266 pass. The new `tests/test_display.py` checks:
  - the screen is twice the layout
  - the art is doubled exactly
  - text lands where it was laid out, including under the camera
  - an overlay covers the text beneath it
  - the font fits its 16-pixel cell and its line
- **Checks:** the accessibility check passes, 60 pages and 0 problems. The canvas fit was checked at three window sizes and two canvas sizes, and the fallback was checked with a canvas sized to the window.
