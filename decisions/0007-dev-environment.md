# D-0007: Python setup and tooling

| | |
|---|---|
| **Status** | Approved, Option A (2026-10-09) |
| **Raised** | 2026-10-08 |
| **Affects** | `pyproject.toml`, `uv.lock`, how anyone runs the project |
| **Built provisionally?** | Yes: `pyproject.toml` + `uv.lock`, tested with Python 3.12 and Pyxel 2.9.9. |

## What's being decided

How do we install Python and Pyxel so the project runs the same on every machine? **Pyxel 2.9 requires Python 3.11 or newer**, and many Macs have an older system Python.

## Options

### A. uv + Python 3.12 + pytest (recommended, already built)
- `uv sync` downloads the right Python and Pyxel into `.venv`, and `uv run …` runs things inside it.
- **Pros:**
  - One command to set up.
  - It installs the right Python for you.
  - The lockfile pins exact versions, so collaborators get the same setup.
  - Very fast.
- **Cons:** One more tool to install (`brew install uv`).

### B. Plain `python -m venv` + `pip install pyxel`
- **Pros:** Uses only standard tools.
- **Cons:**
  - You must install Python 3.11+ yourself first.
  - No lockfile, so versions drift between machines.

### C. Conda
- **Pros:** Common in data-science courses.
- **Cons:** Heavyweight and slower, with no benefit for a pure-Python game.

## My recommendation

**Option A.** It removes the most common failure ("wrong Python version") and makes it easy to hand the project to a student collaborator: clone, `uv sync`, `uv run python main.py`. pytest runs the tests and the content checks.

## Your decision

- [x] **Approve**: go with Option A
- [ ] **Not approve**: say which option you'd prefer, or why
- [ ] **Other**: describe below

**Your notes:**

>
