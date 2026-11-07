// End-to-end check of the real app in a headless phone-sized browser.
// Run: node tests/e2e.mjs   (needs: npm i playwright && npx playwright install chromium)
import { chromium } from "playwright";
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
const TYPES = { ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".css": "text/css", ".png": "image/png", ".json": "application/json", ".mp3": "audio/mpeg", ".woff2": "font/woff2", ".webmanifest": "application/manifest+json" };
const missing = [];
const server = http.createServer((req, res) => {
  let p = decodeURIComponent(req.url.split("?")[0]); if (p === "/") p = "/index.html";
  const f = path.join(root, p);
  if (!f.startsWith(root) || !fs.existsSync(f)) { missing.push(p); res.writeHead(404); return res.end(); }
  res.writeHead(200, { "content-type": TYPES[path.extname(f)] || "application/octet-stream" }); res.end(fs.readFileSync(f));
}).listen(0);
const url = `http://localhost:${server.address().port}/`;
const fail = (m) => { console.error("FAIL:", m); process.exitCode = 1; };
const ok = (c, m) => (c ? console.log("ok -", m) : fail(m));

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
const errors = [];
page.on("pageerror", (e) => errors.push(e.message));

// --- first run: setup screen
await page.goto(url); await page.waitForTimeout(1800);
ok(await page.locator("#goalf").count() === 1, "setup screen shows on first open");
await page.click("[data-act=pickhero][data-h=g2]");
await page.fill("#g-name", "Tester");
await page.click("[data-act=sethome][data-h=wor]");
await page.click("[data-act=togalg][data-c=P]");
await page.click("[data-act=gpre][data-g=maintain]");
await page.click("#goalf button[type=submit]");
await page.waitForTimeout(600);
const prof = await page.evaluate(() => JSON.parse(localStorage.getItem("gq-profile")));
ok(prof.name === "Tester" && prof.hero === "g2" && prof.home === "wor" && prof.avoid.includes("P"), "profile saved with hero, hall and allergies");
ok((await page.textContent("#hud")).includes("TESTER"), "name shows in the header");
ok((await page.locator("h2.sec", { hasText: "NEXT MOVE · WORCESTER" }).count()) === 1, "next move uses the usual hall");

// --- suggestions respect allergies
const peanutInCombo = await page.evaluate(() => comboFor(homeHall(), curMeal()).items.some((r) => (r[17] || "").includes("P")));
ok(!peanutInCombo, "combos never suggest a food with an avoided allergen");

// --- quick log from a sentence (pick a real item served today so the test never depends on the menu)
const dish = await page.evaluate(() => DATA.find((r) => servedToday(r) && r[0].split(" ").length >= 2 && r[2] > 100)[0]);
await page.fill("#qlin", "2 " + dish.toLowerCase());
await page.press("#qlin", "Enter"); await page.waitForTimeout(300);
const found = await page.locator("[data-act=qlgo]").count();
ok(found === 1, `quick log understood "2 ${dish}"`);
if (found) { await page.click("[data-act=qlgo]"); await page.waitForTimeout(400); }
const logged = await page.evaluate(() => (DAYS[curDay()]?.items || []).reduce((a, e) => a + e.q, 0));
ok(logged === 2, "quick log added the right quantity");

// --- boss fight + attack
await page.click(".pin[data-h=berk]"); await page.waitForTimeout(700);
ok(await page.locator(".stage.bgx").count() === 1, "boss fight has its hall backdrop");
await page.locator("#hlist [data-act=eat]").first().click(); await page.waitForTimeout(900);
ok((await page.evaluate(() => DAYS[curDay()].items.length)) >= 2, "tapping + in a fight logs the food");

// --- other screens open without errors
for (const t of ["pack", "trophies", "map"]) { await page.click(`.nav [data-t=${t}]`); await page.waitForTimeout(300); }
await page.click("[data-act=goals]"); await page.waitForTimeout(300);
ok(await page.locator("[data-act=backup]").count() === 1, "settings offers backup and restore");

// --- choose what's tracked at the top
await page.click("[data-act=gpre][data-g=bulk]");
ok((await page.inputValue("#g-k")) === "3400", "bulk preset sets 3,400 calories");
await page.click('.trow[data-k=fiber] [data-act=togtrack]');
await page.click('.trow[data-k=carbs] [data-act=togtrack]');
await page.fill('.trow[data-k=carbs] .tv', "300");
await page.click("#goalf button[type=submit]"); await page.waitForTimeout(400);
const keys = await page.evaluate(() => GOALS.track.map((x) => x.k).join(","));
ok(keys.includes("carbs") && !keys.includes("fiber"), "tracked stats are saved (" + keys + ")");
ok((await page.locator(".stats3 .lab", { hasText: "CARBS" }).count()) === 1, "home screen shows the chosen stat");

// --- data survives a reload
await page.reload(); await page.waitForTimeout(1500);
ok(await page.locator("#goalf").count() === 0, "setup does not reappear after reload");
ok((await page.evaluate(() => DAYS[curDay()].items.length)) >= 2, "log survives a reload");

// --- demo mode: skip setup with sample data, then start fresh
const demo = await browser.newPage({ viewport: { width: 390, height: 844 } });
demo.on("pageerror", (e) => errors.push(e.message));
await demo.goto(url); await demo.waitForTimeout(1800);
await demo.click("[data-act=demo]"); await demo.waitForTimeout(500);
ok(await demo.locator("#goalf").count() === 0 && (await demo.locator(".banner2", { hasText: "Demo mode" }).count()) === 1, "demo skips setup and says it's a demo");
ok((await demo.evaluate(() => Object.keys(DAYS).length)) >= 10, "demo fills in sample days");
await demo.click(".nav [data-t=trophies]"); await demo.waitForTimeout(300);
ok((await demo.locator(".tile.legend, .tile.rare, .tile.unc").count()) >= 3, "demo trophy wall has loot");
await demo.click(".nav [data-t=map]"); await demo.waitForTimeout(300);
await demo.click("[data-act=enddemo]"); await demo.waitForTimeout(400);
ok(await demo.locator("#goalf").count() === 1 && (await demo.evaluate(() => Object.keys(DAYS).length)) === 0, "\"Make it mine\" clears the demo and opens setup");

ok(errors.length === 0, "no JavaScript errors" + (errors.length ? ": " + errors.join(" | ") : ""));
ok(missing.filter((m) => !m.endsWith("favicon.ico")).length === 0, "no missing files" + (missing.length ? ": " + missing.join(", ") : ""));
await browser.close(); server.close();
