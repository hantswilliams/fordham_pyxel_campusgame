"""Build the Rose Hill Campus Guide: the accessible version of the game
(decisions/0037), as plain web pages generated from the game's own content.

    uv run python tools/build_guide.py            # writes build/web/guide/
    uv run python tools/build_guide.py OUT_DIR

Everything comes from the files the game uses, so the guide can't drift
out of step:
- places: content/locations.json and the drawn buildings' card pictures
- areas, directions: the map (content/maps/), walked by game/world/routes.py
- missions and the Ram Passport: content/missions/
- the story and how to play: content/intro.json
- the accessibility contact: content/guide.json

The pages are built for WCAG 2.2 AA: landmarks, a skip link, headings in
order, visible focus, contrast of at least 4.5:1, text that reflows, 24 px
targets, no time limits or motion. tools/check_accessibility.mjs tests them
with axe-core.
"""

import html
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from game import config  # noqa: E402
from game.systems.intro_timeline import load_intro  # noqa: E402
from game.systems.missions import MissionBook, load_missions  # noqa: E402
from game.systems.progress import BADGES, Progress  # noqa: E402
from game.world.buildings import load_buildings  # noqa: E402
from game.world.locations import load_locations  # noqa: E402
from game.world.mapdata import load_map  # noqa: E402
from game.world.routes import place_targets, route_to, sentences  # noqa: E402

SITE = "Rose Hill Campus Guide"
GAME_URL = "../index.html"
START_POINTS = {   # where directions start: the cell just inside each entrance
    "webster": ((5, 72), "the Webster Avenue gate"),
    "main": ((80, 23), "the Main Entrance on Xavier Way"),
}
MAIN_ROUTES = [    # (from location, to location): the trips new students make most
    ("webster_gate", "walsh_library"), ("webster_gate", "mcshane_center"),
    ("walsh_library", "mcshane_center"), ("mcshane_center", "keating_hall"),
    ("walsh_library", "dealy_hall"), ("keating_hall", "ohare_hall"),
    ("mcshane_center", "thebaud_hall"), ("edwards_parade", "hughes_hall"),
]
NAV = [("index.html", "Home"), ("places/index.html", "Places"), ("getting-around.html", "Getting around"),
       ("missions.html", "Missions"), ("passport.html", "Ram Passport"), ("about.html", "About the game"),
       ("accessibility.html", "Accessibility")]
KIND_ORDER = ["academic", "residence", "campus", "athletics", "landmark", "transit"]
KIND_NAMES = {"academic": ("Academic building", "Academic buildings"),
              "residence": ("Residence hall", "Residence halls"),
              "campus": ("Campus building", "Campus buildings"),
              "athletics": ("Athletics", "Athletics"),
              "landmark": ("Landmark", "Landmarks"),
              "transit": ("Getting around", "Getting around")}

