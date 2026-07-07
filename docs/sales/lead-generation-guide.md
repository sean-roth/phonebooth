# Lead Generation Guide — Stocking the Shelf

**Status:** Source of truth for building the night-before dial list. Any Claude session (typically Opus, evenings) executes this guide. The `stock-the-shelf` skill points here.
**Governing scope:** The latest GTM amendment in Drive (`gtm-amendment-YYYY-MM-DD`) always overrides the inline scope below. Check it first. Inline scope current as of 2026-07-07 (DR-2026-07-06-03).
**Cage:** This is an evening task. Never runs during a dial window. Timebox: 30–45 minutes.

---

## Purpose

Produce tomorrow's cold-call list so the morning never starts with an empty shelf. The list is fuel for a proven system — the dial blocks are validated; this guide automates their supply, not their judgment.

## Current target profile (inline scope — verify against latest amendment)

**Segment:** Small and medium manufacturers, ~20–150 employees.
**Geography:** Chicago metro industrial corridors — Elk Grove Village, Bensenville, Franklin Park, Addison, Wood Dale, Schiller Park, Melrose Park, Northlake, Carol Stream, Cicero, Bedford Park, McCook, Alsip, Broadview, and similar. (Elk Grove Village alone is one of the largest industrial parks in North America — it can fuel weeks of lists.)
**Categories that count as manufacturing:** machine shops, CNC machining, metal fabrication, sheet metal, stamping, tool & die, plastics / injection molding, food processing and packaging, job shops, wire forming, welding & fab shops, precision grinding, industrial finishing.

## Hard exclusions (skip, no exceptions)

- **Chemical manufacturers** and anything with a visible OSHA-citation history — deeply safety-tagged engagements excluded until the Durability Standard's safety pipeline exists (counsel, SME review). Do not deep-research every lead for this; act only on what surfaces in the listing or an obvious news hit.
- **Fortune-500 branch plants / national brands** — the flincher and the checkbook must share a wall.
- **Distributors, wholesalers, 3PLs, staffing agencies** mislabeled as manufacturing.
- **Anything with no phone number in the listing.** Every number must trace to the listing — numbers are never inferred, reconstructed, or pulled from memory. A lead without a listed number is a skip, not a research project.

## Size and quality proxies (Maps has no employee counts — triangulate, max 2 minutes per lead)

- Review count roughly 3–60: enough to be real, few enough to be SMB. Zero reviews = higher dead-number risk; 200+ = probably too big or consumer-facing.
- Single location. "Family owned," "since 19XX," founder names on the website — all good signs.
- A modest, slightly dated website is a *positive* signal for this buyer. A slick multi-location site with a careers portal is a size red flag.
- Recent reviews or photos (≤ ~12 months) — best available proxy that the line is live. **Known limitation: no listing data can verify a phone line. Expect some dead numbers anyway; the only real test is a ring.**

## Method

Google Maps queries, worked corridor by corridor. Example query set (vary the corridor):
- `machine shop Elk Grove Village IL`
- `metal fabrication Bensenville IL`
- `injection molding Addison IL`
- `food processing Franklin Park IL`
- `CNC machining Wood Dale IL`
- `tool and die Melrose Park IL`

For each candidate: check category, review count/recency, website in one glance, apply exclusions, keep or skip. When uncertain, **keep with a `?` flag** — uncertain rows are Sean's 30-second morning skim, not the model's silent judgment call.

## Output format (tracker-ready)

12–15 keeps, as a table:

| # | Company | Phone | City | Category | Size proxy | Note |
|---|---------|-------|------|----------|-----------|------|

- **Row 1 is the seal-breaker:** the lowest-stakes keep on the list (smallest shop, least-ideal fit) — per the runbook, the first dial exists to break the seal, not to win.
- Notes are one line: anything useful for the call ("family owned since '82", "reviews mention fast turnaround", "? — might be distributor").
- Times: leads are Central Time; Sean dials from Mountain Time. No best-window research needed — SMB shops answer during business hours.

## Definition of done

The table above, plus a three-line summary: queries run, kept / skipped / flagged counts, and any pattern noticed ("Bensenville plastics heavily consolidated — mostly big players"). Nothing else. **Never contact anyone — no calls, no emails, no form fills. This task produces a list; humans do the talking.**
