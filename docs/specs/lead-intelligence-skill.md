# Lead Intelligence Skill — Spec

A future skill for the phonebooth tool. Not built yet. This doc captures the design before it gets lost.

## The insight

Manual lead-prep on May 5, 2026 surfaced the real value of Google Maps data for this business: **it's not the contact info, it's the reviews.**

Customer reviews are unfiltered ethnographic data on a business's actual operational state, written by people with no agenda to manage. For SOPs Nobody Reads specifically — selling against training gaps, safety failures, and consistency problems — reviews are exactly where those gaps surface in writing. The customer describes the buying trigger so the cold caller doesn't have to surface it.

Reviews are also one of the few signals you can mine at scale that isn't already commoditized by every other sales-intel tool. Apollo, ZoomInfo, Clay etc. all pull contact and firmographic data. Almost none mine review sentiment on small-business listings, because their target customers (B2B SaaS sellers) don't care about Google Maps reviews — those tools are calibrated for mid-market and enterprise.

For owner-operator trades, Google Maps reviews are often the only public signal of operational state. Many of these businesses don't have LinkedIn pages, press, blog content, or any other discoverable surface. The review timeline is the entire data set.

## Three tiers of signal to extract

### Tier 1 — Direct safety/compliance signals

Explicit operational failures with regulatory implications. Highest-priority filter for SOPs Nobody Reads.

- "Didn't wear safety gear / PPE / hard hat"
- "No permits pulled"
- "Cut a wire / hit a pipe / damaged X and didn't tell me"
- "Left a hazardous mess / nails in the driveway"
- "Trespassed on neighbor's property"
- "Worker got hurt on my property"
- "OSHA / inspector showed up because of them"
- "Allergen / contamination / health code issue" (food service)
- "Insurance refused to cover X"

Each of these is a direct buying trigger. A landscaper with a one-star review mentioning "they damaged my neighbor's fence and just left" has a documented liability event in their public record.

### Tier 2 — Consistency and training gap signals

Operational inconsistency that points to a business running without internalized SOPs. Slightly softer signal than Tier 1 but more common.

- "Different person every visit knew different things"
- "The new guy didn't know what to do"
- "They did it differently than last time"
- "Couldn't answer my question"
- "Had to call the boss to find out"
- "The estimator didn't know what the foreman quoted"
- "The crew didn't have the right materials"
- "Said one thing on the phone, did another in person"
- "Last time was great, this time was terrible"

These describe a business that depends on individual workers' tacit knowledge rather than documented procedures. Exactly the customer SOPs Nobody Reads serves.

### Tier 3 — Trajectory signals (the differentiator)

The shape of the review timeline, not the content of any individual review. Most under-utilized signal in the data.

- **Improving:** Average rating climbs over 24 months. Stable shop, expanding capability. Probably not a buyer right now.
- **Declining:** Average drops over 24 months. Operational event happened — owner burnout, crew turnover, generational handoff gone wrong. Pizzeria pattern. Likely buyer if budget exists, but cash flow may be impaired.
- **Bimodal (5s and 1s, few 3s):** Inconsistent crew. Some jobs go great, some go badly. Highest-fit profile for SOPs Nobody Reads — the gap between best and worst worker is exactly what training closes.
- **Cluster of complaints in one month:** Recent operational event. Firing, injury, lost a key employee, switched suppliers. Worth a call within 60 days of the cluster — pain is acute.
- **Stale (no reviews in 6+ months) but high historical rating:** Shop is busy with repeat work, doesn't market, doesn't ask for reviews. Often the strongest financial position in the data set. Hard to reach but worth the call.
- **Stale and low historical rating:** Probably folding. Skip.

## Why trajectory beats sentiment

Sentiment analysis on individual reviews is commodity tech. Every BI tool does it. Trajectory analysis across a rolling 24-month window with shape detection (improving / declining / bimodal / clustered / stale) is genuinely differentiated.

It also gives you the strongest possible cold-call opener:

> "I noticed your reviews shifted around February — anything operational change there?"

That's not a cold call. That's a consultant call. The prospect's defensiveness drops because you've signaled you did real homework, and the question itself surfaces the buying trigger without you having to manufacture pain.

## What the skill should output

Per lead, ideally:

- Standard contact data (name, phone, address, site, hours)
- Average rating + total review count + rating distribution
- Trajectory classification (improving / declining / bimodal / clustered / stale-high / stale-low)
- 3–5 most recent reviews verbatim
- 3–5 highest-signal reviews from the past 24 months (Tier 1 or Tier 2 hits)
- Tier 1 hit count (safety/compliance)
- Tier 2 hit count (training gap)
- One auto-generated cold-call hook based on the strongest signal found

## What the skill should NOT do

- **Don't auto-generate the call script.** Hooks and triggers go in the lead record; the human calls. Auto-script generation produces the same generic pitch every cold-prospect AI tool produces, and it removes the human's ability to actually listen.
- **Don't pre-qualify too aggressively.** Trajectory signals are guidance, not gatekeepers. A "stale-high" listing might still be the best buyer in the queue — they don't market, they don't have an LMS, and a personal call lands hard.
- **Don't scrape against Google's ToS.** Use the Places API properly. The cost is real but trivial relative to a single closed deal.

## Build order

This is a future skill. Build order, when ready:

1. Manual workflow first (currently in progress). Learn what fields actually matter.
2. Wire up the Places API via the cablate MCP server. Already-spec'd in the chat history.
3. Build a Tier 1/Tier 2 keyword classifier on review text. Simple, deterministic, no LLM needed.
4. Build trajectory classifier on rating timeline. Pure stats, no LLM.
5. Use an LLM only for the synthesis step — the auto-generated cold-call hook — and only after the deterministic classification steps. The LLM should never see the raw review text without the classification context.

## When to build it

After 100 manual dials. Not before. The manual prep teaches you what signals actually predict good calls vs. bad calls. If you build the skill before you have that ground truth, you'll automate the wrong filters.

## Origin

Insight from May 5 lead-prep session. Loaded a 1940s pizzeria as a warm-up target and noticed the review trajectory told the entire story: declining service quality, allergen incident, missing-ingredient complaints, burned product. Reviews described a business in operational distress more clearly than any other public signal could have. The same signal applies to every owner-operated trades shop in the target list — and it's information no individual prospect would ever volunteer in a discovery call.
