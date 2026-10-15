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
  #fcq-keys:empty { display: none; }
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
  #fcq-a11y .fcq-short, #fcq-a11y .fcq-arrow, #fcq-resume .fcq-tap, #fcq-pad-help { display: none; }
  #fcq-keys::before { content: "\u25cf  "; color: #8fd18f; }
  #fcq-a11y.fcq-paused #fcq-keys::before { color: #ffd447; }

  /* Phones and tablets (decisions/0043): a one-line bar, labels for Pyxel's
     on-screen gamepad, and no zooming, pull-to-refresh or long-press menus
     on the game. */
  #fcq-a11y { padding-top: max(6px, env(safe-area-inset-top));
    padding-left: max(12px, env(safe-area-inset-left)); padding-right: max(12px, env(safe-area-inset-right)); }
  html.fcq-touch #fcq-a11y { flex-wrap: nowrap; white-space: nowrap; gap: 12px; font-size: 14px; }
  html.fcq-touch #fcq-a11y .fcq-long, html.fcq-touch #fcq-help, html.fcq-touch #fcq-play { display: none; }
  html.fcq-touch #fcq-a11y .fcq-short, html.fcq-touch #fcq-a11y .fcq-arrow { display: inline; }
  html.fcq-touch #fcq-a11y .fcq-note { position: absolute; width: 1px; height: 1px; overflow: hidden;
    clip: rect(0 0 0 0); white-space: nowrap; }
  html.fcq-touch #fcq-keys { margin-left: auto; }
  html.fcq-touch #fcq-resume .fcq-click, html.fcq-touch #fcq-resume:focus .fcq-enter { display: none; }
  html.fcq-touch #fcq-resume .fcq-tap { display: inline; }
  html.fcq-touch, html.fcq-touch body { overscroll-behavior: none; touch-action: manipulation; }
  html.fcq-touch div#pyxel-screen { touch-action: none; -webkit-user-select: none; user-select: none;
    -webkit-touch-callout: none; }
  html.fcq-touch img#pyxel-gamepad-cross { left: max(1%, env(safe-area-inset-left)) !important; }
  html.fcq-touch img#pyxel-gamepad-button { right: max(1%, env(safe-area-inset-right)) !important; }
  /* sideways, the game uses the full height and X / Y do what SELECT / START
     do, so the small menu button (which would sit over the game) is hidden */
  html.fcq-touch.fcq-landscape img#pyxel-gamepad-menu { display: none; }
  #fcq-pad-help div { position: fixed; z-index: 16; pointer-events: none; color: #ffffff;
    font: 600 12px/1.2 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; text-align: center; }
  #fcq-walk { padding: 3px 8px; background: rgba(32, 33, 36, 0.85); border-radius: 10px; }
  #fcq-buttons { display: grid; grid-template-columns: repeat(3, 1fr); gap: 2px; }
  #fcq-buttons span { padding: 2px 4px; background: rgba(32, 33, 36, 0.85); border-radius: 8px; }
  #fcq-buttons b { color: #ffd447; }
</style>
<div id="fcq-a11y" role="region" aria-label="Accessibility">
  <a id="fcq-guide" href="guide/index.html" target="_blank" rel="noopener"><span class="fcq-long">Accessible version: Rose Hill Campus Guide</span><span class="fcq-short">Accessible guide</span> <span class="fcq-note">(opens in a new tab)</span><span class="fcq-arrow" aria-hidden="true">&#8599;</span></a>
  <span id="fcq-help">Tab: missions &middot; M: map &middot; Esc: leave the game</span>
  <span id="fcq-keys" aria-live="polite"></span>
  <button type="button" id="fcq-play">Play with the keyboard</button>
</div>
<button type="button" id="fcq-resume" hidden><span><strong>Game paused</strong>
  <em class="fcq-click">Click here to keep playing</em><em class="fcq-enter">Press Enter or click to keep playing</em><em class="fcq-tap">Tap here to keep playing</em></span></button>
