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
# - the guide opens in a new tab, so the game keeps its place; the link
#   says so, as WCAG advises (decisions/0039)
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
  #fcq-a11y .fcq-note { font-weight: 400; }
  #fcq-a11y button { font: inherit; color: #ffffff; background: #860038; border: 2px solid #ffffff;
    padding: 4px 10px; min-height: 32px; cursor: pointer; }
  #fcq-a11y :focus-visible { outline: 3px solid #ffd447; outline-offset: 2px; }
  #fcq-a11y.fcq-paused #fcq-keys { color: #ffd447; font-weight: 600; }
  #fcq-resume { position: fixed; left: 0; right: 0; bottom: 0; top: var(--fcq-bar-h); z-index: 15;
    display: flex; align-items: center; justify-content: center; border: 0; padding: 16px;
    background: rgba(32, 33, 36, 0.6); cursor: pointer; font: 18px/1.4 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; }
  #fcq-resume[hidden] { display: none; }
  #fcq-resume span { display: flex; flex-direction: column; gap: 4px; padding: 16px 24px; max-width: 28em;
    color: #ffffff; background: #860038; border: 3px solid #ffffff; text-align: center; }
  #fcq-resume strong { font-size: 24px; }
  #fcq-resume em { font-style: normal; }
  #fcq-resume .fcq-enter, #fcq-resume:focus .fcq-click { display: none; }
  #fcq-resume:focus .fcq-enter { display: inline; }
  #fcq-resume:focus-visible span { outline: 4px solid #ffd447; outline-offset: 3px; }
</style>
<div id="fcq-a11y" role="region" aria-label="Accessibility">
  <a id="fcq-guide" href="guide/index.html" target="_blank" rel="noopener">Accessible version: Rose Hill Campus Guide <span class="fcq-note">(opens in a new tab)</span></a>
  <span id="fcq-keys" aria-live="polite">Esc leaves the game.</span>
  <button type="button" id="fcq-play">Play with the keyboard</button>
</div>
<button type="button" id="fcq-resume" hidden><span><strong>Game paused</strong>
  <em class="fcq-click">Click here to keep playing</em><em class="fcq-enter">Press Enter or click to keep playing</em></span></button>
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
    // Who has the keyboard: the game, or the page (decisions/0039). Once the
    // game has started, whenever the page has it the game shows "Game
    // paused" and the bar says how to get back, so it's never a mystery why
    // the keys do nothing (after Esc, or after opening the guide's tab).
    var gameHasKeys = false, started = false;
    var keys = document.getElementById("fcq-keys");
    var resume = document.getElementById("fcq-resume");
    function show() {
      var paused = started && !gameHasKeys;
      resume.hidden = !paused;
      bar.classList.toggle("fcq-paused", paused);
      keys.textContent = !started ? "Esc leaves the game." :
        gameHasKeys ? "Playing. Esc leaves the game." : "Game paused: click the game to keep playing.";
    }
    function play() {
      gameHasKeys = started = true;
      if (document.activeElement) document.activeElement.blur();
      show();
    }
    function pause() { gameHasKeys = false; show(); }
    function stop(e) { if (!gameHasKeys) e.stopImmediatePropagation(); }
    window.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && gameHasKeys) {
        pause();
        e.preventDefault(); e.stopImmediatePropagation();
        document.getElementById("fcq-guide").focus();
        return;
      }
      stop(e);
    }, true);
    window.addEventListener("keyup", stop, true);
    window.addEventListener("keypress", stop, true);
    document.addEventListener("pointerdown", function (e) {
      var inBar = e.target.closest && e.target.closest("#fcq-a11y");
      if (!inBar) play();
      else if (!e.target.closest("#fcq-play")) pause();   // e.g. opening the guide
    }, true);
    resume.addEventListener("click", play);
    // coming back to this tab with the game paused: put focus on "Game
    // paused", so Enter carries on playing instead of reopening the guide
    function backToTab() {
      if (document.visibilityState !== "visible" || !started || gameHasKeys) return;
      var el = document.activeElement;
      if (!el || el === document.body || el.id === "fcq-guide") resume.focus();
    }
    document.addEventListener("visibilitychange", backToTab);
    window.addEventListener("focus", backToTab);
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


# Crisp text (decisions/0038): the game's screen is DISPLAY_SCALE times its
# layout, with the art already doubled. Pyxel would stretch it to the window
# by any amount with hard pixel edges, which makes some strokes thicker than
# others. Instead the canvas stays exactly the game's size, so Pyxel draws it
# 1:1 (2:1 on a Retina screen), and the browser scales it smoothly to fit
# below the bar. As the art is already doubled, it stays sharp.
CRISP = """<style>
  html:not(.fcq-fill) div#pyxel-screen canvas#canvas { width: %(w)dpx !important; height: %(h)dpx !important;
    transform-origin: 0 0; image-rendering: auto; }
</style>
<script>
  (function () {
    var W = %(w)d, H = %(h)d;
    function fitGame() {
      var screen = document.querySelector("div#pyxel-screen");
      var canvas = document.querySelector("canvas#canvas");
      if (!screen || !canvas) return;
      // if Pyxel ever sizes its drawing to the window rather than to the
      // canvas, the picture would come out squashed: go back to Pyxel's own
      // fill-the-window layout instead
      if (canvas.width !== 300 && Math.abs(canvas.width / canvas.height - W / H) > 0.02) {
        document.documentElement.classList.add("fcq-fill");
        canvas.style.transform = "";
        return;
      }
      var r = screen.getBoundingClientRect();
      // on touch screens Pyxel keeps the bottom fifth for its gamepad
      var h = document.querySelector("img#pyxel-gamepad-cross") ? r.height * 0.8 : r.height;
      var k = Math.max(0.1, Math.min(r.width / W, h / H));
      canvas.style.transform = "translate(" + (r.width - W * k) / 2 + "px," + (h - H * k) / 2 + "px) scale(" + k + ")";
    }
    window.addEventListener("resize", fitGame);
    new MutationObserver(fitGame).observe(document.documentElement, { childList: true, subtree: true,
      attributes: true, attributeFilter: ["width", "height"] });
    if (window.ResizeObserver) new ResizeObserver(fitGame).observe(document.documentElement);
  })();
</script>"""

def crisp_css() -> str:
    sys.path.insert(0, str(ROOT))
    from game import config
    if config.DISPLAY_SCALE == 1:
        return ""
    return CRISP % {"w": config.SCREEN_W * config.DISPLAY_SCALE, "h": config.SCREEN_H * config.DISPLAY_SCALE}

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
                        "<title>Fordham Campus Quest</title>\n" + A11Y + LOADING + crisp_css(), 1)
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
