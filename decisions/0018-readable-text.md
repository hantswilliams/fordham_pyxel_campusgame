# D-0018: Readable, Pokémon-style text

| | |
|---|---|
| **Status** | Awaiting review |
| **Raised** | 2026-10-09 (you noticed the text was hard to read; example in `research/images/pokemon_text_example.jpeg`) |
| **Affects** | Every text box: dialogue, intro captions, building cards, the controls card, area banners, the title screen, the campus map |
| **Built provisionally?** | Yes, Option A. Switching to B is a one-line change. C is new art work |

## What's being decided

The game used Pyxel's built-in font, whose letters are only 3×5 pixels on a 256×192 screen. In navy on white, packed 4 lines deep, it was hard to read. Pokémon Red is just as pixelated but stays readable because its text is:
- **big** relative to the screen (8×8-pixel letters)
- **pure black on white**
- set in a box with a heavy **double border**
- limited to **2–3 lines** at a time

What should our text look like?

## Options

### A. PixelMplus 12 for all reading text: black on white, 3 lines per box (recommended, already built)
- A free pixel font with 6×12-pixel letters, twice the size of the old one. It's the same family Pyxel's own examples use.
- **Changes:**
  - Text is black on white, inside a navy and maroon double border.
  - Dialogue and intro captions show **3 lines of up to 38 characters**.
  - Building cards, banners, the controls card, the title screen ("FORDHAM / CAMPUS QUEST" drawn at 2x) and the map's header and footer all use it.
  - The tiny font is kept only for the map legend and small hints.
- **License:** M+ FONTS license (free to use, change and redistribute, including commercially). It's saved in `assets/fonts/LICENSE-PixelMplus.txt`.
- **Pros:**
  - Clearly readable at any window size.
  - Close to the Pokémon feel.
  - No art work needed.
- **Cons:**
  - Fewer words fit per page (38 characters per line instead of 58), so longer lines take two presses of Z.
  - Building cards scroll a little more often. They show arrows when there's more to read.

### B. PixelMplus 10: slightly smaller letters, more words per page
- **Pros:** About 45 characters per line, so fewer pages.
- **Cons:** Noticeably less clear, which is the problem we're trying to fix.

### C. A custom 8×8 "Fordham" pixel font drawn for the game
- **Pros:** The most authentic Pokémon look, and unique to the game.
- **Cons:**
  - About 95 characters to draw and test.
  - Only worth it at the art-polish stage (D-0008).

### D. Keep the built-in tiny font
- **Pros:** No change.
- **Cons:** Hard to read.

## My recommendation

**Option A.** It fixes readability now with a proven, freely licensed font. The cost of fewer words per page is really a writing issue: when Fordham staff review the content, shorter lines of about 70 characters will read best. If you later want a signature look for launch, **C** can replace the font without touching any other code, since all reading text goes through one helper (`game/ui/font.py`).

## Your decision

- [ ] **Approve**: go with Option A
- [ ] **Not approve**: say which option you'd prefer, or why
- [ ] **Other**: describe below

**Your notes:**

>
