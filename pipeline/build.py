#!/usr/bin/env python3
"""Build Opening Cleans: Minneapolis commercial spaces about to open, for commercial cleaners.

Input: pipeline/cache/permits.json (pull.py, Minneapolis CCS_Permits, live).
Writes site/index.html + site/data/free.json (free slice) and private/bundle/full.json.gz
via kit/publish.py. Every number on the page is computed here.
"""
import collections, datetime as dt, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "kit"))
from publish import esc, publish  # noqa: E402

PRODUCT = json.loads((ROOT / "product.json").read_text())
# The page says "pulled <date>": the day pull.py wrote the cache, not the day this script ran,
# so a rebuild never moves the 60-day window or the "issued since" month off the data.
TODAY = dt.date.fromtimestamp((ROOT / "pipeline/cache/permits.json").stat().st_mtime)
JUST_DAYS = 60  # "just finished" = closed in the last 60 days: the space is opening or open
D = lambda x: dt.datetime.fromtimestamp(x / 1000, dt.timezone.utc).date() if x else None

# Work that never makes a space to clean (mpls-permits skill: keyword filters over-match, so exclude explicitly)
EXCL = re.compile(r"water damage|fire damage|vehicle damage|roof|solar|window|parking|\bsign\b|signage|fire barrier|sprinkler|elevator|balcon|"
                  r"fa[cç]ade|masonry|tuckpoint|not a building permit|antenna|cell tower|telecom|monopole|demo only|demolition only|retaining wall|"
                  r"canopy|fence|foundation repair|stucco|siding|guardrail|rooftop unit|\brtu\b|generator|\btank\b|ramp|deck\b|patio|"
                  r"revision after issuance|replace [\w\s'-]{0,25}doors?\b|\bunit #?\d|bedroom|bath(room)? remodel|primary bath|water tower|vehicle impact|playground|\bsfd\b|assisted living|housing for|remodel shower|insulation and drywall|storefront|shaft ?wall|cladding|data closet|shell only|stair(way)? addition|"
                  r"re-?anchor|structural repair|fire escape|bleacher|parking ramp|cooling tower|chimney", re.I)
NOTRES = re.compile(r"townho|dwelling|apartment|condo|residential unit|-unit \d|\bunit \d+ kitchen|\bR-?2\b occupancy", re.I)
# A space someone will move into: build-out language, a change of occupancy, or a named use
FITOUT = re.compile(r"tenant|build ?-?out|remodel|renovat|interior|alteration|change of (use|occupancy)|finish|fit[- ]?out|new (store|restaurant|clinic|office|cannabis|business)|"
                    r"first (build|occupancy)|certificate of occupancy required:?\s*(-\s*)?yes|expansion|conver", re.I)
TYPES = [("Medical or dental", r"clinic|dental|dentist|medical|health|therapy|chiropract|optometr|vision|pharmacy|urgent care|hospital|surgery|dialysis|veterinar|laborator"),
         ("Daycare or school", r"daycare|day care|child ?care|preschool|montessori|early learning|school|classroom|learning center|academy|tutoring"),
         ("Gym or studio", r"\bgym|fitness|yoga|pilates|crossfit|martial|dance|climbing|boxing|training (studio|facility)|barre|cycle studio|soccer"),
         ("Restaurant or bar", r"restaurant|cafe|café|coffee|\bbar\b|brewery|taproom|bakery|pizza|tavern|kitchen|food hall|dining|\bdeli\b"),
         ("Retail", r"retail|\bstore\b|\bshop\b|boutique|grocery|market\b|dispensary|cannabis|cannibis|salon|barber|\bspa\b|showroom|gallery|\bnail|tattoo|florist|mercantile"),
         ("Office", r"floors? \d|\d+(st|nd|rd|th) floor|office|\bsuite\b|corporate|\bbank\b|credit union|law firm|cowork|conference|workspace|call center|headquarters")]
ORDER = ["Office", "Medical or dental", "Gym or studio", "Daycare or school", "Retail", "Restaurant or bar", "Other commercial space"]
STAGES = ["At final inspection", "Just finished", "Under construction"]
CUT = re.compile(r"\s*(certificate of occupancy|const\.? type|building code|energy code|construction documents|special inspection|occupancy:|number of stories|"
                 r"2020 m[sn]bc|engineer:|architect:|sprinkler|shell permit|note:|\(maa\)|\(jjl\)|\(acw\)|-acw|\(sck\)|sck\b|contact|\(same work|"
                 r"mechanical permit|prior to receiving|separate pe|all exiting|0 sac).*", re.I | re.S)
