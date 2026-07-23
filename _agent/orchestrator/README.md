# orchestrator — the lead-gen pipeline

Implements the workflow in `../skills/leads/SKILL.md`: sweep a queue of Midwest
metro/corridor/category slices, source from Google Maps, drop duplicates,
qualify each lead with Sonnet against `../skills/leads/qualification-prompt.md`,
scrub dead numbers with Twilio Lookup, and write callable leads to a dated CSV
(and optionally append to the live Google Sheet).

**Code orchestrates; the model only judges one lead at a time.** Sourcing,
dedup, scrubbing, and output are plain Python. Sonnet is called once per
surviving lead and returns strict JSON. That split is what keeps it cheap and
reliable at volume.

## Install
```
pip install -r requirements.txt
```

## Configure (environment / .env)
| Var | Purpose |
|---|---|
| `GOOGLE_MAPS_API_KEY` | Places API (New) key — Places API enabled + billing on |
| `ANTHROPIC_API_KEY` | the qualification calls |
| `QUALIFY_MODEL` | your current Sonnet model string (default `claude-sonnet-5`) |
| `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN` | Lookup; optional (scrub is skipped if unset) |
| `SLICES_PER_RUN` | productive corridor×category slices per run (default 6) |
| `MAX_PER_SLICE` | Maps results per slice (default 10) |
| `REVISIT_AFTER_DAYS` | rest window before a worked-out/empty slice is sweepable again (default 180) |
| Sheets (optional) | `SHEETS_ENABLED=true`, `SHEETS_SPREADSHEET_ID`, `SHEETS_WORKSHEET`, `SHEETS_REVIEW_WORKSHEET` |
| Sheets auth | **OAuth, not a service-account key** — `GSPREAD_CREDENTIALS` (Desktop-app client-secrets JSON), `GSPREAD_TOKEN` (cached token). Leave both unset to use gspread's defaults. |

Without Sheets configured it always writes `output/leads-YYYY-MM-DD.csv`, which
you paste into your tracker — same as the manual batches.

## First run
1. **Seed the dedup store** from the existing tracker so hand-built batches
   aren't re-sourced as fresh leads: export the Sheet tab(s) to CSV, then
   `python seed.py tracker-export.csv`. Safe to re-run.
2. **Leave `SHEETS_ENABLED=false` for the first run.** Eyeball the CSV, paste
   it into the tracker, and confirm the columns line up before turning the
   append on — `append_sheet` assumes the worksheet's columns match
   `sink.COLUMNS` in order, and the default tab name is "Manufacturer Leads"
   (set `SHEETS_WORKSHEET` to the real tab name).
3. **Expect the review section to be short.** If a whole batch lands in
   review, something upstream broke — API failures route there by design
   rather than killing the run.

## Run
```
python run.py
```
Each run advances through the sweep queue, skips slices marked worked-out or
empty within the last `REVISIT_AFTER_DAYS`, and stops after `SLICES_PER_RUN`
productive slices (hard cap: 3× that on total sweeps, so a dead stretch of the
queue can't burn unlimited Maps calls). A failed qualification call routes that
lead to the review pile instead of killing the run; a failed Maps call stops
the sweep early and delivers what's already gathered. State (seen leads, swept
slices) lives in the SQLite DB from `../data/schema.sql`.

Qualification decisions: `keep` (callable, H/M/L ordered), `reject` (dropped,
remembered), `review` (a genuine judgment call — goes to the review tab/section
for a human, never to the callable list).

## Modules
- `config.py` — env/config
- `slices.py` — the sweep queue (edit to expand territory; mirrors `sweep-matrix.md`)
- `maps.py` — Places API (New) text search + field mask
- `dedup.py` — SQLite seen-leads + swept-slices (with the re-sweep rest window)
- `seed.py` — one-time load of hand-built tracker rows into the dedup store
- `qualify.py` — Sonnet per-lead qualification (loads the committed prompt)
- `scrub.py` — Twilio Lookup
- `sink.py` — CSV writer + optional Google Sheets append (OAuth)
- `run.py` — the orchestrator loop

## Cost notes
- **Maps: ~1,000 free searches/month, not 10,000.** Google bills per SKU and
  charges at the highest tier any requested field belongs to. The field mask
  requests `nationalPhoneNumber`, `websiteUri`, `rating`, `userRatingCount`,
  and `regularOpeningHours` — all of which trigger **Text Search Enterprise** —
  plus `reviews`, which pushes it to **Enterprise + Atmosphere**. Enterprise
  SKUs get 1K free calls/month; the advertised 10K is the Essentials figure.
  One search = one billable call returning up to 20 businesses, so ~6 slices a
  run, daily, is ~180 calls/month. Comfortably free.
- **Do NOT drop `reviews.text` to save money.** Dropping it moves the request
  from Enterprise + Atmosphere down to Enterprise — *still the same 1K bucket*,
  because `nationalPhoneNumber` alone triggers Enterprise and there is no call
  list without phone numbers. You would lose the single best qualification
  signal (owner names, B2B-vs-consumer tells) for zero saving at this volume.
- Set a **daily quota cap** on Places API in the Cloud console. A billing
  budget only alerts after the fact; the quota is the actual hard stop.
- Sonnet: one short call per surviving lead; cents per hundred leads.
  (Sonnet 5 note: `effort` defaults to high on the API — low is plenty for a
  keep/reject judgment and cuts latency/cost, if the installed SDK supports
  setting it.)
- Twilio Lookup: fractions of a cent per number.

## Where Claude Code should extend
- Retries/backoff on the Maps and Anthropic calls. (An errored qualify already
  falls through to review; an errored Maps call stops the sweep early and
  delivers what's gathered.)
- Batch qualification (multiple leads per Sonnet call) if volume climbs.
- Firecrawl size-check on H-tier leads before output (see SKILL.md).
- A CLI (choose metro, dry-run, slice range) and a scheduled cron entry.
