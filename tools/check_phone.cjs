// Phone-sized checks for the game page (decisions/0043).
//
//   node tools/check_phone.cjs [build/web]
//
// Opens the game page as phones (iPhone and Android sizes, upright and
// sideways) and as a computer, with tools/pyxel_standin.js in place of
// Pyxel's runtime, and checks that:
// - on a phone the bar is one line and the game fits below it
// - the game doesn't sit under the on-screen gamepad, and the labels for the
//   gamepad are there and don't cover the game
// - nothing scrolls sideways
// - on a computer the keyboard hints show and the gamepad labels don't
// Exits 1 if anything fails. Needs: npm install --no-save playwright@1.56.0

const fs = require("fs");
const http = require("http");
const path = require("path");
const { chromium } = require("playwright");

const ROOT = path.resolve(process.argv[2] || "build/web");
// the page itself calls launchPyxel(), as it does with the real runtime
const STANDIN = fs.readFileSync(path.join(__dirname, "pyxel_standin.js"), "utf8");
const DEVICES = [
  { name: "iPhone upright", width: 390, height: 844, touch: true },
  { name: "iPhone sideways", width: 844, height: 390, touch: true },
  { name: "Android upright", width: 412, height: 915, touch: true },
  { name: "Android sideways", width: 915, height: 412, touch: true },
  { name: "computer", width: 1280, height: 800, touch: false },
];

function serve() {
  return new Promise((resolve) => {
    const server = http.createServer((req, res) => {
      let p = decodeURIComponent(req.url.split("?")[0]);
      if (p.endsWith("/")) p += "index.html";
      const file = path.join(ROOT, p);
      if (!file.startsWith(ROOT) || !fs.existsSync(file)) { res.writeHead(404); res.end(); return; }
      res.writeHead(200, { "Content-Type": file.endsWith(".html") ? "text/html" : "application/octet-stream" });
      fs.createReadStream(file).pipe(res);
    });
    server.listen(0, "127.0.0.1", () => resolve(server));
  });
}

const overlap = (a, b) => a && b && a.width && b.width &&
  a.left < b.right - 1 && b.left < a.right - 1 && a.top < b.bottom - 1 && b.top < a.bottom - 1;

(async () => {
  const server = await serve();
  const url = `http://127.0.0.1:${server.address().port}/index.html`;
  const browser = await chromium.launch();
  let failures = 0;
  for (const d of DEVICES) {
    const ctx = await browser.newContext({ viewport: { width: d.width, height: d.height },
      isMobile: d.touch, hasTouch: d.touch });
    const page = await ctx.newPage();
    await page.route("**/pyxel.js", (r) => r.fulfill({ contentType: "text/javascript", body: STANDIN }));
    await page.goto(url, { waitUntil: "load" });
    await page.waitForTimeout(800);
    await page.mouse.click(d.width / 2, d.height / 3);            // start playing
    await page.waitForTimeout(300);
    const m = await page.evaluate(() => {
      const rect = (sel) => { const e = document.querySelector(sel);
        if (!e || getComputedStyle(e).display === "none") return null;
        const r = e.getBoundingClientRect(); if (!r.width) return null; return { left: r.left, right: r.right, top: r.top, bottom: r.bottom, width: r.width, height: r.height }; };
      return { bar: rect("#fcq-a11y"), game: rect("canvas#canvas"), cross: rect("img#pyxel-gamepad-cross"),
        buttons: rect("img#pyxel-gamepad-button"), menu: rect("img#pyxel-gamepad-menu"),
        walk: rect("#fcq-walk"), labels: rect("#fcq-buttons"), help: rect("#fcq-help"),
        status: document.getElementById("fcq-keys").textContent,
        scrollW: document.documentElement.scrollWidth, innerW: innerWidth, innerH: innerHeight };
    });
    const bad = [];
    if (m.scrollW > m.innerW + 1) bad.push(`page is ${m.scrollW}px wide`);
    if (!m.game || m.game.top < m.bar.bottom - 1 || m.game.bottom > m.innerH + 1) bad.push("game doesn't fit below the bar");
    if (m.status !== "Playing") bad.push(`status says "${m.status}"`);
    if (d.touch) {
      if (m.bar.height > 44) bad.push(`bar is ${Math.round(m.bar.height)}px tall (more than one line)`);
      for (const [n, r] of [["d-pad", m.cross], ["buttons", m.buttons], ["menu button", m.menu],
                            ["d-pad label", m.walk], ["button labels", m.labels]])
        if (overlap(r, m.game)) bad.push(`the ${n} cover the game`);
      if (!m.walk || !m.labels) bad.push("gamepad labels missing");
      if (m.help) bad.push("keyboard hints showing on a touch screen");
    } else {
      if (m.walk || m.labels) bad.push("gamepad labels showing on a computer");
      if (!m.help) bad.push("keyboard hints missing");
    }
    console.log(`${bad.length ? "FAIL" : "ok  "} ${d.name} (${d.width}x${d.height})` + (bad.length ? "\n  - " + bad.join("\n  - ") : ""));
    failures += bad.length;
    await ctx.close();
  }
  await browser.close();
  server.close();
  console.log(`\n${DEVICES.length} screen sizes checked, ${failures} problem(s).`);
  process.exit(failures ? 1 : 0);
})();
