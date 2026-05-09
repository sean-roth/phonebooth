# Phase 2 — From Softphone to Sales Operation

## What changes

Phase 1 built a single-line browser softphone with disposition capture. It works. Phase 2 expands it into a full outbound sales operation:

- **Lead enrichment pipeline** (sidecar) — Google Maps + website scraping → enriched contact records with pain hooks, written to a real CRM
- **Twenty CRM** — installed on joi, becomes the system of record for all contacts, activities, and pipeline data
- **Parallel dialing** — extend phonebooth's single-line dialer to 3 simultaneous lines via Twilio Conference + AMD
- **Pre-call brief** (the legal substitute for whisper coach) — 60-second AI-generated context panel rendered in the cockpit when a lead loads
- **Follow-up sequence** — AI-drafted post-call emails, LinkedIn messages, and disposition-based callback scheduling
- **Stats dashboard** — three views (today / this week / this month), focused on conversation count and meetings booked

## What stays unchanged

- Phonebooth's core call mechanic — Twilio Voice JS SDK in the browser, no recording on cold calls, Illinois two-party consent posture maintained
- Manual disposition entry after each call (this is fuel for follow-up; don't automate it away)
- ~$1.15/month idle, ~$17/month at moderate single-line volume; parallel dialing adds maybe $5–10 on a heavy calling day

## Architectural shift

```
Phase 1:
  Browser cockpit → Twilio → lead's phone
  SQLite stores leads + calls + dispositions

Phase 2:
  Lead enrichment (sidecar) → Twenty CRM
  Browser cockpit reads call queue from Twenty
  Browser cockpit → Twilio Conference (3 lines + AMD) → first live human
  After hangup → activity + dispo pushed to Twenty
  Stats dashboard reads from Twenty
```

Twenty sits at the heart. Phonebooth becomes the calling layer that reads from Twenty and writes events back to it. Phonebooth's local SQLite shrinks to a thin in-flight call cache.

## ICP — Phase 2 narrows the target

Small commercial trade contractors in Cook County: electricians, plumbers, landscapers, similar trades. 1–15 employees. Owner-operators mostly working out of trucks, with mobile phones as their primary (often only) business line.

Implications:
- AI voice calling stays off the table — TCPA exposure on a mobile-heavy ICP is too large
- Voicemail drops are first-class infrastructure, not an afterthought (high VM rate expected; these guys are on jobsites mid-day)
- Apollo is the wrong primary source for this ICP (these owners aren't on LinkedIn polishing titles); Google Maps + website scraping fits better
- Apollo re-enters the picture if/when ICP expands to commercial property managers, larger GCs, or office-staffed contractors

## Call cadence

Tuesday / Wednesday / Thursday only. Pilot two windows for the first two weeks before adding a third:

- **6:00–7:30am MT** (7:00–8:30am CT) — primary. Owner-operators in the truck before first job. Coffee, low gatekeeper friction, clear head.
- **3:30–5:00pm MT** (4:30–6:00pm CT) — secondary. End-of-day callbacks, driving home from jobs.
- **11:30am–12:30pm MT** (12:30–1:30pm CT) — tertiary. Lunch break. Weakest of the three; pilot only after the other two are calibrated.

Mondays for list building and pre-call research. Fridays for follow-up sequences and CRM cleanup.

## Status

Brainstorming. No specs written yet. This document will gain a `00-build-order.md` analogous to `docs/specs/00-build-order.md` once the architecture firms up.

The next exploration is the **Twenty CRM integration** — schema fit, API contract, auth pattern. Twenty is upstream of everything else in Phase 2, so it gets locked in first.

See `decisions-log.md` for the running log of accepted and rejected directions.
