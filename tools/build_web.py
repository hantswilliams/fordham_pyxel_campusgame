"""Build the web version of the game for quick testing (decisions/0034).

    uv run python tools/build_web.py        # writes build/web/index.html and build/web/guide/

Packs only what the game needs (main.py, game/, assets/, content/) into a
Pyxel app, then turns it into one HTML file that runs in the browser with
Pyodide. The page loads Pyxel's web runtime from a CDN, pinned to the
version we develop with, so a new Pyxel release can't change the test build.

Open build/web/index.html in a browser, or serve the folder:

    cd build/web && python -m http.server 8000     # then http://localhost:8000
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "build" / "web"
APP = "fordham_campus_quest"
PYXEL_VERSION = "2.9.9"           # the Pyxel web runtime the page loads (decisions/0034)
INCLUDE = ["main.py", "game", "assets", "content"]
SKIP = shutil.ignore_patterns("__pycache__", "*.pyc", "_style", ".DS_Store")


# Pyxel's loader shows its own logo while Pyodide downloads, with no option
# to turn it off. Hide it and show a plain loading line instead; it goes
# away when Pyxel's "click to start" prompt (or an error) appears.
LOADING = """<style>
  img#pyxel-logo { display: none !important; }
  html { background: #202124; }
  #fcq-loading { position: fixed; inset: 0; display: flex; align-items: center;
    justify-content: center; pointer-events: none; z-index: 5;
    font: 16px/1.4 ui-monospace, Menlo, monospace; color: #eeeeee; letter-spacing: 1px; }
  #fcq-loading b { color: #ff9798; font-weight: normal; }
</style>
<div id="fcq-loading"><span><b>FORDHAM CAMPUS QUEST</b> &middot; Loading&hellip;</span></div>
<script>
  new MutationObserver((_, obs) => {
    if (document.querySelector("img#pyxel-prompt, #pyxel-error-overlay")) {
      document.getElementById("fcq-loading")?.remove();
      obs.disconnect();
    }
  }).observe(document.documentElement, { childList: true, subtree: true });
</script>"""

# Accessibility (decisions/0037): the game page meets WCAG's non-interference
# rules and points to the accessible Rose Hill Campus Guide before the game.
# - a bar at the top with the guide link: the first thing a keyboard or
#   screen-reader user reaches
# - no keyboard trap: the game only gets the keyboard after you click it (or
#   press "Play with the keyboard"); Esc hands the keyboard back to the page
#   and moves focus to the guide link
# - Pyxel's "click to start" picture gets a text alternative
#
# The bar gets its own strip at the top: Pyxel's screen (which fills the
# window) starts below it, so the bar never covers the top of the game. The
# bar's height is measured, since it wraps onto more lines on a narrow window.
A11Y = """<style>
  :root { --fcq-bar-h: 46px; }
  html div#pyxel-screen { top: var(--fcq-bar-h); height: calc(100% - var(--fcq-bar-h)); }
  #fcq-a11y { position: fixed; top: 0; left: 0; right: 0; z-index: 20; display: flex; flex-wrap: wrap;
    gap: 4px 16px; align-items: center; padding: 6px 12px; background: #202124; color: #ffffff;
    font: 15px/1.4 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; }
  #fcq-a11y a { color: #ffffff; font-weight: 600; text-underline-offset: 3px; }
  #fcq-a11y button { font: inherit; color: #ffffff; background: #860038; border: 2px solid #ffffff;
    padding: 4px 10px; min-height: 32px; cursor: pointer; }
  #fcq-a11y :focus-visible { outline: 3px solid #ffd447; outline-offset: 2px; }
</style>
<div id="fcq-a11y" role="region" aria-label="Accessibility">
  <a id="fcq-guide" href="guide/index.html">Accessible version: Rose Hill Campus Guide</a>
  <span id="fcq-keys">Esc leaves the game.</span>
  <button type="button" id="fcq-play">Play with the keyboard</button>
