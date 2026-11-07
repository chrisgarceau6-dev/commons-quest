#!/usr/bin/env python3
"""Rebuild Commons Quest's data from UMass Dining's public feeds.

  data/menu.json  - 14 days of dining-commons menus with full nutrition + allergens, plus retail items
  data/hours.json - today's opening hours for every dining location

usage: python3 scripts/scrape_menu.py OLD_MENU_JSON OUT_MENU_JSON [START_MM/DD/YYYY] [--hours OUT_HOURS_JSON]

Row format (compact arrays keep the file small for phones):
  [name, serving, kcal, protein, carbs, fat, loc_indexes, meals, station, diet_flags, day_bitmask,
   fiber, sugar, sat_fat, trans_fat, cholesterol, sodium, allergen_codes]
  meals: B L D N G (breakfast, lunch, dinner, late night, grab'n go)
  diet_flags: P plant-based, V vegetarian, H halal
  allergen_codes: M milk, E eggs, G gluten, W wheat, S soy, C corn, X sesame, F fish, K shellfish, P peanuts, N tree nuts
"""
import json, re, sys, html, datetime as dt, urllib.request, time
args = [a for a in sys.argv[1:]]
HOURS = None
if "--hours" in args:
    i = args.index("--hours"); HOURS = args[i + 1]; del args[i:i + 2]
OLD, OUT = args[0], args[1]
start = dt.datetime.strptime(args[2], "%m/%d/%Y").date() if len(args) > 2 else (dt.datetime.utcnow() - dt.timedelta(hours=8)).date()
ALLERGEN = {"milk": "M", "eggs": "E", "gluten": "G", "wheat": "W", "soy": "S", "corn": "C", "sesame": "X", "fish": "F", "shellfish": "K", "peanuts": "P", "tree nuts": "N"}
DAYS = [start + dt.timedelta(days=i) for i in range(14)]
HALLS = {1: 0, 2: 1, 3: 2, 4: 3}            # feed tid -> loc index (Worcester, Franklin, Hampshire, Berkshire)
MEAL = {"breakfast": "B", "lunch": "L", "dinner": "D", "late night": "N", "grabngo": "G"}
old = json.load(open(OLD))
ST = list(old["st"])
def num(v):
    m = re.match(r"\s*([\d.]+)", v or "")
    return float(m.group(1)) if m else 0.0
def r1(x): return round(x * 10) / 10
def get(tid, day):
    url = f"https://www.umassdining.com/foodpro-menu-ajax?tid={tid}&date={day.strftime('%m/%d/%Y')}"
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "CommonsQuest menu sync"}), timeout=40) as r:
                d = json.loads(r.read().decode("utf-8"))
                return d if isinstance(d, dict) else {}
        except Exception as e:
            err = e; time.sleep(2 + attempt * 3)
    print("FAILED", tid, day, err, file=sys.stderr); return None
A = re.compile(r'<a ([^>]*data-dish-name="[^"]*"[^>]*)>')
ATTR = re.compile(r'data-([a-z0-9_-]+)="([^"]*)"')
rows = {}                                    # (name, serving) -> row
failed = 0
for di, day in enumerate(DAYS):
    for tid, li in HALLS.items():
        d = get(tid, day)
        if d is None: failed += 1; continue
        for meal, stations in d.items():
            ml = MEAL.get(meal.strip().lower())
            if not ml or not isinstance(stations, dict): continue
            for stname, blob in stations.items():
                stname = stname.strip()
                for m in A.finditer(blob or ""):
                    a = {k: html.unescape(v) for k, v in ATTR.findall(m.group(1))}
                    name = a.get("dish-name", "").strip()
                    if not name: continue
                    serv = a.get("serving-size", "").strip()
                    key = (name, serv)
                    r = rows.get(key)
                    if r is None:
                        if stname not in ST: ST.append(stname)
                        diet = a.get("clean-diet-str", "")
                        flags = ("P" if "Plant Based" in diet else "V" if "Vegetarian" in diet else "") + ("H" if "Halal" in diet else "")
                        r = [name, serv, round(num(a.get("calories"))), r1(num(a.get("protein"))), r1(num(a.get("total-carb"))), r1(num(a.get("total-fat"))),
                             [], "", ST.index(stname), flags, 0, r1(num(a.get("dietary-fiber"))), r1(num(a.get("sugars"))), r1(num(a.get("sat-fat"))),
                             r1(num(a.get("trans-fat"))), r1(num(a.get("cholesterol"))), r1(num(a.get("sodium"))),
                             "".join(sorted({ALLERGEN[x.strip().lower()] for x in a.get("allergens", "").split(",") if x.strip().lower() in ALLERGEN}))]
                        rows[key] = r
                    if li not in r[6]: r[6].append(li)
                    if ml not in r[7]: r[7] += ml
                    r[10] |= 1 << di
