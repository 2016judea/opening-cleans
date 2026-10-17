# Data model — written before looking at the data (BUSINESS.md rule 5)

**The buyer:** a commercial cleaner who wants recurring contracts and move-in cleans
(Summit Pro Cleaning: offices, medical and dental, gyms, daycares, retail, *"Move-in /
move-out commercial cleaning"*; Connect3 Cleaning Co.: *"Commercial move-in and move-out
cleaning"*). **The question:** which commercial spaces near me are about to open, so I
can win the post-construction clean and then the weekly contract before anyone else is
hired?

## Ideal model

**Space**
| field | answers |
|---|---|
| address, lat/lon | where; distance from my base |
| space type (office, medical/dental, gym, daycare, retail, restaurant, other) | does it fit what I clean |
| stage (under construction, at final inspection, just finished) | when the clean is needed |
| expected opening date | when to call |
| size (sq ft) | how big the contract is |
| tenant business name | who the customer is |
| tenant contact | who signs the cleaning contract |
| general contractor + contact | who hires the post-construction clean |
| description of the work | what kind of mess |

## Reality check (2026-10-17)

| field | source | filled? |
|---|---|---|
| address, lat/lon, description | Minneapolis building permits (CCS_Permits, live) | yes |
| space type | keyword read of the permit description | yes, approximate; unmatched rows say "other commercial space" |
| stage | permit status + milestone ("Final Inspection" = the last step before opening) | yes |
| general contractor, its address | permit applicant (company names only) | yes, address only, no phone |
| size | permit fee (rises with job value; the city publishes no square feet or value) | proxy only |
| expected opening date | none | **no**; final inspection stands in |
| tenant business name | free text, unreliable to parse (wrong 3 of 4 times on 9/28) | **no**; the description is shown raw instead |
| tenant contact | none | **no** |

**Call:** build. Stage is the timing signal and the contractor is the near-term buyer of
the post-construction clean. Tenant name and contact can't be filled; the page says so,
and the description is shown raw so the cleaner can read the tenant off it where the
permit names one. Minneapolis only: St. Paul stopped publishing permits on 2025-06-30.
