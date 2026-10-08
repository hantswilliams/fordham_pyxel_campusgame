# D-0002: How students will play it

| | |
|---|---|
| **Status** | Awaiting review |
| **Raised** | 2026-10-08 |
| **Affects** | Distribution, controls (keyboard vs touch), save system, testing |
| **Built provisionally?** | No. Today it runs as a desktop Python program, which is the development setup under any option. |

## What's being decided

How does a student actually get the game? Pyxel can export to a single web page (`pyxel app2html`), a desktop executable (`pyxel app2exe`), or a `.pyxapp` file that needs Pyxel installed.

## Options

### A. Web first: a link in orientation emails or the student portal (recommended)
- **Pros:**
  - No install: click a link and play.
  - Works on Mac, Windows and Chromebooks.
  - Easy to update: replace one file.
  - Can be embedded on a Fordham webpage.
- **Cons:**
  - Touch controls on phones need work and testing.
  - Save data lives in the browser, so it can be cleared, and it needs testing early.
  - We need somewhere to host it (GitHub Pages, or a Fordham site).

### B. Desktop downloads (.exe for Windows, .app for Mac)
- **Pros:** Smoothest performance and full keyboard and gamepad support.
- **Cons:**
  - Students must download and run an unknown program.
  - macOS and Windows show security warnings unless the app is code-signed, which costs money and setup.
  - Many students won't bother.

### C. Both equally
- **Pros:** Maximum reach.
- **Cons:** Double the testing for little benefit. The web version already covers desktop browsers.

## My recommendation

**Option A.** The whole point is reaching every incoming student with as little friction as possible, and a link does that. We keep developing on desktop (it's the same code) and add a web build step at M6. I'd test one early web build around M2 to catch surprises with save data or touch controls.

## Your decision

- [ ] **Approve**: go with Option A
- [ ] **Not approve**: say which option you'd prefer, or why
- [ ] **Other**: describe below

**Your notes:**

>
