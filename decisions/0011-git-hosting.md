# D-0011: Where the code is hosted

| | |
|---|---|
| **Status** | Approved, Option A (2026-10-09) |
| **Raised** | 2026-10-08 |
| **Affects** | Backups, collaboration, where the web build is hosted (D-0002) |
| **Built provisionally?** | No. Git is set up locally in this folder only, with no remote. |

## What's being decided

The project is under git on your computer. Should it also live on GitHub (or similar), and should it be public?

## Options

### A. Private GitHub repo now; decide on public at launch (recommended)
- **Pros:**
  - Off-machine backup from day one.
  - Easy to add collaborators.
  - Content and branding stay private until Fordham signs off (D-0009).
- **Cons:** Free GitHub accounts can't use GitHub Pages on private repos, so hosting the web build there needs a paid plan, a public repo, or another host (a Fordham site, Netlify, itch.io). That's not needed until M6.

### B. Local git only, for now
- **Pros:** Nothing to set up.
- **Cons:**
  - No backup if the laptop dies.
  - Harder to share with anyone.

### C. Public GitHub repo from day one (open source, like Pyxel)
- **Pros:**
  - Free GitHub Pages hosting.
  - Others can learn from it or contribute.
  - Fits Pyxel's open-source spirit.
- **Cons:** Draft content, unverified campus facts and unapproved branding would be public before the university has seen them.

## My recommendation

**Option A.** Backups matter as soon as there's real work in the repo, and going private first means nothing goes public before Fordham approval. At launch it's one click to make the repo public, if you want it open source. If Fordham IT has a GitHub organization, the repo might eventually belong there.

If you approve, create an empty private repo on GitHub and send me the URL, or ask me to use the `gh` command-line tool if you have it set up. I'll connect it and push.

## Your decision

- [x] **Approve**: go with Option A
- [ ] **Not approve**: say which option you'd prefer, or why
- [ ] **Other**: describe below

**Your notes:**

>