BIZ = re.compile(r"\b(INC|LLC|L\.L\.C|CORP|CORPORATION|CO|COMPANY|CONST|CONSTRUCTION|BUILD|BUILDERS|BUILDING|HOMES|REMODEL|REMODELING|DESIGN|GROUP|"
                 r"PROPERT\w*|DEVELOP\w*|CONTRACT\w*|SERVICES|RENOVAT\w*|ARCHITECT\w*|STUDIO|ENTERPRISES|INTERIORS|COMPANIES|PARTNERS|LTD|SOLUTIONS|MECHANICAL)\b", re.I)


def kind(c):
    for k, p in TYPES:
        if re.search(p, c, re.I):
            return k
    return "Other commercial space"


def what(s):
    s = (s or "").strip()
    if s.lower().startswith("source information"):
        return ""
    s = re.sub(r"^\(DMH[^)]*\)\s*", "", s)
    s = CUT.sub("", s)
    s = re.sub(r"\s+", " ", s).strip(" .-;,")
    if s.isupper():
        s = s.capitalize()
    return s[:180]


def title(s):
    out = []
    for w in (s or "").split():
        if re.match(r"^\d+(st|nd|rd|th)$", w, re.I): out.append(w.lower())
        elif re.match(r"^(\d|[NSEW]{1,2}$|LLC$|INC\.?$|II$)", w, re.I): out.append(w.upper())
        else: out.append(w.capitalize())
    return " ".join(out)


def company(n):
    n = (n or "").strip()
    return title(n).replace(" Llc", " LLC").replace(" Inc", " Inc") if n and BIZ.search(n) else ""


rows, seen = [], set()
for x in json.loads((ROOT / "pipeline/cache/permits.json").read_text()):
    c = x["comments"] or ""
    if x["occupancyType"] not in ("Comm", "Mixed") or x["workType"] not in ("Remodel", "New", "Addition"):
        continue
    if x["status"] in ("Cancelled", "Expired", "In Process") or not x["Latitude"] or EXCL.search(c) or NOTRES.search(c):
        continue
    k = kind(c)
    if k == "Other commercial space" and not FITOUT.search(c):
        continue
    key = (x["Display"], c[:80])
    if key in seen:
        continue
    seen.add(key)
    if x["status"] == "Closed":
        cd = D(x["completeDate"])
        if not cd or (TODAY - cd).days > JUST_DAYS:
            continue
        st = "Just finished"
    elif x["milestone"] == "Final Inspection":
        st = "At final inspection"
    else:
        st = "Under construction"
    issued, done = D(x["issueDate"]), D(x["completeDate"])
    gc = company(x["applicantName"])
    gca = title(" ".join(filter(None, [x.get("applicantAddress1"), x.get("applicantCity")]))) if gc else ""
    fee = round(x["totalFees"] or 0)
    addr = title(x["Display"])
    w = what(c)
    rows.append({
        "id": x["permitNumber"], "g": k, "t": addr, "tag": st, "hot": st == "At final inspection",
        "w": w,
        "m": [k, x["Neighborhoods_Desc"] or "", f"Permit {issued:%b %-d, %Y}", f"Finished {done:%b %-d}" if st == "Just finished" and done else "", f"Permit fee ${fee:,}"],
        "lat": round(x["Latitude"], 5), "lon": round(x["Longitude"], 5),
        "k": {"newest": -int(issued.strftime("%Y%m%d")), "stage": STAGES.index(st), "size": -fee},
        "c": (f"Contractor: <b>{esc(gc)}</b>" + (f" · {esc(gca)}" if gca else "")) if gc else "No contractor company named on the permit",
        "csv": [[st, k, addr, x["Neighborhoods_Desc"] or "", w, gc, gca, issued.isoformat(), done.isoformat() if done and st == "Just finished" else "", fee, x["permitNumber"]]],
        "_issued": issued,
    })

for r in rows:
    r.pop("_issued")
