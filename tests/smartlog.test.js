// Unit tests for the on-device meal parser. Run: node --test tests/
const test = require("node:test");
const assert = require("node:assert/strict");
const SL = require("../src/smartlog.js");

// a slice of a real UMass menu, in the app's row format: [name, serving, kcal, protein, ...]
const MENU = [
  ["Pepperoni Pizza", "1 slice", 290, 13], ["Cheese Pizza", "1 slice", 260, 11], ["Vegetable Pizza", "1 slice", 240, 10],
  ["Chocolate Milk", "8 oz", 190, 8], ["2% Milk", "8 oz", 120, 8], ["Macaroni & Cheese", "1 cup", 410, 16],
  ["Grilled Chicken Thighs", "4 oz", 230, 26], ["Chicken Tenders", "3 each", 340, 22], ["French Fries", "4 oz", 320, 4],
  ["Halal SPARE Beef Burger", "1 each", 520, 28], ["Black Bean Burger", "1 each", 380, 16], ["Caesar Salad", "1 each", 210, 6],
];
const names = (res) => res.items.map((i) => [i.row[0], i.qty]);

test("quantities and units are read off the front of each item", () => {
  assert.deepEqual(names(SL.parse("2 slices of pepperoni pizza", MENU)), [["Pepperoni Pizza", 2]]);
  assert.deepEqual(names(SL.parse("a chocolate milk", MENU)), [["Chocolate Milk", 1]]);
  assert.deepEqual(names(SL.parse("half a cheese pizza", MENU)), [["Cheese Pizza", 0.5]]);
  assert.deepEqual(names(SL.parse("chicken tenders x2", MENU)), [["Chicken Tenders", 2]]);
});

test("several foods in one sentence", () => {
  assert.deepEqual(names(SL.parse("2 slices pepperoni pizza and a chocolate milk", MENU)), [["Pepperoni Pizza", 2], ["Chocolate Milk", 1]]);
  assert.deepEqual(names(SL.parse("burger, fries, caesar salad", MENU)).map((x) => x[0]).slice(1), ["French Fries", "Caesar Salad"]);
});

test("'and' inside a dish name is not a split", () => {
  assert.deepEqual(names(SL.parse("mac and cheese", MENU)), [["Macaroni & Cheese", 1]]);
});

test("slang, plurals and typos", () => {
  assert.equal(SL.parse("choc milk", MENU).items[0].row[0], "Chocolate Milk");
  assert.equal(SL.parse("chiken thighs", MENU).items[0].row[0], "Grilled Chicken Thighs");
  assert.equal(SL.parse("pep za", MENU).items[0].row[0], "Pepperoni Pizza");
});

test("dining hall hints are pulled out of the sentence", () => {
  const r = SL.parse("2 slices pepperoni pizza at berk", MENU);
  assert.equal(r.hall, "berk");
  assert.deepEqual(names(r), [["Pepperoni Pizza", 2]]);
  assert.equal(SL.parse("lunch at worcester: chicken tenders", MENU).hall, "wor");
});

test("nonsense stays unmatched instead of guessing", () => {
  const r = SL.parse("asdkjh qwerty", MENU);
  assert.equal(r.items.length, 0);
  assert.equal(r.unmatched.length, 1);
});

test("alternatives are offered for a swap", () => {
  const r = SL.parse("pizza", MENU);
  assert.ok(r.items[0].alts.length >= 2);
});
