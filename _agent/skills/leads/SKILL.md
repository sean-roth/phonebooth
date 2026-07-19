# Skill: leads — source Midwest manufacturers for cold calling

Point a Claude Code agent at this folder to gather leads and to read/update the
call-tracker spreadsheets in Google Drive.

## Goal
Produce clean, callable lead lists of privately-held Midwest manufacturers
(~50–200 employees) that match the ICP, in the tracker format, appended to the
live Google Sheet. Set genuinely ambiguous ones aside for a human.

## Read first
1. `../../../docs/sales/lead-generation-guide.md` — the governing ICP,
   exclusions, size signals, and output rules. Source of truth.
2. `qualification-prompt.md` — the exact judgment to apply per lead.
3. `sweep-matrix.md` — which metro/corridor/category to work next.
4. `output-format.md` — the columns to write.

## Tools you will have (MCP)
- Google Maps (Places): `maps_search_places`, `maps_place_details` — source
  candidates + get phone/website/hours. Keep the tool surface small.
- Firecrawl (`firecrawl_scrape` only): fetch a company site to confirm identity
  / size signals when a lead is borderline.
- Twilio Lookup (or a number-validation API): flag invalid/disconnected numbers.
- Google Drive: read the tracker, append new rows. The live tracker is the
  Google Sheet named "SNR-Cold-Call-Tracker"; the dated manufacturer lead files
  are named "SNR-Manufacturer-Leads-YYYY-MM-DD".
- GitHub: this repo, for the guide/prompt/matrix.

## Workflow (one run)
1. **Pick slices.** Read `sweep-matrix.md`; take the next few
   metro × corridor × category slices not yet marked worked-out.
2. **Source.** For each slice, run `maps_search_places` with
   "<category> <corridor> <state>" (query patterns in the guide), then
   `maps_place_details` on each hit for phone + website. Details is not
   optional — a lead with no phone is dropped.
3. **Dedup.** Check each candidate's normalized phone (and name+ZIP) against the
   seen-leads store (`../../data/`, see its README). Drop anything already seen.
   Insert survivors into the store.
4. **Qualify.** Send survivors to Sonnet using `qualification-prompt.md` as the
   system prompt. Per lead you get: keep/reject, H/M/L, one-line note. Drop
   rejects.
5. **Scrub numbers.** Run keeper phones through Lookup; drop/flag dead lines.
6. **Deliver.** Append keepers to the Google Sheet in `output-format.md` order,
   H-tier first. Put anything the model marked ambiguous in a "review" tab, not
   the main list.

## Guardrails
- NEVER call anyone. This skill sources and filters only.
- NEVER invent a phone number — it must come from the Maps listing.
- Keep the review pile short; it is the human-judgment queue.
- If a slice returns mostly dupes and sub-50 shops, mark it worked-out in the
  matrix and move on.
- Match a contact's role before treating them as a buyer. A "Client Success" or
  sales contact at a shop is usually NOT the training decision-maker — that's
  the owner / plant manager / ops.

## Human handoff
Every run ends with a short summary: N new callable leads appended, M sent to
review, and any slices newly marked worked-out. The human dials; the agent
never does.
