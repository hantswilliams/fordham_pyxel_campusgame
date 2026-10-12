// Automated accessibility check for the web build (decisions/0037).
//
//   node tools/check_accessibility.cjs [build/web]
//
// Serves the built site, opens every Campus Guide page and the game page in
// Chromium (Playwright), and runs axe-core with the WCAG 2.0 / 2.1 / 2.2 A and
// AA rules. Guide pages are also checked for reflow at 320 px wide (WCAG
// 1.4.10). Exits 1 if anything fails, so the GitHub workflow stops.
//
// Needs: npm install --no-save axe-core@4.13.0 playwright@1.56.0
//        npx playwright install chromium

const fs = require("fs");
const http = require("http");
const path = require("path");
const { chromium } = require("playwright");

const ROOT = path.resolve(process.argv[2] || "build/web");
const AXE = fs.readFileSync(require.resolve("axe-core/axe.min.js"), "utf8");
const TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"];
const TYPES = { ".html": "text/html", ".css": "text/css", ".js": "text/javascript", ".png": "image/png",
                ".pyxapp": "application/octet-stream" };

function pages(dir, rel = "") {
  let out = [];
  for (const name of fs.readdirSync(path.join(dir, rel))) {
    const r = path.join(rel, name);
    if (fs.statSync(path.join(dir, r)).isDirectory()) out = out.concat(pages(dir, r));
    else if (name.endsWith(".html")) out.push(r.split(path.sep).join("/"));
  }
  return out;
}

function serve() {
  return new Promise((resolve) => {
    const server = http.createServer((req, res) => {
      let p = decodeURIComponent(req.url.split("?")[0]);
      if (p.endsWith("/")) p += "index.html";
      const file = path.join(ROOT, p);
      if (!file.startsWith(ROOT) || !fs.existsSync(file)) { res.writeHead(404); res.end(); return; }
      res.writeHead(200, { "Content-Type": TYPES[path.extname(file)] || "application/octet-stream" });
      fs.createReadStream(file).pipe(res);
    });
    server.listen(0, "127.0.0.1", () => resolve(server));
  });
}

(async () => {
  const server = await serve();
  const base = `http://127.0.0.1:${server.address().port}/`;
  const list = pages(ROOT).filter((p) => p === "index.html" || p.startsWith("guide/"));
  const browser = await chromium.launch();
  let failures = 0;
  for (const rel of list) {
    const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
    try {
      await page.goto(base + rel, { waitUntil: "load", timeout: 30000 });
    } catch (e) { /* the game page's runtime may be slow or offline; check what loaded */ }
    await page.addScriptTag({ content: AXE });
    let bad;
    if (rel === "index.html") {
      // The game page is the non-conforming version: the Campus Guide is its
      // accessible alternative. Check what WCAG still asks of it and what we
      // control: the page's title, language and viewport, and the bar with the
      // guide link. Pyxel's runtime adds its own elements (canvas, prompt,
      // touch gamepad) that we can't change, and turns off pinch zoom so the
      // touch gamepad works; zoom isn't one of WCAG's non-interference rules,
      // and the guide (the conforming version) allows it. The keyboard
      // hand-off is on the manual checklist.
      bad = await page.evaluate(async (tags) => {
        const page = await window.axe.run(document, { runOnly: { type: "rule",
          values: ["document-title", "html-has-lang", "html-lang-valid"] } });
        const bar = await window.axe.run({ include: [["#fcq-a11y"]] }, { runOnly: { type: "tag", values: tags } });
        return page.violations.concat(bar.violations);
      }, TAGS);
      const hasBar = await page.evaluate(() => !!document.querySelector("#fcq-a11y a[href='guide/index.html']"));
      if (!hasBar) bad.push({ id: "guide-link", impact: "serious", help: "the game page has no link to the Campus Guide", nodes: [] });
    } else {
      const result = await page.evaluate(async (tags) =>
        await window.axe.run(document, { runOnly: { type: "tag", values: tags } }), TAGS);
      bad = result.violations;
    }
    if (rel.startsWith("guide/")) {
      await page.setViewportSize({ width: 320, height: 640 });
      const wide = await page.evaluate(() => document.documentElement.scrollWidth);
      if (wide > 321) bad.push({ id: "reflow-320", impact: "serious",
        help: `page is ${wide}px wide at a 320px viewport (WCAG 1.4.10)`, nodes: [] });
    }
    if (bad.length) {
      failures += bad.length;
      console.log(`FAIL ${rel}`);
      for (const v of bad) {
        console.log(`  - ${v.id} (${v.impact}): ${v.help}`);
        for (const n of v.nodes.slice(0, 3)) console.log(`      ${n.target.join(" ")}`);
      }
    } else {
      console.log(`ok   ${rel}`);
    }
    await page.close();
  }
  await browser.close();
  server.close();
  console.log(`\n${list.length} pages checked, ${failures} problem(s).`);
  process.exit(failures ? 1 : 0);
})();