</div>
<script>
  (function () {
    // keep the game screen below the bar, however many lines the bar takes
    var bar = document.getElementById("fcq-a11y");
    function fitBar() {
      var h = Math.ceil(bar.getBoundingClientRect().height) + "px";
      if (document.documentElement.style.getPropertyValue("--fcq-bar-h") === h) return false;
      document.documentElement.style.setProperty("--fcq-bar-h", h);
      return true;
    }
    fitBar();
    // runs before Pyxel's own resize handling, so it sees the new size
    window.addEventListener("resize", fitBar, true);
    if (window.ResizeObserver) {
      new ResizeObserver(function () {
        if (fitBar()) window.dispatchEvent(new Event("resize"));   // let Pyxel resize too
      }).observe(bar);
    }
    var gameHasKeys = false;
    function stop(e) { if (!gameHasKeys) e.stopImmediatePropagation(); }
    window.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && gameHasKeys) {
        gameHasKeys = false;
        e.preventDefault(); e.stopImmediatePropagation();
        document.getElementById("fcq-guide").focus();
        return;
      }
      stop(e);
    }, true);
    window.addEventListener("keyup", stop, true);
    window.addEventListener("keypress", stop, true);
    function play() { gameHasKeys = true; if (document.activeElement) document.activeElement.blur(); }
    document.addEventListener("pointerdown", function (e) {
      if (!e.target.closest || !e.target.closest("#fcq-a11y")) play();
    }, true);
    document.getElementById("fcq-play").addEventListener("click", function () {
      play();
      var prompt = document.querySelector("img#pyxel-prompt");
      if (prompt) prompt.click();
    });
    new MutationObserver(function () {
      var prompt = document.querySelector("img#pyxel-prompt");
      if (prompt && !prompt.alt) prompt.alt = "Click or tap here to start the game";
      document.querySelectorAll("canvas").forEach(function (c) {
        if (!c.getAttribute("aria-label")) {
          c.setAttribute("role", "img");
          c.setAttribute("aria-label", "Fordham Campus Quest game screen. The Rose Hill Campus Guide link above has the same content in accessible form.");
        }
      });
    }).observe(document.documentElement, { childList: true, subtree: true });
  })();
</script>"""


def run(*args: str) -> None:
    subprocess.run([sys.executable, "-m", "pyxel", *args], cwd=OUT, check=True,
                   stdout=subprocess.DEVNULL)


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    stage = OUT / APP
    stage.mkdir(parents=True)
    for name in INCLUDE:                      # research/, tests/, tools/ and build/ stay out
        src = ROOT / name
        if src.is_dir():
            shutil.copytree(src, stage / name, ignore=SKIP)
        else:
            shutil.copy2(src, stage / name)
    run("package", APP, f"{APP}/main.py")
    run("app2html", f"{APP}.pyxapp")
    html = (OUT / f"{APP}.html").read_text()
    html, n = re.subn(r"gh/kitao/pyxel@[^/]+/wasm/pyxel\.js",
                      f"gh/kitao/pyxel@{PYXEL_VERSION}/wasm/pyxel.js", html)
    if n != 1:
        sys.exit("build_web: couldn't find Pyxel's script tag in the HTML")
    html = html.replace("<!doctype html>", '<!doctype html>\n<html lang="en">\n<meta charset="utf-8">\n'
                        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
                        "<title>Fordham Campus Quest</title>\n" + A11Y + LOADING, 1)
    (OUT / "index.html").write_text(html)
    (OUT / f"{APP}.html").unlink()
    shutil.rmtree(stage)
    size = (OUT / "index.html").stat().st_size / 1e6
    print(f"wrote {OUT / 'index.html'} ({size:.1f} MB, Pyxel {PYXEL_VERSION})")
    # the accessible Campus Guide, from the same content (decisions/0037)
    sys.path.insert(0, str(ROOT / "tools"))
    import build_guide
    g = build_guide.build(OUT / "guide")
    print(f"wrote {OUT / 'guide'} ({len(g.pages)} pages)")


if __name__ == "__main__":
    main()
