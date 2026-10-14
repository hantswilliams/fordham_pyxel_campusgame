# D-0043: Playing on phones and tablets

| | |
|---|---|
| **Status** | For your review (not built yet) |
| **Raised** | 2026-10-14. On a touch screen some things need a partial redesign for phones |
| **Affects** | The on-screen controls, the button names the game shows, the web page's layout on phones, and testing |
| **Built?** | Not yet. I'll build it on a new branch `mobile` after your decisions |

**Picture:** `decisions/images/0043/phone_layouts_mockup.png` is a mockup of the proposed portrait and landscape layouts. It's drawn by hand around a real game screenshot, not a screenshot from a phone.

## Where we are today

I went through how the web build behaves on a touch screen. Some of it already works:

- **There are on-screen controls.** Pyxel's web runtime shows its own virtual gamepad on touch screens: a d-pad bottom left, four buttons (A, B, X, Y) bottom right, and a small split menu button (SELECT / START) at the bottom middle. It keeps the bottom fifth of the screen for them.
- **The game already understands them:**

  | Button | Does |
  |---|---|
  | D-pad | Walk |
  | A | Talk, read, OK (Z) |
  | B | Back, bike on/off (X) |
  | START | Missions (Tab) |
  | SELECT | Map (M) |
  | X and Y | Nothing |

- **Text is readable.** On a phone held upright the game is about 390 points wide, so the reading font comes out about the size of normal phone text, a little smaller in landscape. Building plaques are small but legible.
- **Saves work.** They live in the browser's storage, and that works on phones.
- **The Campus Guide is phone-friendly already.** Its pages are checked at 320 px wide (decision 0037).

What doesn't work well yet:

1. **The buttons aren't labelled.** Nothing says that A talks, B goes back or hops on the bike, or that Map and Missions hide on the tiny SELECT/START button. X and Y do nothing.
2. **The game names keyboard keys.** About 20 places say "Z: NEXT", "Press X to hop on your bike", "M: CLOSE", "TAB", "ARROWS". That includes the HOW TO PLAY card, the menu and map footers, the ID check and a mission hint.
3. **The top bar is built for keyboards.** On a phone it wraps onto three lines, takes about 140 points of a small screen, and shows "Tab: missions · M: map · Esc" and "Play with the keyboard", which mean nothing on a touch screen.
4. **Some page wording assumes a mouse.** "Game paused: click the game" should say tap.
5. **Phone browsers do phone things.** Double-tap zoom, pull-to-refresh, long-press menus on the buttons, the address bar changing the screen height, and notches all affect a game page. None of that is handled yet.
6. **Landscape wastes space.** The game always keeps the bottom fifth free for the controls, but in landscape the controls sit beside the game, so it could be about 25% bigger.
7. **Speed on phones is unknown.** The crisp text (decision 0038) costs about 4 to 5 ms a frame on a laptop. A phone browser may be several times slower. It needs measuring on real phones.
8. **It has never been tried on a real phone.** Every check so far has been on a desktop browser.

---

# Part 1: Touch controls

### A. Keep Pyxel's on-screen gamepad, label it, and use all four buttons (recommended)

- **Labels:** a small label next to each control: "Walk" by the d-pad, then "Talk / OK" (A), "Back · Bike" (B), "Map" (Y) and "Missions" (X).
- **Bigger buttons for Map and Missions:** Y opens the map and X opens Missions. SELECT and START keep working too.
- **Hidden on computers:** the labels only appear on touch screens, where the gamepad does.
- **Pros:**
  - Small and low risk, since Pyxel already handles multi-touch, holding a direction, and pressing two buttons at once.
  - It's the Game Boy-style layout players expect.
- **Cons:**
  - Pyxel's button pictures stay as they are (grey, unbranded).
  - The labels have to follow Pyxel's button positions.

### B. Our own touch controls

Replace Pyxel's gamepad with our own maroon, labelled HTML buttons.

- **Pros:**
  - Fordham's look.
  - Exactly the size and layout we want.
- **Cons:**
  - More work.
  - We'd own multi-touch handling, sliding a thumb across the d-pad and button repeat, which Pyxel already gets right.
  - Easy to get subtly wrong.

### C. Later, on top of A: tap to walk

