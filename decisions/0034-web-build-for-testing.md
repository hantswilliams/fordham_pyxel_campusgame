# D-0034: A web build for quick testing (Pyodide)

| | |
|---|---|
| **Status** | Approved 2026-10-11 (A for all four parts). Built 2026-10-11; browser check pending (see "Your browser check" below) |
| **Raised** | 2026-10-11. You'd like the game to run as a static web page for quick testing, using Pyxel's web support (Pyodide) |
| **Affects** | A new build script and output file, one change to how the game saves, and possibly one key. The desktop game is unchanged |
| **Built?** | Yes: see "What was built" at the end |

## What's being decided

Pyxel can run our game in a web browser without changing the game's code. It uses **Pyodide**, a version of Python that runs inside the browser. The result is a single HTML file that any static host can serve, with no server code. Anyone with the link could play the latest build in a browser, with nothing to install.

Four things need deciding:
1. how we build the HTML file
2. where the test link lives
3. how saving works in a browser
4. one key that may not behave in a browser

The two-step build (from the [Pyxel Web docs](https://raw.githubusercontent.com/kitao/pyxel/main/docs/pyxel-web-en.md)):

    pyxel package <folder> main.py           # bundles the game into one .pyxapp file
    pyxel app2html <name>.pyxapp             # turns that into one .html file

**Things true whichever options you pick:**
- **First load takes a few seconds.** The browser downloads Pyodide and Pyxel's runtime from a CDN. Later loads come from the browser's cache. The page needs internet the first time.
- **The download is about 3–4 MB.** That's our game: code, art, content and the reading font. The 29 MB `research/` folder must be left out, because `pyxel package` packs everything in the folder it's given.
- **It's a test build.** The desktop game stays the main version, and nothing in `game/` needs a browser.

---

# Part 1: How to build it

### A. A build script that packs only what the game needs (recommended)
`tools/build_web.py` would:
1. copy `main.py`, `game/`, `assets/` and `content/` into `build/web/stage/`, leaving out `research/`, `tests/`, `tools/` and the screenshots
2. run `pyxel package` and `pyxel app2html`
3. pin Pyxel to **2.9.9**, the version we use, so a new Pyxel release can't break the test build overnight
4. write `build/web/fordham_campus_quest.html`

- **Pros:** One command (`uv run python tools/build_web.py`). Small, predictable output. The same file works on any host or opened locally.
- **Cons:** You re-run it whenever you want a fresh test build.

### B. Pyxel's Web Launcher, pointed at the GitHub repo
Pyxel hosts a launcher page that runs a game straight from a GitHub repo, with no build step.

- **Pros:** Nothing to build. Push to GitHub and the link plays the latest code.
- **Cons:**
  - The repo has to be public.
  - The launcher always uses the newest Pyxel, so it could break without us changing anything.
  - Loading the game as many separate files is slower. Pyxel's own docs recommend packaging instead.

### C. Our own `index.html` using Pyxel's script tags
- **Pros:** Full control of the page, e.g. a title, instructions and a Fordham-styled frame round the game.
- **Cons:** It needs a web server even for local testing, and it's more to maintain. Worth it later for a public launch, not for testing.

## Your decision (Part 1)

- [x] **Approve**: Option A
- [ ] **Not approve**: say which option you'd prefer, or why
- [ ] **Other**: describe below

**Your notes:**

>

---

# Part 2: Where the test link lives

### A. GitHub Pages, from the repo you already have (recommended)
The repo is on GitHub (`hantswilliams/fordham_pyxel_campusgame`). A small GitHub Actions workflow would run the build on every push to `main` and publish the HTML to GitHub Pages. Every push then updates a fixed link, e.g. `https://hantswilliams.github.io/fordham_pyxel_campusgame/`.

- **Pros:**
  - Free and automatic.
  - One link to share with testers that's always current.
  - No extra accounts.
- **Cons:**
  - The link is public, though not listed anywhere.
  - GitHub Pages on a **private** repo needs a paid GitHub plan. On a free plan the repo would have to be public.

### B. No hosting: open the HTML file yourself
Build locally and double-click `build/web/fordham_campus_quest.html`, or send the file to someone.

- **Pros:** Nothing to set up and nothing public.
- **Cons:**
  - No shareable link.
  - Each tester needs the latest file.
  - Some browsers are stricter with files opened from disk. If one balks, `python -m http.server` in `build/web/` fixes it.

### C. Netlify (or similar) drag-and-drop
- **Pros:** A private-ish link in a minute, with no GitHub settings.
- **Cons:** Another account, and you upload the file by hand after each build unless you connect it to GitHub too.

## Your decision (Part 2)

- [x] **Approve**: Option A
- [ ] **Not approve**: say which option you'd prefer, or why
- [ ] **Other**: describe below

**Your notes:**

>

---

# Part 3: Saving in the browser

Today the game saves `save.json` to a folder on disk (decision 0031). In the browser that "disk" is temporary, so I'd expect progress to be lost on reload unless we change it.

### A. Browser local storage (recommended)
When the game runs in a browser, `SaveFile` reads and writes the same JSON in the browser's `localStorage`, under one key (e.g. `fordham_campus_quest_save`). On the desktop it keeps using the file. It's about 15 lines in `game/systems/progress.py`, plus a test for the switch.

- **Pros:**
  - Progress survives reloads and closing the tab.
  - CONTINUE works as on the desktop.
  - Nothing is sent anywhere.
  - Our save is a few KB, well inside the limit (about 5 MB per site).
- **Cons:**
  - The save lives in that one browser on that one device.
  - Clearing site data, or a private window, starts fresh.

### B. Cookies
- **Pros:** The same idea.
- **Cons:**
  - About 4 KB per cookie, which a long save could outgrow.
  - Cookies are sent with every request to the host, which is pointless for a static page.
  - Browsers may expire or block them.
  - Nothing cookies do that local storage doesn't do better here.

### C. No saving in the web build
Every visit starts a new game.

- **Pros:** Nothing to build. Testers always see the opening.
- **Cons:** You can't test CONTINUE, missions across sessions or the Ram Passport without replaying.

**Common to A and B:** progress doesn't follow a player between devices. That would need sign-in and a server, which a static page can't do. It's a decision for a real launch, not for testing.

## Your decision (Part 3)

- [x] **Approve**: Option A
- [ ] **Not approve**: say which option you'd prefer, or why
- [ ] **Other**: describe below

**Your notes:**

> 

---

# Part 4: The TAB key

TAB opens the Mission Log and Ram Passport. In a web page TAB normally moves focus to the next link or button, which could pull keyboard focus off the game. I don't know yet whether Pyxel's web runtime stops that.

### A. Test it first; if TAB misbehaves, Q also opens the menu (recommended)
TAB keeps working wherever it can. Q, which isn't used yet, becomes a second key for the menu, and the controls screen and README mention it.

- **Pros:** Nothing changes for desktop players. Browser players always have a key that works.
- **Cons:** One more key to learn, only if needed.

### B. Change the menu key to Q everywhere
- **Pros:** One key that behaves the same everywhere.
- **Cons:** It changes the controls you've already approved (intro, README, screenshots).

## Your decision (Part 4)

- [x] **Approve**: Option A
- [ ] **Not approve**: say which option you'd prefer, or why
- [ ] **Other**: describe below

**Your notes:**

>

---

## Things I'll check once it's built

I'll test the build in a headless browser here if this workspace can reach Pyxel's CDN. If it can't, I'll say so and give you a two-minute checklist to run on your Mac.
- **The campus map (M).** It copies image memory directly (`ctypes`) to build its detailed picture. I expect this to work under Pyodide but haven't proven it. If it doesn't, there's a slower pure-Python fallback that gives the same picture.
- **The reading font** (PixelMplus TTF) loads from inside the package.
- **Saving:** play, reload, and CONTINUE comes back where you were.
- **Keys:** TAB (Part 4), and X / Z / M.
- **Load time** on a first visit and a repeat visit.
- **Phones:** `app2html` adds an on-screen gamepad by default. I'd keep it, since it lets testers try the game on a phone, and note how it plays.

## My recommendation

**A for every part.**
1. A build script that packs only the game.
2. GitHub Pages so every push updates one test link.
3. Local storage so CONTINUE works in the browser.
4. Test TAB, with Q as a fallback.

It's about half a day of work. Nothing in the desktop game changes except the save gaining a browser branch.

---

## What was built (2026-10-11)

**Part 1: build script**
- `tools/build_web.py` copies `main.py`, `game/`, `assets/` and `content/` into a staging folder. It leaves out the drawing scripts in `assets/buildings/_style`.
- It runs `pyxel package` and `pyxel app2html`, pins the page to Pyxel **2.9.9**, and writes `build/web/index.html`.
- The page is **1.4 MB**, because the package is compressed and then base64-encoded. It also writes `build/web/fordham_campus_quest.pyxapp`, which `pyxel play` can run on a desktop.

**Part 2: GitHub Pages**
- `.github/workflows/web.yml` builds the page and publishes it on every push to `main`, or by hand from the Actions tab.
- **One-time setup:** in the repo's Settings, open Pages and set Source to "GitHub Actions". The link will then be https://hantswilliams.github.io/fordham_pyxel_campusgame/.
- Your local `main` is 9 commits ahead of GitHub. The first build runs once you push.

**Part 3: saves**
- In a web page (`sys.platform == "emscripten"`), `SaveFile` uses the browser's `localStorage` under the key `fordham_campus_quest_save`. On the desktop it still uses `save.json`.
- New tests use a stand-in for local storage. They cover a save, a reload, a damaged save and a delete, and check that the desktop never uses local storage.

**Campus map safety net**
- The map's fast pixel copy (`ctypes`) now has a pure-Python fallback that gives the same picture. A test checks the fallback reads the same pixels.
- If the browser lacks `ctypes`, the map still opens; the first opening is just slower.

**Part 4: TAB.** Not changed yet. It's on the checklist below; if TAB misbehaves, Q gets added as a second menu key.

## Your browser check

This workspace can't reach the CDN that serves Pyxel's web runtime (`cdn.jsdelivr.net`), even through your computer's link, so the build couldn't be run in a browser here. The build itself, the package contents and the save code are tested. Please try this on your Mac:

1. `uv run python tools/build_web.py`
2. `cd build/web && python3 -m http.server 8000`, then open http://localhost:8000 in Chrome or Safari.
3. **Loads:** the title screen appears after a few seconds, and the dialogue text is in the clear reading font.
4. **Keys:** walk with the arrows, talk with Z, skip with X.
5. **TAB:** does the Mission Log open, and do the arrows still move you afterwards? If focus jumps away from the game, tell me and I'll add Q.
6. **M:** the campus map opens. Note roughly how long it takes the first time.
7. **Saving:** play a minute, reload the page, and CONTINUE should put you back where you were.
8. **Phone (optional):** after you push and turn on Pages, open the link on a phone. The on-screen gamepad appears; check it's playable.