CSS = """
:root {
  --ink: #1d1d22;        /* body text: 16.4:1 on white */
  --maroon: #860038;     /* Fordham maroon: 9.6:1 on white */
  --muted: #4a4a52;      /* secondary text: 8.6:1 on white */
  --paper: #ffffff;
  --band: #f4eef0;       /* header band: maroon on it is 8.7:1 */
  --focus: #1a4fd6;      /* focus ring: 6.3:1 on white, 3:1+ against maroon */
  --line: #8a8a92;       /* borders: 3.4:1 on white */
}
* { box-sizing: border-box; }
html { font-size: 112.5%; }
body { margin: 0; background: var(--paper); color: var(--ink);
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  line-height: 1.55; overflow-wrap: break-word; }
h1, h2, h3, nav a { overflow-wrap: anywhere; }   /* long names (Hawthorn/Rooney) wrap at 320 px (1.4.10) */
a { color: var(--maroon); text-decoration: underline; text-underline-offset: 0.15em; }
a:hover { text-decoration-thickness: 0.15em; }
:focus-visible { outline: 3px solid var(--focus); outline-offset: 2px; }
.skip { position: absolute; left: 0.5rem; top: -4rem; background: var(--paper); padding: 0.5rem 0.75rem;
  border: 2px solid var(--maroon); z-index: 10; }
.skip:focus { top: 0.5rem; }
header { background: var(--band); border-bottom: 4px solid var(--maroon); }
.wrap { max-width: 46rem; margin: 0 auto; padding: 0 1rem; }
.site { display: block; padding: 0.9rem 0 0.4rem; font-weight: 700; font-size: 1.25rem; color: var(--maroon); }
nav ul { list-style: none; margin: 0; padding: 0 0 0.6rem; display: flex; flex-wrap: wrap; gap: 0.25rem 0.5rem; }
nav a { display: inline-block; padding: 0.35rem 0.5rem; min-height: 2.75rem; line-height: 2rem; }
nav a[aria-current="page"] { font-weight: 700; text-decoration-thickness: 0.2em; }
main { padding: 1.25rem 0 2.5rem; }
h1 { font-size: 1.75rem; line-height: 1.25; color: var(--maroon); margin: 0.5rem 0 1rem; }
h2 { font-size: 1.35rem; line-height: 1.3; margin: 2rem 0 0.5rem; }
h3 { font-size: 1.1rem; margin: 1.5rem 0 0.4rem; }
.kind { display: inline-block; color: var(--muted); font-weight: 600; }
figure { margin: 1rem 0; }
figure img { width: 100%; max-width: 456px; height: auto; image-rendering: pixelated;
  border: 1px solid var(--line); }
figcaption { color: var(--muted); font-size: 0.9rem; }
.check { list-style: none; padding: 0; }
.check li { margin: 0.6rem 0; }
.check label { display: flex; gap: 0.6rem; align-items: flex-start; cursor: pointer; }
.check input { width: 1.5rem; height: 1.5rem; margin: 0.1rem 0 0; flex: none; accent-color: var(--maroon); }
.hint { color: var(--muted); margin: 0.2rem 0 0 2.1rem; }
button { font: inherit; padding: 0.5rem 0.9rem; min-height: 2.75rem; border: 2px solid var(--maroon);
  background: var(--paper); color: var(--maroon); cursor: pointer; }
details { margin: 0.5rem 0; }
summary { cursor: pointer; padding: 0.25rem 0; }
.note { border-left: 4px solid var(--maroon); padding: 0.4rem 0.9rem; background: var(--band); }
footer { border-top: 1px solid var(--line); color: var(--muted); font-size: 0.9rem; padding: 1rem 0 2rem; }
dt { font-weight: 700; margin-top: 0.6rem; }
dd { margin: 0 0 0 1rem; }
@media (prefers-reduced-motion: reduce) { * { scroll-behavior: auto !important; } }
"""

CHECKLIST_JS = """
(function () {
  var KEY = "fcq_guide_checklist";
  var saved = {};
  try { saved = JSON.parse(localStorage.getItem(KEY) || "{}") || {}; } catch (e) { saved = {}; }
  var boxes = document.querySelectorAll("input[data-step]");
  boxes.forEach(function (box) {
    box.checked = !!saved[box.dataset.step];
    box.addEventListener("change", function () {
      saved[box.dataset.step] = box.checked;
      try { localStorage.setItem(KEY, JSON.stringify(saved)); } catch (e) {}
      update();
    });
  });
  var status = document.getElementById("progress");
  function update() {
    if (!status) return;
    var done = 0; boxes.forEach(function (b) { if (b.checked) done++; });
    status.textContent = done + " of " + boxes.length + " steps ticked.";
  }
  var clear = document.getElementById("clear");
  if (clear) clear.addEventListener("click", function () {
    saved = {}; try { localStorage.removeItem(KEY); } catch (e) {}
    boxes.forEach(function (b) { b.checked = false; }); update();
    status && status.focus();
  });
  update();
})();
"""


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def slug(loc_id: str) -> str:
    return loc_id.replace("_", "-")


