# Visibility skill — session state (as of 2026-07-31)

Written at the end of a long session for a fresh Sonnet session with no memory of
today. Read this before touching `visibility_sink.py`, before trusting anything
the "Web Development - Master" tab appears to show, and before running another
slice. Update or replace this file at the end of whatever session reads it next
— it is a snapshot, not a permanent record.

## TL;DR

The pipeline (source → classify → PSI → qualify) is solid and verified twice.
**Sheet delivery is not yet trustworthy** — it failed in two different ways this
session, one fixed and verified, one found but *not* fixed (explicitly told not
to). Before believing anything was "delivered," read a row back from the sheet
via the API yourself. Do not trust a script's success message, and do not trust
what a screenshot or a script *claims* the UI shows without reading the raw grid
directly — see "Broken or uncertain" below for exactly why.

## What's working and verified

- **`visibility_site.py`** — `classify_site()`/`domain_candidates()`/
  `domain_exists()`. Parking-host rejection, domain-mismatch flagging, and the
  apostrophe-tokenizer fix have all held up across two slices (NW/gutters,
  NW/snow removal). One real gap found this session, not fixed: a business name
  with a long legal/legacy suffix ("Glacier Plowing - A Liegel Legacy Home and
  Business Services Company") produces domain guesses that are all garbage,
  because the primary-segment splitter includes the whole suffix. Worth a
  future fix: also try just the first 2-3 tokens of the name as its own
  candidate, independent of the &/"and" segment splitter.
- **`visibility_qualify.py`** — `qualify()`, thinking disabled, retry-once,
  three-state `business_description` contract, `specific/generic/unknown`
  primary-category vocabulary, deterministic score-cap enforcement via
  `_enforce_score_cap()`. Verified across ~30 leads total (13 gutters + 17 snow
  removal). Every row's `profile_subscore + min(website_subscore_raw, 20) +
  buyer_subscore` equaled `score`, either natively or via `_enforce_score_cap`
  catching a real model arithmetic slip (this happened on 5 of 17 snow-removal
  leads — the safety net is doing real work, keep it).
- **Hard gates in `qualification-prompt.md`** — franchise/chain recognition
  (caught "The Grounds Guys of McHenry" by name alone, no explicit franchise
  field), review-count floor (<15) and ceiling (>100), and the "review" bucket
  triggers (score>70 with <20 reviews, ambiguous trade name) all fired
  correctly when tested against real snow-removal data today.
- **PSILink formula fill** (column AJ, rows 2 and 5:83 — rows 3-4 intentionally
  skipped, they carry hardcoded permalink strings that can't be reconstructed
  as a formula). Formula text and cap verified via `value_render_option=FORMULA`
  reads. **Caveat:** this fill is a one-time action on the rows that existed at
  the time. It does not extend itself to rows added by a later run — see "Open"
  below.
- **`visibility_sink.py`'s delivery mechanism**, as of the *current* committed
  version (commit `2f965a3`) — no longer uses `append_rows()`/`values.append`
  at all. It computes the target row directly from the last non-blank Company
  cell and writes with `ws.update()`. Verified with three separate controlled
  live test-writes (single marked row, deleted/cleared immediately after each).
  If you change this function, re-verify the same way before trusting it — see
  next section for why that matters.
- **WebsiteScore column** is now `min(website_subscore_raw, 20)`, not the raw
  value, so `ProfileScore + WebsiteScore + BuyerScore == Score` reads directly
  off the sheet without doing the cap math yourself. Verified on the 4
  delivered snow-removal rows.
- **Status dropdown + conditional formatting + STATUS COLOR KEY legend**
  survived every structural column edit this session (two `insertDimension`
  calls, a 66-row content clear). Verified via the data-validation `ONE_OF_LIST`
  rule and all 12 conditional-format rule ranges.
- **Dedup store** (`_agent/data/seen_leads.db`, shared with the leads/ skill) —
  directly re-queried just now (not just trusted from a script's exit code):
  all 17 snow-removal candidates are recorded with correct decisions, and
  `swept_slices` correctly shows `NW-snow-removal-2026-07-30` as `productive`.
  This part of the pipeline is genuinely solid.

## What's open (no code fix exists yet, needs a decision)

- **No review-tab delivery mechanism.** 5 snow-removal leads got `verdict:
  review` from `qualify()` (Pawlicki Enterprises LLC, 4seasons Landscaping &
  Sealcoating, State Line Landscaping, One Stop Shop LC, Ware Landscaping &
  Snow Removal). `visibility_sink.py` only has `append_leads()` for keepers —
  there is no code path that writes `review` verdicts anywhere. Right now
  their only durable record is the `decision='review'` row in `seen_leads.db`
  (see above) plus whatever the chat transcript from today still contains.
  SKILL.md and output-format.md both say review rows should go to "the review
  tab" but that tab/mechanism doesn't exist for this skill. Decide: build one,
  or decide review verdicts are handled some other way.
- **`qualify()`'s payload is missing `business_status`.** The rubric's own
  first, cheapest hard gate ("businessStatus is anything other than
  OPERATIONAL... apply it before anything else") can't actually be checked by
  the model — the field is never sent. Today's sourcing script pre-filtered on
  this itself before calling qualify(), but that's a property of today's
  one-off script, not of `qualify()`'s contract. A future sourcing script that
  forgets this pre-filter will silently lose this gate.
- **`qualify()`'s payload is missing review dates and review text entirely.**
  The buyer subscore table includes "most recent review inside 90 days" (10pt)
  and "owner's first name appears in review text" (5pt), but there is no line
  in the payload for either. These two signals can never score under the
  current implementation — every lead's effective buyer-subscore ceiling is
  lower than the rubric's nominal max, the same way profile_subscore's
  documented ceiling is 85 not 105. This isn't written down anywhere the way
  the profile-subscore ceiling is — it should be, once someone decides whether
  to fix the payload or just document the lower ceiling.
- **PSILink fill-down is not self-maintaining.** It was filled for rows 2,
  5:83 only. Whoever runs the next slice needs to either fill it again for the
  new row range, or accept that new rows won't have it until someone does.

## What's broken or uncertain — read this before trusting a delivery

Sheet delivery failed in **two different ways** this session:

**1. Fixed and verified.** The first real delivery after today's sheet
restructuring (adding ProfileScore/WebsiteScore/BuyerScore columns) landed 4
rows at `AJ84:BB87` instead of `A84:AC87` — 35 columns off. Root cause:
`append_rows()`/`values.append` searches the *whole sheet* for "a table" to
append after, and the PSILink formula in column AJ (filled in this same
session) creates a second, disjoint block of populated cells at the same
row-depth as the real A:AC data, separated by the blank
Tier/Price/Deposit/Balance/Retainer columns. Google's table-detection followed
that block instead of the real one. **`table_range` does not fix this** — I
tried `table_range="A1:AC1"` first, and the live API response still reported
`tableRange: 'A1:AJ5'` and wrote to row 6 instead of the correct row. The
current fix bypasses `values.append` entirely (see "working" section above).
Manually corrected the 4 misplaced rows in place; re-verified after.

**2. Found, NOT fixed — explicitly told not to.** After the above fix, and
after I reported "4 keepers delivered" as settled, the user reported seeing
only 3 manual rows and a leftover test row in the actual Google Sheets UI —
not the 13 gutters leads or the 4 snow-removal leads. I re-checked directly via
the API (not via a script's earlier claim, an actual fresh read at the end of
the session) and **the data is genuinely present**: rows 71-83 (13 gutters
leads) and rows 84-87 (4 snow-removal leads, correct arithmetic) are all there,
confirmed by reading raw cell values just now. But `Web Development - Master`'s
`basicFilter` has an active sort spec: `{'dimensionIndex': 22, 'sortOrder':
'ASCENDING'}` — column 22 (0-indexed) is Status. Almost every delivered row has
Status = "Not called"; rows 3 and 4 have different values ("No answer", "Left
VM"). A live sort on Status would redistribute every row's visual position
relative to insertion order, which is a very plausible explanation for "the
data I expect at the top isn't there" even though nothing was deleted. **I did
not check for a basicFilter/sortSpec at the start of this session** — only
conditional formatting and data validation — so I cannot say with certainty
whether this sort predates today's work or was somehow produced by one of
today's structural edits. This project has a documented history of exactly
this failure mode on the sibling "Manufacturer Leads - Master" tab (a stuck
filter range, fixed 2026-07-22 per the root CLAUDE.md) — a live sort on this
tab would be the same family of bug. **Next session: check whether clearing
this sort resolves what Sean sees before doing anything else with this tab.**

**3. A leftover test row was missed.** Row 5 currently contains `"TEST ROW -
DELETE ME (table_range verification)"` — a leftover from the *first* failed
fix attempt (the `table_range="A1:AC1"` test), before I'd switched to the
direct-range-write approach. I cleaned up two other test writes (one at row 6,
one at row 88) but missed this one. It's real data sitting in the live sheet
right now: Status "Not called", garbage Score/subscore values, `[NO_SITE]` in
Notes. It needs deleting — I did not do it, per this session's explicit "do
not fix anything" instruction.

**Takeaway for next session:** two sheet-delivery bugs in one session, plus a
missed cleanup, is enough that "the script said N rows written" should not be
treated as confirmation of anything. Read the row back via the API after every
delivery, and if Sean reports something different from what the API shows,
believe both reports and go find the layer in between (filter, sort, view)
that reconciles them — don't assume either side is wrong.

## Where the delivered lead data actually lives

- **Google Sheet**, spreadsheet ID `1CgHgxEqLPmdkOI-2y9wTlvpDSDQdTcY2gs2aV4GJocs`
  (titled "Manufacturer Leads — Master" at the spreadsheet level — this is the
  same spreadsheet the leads/ skill uses, on a different tab), worksheet
  **"Web Development - Master"** (gid `1470416650`):
  - Rows 2-4: 3 manual entries (Thompson Heating and Cooling, Jo Heating &
    Cooling, Bud Chimney & Gutter & Pressure Wash) — pre-existing, human-owned.
  - Row 5: the leftover test row described above — needs deleting.
  - Rows 6-70: blank (cleared earlier this session; legend column AL rows 1-12
    and PSILink formulas in AJ are the only content in this range).
  - Rows 71-83: 13 NW/gutters leads from an earlier phase of this session.
  - Rows 84-87: 4 NW/snow-removal keepers from today (Ivan's Landscaping &
    Snow Removal Corp., Langton Group, Seasonal Landscape Solutions,
    Tomasello's Landscaping).
  - Rows 88+: blank, correctly the next append point.
- **NOT in any local file.** `orchestrator/output/` contains exactly one file,
  `leads-2026-07-22.csv`, from the leads/ (manufacturer) pipeline's maiden
  voyage — nothing from any visibility run. `visibility_sink.py` has no
  local-file fallback at all; delivery is Sheet-only. If the Sheet write is
  ever wrong *and* undetected, there is no local copy to recover from.
- **The 5 "review"-verdict leads** exist only in `seen_leads.db`'s
  `decision='review'` rows (company name, phone digits, category, slice ID —
  no score, no hook, no notes) and in today's chat transcript. If you need the
  full qualification detail (subscores, hook, note) for those 5 and the
  transcript isn't available, it is gone — the JSON intermediates that held it
  were deleted as scratch cleanup at the end of the run, on the assumption that
  the sheet was the durable record. Given finding #2 above, that assumption was
  optimistic. Consider not deleting qualification JSON until a human has
  confirmed the delivery looks right in their own browser, not just via a
  script's read of the API.
- **Dedup store**, `_agent/data/seen_leads.db` — `seen_leads` table has all 30
  leads processed this session (13 gutters + 17 snow removal) with phone
  digits, decision, and slice ID. `swept_slices` has both slices marked
  `productive`. This store is independent of the Sheet and is confirmed
  correct as of this write-up.
