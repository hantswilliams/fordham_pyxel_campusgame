// A stand-in for Pyxel's web runtime, for tools/check_phone.cjs (decisions/0043).
// It makes the same page elements as pyxel.js / pyxel.css 2.9.9, without
// Pyodide or the game: the screen and canvas (sized as SDL sizes it, to the
// canvas's CSS size), and on touch screens the gamepad pictures with Pyxel's
// positions and sizes (20% of the screen's longer side).
(function () {
  const css = document.createElement("style");
  css.textContent = `
div#pyxel-screen{position:absolute;left:0;top:0;width:100%;height:100%;background-color:#202224}
canvas#canvas{position:absolute;left:0;top:0;width:100%;height:100%;image-rendering:pixelated}
img#pyxel-gamepad-cross{position:absolute;left:1%;bottom:5%;pointer-events:none}
img#pyxel-gamepad-button{position:absolute;right:1%;bottom:5%;pointer-events:none}
img#pyxel-gamepad-menu{position:absolute;left:50%;bottom:1%;transform:translateX(-50%);pointer-events:none}`;
  document.head.appendChild(css);
  const PIX = "data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==";
  window.launchPyxel = function () {
    const s = document.createElement("div"); s.id = "pyxel-screen"; document.body.appendChild(s);
    const c = document.createElement("canvas"); c.id = "canvas"; s.appendChild(c);
    // as SDL does: the backing size is the canvas's getBoundingClientRect()
    const size = () => { const r = c.getBoundingClientRect(); c.width = Math.round(r.width); c.height = Math.round(r.height); return r; };
    if (window.matchMedia("(pointer: coarse)").matches) {
      c.style.height = "80%";
      for (const id of ["cross", "button", "menu"]) {
        const img = document.createElement("img"); img.id = "pyxel-gamepad-" + id; img.src = PIX; s.appendChild(img);
      }
    }
    const fit = () => {
      size();
      const r = s.getBoundingClientRect(), n = Math.max(r.width, r.height) * 0.2;
      s.querySelectorAll("img").forEach((i) => { i.style.minWidth = n + "px"; i.style.width = n + "px"; i.style.height = n + "px"; });
    };
    fit(); window.addEventListener("resize", () => setTimeout(fit, 100));
  };
})();
