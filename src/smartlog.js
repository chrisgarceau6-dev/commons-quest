/*
 * SmartLog — turns a sentence like "2 slices pepperoni pizza and a chocolate milk at berk"
 * into menu items with quantities. Runs entirely on the phone: no server, no API key, no cost.
 *
 * Pipeline: normalize -> pull out a dining-hall hint -> split into food segments ->
 * read a quantity off each segment -> score every candidate menu item -> keep the best
 * (with runner-up alternatives the user can swap to).
 *
 * Works in the browser (window.SmartLog) and in Node (module.exports) so it can be unit tested.
 */
(function (root) {
  "use strict";

  const NUMBER_WORDS = { a: 1, an: 1, one: 1, two: 2, three: 3, four: 4, five: 5, six: 6, half: 0.5, couple: 2, few: 3, double: 2, triple: 3 };
  const UNIT_WORDS = new Set(["slice", "slices", "piece", "pieces", "pc", "pcs", "bowl", "bowls", "cup", "cups", "plate", "plates",
    "serving", "servings", "scoop", "scoops", "order", "orders", "glass", "glasses", "bottle", "bottles", "can", "cans",
    "of", "some", "the", "my", "x", "side", "sides", "small", "large", "big", "little"]);
  const FILLER = new Set(["i", "had", "ate", "got", "grabbed", "with", "for", "lunch", "dinner", "breakfast", "today", "just", "also", "then", "plus", "at", "from", "in"]);
  // short forms students actually type
  const SYNONYMS = { choc: "chocolate", mac: "macaroni", pb: "peanut butter", oj: "orange juice", bfast: "breakfast", sammy: "sandwich",
    sando: "sandwich", sub: "sandwich", za: "pizza", pep: "pepperoni", parm: "parmesan", chix: "chicken", chkn: "chicken",
    bbq: "barbecue", hb: "hamburger", burg: "burger", fries: "fries", froyo: "frozen yogurt", icecream: "ice cream", softserve: "soft serve" };
  const HALL_HINTS = { berk: "berk", berkshire: "berk", wor: "wor", woo: "wor", worcester: "wor", frank: "frank", franklin: "frank",
    hamp: "hamp", hampshire: "hamp", cc: "cc", "campus center": "cc", "blue wall": "cc", bluewall: "cc" };

  const norm = (s) => String(s || "").toLowerCase().replace(/[’']/g, "").replace(/[^a-z0-9.,&+ ]+/g, " ").replace(/\s+/g, " ").trim();
  const singular = (w) => (w.length > 3 && w.endsWith("ies") ? w.slice(0, -3) + "y" : w.length > 3 && w.endsWith("es") && /(ch|sh|x|o)es$/.test(w) ? w.slice(0, -2) : w.length > 3 && w.endsWith("s") && !w.endsWith("ss") ? w.slice(0, -1) : w);
  const STOP = new Set(["and", "&", "w", "with", "of", "the", "a", "an", "n"]);
  const tokens = (s) => norm(s).replace(/\bw\//g, " ").split(" ").filter((w) => w && !STOP.has(w)).flatMap((w) => (SYNONYMS[w] ? SYNONYMS[w].split(" ") : [w])).map(singular);

  function editDistanceAtMost1(a, b) {
    if (Math.abs(a.length - b.length) > 1) return false;
    let i = 0, j = 0, edits = 0;
    while (i < a.length && j < b.length) {
      if (a[i] === b[j]) { i++; j++; continue; }
      if (++edits > 1) return false;
      if (a.length > b.length) i++; else if (b.length > a.length) j++; else { i++; j++; }
    }
    return edits + (a.length - i) + (b.length - j) <= 1;
  }

  // how well one typed word matches one word of a menu item name (0..1)
  function wordScore(q, w) {
    if (q === w) return 1;
    if (q.length >= 3 && w.startsWith(q)) return 0.85;          // "pepp" -> "pepperoni"
    if (w.length >= 4 && q.startsWith(w)) return 0.75;
    if (q.length >= 5 && editDistanceAtMost1(q, w)) return 0.7;   // typos: "chiken"
    return 0;
  }

  /** score a segment's words against one menu item name. Returns 0..1+. */
  function scoreName(qTokens, name) {
    const nTokens = tokens(name);
    if (!qTokens.length || !nTokens.length) return 0;
    let hit = 0;
    for (const q of qTokens) {
      let best = 0;
      for (const w of nTokens) best = Math.max(best, wordScore(q, w));
      hit += best;
    }
    const recall = hit / qTokens.length;                    // did we explain what they typed?
    const covered = nTokens.filter((w) => qTokens.some((q) => wordScore(q, w) >= 0.7)).length;
    const precision = covered / nTokens.length;             // prefer "Pepperoni Pizza" over "Pepperoni Pizza Calzone Platter"
    return recall * 0.78 + precision * 0.22;
  }

  /** read a leading/trailing quantity and strip unit words */
  function readQuantity(words) {
    let qty = 1, found = false;
    const rest = [];
    for (let i = 0; i < words.length; i++) {
      const w = words[i];
      if (!found && /^\d+(\.\d+)?$/.test(w)) { qty = parseFloat(w); found = true; continue; }
      if (!found && /^\d+x$/.test(w)) { qty = parseFloat(w); found = true; continue; }
      if (!found && /^x\d+$/.test(w)) { qty = parseFloat(w.slice(1)); found = true; continue; }
      if (!found && NUMBER_WORDS[w] != null && (i === 0 || UNIT_WORDS.has(words[i - 1]) || FILLER.has(words[i - 1]))) { qty = NUMBER_WORDS[w]; found = true; continue; }
      if (UNIT_WORDS.has(w) || FILLER.has(w)) continue;
      rest.push(w);
    }
    if (qty <= 0 || qty > 12) qty = 1;
    return { qty: Math.round(qty * 2) / 2, words: rest };
  }

  /** pull "at berk" / "from worcester" style hints out of the sentence */
  function readHall(text) {
    let hall = null, out = " " + text + " ";
    for (const [k, v] of Object.entries(HALL_HINTS).sort((a, b) => b[0].length - a[0].length)) {
      const re = new RegExp("\\s(?:at|from|in|@)?\\s?" + k.replace(" ", "\\s") + "(?:\\s(?:dc|dining|commons))?(?=\\s)");
      if (re.test(out)) { hall = hall || v; out = out.replace(re, " "); }
    }
    return { hall, text: out.trim() };
  }

  function splitSegments(text) {
    return text.split(/\s*(?:,|;|\+|&|\bplus\b|\bthen\b|\balso\b)\s*/).map((s) => s.trim()).filter(Boolean);
  }

  /**
   * parse(text, rows, opts) -> { hall, items: [{ text, qty, row, score, alts: [row...] }], unmatched: [text] }
   *   rows: menu rows ([name, serving, kcal, protein, ...]) — usually today's menu
   *   opts.preferHall(row) -> bool, opts.minScore
   */
  function parse(text, rows, opts = {}) {
    const minScore = opts.minScore ?? 0.58;
    const { hall, text: rest } = readHall(norm(text));
    const index = rows.map((r) => ({ r, toks: tokens(r[0]) }));
    const items = [], unmatched = [];

    const best = (segText) => {
      const { qty, words } = readQuantity(segText.split(" "));
      const q = words.flatMap((w) => (SYNONYMS[w] ? SYNONYMS[w].split(" ") : [w])).filter((w) => !STOP.has(w)).map(singular);
      if (!q.length) return null;
      const scored = [];
      for (const { r } of index) {
        let s = scoreName(q, r[0]);
        if (s <= 0.3) continue;
        if (opts.preferHall && opts.preferHall(r, hall)) s += 0.06;
        if (opts.taste) s += Math.min(0.06, (opts.taste(r) || 0) * 0.02);   // they've eaten it before
        scored.push({ r, s });
      }
      scored.sort((a, b) => b.s - a.s || a.r[0].length - b.r[0].length);
      const seen = new Set(), alts = [];
      for (const x of scored) { if (seen.has(x.r[0])) continue; seen.add(x.r[0]); alts.push(x); if (alts.length >= 4) break; }
      return alts.length ? { text: segText, qty, row: alts[0].r, score: alts[0].s, alts: alts.slice(1).map((x) => x.r) } : { text: segText, qty, row: null, score: 0, alts: [] };
    };

    for (const seg of splitSegments(rest)) {
      const whole = best(seg);
      // "mac and cheese" should stay one item, "burger and fries" should become two
      if (/\band\b|\bwith\b/.test(seg)) {
        const parts = seg.split(/\s+(?:and|with)\s+/).filter(Boolean);
        const split = parts.map(best);
        const splitOk = split.every((p) => p && p.row && p.score >= minScore);
        const splitAvg = splitOk ? split.reduce((a, p) => a + p.score, 0) / split.length : 0;
        const wholeStrong = whole && whole.row && whole.score >= 0.85;
        if (splitOk && !wholeStrong && (!whole || !whole.row || splitAvg > whole.score + 0.04)) { split.forEach((p) => items.push(p)); continue; }
      }
      if (whole && whole.row && whole.score >= minScore) items.push(whole);
      else if (whole) unmatched.push(seg);
    }
    return { hall, items, unmatched };
  }

  const api = { parse, tokens, scoreName, readQuantity, readHall, splitSegments, norm };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.SmartLog = api;
})(typeof window !== "undefined" ? window : globalThis);
