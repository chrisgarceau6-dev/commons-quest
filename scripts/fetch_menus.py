"""Rebuild gq-app/menu.json from the live UMass Dining feed.

The four dining commons (Worcester, Franklin, Hampshire, Berkshire) are the
bosses in the app and their menus rotate daily, so they are re-fetched for a
rolling window starting today. The retail venues are not served by this feed;
their rows are carried over from the existing menu.json and re-projected onto
the new window using the day-of-week pattern already encoded in their bitmask.

The output schema is byte-for-byte the shape gq-app/index.html expects:

    dates    list of "MM/DD/YYYY", oldest first; row bit i == dates[i]
    locs     venue names - ORDER IS LOAD-BEARING, HALLS hardcodes indices
    commons  how many leading locs entries are dining commons
    st       station names, indexed by row[8]
    rows     [name, serving, kcal, protein, carb, fat, locIdx, meals,
              stIdx, diets, dateMask, fiber, sugar, satFat, transFat,
              cholesterol, sodium]
"""
import json
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta
from html import unescape
from pathlib import Path

APP = Path(__file__).resolve().parent.parent / "gq-app"
MENU = APP / "menu.json"

WINDOW_DAYS = 14
FEED = "https://www.umassdining.com/foodpro-menu-ajax?tid={tid}&date={date}"

# loc index (into `locs`) -> UMass Dining taxonomy term id
COMMONS_TIDS = {0: 1, 1: 2, 2: 3, 3: 4}

MEAL_CODES = {
    "breakfast": "B",
    "lunch": "L",
    "dinner": "D",
    "late night": "N",
    "grabngo": "G",
}

DIET_CODES = [("plant", "P"), ("vegan", "P"), ("vegetarian", "V"), ("halal", "H")]

ANCHOR = re.compile(r"<a\s([^>]*?data-dish-name[^>]*?)>")
ATTR = re.compile(r'data-([a-z-]+)="([^"]*)"')


def num(raw):
    """'3.8g' -> 3.8, '436.6mg' -> 436.6, '' -> 0."""
    if not raw:
        return 0
    m = re.search(r"-?\d+(?:\.\d+)?", raw)
    if not m:
        return 0
    v = float(m.group())
    return int(v) if v == int(v) else v


