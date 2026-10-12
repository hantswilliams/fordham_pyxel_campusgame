"""Build the web version of the game for quick testing (decisions/0034).

    uv run python tools/build_web.py        # writes build/web/index.html

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
    html = html.replace("<!doctype html>", "<!doctype html>\n<title>Fordham Campus Quest</title>\n" + LOADING, 1)
    (OUT / "index.html").write_text(html)
    (OUT / f"{APP}.html").unlink()
    shutil.rmtree(stage)
    size = (OUT / "index.html").stat().st_size / 1e6
    print(f"wrote {OUT / 'index.html'} ({size:.1f} MB, Pyxel {PYXEL_VERSION})")


if __name__ == "__main__":
    main()
