# Skill: visibility — source local contractors for Google Business Profile work

Point a Claude Code agent at this folder to gather contractor leads and append
them to the Web Development tracker tab in Google Drive.

Sibling to `../leads/`, which sources manufacturers for SOPs Nobody Reads.
Different buyer, different offer, different tracker tab. Same plumbing, same
guardrails, same governing `ROADMAP.md`.

## Goal
Produce clean, callable lists of small local contractors in the Chicago metro
whose Google Business Profile is visibly underbuilt — in tracker format,
appended to the live sheet, sorted so the strongest openers surface first.

## Read first
1. `offer.md` — what is actually being sold, at what price, in what voice.
   Read this before writing any note a human will read on a call.
2. `qualification-prompt.md` — the judgment to apply per lead.
3. `sweep-matrix.md` — which corridor and trade to work next, and which trades
   are in season.
4. `output-format.md` — the columns to write and, importantly, the columns to
   leave alone.

## Tools (MCP)
- **Google Maps (Places)**: `maps_search_places`, `maps_place_details` — source
  candidates, then pull phone, website field, rating, review count, photos,
  categories, hours. Details is not optional.
- **PageSpeed Insights API** — no MCP server; call it directly with `WebFetch`:
  `https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=<site>&strategy=mobile&key=<PAGESPEED_API_KEY>`.
  Read the key from `../../orchestrator/.env` (`PAGESPEED_API_KEY`). Free with a
  Google Cloud key. Run only on survivors, never on the raw source list.
- **Firecrawl** (`firecrawl_scrape` only) — confirm a site exists when the
  Places website field is empty. See the unlinked-site rule below.
- **Playwright** — render at a phone viewport, capture a screenshot. Optional;
  only worth running on leads that already scored well.
- **Google Drive** — read and append the tracker. Live sheet is the
  "Web Development - Master" tab.
- **GitHub** — this repo.

## The unlinked-site rule

**An empty Places `websiteUri` does NOT mean the business has no website.**
Many have a site they simply never linked to their profile. This is the single
highest-value finding available, and treating it as "no website" throws it away.

For every candidate with an empty website field:
1. Try domain patterns — `businessname.com`, `businessnametrade.com`,
   hyphenated variants.
2. If nothing resolves, a name-plus-city web search as fallback. Expect this to
   fail often — the businesses with the worst web presence are exactly the ones
   search will not surface. Domain guessing is the primary method, not search.
3. Classify:

| Class | Meaning |
|---|---|
| `SITE_UNLINKED` | Site found, not on the profile. **Highest value.** |
| `SOCIAL_ONLY` | Website field points at Facebook or Instagram |
| `NO_SITE` | Genuinely nothing |
| `SITE_LINKED` | Normal |

## Workflow (one run)
1. **Pick slices.** Read `sweep-matrix.md`. Take the next corridor × trade
   slices that are both unworked and in season. Out-of-season trades are
   skipped, not deprioritized — a roofer in August will not pick up.
2. **Source.** `maps_search_places` with "<trade> <suburb> IL", then
   `maps_place_details` on each hit. A lead with no phone is dropped.
3. **Dedup.** Normalized phone and name+ZIP against the shared store in
   `../../data/`. Drop anything already seen by either skill.
4. **Gate on viability.** Most recent review older than 12 months → drop the
   row entirely, however bad the profile looks. A dead business with a terrible
   listing is not a lead.
5. **Classify the site.** Apply the unlinked-site rule above.
6. **Qualify.** Send survivors to Sonnet with `qualification-prompt.md` as the
   system prompt. Returns keep / reject / review, a provisional score, and a
   one-line hook.
7. **Enrich survivors only.** PageSpeed on keepers that have a reachable site.
   Do not run it on rejects; it is the expensive call.
8. **Deliver.** Append to the tracker in `output-format.md` order, highest
   score first. Ambiguous rows go to the review tab, never the callable list.

## Guardrails
- **NEVER call, email, or contact anyone.** This skill sources and filters.
- **NEVER invent a phone number.** It comes from the Maps listing or it does
  not exist.
- **NEVER write in the Observation or Hook columns as though a human looked at
  the site.** The agent has not seen it the way Sean will. Write what the data
  supports and nothing more.
- Do not source faster than one caller can dial. Per the ROADMAP anti-goals,
  backlog is wasted compute. A run that produces more than ~40 callable rows
  should stop early.
- If a slice returns mostly franchises and 100+ review shops, mark it
  worked-out and move on.

## Scoring is provisional

The weights in `qualification-prompt.md` were written **before any calls were
made**. They encode a hypothesis, not evidence. They have already been revised
twice on reasoning alone.

After the first twenty calls, revise them against what actually opened a
conversation — and treat the pre-call score as a sort order, never as a
decision. The human decides who is worth a call.

## Human handoff
Every run ends with a short summary: N callable rows appended, M sent to
review, which slices were worked, and which were marked out. Note separately
how many landed in each site class — that count is the fastest read on whether
a corridor is worth returning to.