<div id="fcq-pad-help" aria-hidden="true">
  <div id="fcq-walk">D-pad: Walk</div>
  <div id="fcq-buttons"><span></span><span><b>Y</b> Map</span><span></span><span><b>X</b> Missions</span><span></span><span><b>B</b> Back&middot;Bike</span><span></span><span><b>A</b> Talk / OK</span><span></span></div>
</div>
<script>
  (function () {
    // phones and tablets (decisions/0043): the same test Pyxel uses to show
    // its on-screen gamepad
    var touch = window.matchMedia && window.matchMedia("(pointer: coarse)").matches;
    var root = document.documentElement;
    function orient() { root.classList.toggle("fcq-landscape", window.innerWidth > window.innerHeight); }
    if (touch) { root.classList.add("fcq-touch"); orient(); window.addEventListener("resize", orient, true); }
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
      keys.textContent = !started ? "" : gameHasKeys ? "Playing" :
        touch ? "Paused: tap the game" : "Game paused: click the game to keep playing.";
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
#
# Pyxel never draws its screen smaller than 1:1: in a canvas smaller than
# 768 x 576 it shows only the middle of the game, zoomed in (what phones
# showed, decisions/0043). SDL takes the canvas's size from
# getBoundingClientRect(), which counts the scale() that shrinks it to fit,
# so the game canvas reports its own size (768 x 576) instead. The game
# doesn't use the mouse or touches on the canvas (the on-screen gamepad has
# its own pictures), so nothing else depends on that size.
CRISP = """<style>
  div#pyxel-screen canvas#canvas { width: %(w)dpx !important; height: %(h)dpx !important;
    transform-origin: 0 0; image-rendering: auto; }
</style>
<script>
  (function () {
    var W = %(w)d, H = %(h)d;
    var rectOf = HTMLCanvasElement.prototype.getBoundingClientRect;
    function unscaled(canvas) {
      if (canvas.fcqUnscaled) return;
      canvas.fcqUnscaled = true;
      canvas.getBoundingClientRect = function () {
        var r = rectOf.call(this);
        return new DOMRect(r.x, r.y, this.offsetWidth, this.offsetHeight);
      };
      window.dispatchEvent(new Event("resize"));     // let SDL measure it again
    }
    function fitGame() {
      var screen = document.querySelector("div#pyxel-screen");
      var canvas = document.querySelector("canvas#canvas");
      if (!screen || !canvas) return;
      unscaled(canvas);
      var r = screen.getBoundingClientRect();
      // with the on-screen gamepad (decisions/0043): upright, the game sits at
      // the top and the controls go below; sideways, it uses the full height
      // and the controls sit either side
      var pad = !!document.querySelector("img#pyxel-gamepad-cross");
      var wide = r.width > r.height;
      var h = pad && !wide ? r.height * 0.8 : r.height;
      var k = Math.max(0.1, Math.min(r.width / W, h / H));
      var top = pad && !wide ? 0 : (h - H * k) / 2;
      canvas.style.transform = "translate(" + (r.width - W * k) / 2 + "px," + top + "px) scale(" + k + ")";
      if (pad) placePads(r, wide ? null : top + H * k);
      placePadHelp();
    }
    // Upright, Pyxel pins its gamepad to the bottom of the screen, which on a
    // tall phone leaves a wide gap under the game. Bring the d-pad and the
    // buttons up to just below the game (with room for their labels), never
    // lower than Pyxel puts them; the small menu button goes under them.
    // Sideways, Pyxel's own places are kept.
    var padsAt = "";
    function placePads(r, gameBottom) {
      var cross = document.querySelector("img#pyxel-gamepad-cross");
      var btns = document.querySelector("img#pyxel-gamepad-button");
      var menu = document.querySelector("img#pyxel-gamepad-menu");
      var imgs = [cross, btns, menu].filter(Boolean);
      var at = "pyxel";
      if (gameBottom === null) {
        imgs.forEach(function (e) { e.style.removeProperty("top"); e.style.removeProperty("bottom"); });
      } else {
        var n = Math.max(cross ? cross.offsetHeight : 0, btns ? btns.offsetHeight : 0);
        if (!n) return;                                  // pictures not sized yet
        var labels = document.getElementById("fcq-buttons");
        var lh = (labels && labels.offsetHeight) || 90;
        var y = Math.round(Math.min(gameBottom + lh + 16, r.height * 0.95 - n));
        [cross, btns].forEach(function (e) {
          if (!e) return;
          e.style.setProperty("top", y + "px", "important");
          e.style.setProperty("bottom", "auto", "important");
        });
        if (menu) {
          var my = Math.round(Math.min(y + n + 10, r.height * 0.99 - menu.offsetHeight));
          menu.style.setProperty("top", my + "px", "important");
          menu.style.setProperty("bottom", "auto", "important");
        }
        at = y + "/" + n;
      }
      // Pyxel remembers where its gamepad pictures are until the next resize
      if (at !== padsAt) { padsAt = at; window.dispatchEvent(new Event("resize")); }
    }
    // ?debug shows the sizes that matter for fitting the game, for phone testing
    function debugSizes() {
      if (!/debug/.test(location.search)) return;
      var c = document.querySelector("canvas#canvas"), d = document.getElementById("fcq-debug");
      if (!c) return;
      if (!d) { d = document.createElement("div"); d.id = "fcq-debug";
        d.style.cssText = "position:fixed;left:4px;bottom:4px;z-index:30;font:11px monospace;color:#fff;background:#000a;padding:2px 4px;pointer-events:none";
        document.body.appendChild(d); }
      var r = rectOf.call(c);
      d.textContent = "window " + innerWidth + "x" + innerHeight + " dpr " + devicePixelRatio +
        " | canvas css " + Math.round(r.width) + "x" + Math.round(r.height) + " backing " + c.width + "x" + c.height +
        " | " + document.documentElement.className;
    }
    setInterval(debugSizes, 1000);
    // labels for the on-screen gamepad, just above the d-pad and the buttons
    function placePadHelp() {
      var help = document.getElementById("fcq-pad-help");
      var cross = document.querySelector("img#pyxel-gamepad-cross");
      var btns = document.querySelector("img#pyxel-gamepad-button");
      if (!help || !cross || !btns) return;
      help.style.display = "block";
      var canvas = document.querySelector("canvas#canvas");
      var g = canvas ? rectOf.call(canvas) : null;
      [["fcq-walk", cross], ["fcq-buttons", btns]].forEach(function (pair) {
        var box = document.getElementById(pair[0]), r = pair[1].getBoundingClientRect();
        if (!r.width) return;
        // sideways the controls sit beside the game: keep the labels off it
        var lo = 4, hi = window.innerWidth - 4;
        if (g && g.width && r.left >= g.right - 1) lo = g.right + 4;
        if (g && g.width && r.right <= g.left + 1) hi = g.left - 4;
        box.style.width = pair[0] === "fcq-buttons" ? Math.min(hi - lo, Math.max(r.width, 180)) + "px" : "auto";
        var w = box.getBoundingClientRect().width;
        box.style.left = Math.max(lo, Math.min(hi - w, r.left + (r.width - w) / 2)) + "px";
        box.style.top = Math.max(0, r.top - box.getBoundingClientRect().height - 6) + "px";
      });
    }
    window.addEventListener("resize", function () { fitGame(); setTimeout(fitGame, 250); });
    // Pyxel sizes its gamepad pictures after they load: keep them, and their
    // labels, in place
    if (window.matchMedia && window.matchMedia("(pointer: coarse)").matches) setInterval(fitGame, 500);
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
                        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
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
