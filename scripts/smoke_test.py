"""Pre-deploy smoke test for the Gainz Quest app.

Checks only that the published bundle is internally consistent. It never
modifies the app; a failure here means the bundle would be broken in prod.
"""
import datetime
import json
import re
import struct
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

APP = Path(__file__).resolve().parent.parent / "gq-app"
failures = []


def fail(msg):
    failures.append(msg)
    print(f"FAIL  {msg}")


def ok(msg):
    print(f"ok    {msg}")


def png_size(path):
    with open(path, "rb") as fh:
        head = fh.read(33)
    return struct.unpack(">II", head[16:24])


index = APP / "index.html"
if not index.is_file() or index.stat().st_size == 0:
    fail("gq-app/index.html is missing or empty")
    sys.exit(1)
html = index.read_text(encoding="utf-8")
ok(f"index.html present ({len(html)} bytes)")

# menu.json must parse and carry a usable date range
menu_path = APP / "menu.json"
try:
    menu = json.loads(menu_path.read_text(encoding="utf-8"))
    dates = menu["dates"]
    if not dates:
        fail("menu.json has no dates")
    else:
        ok(f"menu.json parses, {len(dates)} days: {dates[0]} -> {dates[-1]}")
        ok(f"menu.json has {len(menu['rows'])} rows across {len(menu['locs'])} locations")
except Exception as exc:  # noqa: BLE001
    fail(f"menu.json unreadable: {exc}")
    dates = []

# The menu feed is rebuilt nightly; a window that no longer reaches the
# current dining day is the failure that silently empties every boss.
# Uses the app's 4am rollover (index.html questNow) so the two agree.
now = datetime.datetime.now(ZoneInfo("America/New_York")) - datetime.timedelta(hours=4)
today = f"{now.month:02d}/{now.day:02d}/{now.year}"
if dates:
    if today in dates:
        ahead = len(dates) - dates.index(today) - 1
        ok(f"menu covers today ({today}), {ahead} day(s) of runway after it")
        if ahead < 2:
            fail(f"only {ahead} day(s) of menu left after today - rerun scripts/fetch_menus.py")
    else:
        fail(f"menu has no entry for today ({today}); window is {dates[0]} -> {dates[-1]}")

# PWA surface
manifest_path = APP / "manifest.webmanifest"
try:
    mf = json.loads(manifest_path.read_text(encoding="utf-8"))
    missing = [k for k in ("name", "start_url", "display", "icons") if not mf.get(k)]
    if missing:
        fail(f"manifest.webmanifest missing: {', '.join(missing)}")
    else:
        ok(f"manifest.webmanifest ok ({mf['display']}, {len(mf['icons'])} icons)")
    for icon in mf.get("icons", []):
        if not (APP / icon["src"]).is_file():
            fail(f"manifest icon missing: {icon['src']}")
except Exception as exc:  # noqa: BLE001
    fail(f"manifest.webmanifest unreadable: {exc}")

if (APP / "sw.js").is_file():
    ok("sw.js present")
else:
    fail("sw.js missing")

for tag in ('rel="manifest"', 'name="viewport"', "serviceWorker"):
    if tag in html:
        ok(f"index.html wires up {tag}")
    else:
        fail(f"index.html is missing {tag}")

# Every local asset the page references must actually ship
refs = set(re.findall(r"""['"(]([A-Za-z0-9_./-]+\.(?:png|json|wav|woff2))['")]""", html))
for ref in sorted(refs):
    if ref.startswith(("http:", "https:", "//")):
        continue
    if (APP / ref).is_file():
        ok(f"asset {ref}")
    else:
        fail(f"referenced asset missing: {ref}")

# Boss sprite sheets must match the frame height the CSS lays out with.
# The art pipeline can emit 84px-tall sheets once hats are added; shipping
# those without updating .bossspr would misalign every boss animation.
css_h = re.search(r"\.bossspr\{[^}]*?height:calc\((\d+)px", html)
if not css_h:
    fail("could not find .bossspr frame height in index.html")
else:
    expected = int(css_h.group(1))
    ok(f".bossspr expects {expected}px frames")
    sheets = re.findall(r"src:'([a-z_]+\.png)',fw:(\d+)", html)
    if not sheets:
        fail("could not find SHEETS sprite declarations")
    for src, fw in sheets:
        path = APP / src
        if not path.is_file():
            fail(f"sprite sheet missing: {src}")
            continue
        w, h = png_size(path)
        if h != expected:
            fail(f"{src} is {w}x{h}, but .bossspr lays out {expected}px frames")
        elif w % int(fw) != 0:
            fail(f"{src} width {w} is not a whole number of {fw}px frames")
        else:
            ok(f"{src} {w}x{h} = {w // int(fw)} frames of {fw}x{h}")

print()
if failures:
    print(f"{len(failures)} check(s) failed")
    sys.exit(1)
print("all checks passed")
