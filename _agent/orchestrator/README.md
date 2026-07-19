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
| `SLICES_PER_RUN` | corridor×category slices per run (default 6) |
| `MAX_PER_SLICE` | Maps results per slice (default 10) |
| Sheets (optional) | `SHEETS_ENABLED=true`, `SHEETS_SPREADSHEET_ID`, `SHEETS_WORKSHEET`, `GOOGLE_SERVICE_ACCOUNT_JSON` |

Without Sheets configured it always writes `output/leads-YYYY-MM-DD.csv`, which
you paste into your tracker — same as the manual batches.

## Run
```
python run.py
```
Each run advances through the sweep queue, skips slices already marked
worked-out, and stops after `SLICES_PER_RUN` productive slices. State (seen
leads, worked-out slices) lives in the SQLite DB from `../data/schema.sql`.

## Modules
- `config.py` — env/config
- `slices.py` — the sweep queue (edit to expand territory; mirrors `sweep-matrix.md`)
- `maps.py` — Places API (New) text search + field mask
- `dedup.py` — SQLite seen-leads + swept-slices
- `qualify.py` — Sonnet per-lead qualification (loads the committed prompt)
- `scrub.py` — Twilio Lookup
- `sink.py` — CSV writer + optional Google Sheets append
- `run.py` — the orchestrator loop

## Cost notes
- Maps: within the monthly free credit at this volume. `reviews.text` is the
  priciest field in the mask — drop it from `maps.FIELD_MASK` to cut cost
  (qualification loses some signal, e.g. owner names / auto-shop tells).
- Sonnet: one short call per surviving lead; cents per hundred leads.
- Twilio Lookup: fractions of a cent per number.

## Where Claude Code should extend
- Rate-limit handling / retries on the Maps and Anthropic calls.
- Batch qualification (multiple leads per Sonnet call) if volume climbs.
- Firecrawl size-check on H-tier leads before output (see SKILL.md).
- A CLI (choose metro, dry-run, slice range) and a scheduled cron entry.
