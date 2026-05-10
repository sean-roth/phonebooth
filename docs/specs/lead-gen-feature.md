# Lead Generation Feature — Spec

**Status:** Future feature for phonebooth. Not built. This doc captures the architecture before it gets lost.

**Critical reframe:** This is not an agent. This is software. There is no LLM in the hot path, no autonomous decision-making, no permissions to manage. It's a button in the phonebooth dashboard labeled something like "Pull leads" that takes a city and a count, runs a deterministic pipeline, and returns a sorted list.

The earlier framing of "lead gen agent" was wrong. Agents are for tasks that require reasoning or judgment under uncertainty. This task requires neither. The data is sparse and the rules are deterministic.

## What the feature does

User input:
- Target city or ZIP range (e.g., "Cook County, IL")
- Target trade (electrical contractors, landscapers, etc.)
- Count (30–50 typical)

Output:
- Ranked list of leads written to phonebooth's lead table
- Each lead includes: contact info, signal scores, trajectory classification, and a short auto-generated cold-call hook
- Source data preserved so the user can spot-check any decision

User experience: Click button. Wait 30–90 seconds. Calls a stored list to dial through tomorrow morning.

## Architecture: deterministic pipeline, model only at the end

The pipeline has six stages. Five are deterministic. One uses a small model, and only for final synthesis.

### Stage 1 — Fetch

Google Maps Places API (New). Two calls per business:
- `searchText` to get the business list for a query like "landscaping contractors Cook County"
- `placeDetails` per result to get phone, website, hours, reviews

Pricing (May 2026): roughly $32 per 1,000 text searches, $5 per 1,000 detail requests. For a batch of 50 leads with full reviews, cost is under $0.05. Google's $200/month free Maps credit covers it entirely at this scale.

Library option: the `@cablate/mcp-google-map` server already in the toolchain, or direct REST calls — both work. Direct REST is simpler for a server-side feature.

### Stage 2 — Filter

Deterministic rules from `docs/marketing/lead-targeting.md`:
- Permanently closed? Drop.
- Most recent review > 18 months ago? Drop.
- Zero reviews and no website? Drop.
- Franchise or chain (matched against a small chain list)? Drop.
- More than 50 employees (estimated from photo count, review patterns, or explicit team mentions)? Flag for the "polished" segment but keep.

Pure Python. No model.

### Stage 3 — Trajectory classification

Pure statistics. For each business with 5+ reviews:
- Sort reviews by date
- Compute rolling 3-month average rating
- Fit a linear trend over 24 months
- Classify: improving, declining, stable, volatile, bimodal, stale-high, stale-low, cluster-event (cluster of complaints in single month)

Roughly 30 lines of Python with numpy. No model.

### Stage 4 — Signal extraction

Keyword and phrase matching against a curated dictionary organized by signal tier:

**Tier 1 — direct safety/compliance signals:**
- "no PPE" / "no hard hat" / "didn't wear safety gear"
- "damaged" / "broke" / "destroyed"
- "left a mess" / "nails in driveway"
- "trespassed" / "wrong property"
- "got hurt" / "injured"
- "no permit" / "without a permit"

**Tier 2 — training and consistency gap signals:**
- "didn't know" / "couldn't answer"
- "had to call the boss" / "had to ask"
- "new guy" / "different guy" / "different person every time"
- "did it differently than" / "last time was"
- "didn't have the right" / "wrong materials"
- "said one thing" / "told me on the phone"

Matched with `rapidfuzz` for fuzzy phrase matching (handles "didn't no" → "didn't know" typos common in reviews).

Each review scored on tier 1 hit count, tier 2 hit count. Aggregated per business.

No model. Deterministic. Fully debuggable — the user can see exactly which phrases matched.

### Stage 5 — Optional embedding fallback for gray-zone reviews

Some review phrasings won't match the dictionary literally but should match semantically. Example: *"the new guy seemed lost"* should match tier 2 but the literal phrase isn't in the dictionary.

Run embeddings on:
- The seed phrases in the dictionary
- Each review

Compare via cosine similarity. Above a threshold (0.7+) = additional signal hit.

Two options for the embedding model:
- **Cloud:** `text-embedding-3-small` (OpenAI), $0.02 per million tokens, ~$0.50 to embed 25,000 reviews across 1,000 businesses
- **Local:** `nomic-embed-text` via Ollama on the joi server, free, no API dependency

Recommend local for the long-running phonebooth deployment. Cloud for prototyping.

No generation. Just vector similarity. Still no LLM in the reasoning loop.

### Stage 6 — Final hook synthesis (the only model step)

Once per lead, after all signals are extracted, generate a one-sentence cold-call hook.

Input to the model (deterministic, all fields known):
- Business name
- Trade
- Trajectory classification
- Tier 1 hits with example quotes
- Tier 2 hits with example quotes
- Notable rating shifts (e.g., "average dropped from 4.6 to 3.8 since February")

Prompt shape:
> "Given the following signals from a contractor's Google reviews, write a one-sentence cold-call hook that references the most distinctive operational pattern. Be specific, cite the trajectory if relevant, and don't be salesy. Output format: a single sentence under 30 words."

Model options ranked by fit for this task:

- **Gemma 3 4B** (Google, open source, runs on the joi server via Ollama, free, fast) — primary recommendation
- **Gemini 2.5 Flash** (Google, API, free tier covers this scale) — backup if local inference is slow
- **Llama 3.2 3B** (Meta, open source, smaller than Gemma 3 4B) — backup if Gemma is unavailable

Cost at scale: roughly zero. Local inference on the joi server is free. Cloud Gemini 2.5 Flash at ~150 tokens per lead × 50 leads per batch is under $0.01.

**Note on the Gemma family:** Gemma 4 was announced and small variants (Gemma 4 1B, 4B) are designed for on-device inference including cell phones. As of May 2026, Gemma 3 is the current stable family. Track Gemma 4 release timing — when stable, it becomes the primary recommendation for this stage.

## Why this works as a phonebooth feature, not a separate service

The whole pipeline is small. Total code: probably 300–500 lines of Python. No external orchestration needed. Runs in 30–90 seconds for a 50-lead batch. Can be triggered from a button in the phonebooth dashboard, write results directly to phonebooth's lead table.

No background workers, no queue system, no separate deployment. Just a function in the phonebooth backend that fetches, scores, ranks, and stores.

## Why this is not an agent

Agents involve:
- Autonomous decision-making under uncertainty
- Tool selection
- Multi-step reasoning
- Permissions management
- Recovery from failure

This pipeline involves none of those. Every step has a clear input, a clear output, and a deterministic rule for what to do next. It's a script. The model call in stage 6 is bounded, single-purpose, and produces text that the user reviews before acting on.

Calling it an agent introduces failure modes (hallucinated leads, runaway tool calls, ambiguous behavior) that don't exist in deterministic software. Don't call it an agent. Call it a feature.

## Claude's role: auditor, not operator

This system is software that runs without LLM intelligence in the loop. When Sean wants to review or improve the system, that's where Claude earns its keep:

- **Spot-check signal extractions.** Sean pastes a batch of leads with their signal scores; Claude reviews whether the scores match the underlying review text. Catches dictionary gaps and false positives.
- **Improve the keyword dictionary.** As new patterns emerge in real review data, Claude suggests additions to the tier 1 and tier 2 phrase lists.
- **Sanity-check the trajectory classifications.** Claude reviews a sample of "declining" or "bimodal" classifications and confirms the math matches the human read.
- **Refine the hook synthesis prompt.** As Sean uses the hooks on calls and sees which ones produce conversations, the prompt gets tuned.
- **Review the cold-call hooks themselves.** Before a dial day, Claude can read through the auto-generated hooks for the upcoming list and flag any that sound off-brand or factually weak.

The Google Maps MCP tool (already specced — `@cablate/mcp-google-map`) gives Claude read access to pull the same data the feature pulls, so spot-checking is direct. Claude looks at the same source data the feature looked at and confirms the feature's output is reasonable.

This is a much better division of labor than making Claude the lead gen engine. Claude's pattern recognition and editorial judgment are useful at the review layer. Claude's tendency to hallucinate, drift, or rationalize is dangerous at the operational layer. Keep the operational layer deterministic and let Claude audit.

## What this displaces

The full lead-intelligence-skill spec in `docs/specs/lead-intelligence-skill.md` was a sketch of what an LLM-driven agent would do. This doc replaces that vision with a deterministic pipeline that achieves the same outcomes with less risk and lower cost.

Keep `lead-intelligence-skill.md` as historical record of the design evolution, but mark it superseded by this doc.

## Build order, when ready

Do not build before 100 hand-prepped manual calls are complete. The dictionary in stage 4 only gets sharp through real exposure to review data and real exposure to which signals predict productive conversations.

When trigger is met:

1. Wire up Places API in phonebooth backend
2. Build stage 2 (filter rules) — pure Python, 30 minutes
3. Build stage 3 (trajectory classifier) — pure Python, 1 hour
4. Build stage 4 (keyword extraction) with initial dictionary from manual prep observations — 2 hours
5. Add stage 5 (embedding fallback) using local nomic-embed-text — 1 hour
6. Add stage 6 (hook synthesis) using local Gemma 3 4B — 30 minutes
7. Wire to phonebooth UI as a single button — 1 hour

Estimated total: one focused day. Build it when the dictionary in stage 4 has real validation, not before.

## What to track once it's live

- Time per batch (target: under 90 seconds for 50 leads)
- API cost per batch (target: under $0.10)
- Dictionary hit rate (Tier 1 + Tier 2 hits per 100 reviews)
- Hook usefulness rating (Sean rates each hook 1–3 after the call; aggregate over time)
- False positive rate (leads that scored high but were bad calls)
- False negative rate (leads that scored low but were good calls — caught from segments where Sean called outside the system's top picks)

The metrics drive dictionary updates and prompt refinements. Quarterly review.

## Stack summary

- **Google Maps Places API (New)** — raw data
- **Python + numpy** — filtering, trajectory math, keyword extraction
- **rapidfuzz** — fuzzy phrase matching
- **nomic-embed-text via Ollama (local)** — embedding fallback for gray-zone reviews
- **Gemma 3 4B via Ollama (local)** — hook synthesis only
- **phonebooth's existing SQLite** — storage

Net new dependencies: Ollama (already installed on joi if you've used it), nomic-embed-text model pull, Gemma 3 4B model pull, rapidfuzz pip install, Google Maps API key. Everything else already in stack.

Total monthly operating cost at expected volume: under $5, mostly Google Maps API even with the free credit.
