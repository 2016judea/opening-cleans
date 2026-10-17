# Opening Cleans

**Live:** https://opening-cleans.vercel.app

Minneapolis offices, clinics, gyms, daycares, shops and restaurants being built out
right now, by stage, from the city's building permits. A space at final inspection is
days from opening: it needs a post-construction clean, and then a cleaning contract.
The permit names the contractor building it, who usually hires that first clean.

For commercial cleaners. The first two it was built for named the work in their own
posts: Summit Pro Cleaning (offices, medical and dental, gyms, daycares, retail,
*"Move-in / move-out commercial cleaning"*) and Connect3 Cleaning Co. (*"Commercial
move-in and move-out cleaning"*).

## What's free, what's paid, and why

| free (on the page, no login) | paid ($5, once) |
|---|---|
| counts by stage and by space type; the map of every space | **every address** |
| 10 real rows at final inspection, with address, type, description and permit date | **the general contractor on each, with its address** |
| filter by space type | the sort by distance from your base, by stage (closest to opening), by job size |
| | the spreadsheet |

The free rows prove the list is real and current. What a cleaner acts on is *which of
these is near me, how close to opening, and who do I call*: that is the distance and
stage sorts and the contractor, so that is the wall.

## Price

**$5, once.** Set by Aidan on 2026-10-17 as a hypothesis under test. A tenth of one
use would be higher: one post-construction clean of a small office runs a few hundred
dollars, and the recurring contract after it several thousand a year. $5 tests whether
price is what stops a one-person cleaning business from buying at all. Revise on the
funnel: `preview_open`, `checkout_open`, `paid`, `unlock`.

## Data

`DATA_MODEL.md` has the ideal model and the field-by-field reality check. One source:
the City of Minneapolis building permit register (CCS_Permits, ArcGIS, live).
Commercial and mixed-use remodels, additions and new buildings from the last 14 months,
still open or closed in the last 60 days. Roofs, windows, signs, facades, doors and
apartments are filtered out (`EXCL`, `NOTRES` in `pipeline/build.py`). Not filled:
tenant contact, opening date, square feet. Minneapolis only; St. Paul stopped
publishing permits on 2025-06-30.

## The paywall

Same as unit-turns-mpls and buying-window. `site/` ships only the free slice;
`private/bundle/full.json.gz` is uploaded as `api/_full/` and read only by `/api/data`
(401 without a password, 402 unpaid). `POST /api/checkout` is Stripe embedded Checkout
at $5 and mints the password; `/api/stripe-webhook` emails it (Mailgun) and notifies
Aidan; `/api/session-status` is the return page. A lost password:
`python3 scripts/fulfil.py <session_id>`; a free copy: `--comp "<label>"`. Analytics:
Vercel Web Analytics + PostHog.

## Run it

```
python3 pipeline/pull.py && python3 pipeline/build.py
python3 scripts/build_for.py      # /for/<token>/ pages (local ledger)
python3 -m pytest -q tests
VERCEL_TOKEN=... python3 scripts/deploy.py
```

`site/index.html` is generated from `kit/template.html`.

## Licence

MIT. Minnesota public data may be reused and sold (AG op. 852, 1995).
