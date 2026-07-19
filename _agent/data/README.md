# _agent/data — dedup store and CSV storage

## What lives here
- `schema.sql` — the SQLite "seen leads" table. This is the memory that keeps
  the agent from re-surfacing the same shops every week over the same corridors.
  Without it, duplicates drown the pipeline within a few weeks.
- `.gitignore` — keeps the live DB and large/sensitive CSVs out of git.
- CSV exports and snapshots (see below).

## Can I store CSVs here?
Yes — GitHub handles CSVs fine at reasonable sizes (well under ~50 MB). Two
rules:
1. Don't commit CSVs containing anything you wouldn't want permanently in git
   history. Lead lists of public business names + phones are fine; anything more
   sensitive is not.
2. Don't commit the live, constantly-changing seen-leads data — it bloats the
   repo. Keep the working store local (gitignored) and, if you want a backup in
   git, commit a periodic dated snapshot (e.g., `seen-leads-snapshot-YYYY-MM-DD.csv`)
   instead.

## The dedup check (how the agent uses it)
For each Maps candidate, normalize the phone to digits and build a fallback key
of lowercased name + ZIP. Look both up in `seen_leads`. If either matches, drop
the candidate. Otherwise insert it (with today's date and the slice it came
from) and keep processing. Once a lookup marks a number dead, store that too so
it's never re-checked.

## Seeding (before the agent's first run)
The store starts empty — it has never heard of the hand-built batches. Export
the tracker tab(s) to CSV and run `python ../orchestrator/seed.py <export.csv>`
once, so already-called shops aren't re-sourced as fresh leads. Safe to re-run;
seeded rows match on phone only (the tracker's Region has no ZIP).

## Where the real lead data lives
The callable lists and their outcomes live in Google Drive (SNR-Cold-Call-Tracker
and the dated SNR-Manufacturer-Leads files), not here. This folder is machinery,
not the call record.