def get(url, attempts=4):
    last = None
    for i in range(attempts):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "gainz-quest-menu-bot"})
            with urllib.request.urlopen(req, timeout=45) as resp:
                return json.loads(resp.read().decode("utf-8", "replace"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
            last = exc
            time.sleep(2 * (i + 1))
    raise RuntimeError(f"giving up on {url}: {last}")


def main():
    prev = json.loads(MENU.read_text(encoding="utf-8"))
    locs = prev["locs"]              # order is load-bearing; never rebuild this
    commons = prev["commons"]

    # Anchor on the app's dining day, not the calendar day: index.html rolls
    # over at 4am (questNow), so between midnight and 4am the current dining
    # day is still yesterday and the window has to start there.
    today = (datetime.now() - timedelta(hours=4)).date()
    dates = [(today + timedelta(days=i)).strftime("%m/%d/%Y") for i in range(WINDOW_DAYS)]
    full_mask = (1 << WINDOW_DAYS) - 1

    stations = []
    st_index = {}

    def station_id(name):
        key = name.strip()
        if key not in st_index:
            st_index[key] = len(stations)
            stations.append(key)
        return st_index[key]

    # name|serving -> row under construction
    items = {}
    fetched = 0
    live_days = set()

    for day_i, day in enumerate(dates):
        for loc_i, tid in sorted(COMMONS_TIDS.items()):
            payload = get(FEED.format(tid=tid, date=day))
            if not payload:
                continue
            fetched += 1
            live_days.add(day_i)
            for meal, cats in payload.items():
                code = MEAL_CODES.get(meal.strip().lower())
                if not isinstance(cats, dict) or not code:
                    continue
                for cat, blob in cats.items():
                    sid = station_id(cat)
                    for m in ANCHOR.finditer(blob):
                        a = {k: unescape(v) for k, v in ATTR.findall(m.group(1))}
                        name = a.get("dish-name", "").strip()
                        if not name:
                            continue
                        serving = a.get("serving-size", "").strip()
                        key = name.lower() + "|" + serving.lower()
                        row = items.get(key)
                        if row is None:
                            diet = a.get("clean-diet-str", "").lower()
                            codes = sorted({c for word, c in DIET_CODES if word in diet})
                            row = {
                                "n": name, "s": serving,
                                "k": num(a.get("calories")),
                                "p": num(a.get("protein")),
                                "c": num(a.get("total-carb")),
                                "f": num(a.get("total-fat")),
                                "fi": num(a.get("dietary-fiber")),
                                "su": num(a.get("sugars")),
                                "sf": num(a.get("sat-fat")),
                                "tf": num(a.get("trans-fat")),
                                "ch": num(a.get("cholesterol")),
                                "na": num(a.get("sodium")),
                                "st": sid, "diets": "".join(codes),
                                "locs": set(), "meals": set(), "mask": 0,
                            }
                            items[key] = row
                        row["locs"].add(loc_i)
                        row["meals"].add(code)
                        row["mask"] |= 1 << day_i

    if fetched == 0:
        raise RuntimeError("feed returned nothing for any commons/date - refusing to write")

    # The feed only serves present and future dates. Between midnight and 4am
    # the current dining day is yesterday, which the feed will no longer hand
    # over, so reuse whatever the last build captured for those days rather
    # than shipping a window whose first day is empty.
    carried_days = []
    prev_by_date = {ds: i for i, ds in enumerate(prev["dates"])}
    for day_i, day in enumerate(dates):
        if day_i in live_days or day not in prev_by_date:
            continue
        src_bit = prev_by_date[day]
        recovered = 0
        for r in prev["rows"]:
            loc_ids = [int(x) for x in str(r[6]).split(",") if x != ""]
            if not any(i < commons for i in loc_ids):
                continue
            if not (r[10] >> src_bit) & 1:
                continue
            key = str(r[0]).lower() + "|" + str(r[1]).lower()
            row = items.get(key)
            if row is None:
                items[key] = {
                    "n": r[0], "s": r[1], "k": r[2], "p": r[3], "c": r[4], "f": r[5],
                    "fi": r[11], "su": r[12], "sf": r[13], "tf": r[14],
                    "ch": r[15], "na": r[16],
                    "st": station_id(prev["st"][r[8]]) if r[8] < len(prev["st"]) else station_id("Other"),
                    "diets": r[9],
                    "locs": set(loc_ids), "meals": set(str(r[7])), "mask": 1 << day_i,
                }
            else:
                row["locs"].update(loc_ids)
                row["meals"].update(str(r[7]))
                row["mask"] |= 1 << day_i
            recovered += 1
        if recovered:
            carried_days.append(f"{day} ({recovered})")

    rows = []
    for row in items.values():
        rows.append([
            row["n"], row["s"], row["k"], row["p"], row["c"], row["f"],
            ",".join(str(i) for i in sorted(row["locs"])),
            "".join(sorted(row["meals"])),
            row["st"], row["diets"], row["mask"],
            row["fi"], row["su"], row["sf"], row["tf"], row["ch"], row["na"],
        ])
    commons_count = len(rows)

    # Carry retail forward on its day-of-week pattern.
    prev_dates = prev["dates"]
    prev_dow = {}
    for i, ds in enumerate(prev_dates):
        mo, dy, yr = (int(x) for x in ds.split("/"))
        prev_dow.setdefault(date(yr, mo, dy).weekday(), []).append(i)
    new_dow = {}
    for i, ds in enumerate(dates):
        mo, dy, yr = (int(x) for x in ds.split("/"))
        new_dow.setdefault(date(yr, mo, dy).weekday(), []).append(i)

    retail = 0
    for r in prev["rows"]:
        loc_ids = [int(x) for x in str(r[6]).split(",") if x != ""]
        if any(i < commons for i in loc_ids):
            continue  # commons rows come from the live feed, not the old file
        served_dow = {
            dow for dow, idxs in prev_dow.items()
            if any((r[10] >> i) & 1 for i in idxs)
        }
        mask = 0
        for dow in served_dow:
            for i in new_dow.get(dow, []):
                mask |= 1 << i
        if not mask:
            continue
        out = list(r)
        out[8] = station_id(prev["st"][r[8]]) if r[8] < len(prev["st"]) else station_id("Other")
        out[10] = mask
        rows.append(out)
        retail += 1

    MENU.write_text(
        json.dumps(
            {"dates": dates, "locs": locs, "commons": commons, "st": stations, "rows": rows},
            separators=(",", ":"), ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(f"window      {dates[0]} -> {dates[-1]} ({WINDOW_DAYS} days)")
    print(f"feeds ok    {fetched}/{WINDOW_DAYS * len(COMMONS_TIDS)}")
    if carried_days:
        print(f"carried     {', '.join(carried_days)} (feed no longer serves these)")
    print(f"commons     {commons_count} rows")
    print(f"retail      {retail} rows carried forward")
    print(f"stations    {len(stations)}")
    print(f"total       {len(rows)} rows, {MENU.stat().st_size} bytes")
    if full_mask and commons_count == 0:
        print("WARNING: no commons rows parsed", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