Tap a spot on the map and you walk there; tap a person or a sign to talk to it. The game already has a path-finder (the Campus Guide's directions use it). It's the most natural way to play on a phone, but it's a bigger piece of work, so I'd do it as its own decision after A.

## Your decision (Part 1)

- [ ] **Approve**: A now (C can come later)
- [ ] **Not approve**: say which option you'd prefer
- [ ] **Other**: describe below

**Your notes:**

>

---

# Part 2: Button names that match the device

On a touch screen the game names the touch buttons; on a computer it names the keys:

| Keyboard | Touch |
|---|---|
| Z: NEXT | A: NEXT |
| X: SKIP | B: SKIP |
| M: CLOSE | Y: CLOSE |
| TAB: CLOSE | X: CLOSE |
| Press X to hop on your bike | Press B to hop on your bike |

The HOW TO PLAY card lists the touch buttons on a phone ("D-pad: Walk", "A: Talk, read, open a card", and so on).

**How:**
- One table of button names in the code.
- In the content files, key names become placeholders such as `{confirm}` and `{back}`, which the game fills in.
- The game tells touch from keyboard the same way Pyxel does when it shows the gamepad.
- The Campus Guide keeps removing button instructions, as it does now.

**Alternative:** show both everywhere ("Z/A: NEXT"). That's simpler, but it's cluttered and confusing on both.

## Your decision (Part 2)

- [ ] **Approve**: names follow the device
- [ ] **Not approve**: show both everywhere
- [ ] **Other**: describe below

**Your notes:**

>

---

# Part 3: The page on a phone

**A compact top bar on touch screens.** One line, about 36 points tall:
- **"Accessible guide ↗"**: the same link, shorter, still first on the page and still opening in a new tab
- **a status dot:** "Playing", or "Paused: tap the game"

The keyboard hints and "Play with the keyboard" button are hidden on touch screens and stay on computers.

**Portrait:**
- The game sits right under the bar, full width.
- The controls go in the space below, within thumb reach.

**Landscape:**
- The game uses the full height.
- The d-pad and buttons sit in the empty space on its left and right, as in the mockup.

**Phone browser fixes:**
- **Accidental zooming:** double-tap and pinch don't zoom the game. The Campus Guide still zooms, as WCAG requires of the accessible version.
- **Accidental reloads:** dragging down doesn't pull-to-refresh and reload the page mid-game.
- **Long-press:** holding a button doesn't select text or open the long-press menu.
- **Notches:** the bar and controls stay clear of notches and rounded corners.
- **Address bar:** the layout follows the visible screen height as the address bar shows and hides.

**Touch wording:** "Tap here to keep playing" on the paused screen. Tapping the game resumes it, as clicking does now.

## Your decision (Part 3)

- [ ] **Approve**
- [ ] **Other**: describe below, for example portrait only

**Your notes:**

>

---

# Part 4: Text size on phones

### A. Keep the current sizes for now (recommended)

At phone size the reading text is about normal phone-text size, so it's readable. The building plaques are the smallest words on screen. I'd check them on real phones (Part 5) before changing anything.

### B. A "phone view" that shows less of campus, bigger

The screen would show about two-thirds as many tiles, so everything is 1.5× bigger.

- **Pros:** much easier to read on small phones.
- **Cons:**
  - Every text box, menu and card was laid out for the current size and would need a phone version.
  - A big redesign.
  - You'd see less of campus at once.

## Your decision (Part 4)

- [ ] **Approve**: A, and revisit after testing on real phones
- [ ] **Not approve**: B
- [ ] **Other**: describe below

**Your notes:**

>

---

# Part 5: Speed and real-phone testing

**A frame-rate check.** Adding `?perf` to the page address (for example `…/fordham_pyxel_campusgame/?perf`) shows Pyxel's built-in frame-rate counter, so you can see on a phone whether the game holds 30 frames a second.

**If phones are too slow**, in order of effort:
1. Draw the world layer once per step instead of every frame.
2. Double only the parts of the screen that changed.
3. On slow phones only, fall back to the pixel text (decision 0036).

I'd only pick one of these if testing shows the need.

**Automatic checks.** The GitHub workflow also opens the game page and the guide as an iPhone-sized and an Android-sized phone, upright and sideways, and checks that:
- the bar is one line
- the game fits below it
- nothing scrolls sideways
- the controls' labels are there

**A manual phone checklist** in `docs/accessibility-checklist.md`, about 10 minutes per release, on an iPhone (Safari) and an Android phone (Chrome):
- walk, talk and ride the bike
- open the map and Missions
- turn the phone sideways
- leave the game for the guide and come back
- reload and continue

## Your decision (Part 5)

- [ ] **Approve**
- [ ] **Other**: describe below

**Your notes:**

>

---

## My recommendation

Approve **1A, 2, 3, 4A and 5**. The game is already close to playable on a phone; this makes it obvious to use and comfortable. Rough effort:
- labels and the X/Y buttons: half a day
- button names that follow the device: half a day
- the phone page layout and browser fixes: a day
- `?perf`, the automatic phone checks and the checklist: half a day

Tap-to-walk (1C) and a phone view (4B) can follow as their own decisions once we've watched people play on real phones.

**What I need from you after the build:** 10 minutes with your phone on the test site, plus an Android phone if you can borrow one.
