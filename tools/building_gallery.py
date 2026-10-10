"""Build one review page for every drawn building (decisions/0020).

Each building gets a row with: its reference photo, how it looks in the
game, how it looked as plain tiles, the map drawing on its own, the card
picture, its footprint, its status, and its notes.

    uv run python tools/building_gallery.py      # build/building_gallery.html

The page is self-contained (images are embedded), so it can be opened from
the folder, sent to someone, or published as a private link for review.
"""

import base64
import html
import json
import re
import sys
import tempfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pyxel  # noqa: E402

from game import config  # noqa: E402
from game.gfx.building_art import draw_on_map  # noqa: E402
from game.gfx.building_overlay import draw_overlay  # noqa: E402
from game.gfx.placeholder_art import CHAR_IMAGE_BANK, build_all, character_uv  # noqa: E402
from game.scenes.overworld import bake_tilemap  # noqa: E402
from game.world.buildings import load_buildings  # noqa: E402
from game.world.directions import Direction  # noqa: E402
from game.world.locations import load_locations  # noqa: E402
from game.world.mapdata import load_map  # noqa: E402

TILE = config.TILE
MARGIN = 3  # tiles of surroundings around each building in the in-game views
OUT = ROOT / "build" / "building_gallery.html"
PHOTO_TYPES = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png"}
STATUS_TEXT = {"draft": "Draft", "in review": "In review", "approved": "Approved"}
LEGEND_NOTE = {"A": "entrance (glass arch)", "D": "entrance (door)", "J": "entrance (glass door)",
               ":": "walkway", "G": "roof", "t": "tower", "S": "stone", "R": "roof",
               "O": "roof", "Q": "roof", "W": "wall", "w": "window"}


def data_uri(path: Path) -> str:
    mime = PHOTO_TYPES.get(path.suffix.lower(), "image/png")
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def photo_uri(path: Path, max_w: int = 900) -> str:
    """A reference photo, shrunk to a JPEG so the page stays small
    (needs Pillow, a dev dependency; without it the photo goes in as is)."""
    try:
        from io import BytesIO

        from PIL import Image
    except ImportError:
        return data_uri(path)
    im = Image.open(path).convert("RGB")
    if im.width > max_w:
        im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
    buf = BytesIO()
    im.save(buf, "JPEG", quality=82)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def render_map(m, with_buildings: bool, locations=None) -> "pyxel.Image":
    bake_tilemap(m, 0)
    img = pyxel.Image(m.width * TILE, m.height * TILE)
    img.bltm(0, 0, 0, 0, 0, m.width * TILE, m.height * TILE)
    if with_buildings:
        for b in m.buildings:
            draw_on_map(b, img)
        draw_overlay(img, m, locations or {})
    return img


def draw_people(img, m, b) -> None:
    """NPCs nearby plus a player standing at the first entrance, for scale."""
    for o in m.objects:
        if o.type == "npc":
            u, v = character_uv(o.sprite, o.facing, 0)
            img.blt(o.x * TILE, o.y * TILE - 2, CHAR_IMAGE_BANK, u, v, TILE, TILE, 0)
    ex, ey = b.entrances()[0]
    for d in Direction:
        px, py = ex - d.dx, ey - d.dy
        if not m.is_blocked(px, py):
            u, v = character_uv(0, d, 0)
            img.blt(px * TILE, py * TILE - 2, CHAR_IMAGE_BANK, u, v, TILE, TILE, 0)
            break


def crop_png(img, b, m) -> str:
    """The building and its surroundings, as a PNG data URI."""
    (ox, oy), (w, h) = b.origin, b.size
    x0, y0 = max(0, ox - MARGIN), max(0, oy - MARGIN)
    x1, y1 = min(m.width, ox + w + MARGIN), min(m.height, oy + h + MARGIN)
    out = pyxel.Image((x1 - x0) * TILE, (y1 - y0) * TILE)
    out.blt(0, 0, img, x0 * TILE, y0 * TILE, out.width, out.height)
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "crop.png"
        out.save(str(p), 1)
        return data_uri(p)


def md_to_html(text: str) -> str:
    """Just enough Markdown for notes.md: headings, bullets, bold, code."""
    def inline(s: str) -> str:
        s = html.escape(s)
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        return re.sub(r"`(.+?)`", r"<code>\1</code>", s)

    out, in_list = [], False
    for line in text.splitlines():
        if line.startswith("- "):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{inline(line[2:])}</li>")
            continue
        if in_list:
            out.append("</ul>")
            in_list = False
        if line.startswith("# "):
            continue  # the row already has the building's name
        if line.startswith("## "):
            out.append(f"<h4>{inline(line[3:])}</h4>")
        elif line.strip():
            out.append(f"<p>{inline(line)}</p>")
    if in_list:
        out.append("</ul>")
    return "\n".join(out)


