#!/usr/bin/env python3
"""Pull Minneapolis building permits (CCS_Permits, live) into pipeline/cache/permits.json (gitignored).
Commercial permits issued in the last 14 months, every field."""
import datetime as dt, json, urllib.parse, urllib.request
from pathlib import Path

C = Path(__file__).resolve().parent / "cache"
C.mkdir(exist_ok=True)
U = "https://services.arcgis.com/afSMGVsC7QlRK1kZ/arcgis/rest/services/CCS_Permits/FeatureServer/0/query"
since = (dt.date.today() - dt.timedelta(days=425)).isoformat()
where = f"permitType='Commercial' AND issueDate >= date '{since}'"
rows, off = [], 0
while True:
    p = urllib.parse.urlencode(dict(where=where, outFields="*", f="json", resultOffset=off, resultRecordCount=2000, orderByFields="issueDate DESC", returnGeometry="false"))
    d = json.load(urllib.request.urlopen(U + "?" + p))
    fs = [f["attributes"] for f in d["features"]]
    rows += fs
    if not d.get("exceededTransferLimit") or not fs:
        break
    off += len(fs)
(C / "permits.json").write_text(json.dumps(rows))
print("permits", len(rows), "since", since)
