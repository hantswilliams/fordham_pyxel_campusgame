# D-0037: Accessibility (WCAG 2.2 AA) through a generated Campus Guide

| | |
|---|---|
| **Status** | Awaiting review |
| **Raised** | 2026-10-11. You need the tool to be accessible (ADA, WCAG 2.2 AA) for Fordham and other universities, ideally kept up to date by a script |
| **Affects** | A new generated website (the Campus Guide), the web build's page wrapper, the GitHub Pages workflow, and one keyboard behaviour in the game |
| **Built provisionally?** | No |

## What's being decided

From our conversation:
- The **browser is the main way people will play**.
- The game keeps its **pixel-art look**, including its text, for now.
- Accessibility should be **automated**: when gameplay changes, one script (or a push) updates the accessible version.
- The target is **WCAG 2.2 AA**.

**Why the game itself can't meet WCAG as it stands.**

Pyxel draws everything onto one canvas, so a screen reader sees a single picture with no text in it. Pixel text can't be zoomed to 200% or restyled, and the Bike Courier mission has a timer. WCAG has no exemption for games. It does allow a **conforming alternate version**: a fully accessible version with the same information and functions, which people can find from the original.

**Background.** I'm not a lawyer, so check this with Fordham's accessibility office.
- The DOJ's ADA Title II rule requires WCAG 2.1 AA from **public** colleges. In April 2026 the deadlines moved to **April 26, 2027** for large public entities and **April 26, 2028** for small ones.
- **Fordham is private**, so the rule doesn't apply to it directly. It's still covered by ADA Title III and Section 504, where WCAG AA is the usual yardstick.
- Universities buying software, especially public ones, usually ask for a conformance report (a VPAT) against WCAG 2.1 or 2.2 AA. Aiming for **2.2 AA** covers both.

---

# Part 1: The approach

### A. A generated, conforming alternate version: the Rose Hill Campus Guide (recommended)
A script builds an accessible website from the **same content files the game uses**:
- `content/locations.json`
- the missions
- `content/intro.json`
- the map

So the guide can't drift out of step with the game.

- **Pros:**
  - Meets 2.2 AA in plain, well-tested web pages.
  - Fully automatic.
  - Leaves the game's look alone.
  - Works with every screen reader, zoom setting and browser.
- **Cons:**
  - It's a separate experience. Some disability offices prefer one inclusive experience, so it's worth telling Fordham's office early.
  - Students using the guide don't get the game itself.

### B. Make the game itself accessible
Draw all text as real web text over the game, add screen-reader announcements, text size, no timers and high contrast.

- **Pros:** One experience for everyone.
- **Cons:**
  - A big rework of every screen, and the text stops looking like pixel art, which you don't want yet.
  - Exploring a 2D world by screen reader stays hard even then.
  - Proving 2.2 AA conformance for a game is much harder than for web pages.

### C. Both now
- **Pros:** The best experience.
- **Cons:** Twice the work up front. B can follow later as in-game options, built on top of A.

## Your decision (Part 1)

- [ ] **Approve**: Option A now (in-game options can come later)
- [ ] **Not approve**: say which option you'd prefer, or why
- [ ] **Other**: describe below

**Your notes:**

>

---

# Part 2: What the Campus Guide contains

**Home**
- what the guide is
- a link to the game
- how the campus is laid out (its areas)

**Places:** one page per building and landmark, from its card:
- name, type and description
- the "In real life" entrance note and what's inside
- which area it's in
- the card picture, with a text description (alt text)
- **how to get there** from the Webster Ave gate and from the main gate on Xavier Way

**Getting around**
- gates, Ram Van stops and main roads
- **walking directions for the main routes**, worked out from the game map: the gate to the library, the library to McShane, the library to Keating, and so on. For example: "From the Webster Ave gate: north along the walkway past Campbell Hall, about 20 steps, to Walsh Library on your right."

**Missions**
- the **First Week checklist** as real checkboxes that remember your ticks in your browser
- each optional mission as a list of steps with its hints
- **no timers**: Bike Courier becomes "take the package from McShane to O'Hare Hall"

**Ram Passport:** what each mission earns, and the badges.

**About the game:** the intro story and "How to play", as text.

