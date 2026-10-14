# D-0039: Guide link in a new tab, and readable signs and building names

| | |
|---|---|
| **Status** | Decided 2026-10-13: Part 1 approved, Part 2 A, Part 3 A. Built on branch `crisp-signs` |
| **Raised** | 2026-10-13. The guide link replaces the game in the same tab. Words in the intro art (the train's next-stop sign, the station signs, the Ram Van, the Fordham sign) and the building names in the game are hard to read |
| **Affects** | The web page's accessibility bar, the intro scenes, and the name plaques on buildings |
| **Built?** | Yes, on branch `crisp-signs` |

## What's being decided

1. **The guide link.** "Accessible version: Rose Hill Campus Guide" opens in the same tab, so the game is lost and has to load again.
2. **Words painted in the intro art.** These are drawn in Pyxel's tiny 4-pixel font as part of the picture, then scaled up 1.5×, then doubled. The 1.5× step makes letters lopsided ("FORDHAM" with one fat stroke), and the Ram Van in front hides "ROSE HILL" on the Fordham sign.
3. **Building names in the game.** The plaques ("WALSH LIBRARY", "MCSHANE") use a small pixel font baked into the map picture, so they don't get the crisp text from decision 0038.

**Pictures** (in `decisions/images/0039/`, all at a laptop's size):
- `intro_train.png`: the next-stop sign
- `intro_train_arrives.png`: the platform sign seen through the window
- `intro_station.png`: the station signs
- `intro_street.png` and `intro_gate.png`: the Ram Van and the Fordham sign
- `plaques_mcshane.png`, `plaques_walsh.png`, `plaques_campbell.png`: building plaques, today against options A and B

---

# Part 1: Open the guide in a new tab

The link opens the Campus Guide in a new tab, so the game stays where it was. The link says "(opens in a new tab)", because WCAG advises warning people before a link opens a new window. Esc still moves the keyboard from the game to this link.

**Checked:** the accessibility check passes (60 pages, 0 problems), and the game still sits below the bar, which is now a little longer.

## Your decision (Part 1)

- [x] **Approve**
- [ ] **Not approve**: say why
- [ ] **Other**: describe below

**Your notes:**

>

---

# Part 2: Signs in the intro

### A. Letter the signs in the crisp font, and scale the intro art in one step (recommended)

**Signs:**
- Each sign keeps its place, colour and size. Only its words change: they're drawn at full detail in the bold cut of the game's font (M PLUS 1 Code Bold).
- This covers "NEXT STOP: FORDHAM", the station's "FORDHAM" and "EXIT", "RAM VAN" on the bus, and "FORDHAM / ROSE HILL" on the fence.
- The words only show where their sign does, so anything passing in front still covers them.

**Scene changes:**
- The Fordham sign moves up the fence a little and gets slightly taller, so the passing Ram Van no longer hides "ROSE HILL".
- When the train stops, "FORDHAM" through the window gets a small blue platform sign behind it. Before, the word floated over the buildings.

**Even pixels:** the intro scenes are scaled 3× in one step instead of 1.5× and then 2×. Every pixel of the people, train and buildings is now the same size, so faces and edges look even (compare the passengers in `intro_train_arrives.png`).

**Pros:** readable signs that match the dialogue text, and evenly scaled art in the intro.

**Cons:** the signs no longer look hand-pixelled.

### B. Keep pixel lettering, but bigger and even
Redraw each sign's words in a bolder pixel font at whole-number sizes.

- **Pros:** keeps the pixel-art look.
- **Cons:**
  - Still blocky.
  - Signs would need to grow to fit bigger pixel letters.
  - More hand work for each sign.

## Your decision (Part 2)

- [x] **Approve**: A
- [ ] **Not approve**: say which option you'd prefer
- [ ] **Other**: describe below

**Your notes:**

>

---

# Part 3: Building names in the game

Both options letter the plaques at full detail in M PLUS 1 Code Bold, redrawn each frame like the dialogue text. The words only show where the plaque does, so the area banner, the mission bar, "!" bubbles and people walking past still cover them.

### A. Crisp, same plaque size
- **Pros:** sharper letters with nothing else changed.
- **Cons:** the letters are still small, about 7 pixels tall.

### B. Crisp, bigger plaques (recommended)
- Plaques grow from 11 to 14 pixels tall.
- Names are lettered as big as the wall allows: 7 pixels a letter (up from 5) where there's room, stepping down to 6, 5 or 4 for long names on narrow walls. "WALSH LIBRARY" and "MCSHANE" get the biggest size; "CAMPBELL" stays about today's size because its wall is narrow.

- **Pros:** names are clearly readable while you walk around.
- **Cons:**
  - Bigger plaques cover a little more of some building fronts, such as the tops of Walsh Library's doors. I'd check every building and nudge any that look crowded.
  - Plaques on narrow walls stay smaller, so sizes vary from building to building.

## Your decision (Part 3)

- [x] **Approve**: A
- [ ] **Not approve**: say which option you'd prefer
- [ ] **Other**: describe below

**Your notes:**

>

---

## Notes

**Speed.** Lettering the plaques each frame adds about 1 ms per frame on top of decision 0038's 4 to 5 ms. I'll trim that when building it properly. The intro's one-step scaling costs about the same as before.

**Other small pixel words.** The ID card ("FORDHAM", "TAP ID") and the title screen's "Prototype - placeholder art" note still use the tiny pixel font. I can give them the same treatment as part of this.

**The campus map (M key)** shows the whole campus shrunk down, so its plaques stay as they are. Its pin labels already use the crisp text.

## What the prototype changed (branch `crisp-signs`)

- **`tools/build_web.py`:** the guide link opens in a new tab and says so.
- **`game/gfx/display.py`:**
  - draws the intro picture at 3× in one step (`queue_image`)
  - masks painted words to their sign's colour (`bg`), so things in front cover them
- **`game/ui/font.py`:** `font.sign()` letters words on signs and plaques in M PLUS 1 Code Bold (new file `assets/fonts/MPLUS1Code-Bold.ttf`, Latin letters only, 25 KB).
- **`game/gfx/intro_art.py`:**
  - signs go through `font.sign()`
  - the Fordham sign moves up and gets taller
  - the platform sign is added through the train window
- **`game/gfx/building_overlay.py` and `game/scenes/overworld.py`:** plaques are drawn without words, and their names are lettered each frame (option B).
- **Tests:** all 266 pass. Tests for the new parts come with the final build.

## What was built (2026-10-13)

As decided: the guide opens in a new tab, intro signs are lettered crisp (A), and building plaques are crisp at today's size (A).

- **Plaques (Part 3 A):** same 11-pixel plaques, with names lettered in M PLUS 1 Code Bold at 5 pixels a letter (4 for names too long for their wall), centred on the plaque. The bigger-plaque prototype (B) was taken out.
- **Speed:** the overworld takes about 4.8 ms a frame, against 4.3 ms before this change. Building pictures were also being looked up on disk every frame (about 0.7 ms); they're now looked up once, which pays for most of the plaques' cost.
- **Tests:** 267 pass, with new checks that:
  - signs are covered by what's drawn over them
  - the intro art is scaled 3× in one step, every art pixel exactly 3 × 3
  - every plaque name is lettered at full detail
  - the guide link opens in a new tab and says so
- **Accessibility check:** 60 pages, 0 problems.
- **Not done:** the ID card's "FORDHAM" / "TAP ID" and the title screen's prototype note still use the tiny pixel font. Say if you'd like them crisp too.

## Follow-up (2026-10-13): the keyboard after visiting the guide

**What went wrong:** after opening the guide in its new tab and coming back, Enter didn't reach the game. The guide link still had focus, so Enter opened the guide again, and you had to click the game to get the keys back.

**Fixed:**
- **A visible paused state.** Whenever the game has started but the page has the keyboard (after Esc, or after clicking the guide link), the game shows **"Game paused"** with "Click here to keep playing". The bar's message turns yellow and reads "Game paused: click the game to keep playing." Screen readers announce the change.
- **Coming back to the tab:** "Game paused" takes focus and reads "Press Enter or click to keep playing", so Enter carries on playing instead of reopening the guide.
- **Clicking a link in the bar** now hands the keyboard to the page, so keys no longer go to the link and the game at once.

**Checked:** with a stand-in for Pyxel's runtime, I walked through it step by step: playing, Esc, pausing, clicking to resume, opening the guide, returning, and pressing Enter to resume. Keys reach the game only while it's playing, and no extra guide tabs open. The accessibility check still passes (60 pages, 0 problems). Two steps were added to `docs/accessibility-checklist.md`.

