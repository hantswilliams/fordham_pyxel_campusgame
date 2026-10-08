# D-0006: Where game text and campus facts live

| | |
|---|---|
| **Status** | Awaiting review |
| **Raised** | 2026-10-08 |
| **Affects** | `content/`, how orientation staff contribute, how facts stay accurate |
| **Built provisionally?** | Yes: JSON files in `content/maps/`. M4 adds `locations.json`, `quests.json` and similar. |

## What's being decided

The game is full of facts that change every year: office locations, services, links. Who updates them, and where do they live?

## Options

### A. JSON files in `content/`, edited by developers, reviewed by staff (recommended, already built)
- **Pros:**
  - Simple and versioned in git.
  - Tests catch broken references.
  - No extra tooling.
- **Cons:**
  - Staff can't easily edit JSON themselves.
  - Changes go through a developer.

### B. A shared Google Sheet that a script converts to JSON
- **Pros:**
  - Orientation staff edit a familiar spreadsheet directly.
  - We run one command to pull the updates in.
- **Cons:**
  - Another moving part: a sync script and sheet permissions.
  - Someone can break the format.
  - Worth it only if staff edit often.

### C. Text written directly in Python code
- **Pros:** Fewest files.
- **Cons:**
  - Every text change is a code change.
  - Non-programmers are shut out.
  - Mixes facts with logic.

## My recommendation

**Option A for now, with B revisited at M4.** JSON keeps things simple while the content is small and we're the only ones editing. When the Campus Guide arrives at M4 and staff start supplying dozens of entries, a Google Sheet import may be worth adding. Either way, entries link to official Fordham pages for details like hours, rather than copying them, so the game doesn't go stale.

## Your decision

- [ ] **Approve**: go with Option A (B revisited at M4)
- [ ] **Not approve**: say which option you'd prefer, or why
- [ ] **Other**: describe below

**Your notes:**

>
