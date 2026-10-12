# D-0036: Text size on the bigger screen

| | |
|---|---|
| **Status** | Awaiting review |
| **Raised** | 2026-10-11. After the move to 384 × 288 (decision 0035), you asked whether the text needs adjusting |
| **Affects** | The reading font everywhere (dialogue, menus, cards, map, HUD) and the name plaques on buildings |
| **Built provisionally?** | Option B of Part 1 is built on branch `bigger-text`. Part 2 is a mock-up only. `main` is unchanged |

## What's being decided

The screen got 1.5× more pixels, but the reading font stayed 12 px tall. In the same window, text now shows at about two-thirds the size it used to. It's still sharp, just noticeably smaller.

Two questions:
1. **The reading font:** keep it, swap to a bigger pixel font, or draw the current one bigger.
2. **The building name plaques on the map** ("MCSHANE", "LOMBARDI"): these use Pyxel's tiny built-in font, so they shrank the most.

**Pictures** (all at the same window size, in `decisions/images/0036/`):
- `text_options_1.png`: a dialogue box, the Mission Log and a building card, with A, B and C side by side
- `text_options_2.png`: the controls card, the title screen and the campus map
- `text_options_plaques.png`: the plaques, today and bigger

---

# Part 1: The reading font

### A. Keep PixelMplus 12 (6 px letters)
- **Pros:** Nothing to change. Fits the most text, about 60 characters per dialogue line.
- **Cons:** The smallest letters on screen, about two-thirds of their old size. Long dialogue lines are tiring to read.

### B. Switch to DotGothic16, drawn at 15 px (8 px letters) (recommended; built on `bigger-text`)
DotGothic16 is a free pixel font (SIL Open Font License, from Google Fonts). At 15 px it renders cleanly; at 16 px the strokes smear, which is why it's drawn at 15. Capitals are 12 px tall instead of 9, so text comes back to about its old size on screen. A dialogue line holds about 45 characters.

What changed on the branch:
- `game/ui/font.py` and `game/ui/text.py` use the new font. `text.py` now holds the font's size in one place (`BIG_CHAR_W`, `BIG_LINE_H`, `TEXT_H`, `GROW`).
- Every box sized for the old font grows to fit: the mission bar, area banner, toasts and "!" bubbles; menu headers and rows; the campus map's header, footer, name tag and key; card headers and tags; the ID check panel; the intro's controls card; and the speaker tag on dialogue.
- The controls card lines its actions up after the longest key name instead of at a fixed spot.
- The title screen is re-spaced for the bigger letters.
- The ID check's two small hints now use the reading font too.
- Tests: all 254 pass. The controls-card test now checks against the real card width.

- **Pros:** Crisp, as big as before, and easy to read at a glance, which matters for new students skimming signs.
- **Cons:**
  - The font is monospaced, so narrow letters (i, l) get wide gaps ("M I SSIONS" is the most visible case).
  - Fewer words per line means a few more dialogue pages.
  - It adds a 2 MB font file (about 1 MB more to the web download).

### C. Draw today's font 1.5× bigger (9 px letters) (mock-up only)
- **Pros:** Same look as today, just bigger.
- **Cons:**
  - Scaling by 1.5 makes some strokes 1 px and some 2 px, so letters look uneven and slightly blurry.
  - Each line of text is drawn to a buffer first, which is slower.
  - The biggest of the three, so the least fits on a line.
  - The mock-up hasn't had the layout fixes B got: the title overlaps and the controls card clips at the bottom.

## Your decision (Part 1)

- [ ] **Approve**: Option B (merge the `bigger-text` branch)
- [ ] **Not approve**: say which option you'd prefer, or why
- [ ] **Other**: describe below

**Your notes:**

>

---

# Part 2: Building name plaques on the map

### A. Keep Pyxel's built-in 4 × 6 font
- **Pros:** Small plaques that don't cover the buildings.
- **Cons:** Hard to read on the bigger screen.

### B. PixelMplus 10 (5 px letters, about 1.4× taller) (recommended; mock-up only)
- **Pros:** Readable at a glance, still a plaque rather than a sign.
- **Cons:** Plaques get about 25% wider. A long name like ROSE HILL GYM fills more of a small front, though it still fits on every drawn building I checked.

## Your decision (Part 2)

- [ ] **Approve**: Option B
- [ ] **Not approve**: keep them as they are
- [ ] **Other**: describe below

**Your notes:**

>

---

## My recommendation

**B and B.**
- **Part 1:** DotGothic16 brings the text back to a comfortable size and stays crisp. The wide spacing on narrow letters is the only real cost, and the alternatives are either small or uneven.
- **Part 2:** the 10 px font makes the plaques readable without turning them into signs.

If you approve, I'll merge `bigger-text`, add the plaque change, and check every screenshot again.