def no_controls(text: str) -> str:
    """Drop sentences about game keys ("Press X to ..."): they don't apply here."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return " ".join(p for p in parts if not re.match(r"Press [A-Z]\b", p)).strip()


class Guide:
    def __init__(self, out: Path):
        self.out = out
        self.locations = load_locations(config.LOCATIONS_FILE)
        self.names = {k: v.name for k, v in self.locations.items()}
        self.map = load_map(config.START_MAP, config.MAPS_DIR)
        self.missions = load_missions(config.CONTENT_DIR / "missions")
        self.book = MissionBook(self.missions, Progress(), self.names)
        self.intro = load_intro(config.INTRO_FILE)
        meta_path = config.CONTENT_DIR / "guide.json"
        self.meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
        self.cards = {}
        for b in load_buildings(config.BUILDINGS_DIR):
            if b.card_png and b.location not in self.cards:
                self.cards[b.location] = (b.card_png, b.notes.get("_card_alt", ""))
        self.built = date.today().isoformat()
        self.pages: list[Path] = []
        self.routes_checked: list = []     # (route, from, to) for the tests

    # --- layout ---------------------------------------------------------------------
    def page(self, rel: str, title: str, body: str, script: str = "") -> None:
        depth = rel.count("/")
        up = "../" * depth
        nav = "".join(
            f'<li><a href="{up}{href}"{" aria-current=\"page\"" if href == rel else ""}>{esc(label)}</a></li>'
            for href, label in NAV)
        doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} – {SITE}</title>
<link rel="stylesheet" href="{up}guide.css">
</head>
<body>
<a class="skip" href="#main">Skip to main content</a>
<header>
  <div class="wrap">
    <a class="site" href="{up}index.html">{SITE}</a>
    <nav aria-label="Guide"><ul>{nav}</ul></nav>
  </div>
</header>
<main id="main" tabindex="-1">
  <div class="wrap">
{body}
  </div>
</main>
<footer>
  <div class="wrap">
    <p>The accessible version of <a href="{up}{GAME_URL}">Fordham Campus Quest</a>, built from the same content as the game
    on {self.built}. <a href="{up}accessibility.html">Accessibility statement</a>.</p>
  </div>
</footer>
{f"<script>{script}</script>" if script else ""}
</body>
</html>
"""
        path = self.out / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(doc)
        self.pages.append(path)

    # --- helpers ----------------------------------------------------------------------
    def area_of(self, loc_id: str) -> str:
        for o in place_targets(self.map, loc_id):
            a = self.map.area_at(o.x, o.y)
            if a:
                return a.name
        return ""

    def link(self, loc_id: str, up: str = "") -> str:
        if loc_id in self.locations:
            return f'<a href="{up}places/{slug(loc_id)}.html">{esc(self.names[loc_id])}</a>'
        return esc(loc_id)

    def start_cell(self, loc_id: str):
        """A walkable cell beside a place, to start directions from."""
        for o in place_targets(self.map, loc_id):
            for dx, dy in ((0, 1), (0, -1), (-1, 0), (1, 0)):
                if not self.map.is_blocked(o.x + dx, o.y + dy):
                    return (o.x + dx, o.y + dy)
        return None

    def directions(self, start, start_name: str, to: str, from_loc: str | None = None) -> str:
        r = route_to(self.map, start, to, self.names, start_name)
        if r is None:
            return f"<p>Directions to {esc(self.names.get(to, to))} aren't available yet.</p>"
        self.routes_checked.append((r, start_name, to))
        steps = sentences(r)
        items = "".join(f"<li>{esc(s)}</li>" for s in steps)
        return (f"<p>About {r.steps} steps (one step is one square in the game).</p>"
                f"<ol>{items}</ol>")

    # --- pages ------------------------------------------------------------------------
    def build(self) -> None:
        if self.out.exists():
            shutil.rmtree(self.out)
        (self.out / "img").mkdir(parents=True)
        (self.out / "guide.css").write_text(CSS.strip() + "\n")
        self.home()
        self.places()
        self.getting_around()
        self.missions_page()
        self.passport()
        self.about()
        self.statement()

    def home(self) -> None:
        by_area: dict[str, list[str]] = {}
        for loc_id, loc in self.locations.items():
            if loc.kind == "transit" or not place_targets(self.map, loc_id):
                continue
            by_area.setdefault(self.area_of(loc_id) or "Elsewhere on campus", []).append(loc_id)
        areas = ""
        for a in self.map.areas:
            locs = by_area.get(a.name)
            if not locs or a.name.endswith("!"):
                continue
            items = "".join(f"<li>{self.link(i)}</li>" for i in sorted(locs, key=lambda i: self.names[i]))
            areas += f"<h3>{esc(a.name)}</h3><ul>{items}</ul>"
        body = f"""<h1>{SITE}</h1>
<p>Fordham Campus Quest is a game about finding your way around Fordham's Rose Hill campus in the Bronx in your first week.
This guide has everything the game teaches, as plain, accessible web pages: every place and what's inside, how to walk
between them, the First Week checklist and the optional missions.</p>
<p class="note">You can use this guide instead of the game, or alongside it.
<a href="{GAME_URL}">Play Fordham Campus Quest</a> (a pixel-art game in your browser).</p>
<h2>Start here</h2>
<ul>
  <li><a href="missions.html">The First Week checklist</a>: the places every new student needs.</li>
  <li><a href="getting-around.html">Getting around</a>: the gates, the Ram Van shuttle and walking directions.</li>
  <li><a href="places/index.html">All places</a>, by type.</li>
</ul>
<h2>How the campus is laid out</h2>
<p>Most students arrive by Metro-North at Fordham station and walk in through the Webster Avenue gate, on the south-west
corner. Cars and the Ram Van come in through the Main Entrance on Xavier Way, on the east side. The big lawn in the middle
is Edwards Parade.</p>
{areas}"""
        self.page("index.html", "Home", body)

    def places(self) -> None:
        groups = ""
        for kind in KIND_ORDER:
            locs = [i for i, l in self.locations.items() if l.kind == kind]
            if not locs:
                continue
            items = "".join(f"<li>{self.link(i, '../')}</li>" for i in sorted(locs, key=lambda i: self.names[i]))
            groups += f"<h2>{esc(KIND_NAMES[kind][1])}</h2><ul>{items}</ul>"
        self.page("places/index.html", "Places", f"<h1>Places</h1>\n<p>Every building and landmark in the game, "
                  f"with what's inside and how to get there.</p>{groups}")
        for loc_id, loc in self.locations.items():
            self.place(loc_id, loc)

    def place(self, loc_id: str, loc) -> None:
        parts = [f"<h1>{esc(loc.name)}</h1>",
                 f'<p><span class="kind">{esc(KIND_NAMES[loc.kind][0])}</span>'
                 + (f" in {esc(self.area_of(loc_id))}" if self.area_of(loc_id) else "") + "</p>"]
        if loc_id in self.cards:
            src, alt = self.cards[loc_id]
            shutil.copy2(src, self.out / "img" / f"{slug(loc_id)}.png")
            alt = alt or f"Drawing of {loc.name} as it appears in the game."
            parts.append(f'<figure><img src="../img/{slug(loc_id)}.png" width="228" height="88" alt="{esc(alt)}">'
                         f"<figcaption>{esc(loc.name)} in Fordham Campus Quest.</figcaption></figure>")
        parts.append(f"<p>{esc(loc.blurb)}</p>")
        if loc.real_entrance:
            parts.append(f"<h2>In real life</h2><p>{esc(loc.real_entrance)}</p>")
        if loc.inside:
            parts.append("<h2>What's here</h2><ul>" + "".join(f"<li>{esc(i)}</li>" for i in loc.inside) + "</ul>")
        if loc.url:
            parts.append(f'<p><a href="{esc(loc.url)}">More about {esc(loc.name)} on fordham.edu</a></p>')
        missions = [m for m in self.missions if any(
            s.get("location") == loc_id or any(t.get("location") == loc_id for t in s.get("targets", []))
            for s in m.steps)]
        if missions:
            parts.append("<h2>In the missions</h2><ul>" + "".join(
                f'<li><a href="../missions.html#{m.id}">{esc(m.title)}</a></li>' for m in missions) + "</ul>")
        if place_targets(self.map, loc_id) and loc.kind != "transit":
            parts.append("<h2>How to get here</h2>")
            for key, (cell, name) in START_POINTS.items():
                parts.append(f"<h3>From {esc(name)}</h3>" + self.directions(cell, name, loc_id))
        elif loc.kind == "transit":
            stops = place_targets(self.map, loc_id)
            areas = sorted({self.map.area_at(o.x, o.y).name for o in stops if self.map.area_at(o.x, o.y)})
            if areas:
                parts.append("<h2>Where you'll find it</h2><ul>" + "".join(f"<li>{esc(a)}</li>" for a in areas)
                             + "</ul>")
        self.page(f"places/{slug(loc_id)}.html", loc.name, "\n".join(parts))

    def getting_around(self) -> None:
        transit = [i for i, l in self.locations.items() if l.kind == "transit"]
        tlist = "".join(f"<li>{self.link(i)}: {esc(self.locations[i].blurb)}</li>" for i in transit)
        routes = ""
        for a, b in MAIN_ROUTES:
            if a not in self.locations or b not in self.locations:
                continue
            start = self.start_cell(a)
            if start is None:
                continue
            title = f"{self.names[a]} to {self.names[b]}"
            routes += f"<h3>{esc(title)}</h3>" + self.directions(start, self.names[a], b)
        body = f"""<h1>Getting around</h1>
<h2>Gates and transport</h2>
<ul>{tlist}</ul>
<h2>Main walking routes</h2>
<p>Directions follow the campus walkways and roads. Headings are compass directions: north is towards the athletics
fields and McShane, south is towards East Fordham Road. Every place's page also has directions from both entrances.</p>
{routes}"""
        self.page("getting-around.html", "Getting around", body)

    def mission_steps(self, m) -> str:
        items = []
        for i, s in enumerate(m.steps):
            text = re.sub(r"\s*\(\d+/\d+\)$", "", self.book.step_text(m, i))   # no game progress counters
            if s.get("do") == "ride":
                text = text.replace("Get to", "Take it to")
            if s.get("location") in self.locations:
                text += f' (<a href="places/{slug(s["location"])}.html">about {esc(self.names[s["location"]])}</a>)'
                label = text
            else:
                label = esc(text)
            extra = ""
            if s.get("targets"):
                extra += "<ul>" + "".join(f"<li>{self.link(t['location'])}</li>" for t in s["targets"]
                                          if t.get("location") in self.locations) + "</ul>"
            if s.get("hint") and no_controls(s["hint"]):
                extra += f'<p class="hint">Hint: {esc(no_controls(s["hint"]))}</p>'
            if s.get("do") == "answer":
                opts = s.get("options", [])
                ans = opts[s["correct"]] if opts else ""
                extra += (f'<details class="hint"><summary>The question: {esc(s["question"])}</summary>'
                          f"<p>Choices: {esc(', '.join(opts))}. Answer: {esc(ans)}. "
                          f"{esc(' '.join(s.get('say', [])))}</p></details>")
            elif s.get("say"):
                learn = no_controls(" ".join(x.replace("Checklist: ", "") for x in s["say"]))
                if learn and not learn.lower().startswith("you "):      # skip "you did it" lines
                    extra += f'<p class="hint">You\'ll learn: {esc(learn)}</p>'
            items.append(f'<li><label><input type="checkbox" data-step="{m.id}:{i}"> '
                         f"<span>{label}</span></label>{extra}</li>")
        return f'<ol class="check">{"".join(items)}</ol>'

    def missions_page(self) -> None:
        secs = ""
        for m in self.missions:
            giver = ""
            if m.giver:
                area = self.map.area_at(*m.giver["at"])
                where = f" in {esc(area.name)}" if area else ""
                giver = (f"<p>In the game, this starts when you talk to the {esc(m.giver['npc'])}{where}. "
                         f"Here, just work through the steps.</p>")
            if any(s.get("seconds") for s in m.steps):
                giver += "<p>The game times one step of this mission. The guide has no time limits.</p>"
            reward = self.reward_text(m)
            secs += (f'<section aria-labelledby="{m.id}"><h2 id="{m.id}">{esc(m.title)}</h2>'
                     f"<p>{esc(m.summary)}</p>{giver}{self.mission_steps(m)}"
                     + (f"<p>Reward: {esc(reward)}.</p>" if reward else "") + "</section>")
        body = f"""<h1>Missions</h1>
<p>The First Week checklist is the game's main mission; the others are optional. Tick each step as you go: your ticks are
saved in this browser only.</p>
<p id="progress" tabindex="-1" role="status"></p>
{secs}
<p><button type="button" id="clear">Clear all my ticks</button></p>"""
        self.page("missions.html", "Missions", body, CHECKLIST_JS)

    def reward_text(self, m) -> str:
        r = m.reward
        bits = []
        if r.get("stamp"):
            bits.append(f"the {r.get('stamp_name', m.title)} stamp in your Ram Passport")
        if r.get("badge"):
            bits.append(f"the {r['badge'].title()} badge")
        if r.get("unlock"):
            bits.append(r.get("unlock_name", r["unlock"]))
        return ", ".join(bits)

    def passport(self) -> None:
        stamps = "".join(f'<li><a href="missions.html#{m.id}">{esc(m.title)}</a>: '
                         f"{esc(self.reward_text(m) or 'no reward')}</li>" for m in self.missions)
        badge_steps: dict[str, list[str]] = {}
        for m in self.missions:
            if m.reward.get("badge"):
                badge_steps.setdefault(m.reward["badge"], []).append(f"finish {m.title}")
            for i, s in enumerate(m.steps):
                if s.get("badge"):
                    badge_steps.setdefault(s["badge"], []).append(self.book.step_text(m, i).rstrip(".").lower())
        badges = "".join(f"<dt>{esc(b.title())}</dt><dd>"
                         + (esc("; ".join(badge_steps[b])).capitalize() if b in badge_steps else "Coming soon")
                         + "</dd>" for b in BADGES)
        body = f"""<h1>Ram Passport</h1>
<p>In the game, finishing a mission earns a stamp in your Ram Passport, and some steps earn badges.</p>
<h2>Stamps</h2><ul>{stamps}</ul>
<h2>Badges</h2><dl>{badges}</dl>"""
        self.page("passport.html", "Ram Passport", body)

    def about(self) -> None:
        story = "".join(f"<li>{esc(b.caption)}</li>" for b in self.intro.beats)
        rows = "".join(f"<dt>{esc(k)}</dt><dd>{esc(a)}</dd>" for k, a in self.intro.controls_rows)
        body = f"""<h1>About the game</h1>
<p><a href="{GAME_URL}">Fordham Campus Quest</a> is a pixel-art game: you walk around Rose Hill, read signs, meet people
and take on missions. It runs in the browser and is played with the keyboard (or an on-screen gamepad on phones).</p>
<h2>The story so far</h2>
<p>The game opens with your arrival:</p>
<ol>{story}</ol>
<h2>How to play</h2>
<dl>{rows}</dl>
<p>{esc(self.intro.tip)}</p>
<p>In the browser, <strong>Esc</strong> moves you out of the game to the link to this guide.</p>"""
        self.page("about.html", "About the game", body)

    def statement(self) -> None:
        name, email = self.meta.get("contact_name", ""), self.meta.get("contact_email", "")
        contact = (f'<a href="mailto:{esc(email)}">{esc(name or email)}</a>' if email
                   else "the team that runs Fordham Campus Quest (contact details to be added)")
        body = f"""<h1>Accessibility statement</h1>
<p>This guide aims to meet the <a href="https://www.w3.org/TR/WCAG22/">Web Content Accessibility Guidelines (WCAG) 2.2</a>
at level AA.</p>
<h2>The game and this guide</h2>
<p>Fordham Campus Quest is a pixel-art game drawn on a canvas, which screen readers and text resizing can't reach. This
guide is its accessible alternative: it has the same places, directions, missions and rewards, and is rebuilt from the
game's content every time the game changes. The game page links here before the game starts, and Esc moves keyboard
focus out of the game to that link.</p>
<h2>How we check</h2>
<ul>
  <li>Every build is tested automatically with axe-core against WCAG 2.2 AA rules.</li>
  <li>Before each release, the guide is checked by hand with a keyboard only, with VoiceOver, and at 200% and 400% zoom.</li>
</ul>
<h2>Problems and feedback</h2>
<p>If anything in this guide or the game doesn't work for you, contact {contact}.</p>
<p>This guide was last built on {self.built}.</p>"""
        self.page("accessibility.html", "Accessibility statement", body)


def build(out: Path) -> Guide:
    g = Guide(out)
    g.build()
    return g


def main() -> None:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "build" / "web" / "guide"
    g = build(out)
    print(f"wrote {len(g.pages)} pages to {out}")


if __name__ == "__main__":
    main()
