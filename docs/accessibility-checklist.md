# Accessibility checklist (before each release)

Automated checks run on every push (decisions/0037):
- `pytest`: the guide covers every place, mission step and route, and its colours pass contrast.
- `node tools/check_accessibility.cjs build/web`: axe-core with the WCAG 2.2 AA rules, plus reflow at 320 px.

They catch roughly a third of WCAG issues. Do this by hand before each release, on the published site (or `build/web` served with `python3 -m http.server`). It takes about 20 minutes.

## 1. Keyboard only (no mouse)
- [ ] On the game page, the first Tab goes to "Accessible version: Rose Hill Campus Guide".
- [ ] Tab reaches "Play with the keyboard"; Enter starts the game and the arrow keys move you.
- [ ] Esc leaves the game: focus goes to the guide link, and Tab moves through the page again. "Game paused" shows over the game and the bar says how to get back.
- [ ] Open the guide (it opens in a new tab), then come back to the game's tab: "Game paused" has focus, and Enter carries on playing without opening the guide again.
- [ ] In the guide, the first Tab shows "Skip to main content", and Enter jumps to the page heading.
- [ ] Every link, checkbox and button can be reached and used, in a sensible order, with focus always visible.
- [ ] On Missions, ticking a box with Space works, survives a reload, and "Clear all my ticks" clears them.

## 2. Screen reader (VoiceOver on Mac: Cmd+F5)
- [ ] Each guide page announces its title, and the headings list (VO+U) makes sense.
- [ ] Pictures are announced with their description.
- [ ] Checkboxes announce their step and whether they're ticked; the "steps ticked" count is read when it changes.
- [ ] On the game page, the guide link is announced first, and the game screen has a label.

## 3. Zoom and reflow
- [ ] At 200% browser zoom, nothing is cut off or overlapping.
- [ ] At 400% zoom (or a 320 px wide window), the guide reads in one column with no sideways scrolling.

## 4. Content
- [ ] New places have a sensible picture description (`"_card_alt"` in their `building.json` if the default isn't good enough).
- [ ] Directions on a few new or changed places read correctly.
- [ ] The accessibility statement has a contact (`content/guide.json`).

Record the date, who checked, and anything found in the release notes or a new decision doc.

## Phones (decisions/0043), about 10 minutes

On an iPhone (Safari) and an Android phone (Chrome), on the published site:

- [ ] The top bar is one line: "Accessible guide ↗" and a "Playing" / "Paused" dot.
- [ ] The d-pad walks, A talks, B goes back (and hops on and off the bike), Y opens the map, X opens Missions. Labels sit above the controls.
- [ ] The game's own text says A / B / X / Y / D-PAD, not Z / X / M / TAB (HOW TO PLAY, card and map footers, the bike lines).
- [ ] Upright: the game sits at the top with the controls below. Sideways: the game fills the height with the controls either side.
- [ ] Double-tapping or pinching the game doesn't zoom, and dragging down doesn't reload the page.
- [ ] Tap "Accessible guide", come back: "Tap here to keep playing" shows, and tapping resumes.
- [ ] Reload: CONTINUE puts you back where you were.
- [ ] Add `?perf` to the address: the frame counter stays near 30 while walking and with the menu open.

