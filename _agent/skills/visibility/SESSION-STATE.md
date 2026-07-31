# Visibility skill — session state (as of 2026-07-31, end of day)

Written for a fresh Sonnet session with no memory of today. Read this before
touching `visibility_sink.py` or `visibility_qualify.py`, before running
another slice, and before assuming anything about the sheet's row layout —
Sean actively sorts both tabs by Status as part of his own calling workflow,
so row numbers are not stable and should not be hardcoded or relied on across
sessions. Update or replace this file at the end of whatever session reads it
next — it is a snapshot, not a permanent record.

## TL;DR

The pipeline (source → classify → PSI → qualify → persist → deliver) is
solid and verified across three slices today. Both known sheet-delivery bugs
from earlier today are fixed and verified. A real scoring regression
(`primary_type='service'` reading as `unknown` instead of `generic`) was
found and fixed today — verify any qualify() output that shows
`primary_category_specific: "unknown"` was actually unreturned by Places,
not just unfamiliar-looking, if you see it again. Three items remain
open by design, not oversight — see "Deferred, not forgotten" below.

## What's working and verified

- **`visibility_site.py`** — `classify_site()`/`domain_candidates()`/
  `domain_exists()`. Parking-host rejection, domain-mismatch flagging, and
  the apostrophe-tokenizer fix have held up across three slices (NW/gutters,
  NW/snow removal, N/chimney sweep, N/gutters). One real gap found, not
  fixed: a business name with a long legal/legacy suffix ("Glacier Plowing -
  A Liegel Legacy Home and Business Services Company") produces domain
  guesses that are all garbage, because the primary-segment splitter
  includes the whole suffix. Worth a future fix: also try just the first
  2-3 tokens of the name as its own candidate, independent of the &/"and"
  segment splitter.
- **`visibility_qualify.py`** — `qualify()`, thinking disabled, retry-once,
  three-state `business_description` contract, deterministic score-cap
  enforcement via `_enforce_score_cap()`. Verified across ~45 leads total
  (13 gutters + 17 snow removal + 13 chimney sweep + 17 gutters-round-2).
  Every row's `profile_subscore + min(website_subscore_raw, 20) +
  buyer_subscore` equals `score`, either natively or via
  `_enforce_score_cap` catching a real model arithmetic slip (roughly a
  third of leads needed that correction across the day — the safety net is
  doing real, constant work, keep it).
- **`primary_category_specific` scoring — fixed today.** Was intermittently
  declaring `unknown` instead of `generic` for values like `primary_type:
  "service"` (the model's own reasoning: "I don't recognize this as a
  documented category" → treated as unrecognized → unknown). This is wrong
  — `unknown` must mean Places returned nothing, never "the model doesn't
  recognize this value." Fixed in `qualification-prompt.md` with a
  mechanical 3-step rule (not returned → unknown; names the trade →
  specific; anything else present → generic, no exceptions), an explicit
  known-generic value list, and a worked example. Verified by re-running
  Vince Chimney Sweeps (the exact lead that scored `unknown` today) through
  `qualify()` after the fix — `signals.primary_category_specific` now reads
  `generic`, and with a viable review count the 35 points correctly land in
  `profile_subscore`. If you see `primary_category_specific: "unknown"`
  again, check the payload literally says "not returned by Places" for
  `primary_type` — if a value is present, unknown is wrong regardless of
  how the model justifies it.
- **Hard gates in `qualification-prompt.md`** — franchise/chain recognition
  (caught "The Grounds Guys of McHenry" by name alone), review-count floor
  (<15) and ceiling (>100), and the "review" bucket triggers (score>70 with
  <20 reviews, ambiguous trade name, suspicious rating patterns) have all
  fired correctly across every slice run today.
- **`visibility_sink.py`'s delivery mechanism** — no longer uses
  `append_rows()`/`values.append` at all (see "Resolved bugs" below for
  why). Computes the target row from the last non-blank Company cell,
  writes with `ws.update()`. The same `_write_rows()` helper now backs both
  `append_leads()` (Web Development - Master) and `append_review_leads()`
  (Review tab). Verified with controlled live test-writes each time it's
  been touched. If you change this function again, re-verify the same way
  — an actual API read after the write, not trust in the return value.
- **`persist_qualified()` — new today.** Appends every lead's full record
  (including its `qualification` dict) to
  `output/visibility-qualify-YYYY-MM-DD.jsonl`, one JSON object per line,
  append-only, never truncated. SKILL.md's workflow step 8 now calls for
  this before any sheet delivery, with the COMPLETE post-qualify list
  (every verdict — keep, review, and reject), not just what's being
  delivered. Today's file has 15 real backfilled records (6 keep + 9
  review from today's three slices, reconstructed from chat/terminal
  history since the mechanism didn't exist yet when those ran); today's 15
  rejects were not backfilled — every future run captures rejects
  automatically, this was just a one-time gap-closing pass, not worth
  hand-reconstructing further.
- **Review tab — new today.** Duplicated from Web Development - Master (so
  the Status dropdown, conditional formatting, and column layout match
  exactly), holds `verdict: review` leads that need a human's eyes before
  either calling or discarding. Currently has 9 leads (5 from the
  2026-07-30 snow-removal slice, 4 from today's chimney-sweep/gutters
  slices). One of them (Ware Landscaping & Snow Removal) has its Notes
  field prefixed `[reconstructed]` — its qualify() note text didn't survive
  the scratch-file cleanup before persist_qualified() existed, so what's
  there is rebuilt from flags, not verbatim. Everything else in both tabs
  is real, unaltered qualify() output.
- **Status dropdown + conditional formatting + STATUS COLOR KEY legend +
  basic filter** — all correctly configured on both tabs as of today.
  Sean uses the basic filter's sort-by-Status feature as his own active
  calling workflow (confirmed directly by him — this is intentional, not a
  bug, don't "fix" it in a future session). Two real issues with it were
  found and fixed today: the legend was missing its "Callback" entry
  (restored, with the correct gold color pulled from the actual
  conditional-format rule, not guessed) on both tabs, and the filter's
  column range was A:AC only, excluding Tier/Price/Deposit/Balance/
  Retainer/DocLink/PSILink from the sort — meaning those columns wouldn't
  move with their row when Sean sorts, silently misaligning them from the
  lead they belong to. Widened to A:AJ (still excluding the blank spacer
  and the legend) on both tabs. Verified: legend text+color read back
  correctly, filter range read back correctly, and conditional-format rule
  count (12) and dropdown validation unaffected by either change.
- **Dedup store** (`_agent/data/seen_leads.db`, shared with the leads/
  skill) — directly re-queried multiple times today, not just trusted from
  exit codes. All leads across all four slices are recorded with correct
  decisions; `swept_slices` correctly shows each slice as `productive`.
  Genuinely solid, unchanged today.

## Deferred, not forgotten

Three known gaps, explicitly not fixed today (in scope for a future
session, not overlooked):

- **`business_status` enforcement lives outside `qualify()`.** The
  rubric's own first, cheapest hard gate ("businessStatus is anything
  other than OPERATIONAL... apply it before anything else") can't actually
  be checked by the model — the field is never in the payload. Every
  slice's sourcing script has pre-filtered this itself before calling
  qualify(), but that's a property of each one-off script, not a guarantee
  qualify() provides. A future sourcing script that forgets this pre-filter
  will silently lose the gate.
- **Reviews (dates and text) are missing from `qualify()`'s payload
  entirely.** Two consequences: (1) the buyer subscore's "most recent
  review inside 90 days" (10pt) and "owner's first name in review text"
  (5pt) signals can never score — every lead's effective buyer-subscore
  ceiling is quietly lower than the rubric's nominal max, undocumented the
  way profile_subscore's 85-not-105 ceiling is. (2) This is also why the
  "review" bucket's "duplicate review text / templated reviews /
  purchased-package" trigger is currently dead — there's no review text in
  the payload for the model to notice a pattern in. Fixing this payload
  gap re-enables purchased-review detection as a side effect, not just the
  buyer-subscore points.
- **PSILink generation should move into `visibility_sink.py`,** not stay a
  manual, one-time fill-down. It was filled for the rows that existed
  2026-07-30 (row 2, 5:83) and has not been extended since — the 30+ leads
  delivered today (rows 84 onward as of this morning, now scattered by
  Sean's sort) do not have it. The fix isn't "fill it down again" — that's
  the same manual gap recurring. It's: have `_row()` or a sibling function
  write the PSILink formula text directly into new rows at delivery time,
  the same way every other column gets populated, so it never depends on
  a human or a future session remembering a separate step.

## Resolved bugs (context for pattern-recognition, not action items)

Sheet delivery failed in three different ways today, all now fixed and
verified. Keeping this history because the failure mode ("a script says N
rows written, but what actually landed is wrong") recurred twice in one day
before the fix held — if something looks delivered but wrong again, this is
the shape it'll probably take:

1. **Column-shift bug.** `append_rows()`/`values.append` searches the whole
   sheet for "a table" to append after. The PSILink formula in column AJ
   created a second, disjoint block of populated cells at the same
   row-depth as the real A:AC data (separated by blank Tier/Price/Deposit
   columns), and Google's table-detection followed that block instead —
   rows landed 35 columns off target. Tried `table_range` as a fix; it
   didn't work (live API response still reported the wrong table and wrote
   to the wrong row). Fixed by bypassing `values.append` entirely — see
   "working" section above.
2. **WebsiteScore was uncapped.** Wrote the raw `website_subscore_raw`
   instead of `min(raw, 20)`, so the three subscore columns didn't sum to
   Score by direct sheet arithmetic. Fixed.
3. **A "sort looks like missing data" scare that turned out to be
   intentional.** Sean reported seeing far fewer rows than expected;
   turned out he'd been using the basic filter's sort-by-Status feature
   himself, which is a real, wanted workflow feature, not a bug — confirmed
   directly by him. Real bugs found *while investigating that report*: the
   legend's missing Callback entry and the filter's too-narrow column range
   (both above, both fixed). Lesson that held up twice today: read a row
   back via the API after every delivery, and if a human reports something
   different from what the API shows, believe both reports and go find the
   layer in between (filter, sort, view) that reconciles them — don't
   assume either side is wrong, and don't assume the filter/sort setup is
   broken just because it's unfamiliar.

## Where the delivered lead data actually lives

Row numbers are **not stable** — Sean re-sorts both tabs by Status as part
of his own workflow. Describing contents by name/count, not row number.

- **Google Sheet**, spreadsheet ID
  `1CgHgxEqLPmdkOI-2y9wTlvpDSDQdTcY2gs2aV4GJocs` (titled "Manufacturer
  Leads — Master" at the spreadsheet level — shared with the leads/ skill,
  different tabs):
  - **"Web Development - Master"** (gid `1470416650`): 3 manual entries
    (Thompson Heating and Cooling, Jo Heating & Cooling, Bud Chimney &
    Gutter & Pressure Wash) plus 23 agent-delivered keepers across four
    slices (13 NW/gutters, 4 NW/snow-removal, 3 N/chimney-sweep, 3
    N/gutters). 26 real data rows total, verified via a fresh Company
    column read, not computed by hand.
  - **"Review"** (gid `1632838256`): 9 review-verdict leads (see above).
- **`output/visibility-qualify-2026-07-31.jsonl`** — 15 records (today's
  backfill; see "persist_qualified()" above). This is a new, permanent,
  append-only location — never delete files here.
- **NOT in any other local file.** `orchestrator/output/` otherwise
  contains only `leads-2026-07-22.csv` from the leads/ (manufacturer)
  pipeline's maiden voyage. `orchestrator/output/` itself is untracked in
  git (matches the leads/ pipeline's existing convention) — the JSONL
  files are a durable local record, not a git-backed one, unless a future
  session is asked to start tracking them.
- **Dedup store**, `_agent/data/seen_leads.db` — every lead from every
  slice run so far, with phone digits, decision, and slice ID.
  Independent of the Sheet, confirmed correct as of this write-up.
