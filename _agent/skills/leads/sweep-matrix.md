# Sweep matrix — metro × corridor × category

The queue the lead agent advances through. One run takes the next few UNWORKED
slices, sources them, and (if a slice comes back mostly dupes and sub-50 shops)
marks it worked-out. Revisit worked-out slices only after a long gap — new shops
appear, and the dedup store prevents re-listing old ones.

## Categories (apply to every corridor)
machine shop / CNC · screw machining · metal fabrication · sheet metal · metal
stamping · tool & die · injection molding / plastics · springs & wire forming ·
precision grinding · industrial finishing (B2B) · food processing & packaging ·
welding & fabrication (B2B)

## Metro 1 — Chicago (WORK FIRST)
Corridors:
- Elk Grove Village, Bensenville, Wood Dale, Addison, Itasca
- Franklin Park, Schiller Park, Melrose Park, Northlake, Stone Park, Bellwood
- Broadview, Hillside, Bedford Park, McCook, Summit, Cicero, Berwyn
- Des Plaines, Mt Prospect, Arlington Heights, Niles, Skokie, Morton Grove
- Elgin, South Elgin, Carol Stream, Bloomingdale, Glendale Heights
- Alsip, Bridgeview, Chicago city (Clearing, Archer Heights, Pilsen, Ravenswood
  industrial)

Status note (as of 2026-07-12): batches worked Elk Grove Village, Bensenville,
Wood Dale, Addison, Franklin Park, Schiller Park, and Melrose Park heavily
(machining, stamping, tool & die, molding, springs, grinding). Still fresh: the
south/southwest (Bedford Park, Cicero, Bridgeview, Alsip), Chicago city
industrial, and food processing OUTSIDE the Bedford Park/Summit corridor (which
skews national — Ingredion / ACH / Argo).

## Metro 2 — Detroit (WORK SECOND)
Corridors (Macomb / Oakland / Wayne supplier belt):
- Warren, Sterling Heights, Center Line, Roseville, Fraser, Clinton Twp,
  Madison Heights, Hazel Park, Ferndale
- Troy, Auburn Hills, Rochester Hills, Farmington Hills, Novi, Wixom
- Livonia, Plymouth, Canton, Redford, Romulus, Taylor, Dearborn, Wyandotte

Notes: automotive-supplier machine shops, stamping, tool & die, and molding are
extremely dense here (Warren / Sterling Heights especially). Same ICP — a
120-person stamping shop in Warren qualifies exactly like one in Melrose Park.

## Long-term rings (only when 1 & 2 genuinely thin)
Milwaukee / Waukesha · Grand Rapids (furniture, plastics) · Rockford (aerospace
machining) · Cleveland / Akron (rubber, polymers) · Toledo · Fort Wayne ·
Columbus · Cincinnati / Dayton · Indianapolis · Kalamazoo

## How to record progress
Keep a simple worked-slices log — the `swept_slices` table in `../../data/`
(see `schema.sql`), or a checklist here. Mark "<corridor> × <category>" done
with a date when a sweep of it returns mostly dupes/sub-50. The dedup store is
the real memory; this list is the human's map of the territory.