**Accessibility statement:**
- the standard (WCAG 2.2 AA)
- a contact for problems
- the date the guide was last built

**Built to 2.2 AA from the start.** The pages use:
- headings in order
- landmarks (header, nav, main)
- a "skip to content" link
- visible keyboard focus
- colour contrast of at least 4.5:1
- text that reflows at 400% zoom and 320 px wide
- buttons and checkboxes at least 24 × 24 px
- no time limits, nothing that moves or flashes, and no drag-only controls

**Decided at your request:**
- **Name and place:** "Rose Hill Campus Guide", at `/guide/` on the same GitHub Pages site.
- **Progress** in the guide is kept separate from the game's save for now. It's simpler and can't break the game. Linking the two can come later.
- **Directions:** generated write-ups for the main routes, plus "how to get here" from both entrances on every place page. A from-anywhere-to-anywhere picker can come later.

## Your decision (Part 2)

- [ ] **Approve**: build the guide with these contents
- [ ] **Other**: add or remove sections below

**Your notes:**

>

---

# Part 3: Changes to the game page itself

Even with an alternate version, the game page has to meet WCAG's four "non-interference" rules and point people to the guide.

1. **A visible "Accessible Campus Guide" link before the game.** It's the first thing a keyboard or screen-reader user reaches, and the page title and language are set properly.
2. **No keyboard trap.** Today the game takes every key, TAB included, so keyboard users can't get back out to the page. Fix:
   - **Esc** moves focus out of the game to the guide link.
   - Pressing Esc in the browser no longer stops the game (Pyxel's default).
   - A short note under the game says this.
   - The desktop version keeps Esc as quit.
3. **Nothing flashing** more than 3 times a second. Already true; a check will keep it that way.
4. **No audio that plays on its own.** Already true, since the game has no sound. If sound is added later, it needs a mute control.

## Your decision (Part 3)

- [ ] **Approve**
- [ ] **Other**: describe below

**Your notes:**

>

---

# Part 4: Keeping it accessible automatically

**One command builds everything.** `uv run python tools/build_web.py` builds the game and the guide; the guide comes from a new `tools/build_guide.py`. The GitHub Pages workflow publishes both on every push.

**Checks that fail the build:**
- **axe-core**, the engine behind most accessibility audit tools, run against every guide page and the game page's wrapper, set to WCAG 2.2 AA rules.
- **Our own tests:**
  - every place has a description and picture text
  - every route the guide describes can be walked on the map
  - every mission step appears in the guide
  - the guide's colours pass contrast

**Things automation can't prove.** Automated tools catch roughly a third of WCAG issues. A **short manual checklist** in `docs/accessibility-checklist.md` covers the rest, to run before each release:
- a keyboard-only pass
- a VoiceOver pass
- 200% and 400% zoom
- the Esc way out of the game

**Before selling to another university:** an outside audit and a conformance report (VPAT 2.5, WCAG edition). The guide's structure makes that straightforward.

## Your decision (Part 4)

- [ ] **Approve**
- [ ] **Other**: describe below

**Your notes:**

>

---

## Also decided at your request

**`bigger-text` is merged** (pull request #2). The DotGothic16 text and bigger plaques (decision 0036) are in `main`. The game's text is now a style choice, not a compliance problem, so smoother in-game text can be revisited later as part of Option B.

## My recommendation

**Approve all four parts.** It gets you a defensible WCAG 2.2 AA story, keeps the game as you like it, and stays up to date without anyone remembering to do it. Rough effort:
- the guide generator and its pages: about a day
- the game-page fixes: a couple of hours
- the automated checks and checklist: about half a day

## Sources
- [Department of Justice Delays Compliance Deadlines for ADA Web Accessibility (BBK)](https://bbklaw.com/resources/department-of-justice-delays-compliance-deadlines-for-ada-web-accessibility)
- [Title II of the ADA: What does it mean for us? (UC Berkeley)](https://dap.berkeley.edu/ada-title-ii-updates/title-ii-ada-what-does-it-mean-us)
- [Accessibility at Fordham](https://www.fordham.edu/resources/accessibility-at-fordham)
- [WCAG 2.2, conformance requirements: conforming alternate versions and non-interference (W3C)](https://www.w3.org/TR/WCAG22/#conformance-reqs)
