# D-0004: Screen resolution and tile size

| | |
|---|---|
| **Status** | Awaiting review |
| **Raised** | 2026-10-08 |
| **Affects** | All art, text box layout, how much campus is visible at once |
| **Built provisionally?** | Yes: 256×192, 16px tiles, 30 fps. The values are in `game/config.py`. Changing them later means redrawing art, so it's best decided before real art starts. |

## What's being decided

Pyxel draws at a low internal resolution and scales it up to the window. The resolution sets how retro it feels, how much text fits in a dialogue box, and how much art we need.

## Options

### A. 256×192, 16×16 tiles, 30 fps (recommended, already built)
- Shows 16×12 tiles at once.
- **Pros:**
  - Classic Pokémon proportions (16px characters).
  - Fits about 58 characters per line in the text box, enough for useful campus info.
  - The 4:3 shape scales cleanly on laptops.
- **Cons:** A slightly wider view than Game Boy games, which is less "authentic."

### B. 160×144 (true Game Boy)
- **Pros:** Maximum nostalgia.
- **Cons:**
  - Only about 35 characters per line, so resource descriptions get chopped into many tiny pages.
  - Only 10×9 tiles visible, so you see very little of campus.

### C. 320×240 or larger
- **Pros:** More room for text and detail.
- **Cons:**
  - More pixels to fill with art.
  - Starts to look less like a retro game.
  - Pyxel's built-in font gets tiny relative to the screen.

## My recommendation

**Option A.** This is an onboarding game, so text readability matters as much as nostalgia. Option A keeps the Pokémon look while leaving room for real sentences. You can judge it yourself by running the prototype.

## Your decision

- [ ] **Approve**: go with Option A
- [ ] **Not approve**: say which option you'd prefer, or why
- [ ] **Other**: describe below

**Your notes:**

>
