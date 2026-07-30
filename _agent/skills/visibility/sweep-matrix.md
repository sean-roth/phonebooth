# Sweep matrix — Chicago metro, residential trades

Corridor × trade. Mark slices worked-out as they thin.

## Two rules that govern this matrix

**Season, not preference.** The best time to reach a seasonal contractor is
six to ten weeks before his season starts: reachable because he is not yet
slammed, motivated because the rush is visible. Out-of-season trades are
skipped entirely, not deprioritized.

**Second ring, not the city.** Chicago proper is saturated with agencies and
the profiles are already built. The far exurbs run thin on money. The band
between them is the target.

## Corridors

| Code | Area | Towns |
|---|---|---|
| NW | McHenry / NW Cook | Crystal Lake, McHenry, Woodstock, Huntley, Algonquin, Cary, Lake in the Hills, Barrington |
| N | Lake County | Libertyville, Mundelein, Grayslake, Wauconda, Antioch, Lake Zurich, Round Lake |
| W | Kane / west DuPage | Elgin, St. Charles, Geneva, Batavia, Wheaton, Carol Stream |
| SW | Will / SW Cook | Joliet, Plainfield, New Lenox, Frankfort, Orland Park, Tinley Park |
| NDP | Near DuPage | Addison, Bensenville, Wood Dale, Itasca, Elmhurst, Lombard, Glen Ellyn |

NDP overlaps the SOPs manufacturing corridors. Different buyer entirely —
residential contractors, not shops — but expect more dedup hits there.

## Trades by season

Current date governs which block is live. Check it before sweeping.

### Live in August–October
| Trade | Season | Why now |
|---|---|---|
| Chimney sweep / fireplace | Sep–Nov | Quiet now, slammed in six weeks. Rarely agency-touched. |
| Gutter install & cleaning | Oct–Nov | Leaf season. Same pattern. |
| Snow removal | Contracts signed Aug–Oct | **Sharpest slice on this list.** They are thinking about it right now and nobody is calling them. |
| Interior painting | Oct–Feb | Work moves indoors in fall. |
| Garage doors | Nov–Feb | Springs break in the first hard freeze. |
| Duct cleaning | Sep–Nov | Rides the heating-season wave. |

### Hold until September
| Trade | Why wait |
|---|---|
| HVAC | Peak AC season — they will not answer. Also the most agency-saturated trade in the country. Approach for the heating side in September. |
| Water heaters / plumbing | Heavily marketed. Low priority regardless of season. |

### Hold until late winter / spring
Roofing (storm season now, and storm-chaser marketing has saturated it),
concrete and masonry, landscaping and hardscape, decks and fences, driveway
sealing, window and siding, pressure washing.

### Year-round, no season gate
Handyman, appliance repair, drywall, epoxy flooring, junk removal, septic,
well service, insulation, waterproofing.

## Queue

Work top to bottom. Mark `worked-out` when a slice returns mostly dupes,
franchises, or 100+ review shops.

| # | Corridor | Trade | Status |
|---|---|---|---|
| 1 | NW | Chimney sweep | |
| 2 | NW | Snow removal | |
| 3 | N | Chimney sweep | |
| 4 | N | Snow removal | |
| 5 | NW | Gutters | |
| 6 | W | Chimney sweep | |
| 7 | N | Gutters | |
| 8 | SW | Snow removal | |
| 9 | W | Snow removal | |
| 10 | NW | Garage doors | |
| 11 | W | Gutters | |
| 12 | N | Garage doors | |
| 13 | SW | Chimney sweep | |
| 14 | NDP | Gutters | |
| 15 | W | Interior painting | |
| 16 | SW | Gutters | |
| 17 | NW | Duct cleaning | |
| 18 | N | Interior painting | |
| 19 | SW | Garage doors | |
| 20 | NDP | Chimney sweep | |

A slice is roughly one `maps_search_places` query per town in the corridor.
Expect 3–8 keepers per slice; below three, the slice is thin.