def footprint_html(b) -> str:
    rows = []
    for row in b.footprint:
        cells = "".join(
            f'<span class="fp fp-{"door" if ch in "ADJ" else "walk" if ch in ":." else "none" if ch == " " else "solid"}">'
            f"{html.escape(ch) if ch != ' ' else '&nbsp;'}</span>" for ch in row)
        rows.append(f"<div>{cells}</div>")
    used = sorted({ch for row in b.footprint for ch in row if ch != " "})
    key = " · ".join(f"<code>{html.escape(c)}</code> {LEGEND_NOTE.get(c, '')}" for c in used)
    return f'<div class="footprint">{"".join(rows)}</div><p class="key">{key}</p>'


def panel(title: str, body: str, note: str = "", wide: bool = False) -> str:
    cls = "panel wide" if wide else "panel"
    note_html = f'<figcaption>{note}</figcaption>' if note else ""
    return f'<figure class="{cls}"><h3>{title}</h3>{body}{note_html}</figure>'


def building_section(b, locations) -> str:
    meta = json.loads((b.folder / "building.json").read_text(encoding="utf-8"))
    m = load_map(b.map_id, config.MAPS_DIR)
    drawn = render_map(m, True, locations)
    draw_people(drawn, m, b)
    tiles = render_map(m, False)
    draw_people(tiles, m, b)

    panels = []
    for src in meta.get("sources", []):
        rel = src.split(" (")[0]
        p = ROOT / rel
        if p.suffix.lower() in PHOTO_TYPES and p.exists():
            panels.append(panel("Reference photo", f'<img class="photo" src="{photo_uri(p)}" alt="Reference photo of {html.escape(b.name)}">',
                                html.escape(src.split(" (", 1)[1].rstrip(")") if " (" in src else rel)))
            break
    panels.append(panel("In the game", f'<img class="px" src="{crop_png(drawn, b, m)}" alt="{html.escape(b.name)} as drawn, in the game">',
                        "The drawing over the map, with a player at an entrance for scale."))
    panels.append(panel("Before: tiles only", f'<img class="px" src="{crop_png(tiles, b, m)}" alt="{html.escape(b.name)} built from tiles">',
                        "What shows if map.png is missing. The minimap reads these tiles."))
    if b.map_png:
        panels.append(panel("Map drawing", f'<img class="px checker" src="{data_uri(b.map_png)}" alt="map.png">',
                            f"map.png · {b.size[0]}×{b.size[1]} tiles · offset {b.sprite_offset[0]}, {b.sprite_offset[1]} px"))
    if b.card_png:
        panels.append(panel("Card picture", f'<img class="px" src="{data_uri(b.card_png)}" alt="card.png">',
                            "card.png · shown at the top of the building card", wide=True))
    panels.append(panel("Footprint", footprint_html(b),
                        f"Origin tile {b.origin[0]}, {b.origin[1]} on {b.map_id} · {len(b.entrances())} entrances"))

    loc = locations.get(b.location)
    blurb = html.escape(loc.blurb) if loc else ""
    notes = b.folder / "notes.md"
    notes_html = md_to_html(notes.read_text(encoding="utf-8")) if notes.exists() else ""
    status = b.status
    return f"""
<section class="building" id="{b.id}">
  <header class="bhead">
    <div>
      <p class="eyebrow">{html.escape(b.id)} · faces {b.faces}</p>
      <h2>{html.escape(b.name)}</h2>
      <p class="blurb">{blurb}</p>
    </div>
    <span class="status status-{status.replace(' ', '-')}">{STATUS_TEXT[status]}</span>
  </header>
  <div class="panels">{''.join(panels)}</div>
  <details class="notes" open><summary>Notes, sources and open questions</summary>{notes_html}</details>
</section>"""