if failed > 8:
    sys.exit(f"too many failed fetches ({failed}); keeping the old menu")
# rows that don't come from the dining-commons feed (retail spots, manual extras): keep, re-aim their day pattern at the new window
oldd = [dt.datetime.strptime(x, "%m/%d/%Y").date() for x in old["dates"]]
commons = old.get("commons", 4)
keep = []
for r in old["rows"]:
    locs = [int(x) for x in str(r[6]).split(",") if x != ""]
    icecream = r[8] < len(old["st"]) and old["st"][r[8]] == "Ice Cream & Toppings"
    sl = locs if icecream else [l for l in locs if l >= commons]      # the non-feed part of this item
    if not sl: continue
    wd = {oldd[i].weekday() for i in range(len(oldd)) if (r[10] >> i) & 1}
    mask = sum(1 << i for i, day in enumerate(DAYS) if day.weekday() in wd)
    hit = rows.get((r[0], r[1]))
    if hit is not None:                         # same food is also on a dining-hall menu: one entry, both places
        for l in sl:
            if l not in hit[6]: hit[6].append(l)
        hit[10] |= mask
        continue
    r = list(r) + [""] * (18 - len(r)); r[6] = ",".join(map(str, sl)); r[10] = mask
    if not icecream: r[7] = ""
    keep.append(r)
out = []
for r in rows.values():
    r[6] = ",".join(map(str, r[6])); out.append(r)
dining = sum(1 for r in out)
if dining < 300:
    sys.exit(f"only {dining} dining items found; keeping the old menu")
json.dump({"dates": [x.strftime("%m/%d/%Y") for x in DAYS], "locs": old["locs"], "commons": commons, "st": ST, "rows": keep + out},
          open(OUT, "w"), separators=(",", ":"))
if HOURS:
    try:
        with urllib.request.urlopen(urllib.request.Request("https://www.umassdining.com/uapp/get_infov2", headers={"User-Agent": "CommonsQuest menu sync"}), timeout=40) as r:
            info = json.loads(r.read().decode("utf-8"))
        key = lambda n: re.sub(r"[^a-z]", "", n.lower().replace("dining commons", "").replace("commons", ""))
        names = {key(n): n for n in old["locs"]}
        def t24(t):
            m = re.match(r"(\d+):(\d+)\s*([AP]M)", t or "")
            if not m: return None
            h = int(m.group(1)) % 12 + (12 if m.group(3) == "PM" else 0)
            return f"{h:02d}:{m.group(2)}"
        hours = {}
        for x in info:
            k = key(x.get("location_title", ""))
            match = names.get(k) or next((v for kk, v in names.items() if kk and (k.startswith(kk) or kk.startswith(k))), None)
            if not match or match in hours: continue
            o, c = t24(x.get("opening_hours")), t24(x.get("closing_hours"))
            hours[match] = {"open": o, "close": c} if o and c else {"closed": True}
        json.dump({"date": start.strftime("%m/%d/%Y"), "locations": hours}, open(HOURS, "w"), separators=(",", ":"))
        print(f"hours: {len(hours)} locations")
    except Exception as e:
        print("hours fetch failed (menus still updated):", e, file=sys.stderr)
print(f"ok: {dining} dining items, {len(keep)} retail/extra items, {DAYS[0]} to {DAYS[-1]}, {failed} failed fetches")
