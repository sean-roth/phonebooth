# _agent — Context & Handoff (for Claude / future sessions)

Durable context for the **phonebooth Outreach Agent**. If a session is interrupted,
start here. Keep this file updated when the setup changes.

**Guiding principle** (from README.md): *this system exists to put Sean on the phone
more — not to become a bigger thing to build instead of calling.* The agent only
sources and filters leads; humans make the calls. Prefer the smallest change that
works over new machinery.

**Last verified:** 2026-07-22 — maiden voyage completed. State: ~72 leads in the
master sheet (Batch 2 + Batch 3 + first agent run), dedup DB seeded, `SHEETS_ENABLED=true`.

## What it is
Finds privately-held SMB manufacturers (~50–200 employees) in the Chicago and
Detroit metros and produces callable leads. Pipeline:

`sweep queue → Google Maps (Places API New) → dedup → Sonnet qualify → Twilio scrub → dated CSV (+ Google Sheet)`

## How to run
From `_agent/orchestrator/`:
```
python run.py                    # default: 6 productive slices
SLICES_PER_RUN=2 python run.py   # smaller run
```
Output: dated CSV in `orchestrator/output/`, plus rows appended to the master sheet
when `SHEETS_ENABLED=true`. The dedup DB prevents re-sourcing. Run it in the user's own
terminal or via Claude Code (works — see gotcha #1).

## Module map (`orchestrator/`)
- `run.py` — the loop; targets `SLICES_PER_RUN` productive slices, caps total sweeps at 3×.
- `slices.py` — sweep queue: metro × corridor × category (Chicago then Detroit). Mirrors `skills/leads/sweep-matrix.md`.
- `maps.py` — Places API (New) text search (`places:searchText`). Field mask includes reviews (priciest field).
- `dedup.py` — SQLite seen-leads store (`../data/seen_leads.db`); **phone digits = primary dedup key** (name+ZIP fallback, but region has no ZIP).
- `qualify.py` — one Sonnet call per lead; system prompt from `skills/leads/qualification-prompt.md`. Returns keep/reject/review + H/M/L confidence.
- `scrub.py` — Twilio Lookup v2 → valid/dead/unknown (unknown if Twilio unset). Optional.
- `sink.py` — writes the CSV (always) and appends to the Sheet (if enabled) via OAuth (`_gspread_client()`).
- `seed.py` — one-time seeder: `python seed.py <tracker-export.csv>` loads hand-built rows into the dedup DB (matches Company/Phone/Region headers).
- `oauth_setup.py` — one-time interactive Google OAuth bootstrap.
- `config.py` — loads `.env`.

## Config & secrets (`orchestrator/.env`, gitignored)
Required: `GOOGLE_MAPS_API_KEY` (Places API **New** + billing enabled), `ANTHROPIC_API_KEY`.
Optional: `TWILIO_ACCOUNT_SID`/`TWILIO_AUTH_TOKEN` (scrub), `SHEETS_*` (Sheet sync).
`QUALIFY_MODEL` defaults to `claude-sonnet-5`.

Google auth is **user OAuth**, not a service-account key (security preference; also
dodges org policies that block service-account key creation):
- OAuth client JSON (Desktop app) → `~/.config/phonebooth/oauth-client.json`
- Cached token → `~/.config/phonebooth/authorized_user.json` (both OUTSIDE the repo)
- Scope: `spreadsheets` only. Bootstrap once (opens a browser): `python oauth_setup.py`
- Kept the broad `spreadsheets` scope (not `drive.file`) so the agent can open the
  pre-existing, hand-made master sheet.

## The master sheet (tracker + format template)
Sheet **"Manufacturer Leads - Master"** (ID in `.env` → `SHEETS_SPREADSHEET_ID`). The
single tab's name must equal `SHEETS_WORKSHEET`. Treat this tab as the FORMAT TEMPLATE.
- Columns **A–M** = lead data (must match `sink.py` `COLUMNS`).
- Columns **N (blank) + O ("STATUS COLOR KEY" legend)** sit beside the data and are kept
  OUT of the data/filter range.
- Formatting spans the whole column (rows 2–1000) so agent-appended rows auto-style:
  - **Status (col G)** dropdown, 11 values: Not called, No answer, Left VM, Callback,
    Interested, Email only, Disqualified, Refused, Booked, Pilot, z_Dead Number.
  - Per-status conditional colors (**TEXT_EQ**). `z_Dead Number` = dark purple (its `z_`
    prefix sorts it to the bottom so dead numbers aren't re-worked).
  - Overdue **Next Touch (col I)** red highlight: `=AND($I2<>"",$I2<TODAY())`.
  - **Basic filter spans A:M (all rows)** so sorting covers every lead while the N/O
    legend stays put. (Bug fixed 2026-07-22: filter was stuck at A1:M41.)

## Operational gotchas (hard-won — read before debugging)
1. **Stale ANTHROPIC key in Claude Code's shell.** The tool shell injects an invalid
   `ANTHROPIC_API_KEY` (process scope) that 401s and would shadow `.env`. `config.py`
   uses `load_dotenv(override=True)` so `.env` wins. It is NOT in the user's real env.
2. **`python -c` + dotenv.** Under `python -c`, python-dotenv thinks it's interactive,
   searches cwd upward, and misses `orchestrator/.env` — so `config.*` values come back
   empty. Run script FILES, or pass values (e.g. the sheet ID) explicitly.
3. **Sheet writes:** append with `value_input_option="USER_ENTERED"` (dates render,
   phones stay text). "Text is exactly" color rules must be **TEXT_EQ** — the sheet
   originally had a malformed `NUMBER_EQ`-with-text that the API refuses to rewrite.
4. **Dedup timing:** every qualified lead is recorded in `seen_leads` during a run, even
   with `SHEETS_ENABLED=false`. So a lead sourced to CSV-only won't reappear — move it to
   the master deliberately (it won't re-source). Seed new hand-built batches with
   `seed.py` BEFORE the next run.

## Common tasks
- **Fold a new batch into the master:** append columns A–M (dedup by phone digits), then
  `python seed.py <export.csv>` on the same rows so they aren't re-sourced.
- **Add a Status option:** extend the col-G validation list AND add a matching TEXT_EQ
  color rule across G2:G, AND add a legend entry in column O.
- **Change territory:** edit BOTH `slices.py` and `skills/leads/sweep-matrix.md` in one commit.

## Pointers
- `README.md`, `ROADMAP.md`, `strategy/sales-strategy.md`, `skills/leads/*.md` — strategy & prompts.
- Claude's cross-session memory (local to this machine) also indexes this project:
  `~/.claude/projects/C--Users-seanr/memory/MEMORY.md`.