STYLE = """
/* Layout: one section per building; a wrapping grid of labelled panels. */
:root {
  --bg: #f3f1ec; --surface: #fffdf9; --ink: #26223a; --muted: #6b6578;
  --line: #ddd6ca; --accent: #860038; --stone: #c6bdae;
  --ok: #2f6b3a; --warn: #8a5a00; --info: #2b4f8a;
  --display: "Pixelify Sans", "Courier New", monospace;
  --body: "Source Sans 3", "Segoe UI", system-ui, sans-serif;
  --mono: "IBM Plex Mono", ui-monospace, Menlo, monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #1b1922; --surface: #24212d; --ink: #ece7df; --muted: #a59eb0;
  --line: #3a3546; --accent: #e0668f; --stone: #6f685e;
  --ok: #7cc98a; --warn: #e9c35b; --info: #8fb0ef; color-scheme: dark } }
:root[data-theme="dark"] {
  --bg: #1b1922; --surface: #24212d; --ink: #ece7df; --muted: #a59eb0;
  --line: #3a3546; --accent: #e0668f; --stone: #6f685e;
  --ok: #7cc98a; --warn: #e9c35b; --info: #8fb0ef; color-scheme: dark }
body { background: var(--bg); color: var(--ink); font: 16px/1.5 var(--body); }
.wrap { max-width: 1180px; margin: 0 auto; padding-inline: 16px; padding-block: 28px 56px; display: grid; grid-template-columns: minmax(0, 1fr); gap: 32px; }
.top h1 { font: 600 2rem/1.1 var(--display); margin: 0 0 6px; color: var(--accent); text-wrap: balance; }
.top p { margin: 0; max-width: 68ch; color: var(--muted); }
.top .meta { font: 0.8rem var(--mono); margin-top: 8px; }
.check { margin: 14px 0 0; padding-left: 1.2em; max-width: 72ch; }
.check li { margin: 2px 0; }
.building { background: var(--surface); border: 1px solid var(--line); border-radius: 6px; padding: 20px; display: grid; grid-template-columns: minmax(0, 1fr); gap: 18px; min-width: 0; }
.bhead { display: flex; gap: 16px; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; }
.bhead > div { min-width: 0; flex: 1 1 320px; }
.eyebrow { font: 0.75rem var(--mono); letter-spacing: 0.06em; text-transform: uppercase; color: var(--muted); margin: 0; }
h2 { font: 600 1.5rem/1.2 var(--display); margin: 2px 0 6px; text-wrap: balance; }
.blurb { margin: 0; max-width: 70ch; }
.status { font: 600 0.8rem var(--mono); letter-spacing: 0.04em; text-transform: uppercase; padding: 4px 10px; border-radius: 999px; border: 1.5px solid currentColor; white-space: nowrap; }
.status-draft { color: var(--muted); } .status-in-review { color: var(--warn); } .status-approved { color: var(--ok); }
.panels { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 330px), 1fr)); gap: 16px; align-items: start; }
.panel { margin: 0; min-width: 0; display: grid; gap: 8px; }
.panel.wide { grid-column: span 2; }
@media (max-width: 720px) { .panel.wide { grid-column: auto; } .building { padding: 14px; } }
.panel h3 { font: 600 0.78rem var(--mono); letter-spacing: 0.06em; text-transform: uppercase; color: var(--accent); margin: 0; }
.panel img { display: block; width: 100%; height: auto; border: 1px solid var(--line); border-radius: 3px; }
.panel img.px { image-rendering: pixelated; }
.checker { background: repeating-conic-gradient(var(--line) 0% 25%, var(--surface) 0% 50%) 0 0 / 16px 16px; }
figcaption { font-size: 0.85rem; color: var(--muted); }
.footprint { font: 0.95rem/1 var(--mono); display: grid; gap: 2px; overflow-x: auto; }
.footprint div { display: flex; gap: 2px; }
.fp { width: 1.6em; height: 1.6em; display: grid; place-items: center; border-radius: 2px; }
.fp-solid { background: var(--stone); color: var(--ink); }
.fp-door { background: var(--info); color: var(--surface); font-weight: 600; }
.fp-walk { background: transparent; border: 1px dashed var(--line); color: var(--muted); }
.fp-none { background: transparent; }
.key { font-size: 0.8rem; color: var(--muted); margin: 0; }
code { font-family: var(--mono); font-size: 0.9em; overflow-wrap: anywhere; }
.notes { border-top: 1px solid var(--line); padding-top: 12px; }
.notes summary { cursor: pointer; font-weight: 600; }
.notes summary:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.notes h4 { font: 600 0.95rem var(--body); margin: 14px 0 4px; }
.notes p, .notes ul { margin: 4px 0; max-width: 75ch; }
"""


def main() -> None:
    pyxel.init(config.SCREEN_W, config.SCREEN_H, headless=True)
    config.apply_palette(pyxel.colors)
    build_all()
    locations = load_locations(config.LOCATIONS_FILE)
    buildings = load_buildings(config.BUILDINGS_DIR)
    sections = "".join(building_section(b, locations) for b in buildings)
    count = {s: sum(b.status == s for b in buildings) for s in STATUS_TEXT}
    summary = ", ".join(f"{n} {STATUS_TEXT[s].lower()}" for s, n in count.items() if n)
    page = f"""<title>Campus Quest Buildings</title>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Pixelify+Sans:wght@600&family=Source+Sans+3:wght@400;600&display=swap">
<style>{STYLE}</style>
<main class="wrap">
  <header class="top">
    <h1>Fordham Campus Quest · Buildings</h1>
    <p>Drawn buildings for review (decisions/0020). Each one is compared with its reference photo and with how it looked as plain tiles.</p>
    <ul class="check">
      <li>Would a first-year recognise the building from the lawn?</li>
      <li>Are the entrances on the right side, and easy to spot?</li>
      <li>Does the outline match the campus map closely enough?</li>
      <li>Is the card picture accurate, with nothing that isn't really there?</li>
    </ul>
    <p class="meta">{len(buildings)} building{'s' if len(buildings) != 1 else ''} · {summary} · built {date.today().isoformat()}</p>
  </header>
  {sections}
</main>
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page, encoding="utf-8")
    print("saved", OUT.relative_to(ROOT), f"({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