gc_ = collections.Counter(r["g"] for r in rows)
sc = collections.Counter(r["tag"] for r in rows)
named = sum(r["g"] in ("Office", "Medical or dental", "Gym or studio", "Daycare or school", "Retail") for r in rows)
# free sample: the newest at final inspection, one or two per type, so every chip has a real row
free_items, per = [], collections.Counter()
for r in sorted(rows, key=lambda r: (STAGES.index(r["tag"]), r["k"]["newest"])):
    if per[r["g"]] < 2 and len(free_items) < 10:
        per[r["g"]] += 1
        free_items.append({**{k: v for k, v in r.items() if k not in ("c", "csv", "rows")}, "rows_locked": "Contractor and its address in the full list"})
points = [[round(r["lat"], 3), round(r["lon"], 3), r["g"]] for r in rows]
built = TODAY.isoformat()
free = {
    "built": built,
    "eyebrow": f"Opening Cleans · Minneapolis building permits · built {TODAY:%b %-d, %Y}",
    "h1": f"{sc['At final inspection']} Minneapolis commercial spaces at final inspection right now",
    "lede": (f"A build-out needs a post-construction clean before the doors open, and a cleaning contract after. "
             f"These are the Minneapolis offices, clinics, gyms, daycares, shops and restaurants being built out now. "
             f"<b>{sc['At final inspection']} are at final inspection</b>, the last step before opening; {sc['Just finished']} finished in the last {JUST_DAYS} days "
             f"and {sc['Under construction']} are still under construction."),
    "stats": [[str(len(rows)), "commercial build-outs open or just finished"], [str(sc["At final inspection"]), "at final inspection now"],
              [str(named), "offices, clinics, gyms, daycares and shops"]],
    "pay_h": f"The full list: all {len(rows)} spaces, and who's building them",
    "pay_line": ("Every address, the general contractor and its address (they hire the post-construction clean), the sort by distance "
                 "from your base, the sort by stage and by job size, and the spreadsheet."),
    "checkout_line": f"{len(rows)} Minneapolis commercial build-outs by stage and space type, with the contractor on each.",
    "noun": "spaces",
    "ghost": "1234 Example Ave S · Contractor: Example Builders Inc · 555 Main St",
    "total": len(rows),
    "group_counts": {g: gc_[g] for g in ORDER},
    "group_order": ORDER,
    "legend": [["Office", "var(--c1)"], ["Medical or dental", "var(--c2)"], ["Gym or studio", "var(--c3)"], ["Daycare or school", "var(--c4)"],
               ["Retail", "var(--c5)"], ["Restaurant or bar", "var(--c6)"], ["Other commercial space", "var(--mid)", "Other"]],
    "points": points,
    "sorts": [{"key": "newest", "label": "Newest permit"}, {"key": "stage", "label": "Closest to opening", "paid": True},
              {"key": "near", "label": "Closest to", "near": True, "paid": True}, {"key": "size", "label": "Biggest job (permit fee)", "paid": True}],
    "origins": [["Brooklyn Park", 45.0941, -93.3563], ["Saint Paul", 44.9537, -93.0900], ["Downtown Minneapolis", 44.9778, -93.2650],
                ["Bloomington", 44.8408, -93.2983], ["Roseville", 45.0061, -93.1566], ["Edina", 44.8897, -93.3499], ["Anoka", 45.1977, -93.3872]],
    "csv_cols": ["stage", "space type", "address", "neighborhood", "permit description", "contractor", "contractor address", "permit issued", "finished", "permit fee", "permit"],
    "items": free_items,
    "note": (f"<p>Source: City of Minneapolis building permit register (CCS_Permits), pulled {built}. Commercial build-outs, remodels, additions and new "
             f"buildings in commercial and mixed-use buildings issued since {(TODAY - dt.timedelta(days=425)):%b %Y}, still open or finished in the last {JUST_DAYS} days. "
             f"Roofs, windows, signs, facades, doors and other work that leaves no space to clean are left out, as are apartments and condos.</p>"
             f"<p>Space type is read from the permit description, so some rows land in Other. The permit names the contractor, not the tenant; the description "
             f"often names the business. The city publishes no square footage or job value, so the permit fee stands in for size. Minneapolis only: "
             f"St. Paul stopped publishing permits in mid-2025.</p><p>Made by Aidan Jude at Brick &amp; Mortar (aidan@brickandmortar.dev).</p>"),
}
publish(ROOT, PRODUCT, free, {"items": rows})
print(f"spaces {len(rows)} · stages {dict(sc)} · types {dict(gc_)} · named-type {named} · with contractor {sum('<b>' in r['c'] for r in rows)}")
