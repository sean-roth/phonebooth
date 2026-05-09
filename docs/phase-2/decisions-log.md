# Phase 2 Decisions Log

A running log of architectural and product decisions made during Phase 2 brainstorming. Includes both accepted directions and **explicitly rejected** ones, with reasoning, so we don't relitigate.

---

## Accepted

### Sean is the live voice on every call

**Decision:** No autonomous AI agent talks to prospects. Sean is on every cold call.

**Why:** The ICP (small contractors) uses mobile phones as the primary business line. AI-generated voice calls to mobile numbers require prior express consent under the TCPA (FCC declaratory ruling, February 2024). Penalties are $500–$1,500 per call with no cap, plus state stacking. Live human cold calling to business phones — even mobile — does not require the same consent for B2B. The legal-risk delta between AI-voice and live-voice for this ICP is too large to bridge.

### Twenty CRM as system of record

**Decision:** Install Twenty on joi (the Linux server). Twenty becomes the source of truth for contacts, activities, dispositions, and pipeline data. Phonebooth becomes the calling layer that reads from and writes to Twenty.

**Why:** Migration cost compounds the longer it's delayed. Building phonebooth's local schema as if it's the CRM means painful ETL later. Standing Twenty up now is roughly a half-day of work. The data portability win is large; the integration is contained. Twenty is open-source, self-hosts cleanly, and has a GraphQL API.

### Parallel dialing via Twilio Conference + AMD

**Decision:** Extend phonebooth to dial 3 numbers simultaneously using Twilio's Conference + Answering Machine Detection primitives. Not Nooks/Orum.

**Why:** Phonebooth already uses Twilio. Pay-as-you-go cost model (~$5–10 on a heavy day, $1.15/month idle) matches the runway constraint. Premium dialers are $5K/year/seat — not appropriate at this scale. The DIY architecture is contained: new endpoints under `/calls/parallel`, a Conference name field on the Call model, an AMD webhook handler.

### 3 lines, not 7

**Decision:** Start at 3 parallel lines. Scale up only if pickup data supports it.

**Why:** At ~5–10% B2B connect rates, 3 lines yields ~2.5x conversation rate vs single-line with sub-1% abandoned-call rate. 7 lines is spam-flag and reputation risk for a brand-new outbound motion. Once numbers are flagged "Spam Likely," pickup rate collapses and DIDs have to be replaced at $10–15 each.

### Pre-call AI brief replaces whisper coach

**Decision:** A 60-second Claude-generated brief renders in the cockpit when a lead loads. No real-time AI listening during the call.

**Why:** Illinois Eavesdropping Act (two-party consent) makes real-time STT a legal exposure even with non-persistent buffers. Pre-call briefs achieve most of the same prep value without recording anything. Sean reads the brief in 30 seconds before dialing.

### Stats dashboard: three views, no XP

**Decision:** Today / This Week / This Month. Conversation count and meetings booked are the headline metrics. No leveling, achievements, streaks, or RPG mechanics.

**Why:** Goodhart's law. Gamifying dial counts produces poor dialing to hit dial counts. The metrics that survive are downstream of dial *quality* — conversations and meetings booked. An aesthetic styling pass on the same data (captain's-log treatment, Instrument Serif headers) is fine; new mechanics aren't.

### Lead enrichment as a sidecar (Claude Code + skills)

**Decision:** Enrichment runs as a separate orchestrator using Claude Code with Google Maps, Firecrawl, and Twilio Lookup skills. Not as a Laravel job inside phonebooth. Writes directly to Twenty.

**Why:** Keeps phonebooth focused on calling. Enrichment can be invoked manually or scheduled. Skills are composable. Phonebooth doesn't need to know how leads got into Twenty.

### Google Maps official API over scraping

**Decision:** Use Google Places API (~$0.03–0.05/lead fully detailed) rather than scraping Maps.

**Why:** At 100–200 leads/batch volume, official API costs ~$5/batch. Scraping is against Google's ToS, data quality is variable, and legal/account-suspension risk isn't worth saving a few dollars per batch.

---

## Rejected

### Autonomous AI voice calling

**Considered:** Bland, Retell, Synthflow, Vapi, Air AI as the live voice on cold calls.

**Rejected because:** TCPA exposure on mobile-heavy ICP. The consent-first pattern (email/LinkedIn opt-in → AI calls only consenting prospects) is workable in theory but if a prospect engaged with the email, you can close the meeting in email. AI voice doesn't add value for the kind of buyer who needs voice contact to commit.

### Real-time whisper coach (live AI listening)

**Considered:** Deepgram + Claude streaming during calls, Nooks/Orum-style live coaching that listens to the rep and surfaces objection responses in real time.

**Rejected because:** Illinois two-party consent. Real-time STT counts as "recording" under the Eavesdropping Act regardless of persistence. Pre-call briefing achieves most of the prep value legally.

### Premium parallel dialers (Nooks, Orum, Kixie)

**Considered:** Nooks (~$5K/year), Orum (~$5K/year), Salesfinity, Kixie (~$35–95/seat/mo), ServiceBell.

**Rejected because:** Cost. The existing Twilio integration covers ~80% of what these tools wrap. The remaining 20% (number reputation monitoring, advanced analytics, virtual sales floor) doesn't matter at solo scale.

### Apollo as primary lead source for Phase 2

**Considered:** Apollo or ZoomInfo for contact discovery.

**Rejected because:** Wrong ICP fit. Owner-operators of small contractors aren't on LinkedIn polishing VP Operations titles. Google Maps + website scraping is the right source for this audience. Apollo re-enters the picture for a future ICP (commercial property managers, larger GCs, office-staffed contractors).

### CRM-from-scratch in phonebooth

**Considered:** Building phonebooth's lead/contact/activity model into a fuller CRM-like surface to delay Twenty.

**Rejected because:** Twenty already exists, is open-source, and self-hosts cleanly. Building CRM features in phonebooth is yak-shaving. Phonebooth stays focused on calling. Twenty handles contacts, activities, opportunities, and pipeline.

### Multi-user auth, email sending automation, web admin UI for templates

**Rejected (for now) because:** Solo operator. Each of these earns its place at 5+ clients or a team, not before. Drafts get written by Claude, copied into Gmail, sent manually. Templates live as markdown files in the repo, edited directly.

---

## Open Questions

These aren't decisions yet. Each needs a small spike or a dedicated brainstorm before specifying.

1. **Twenty's API rate limits at our call volume.** Ceiling on writes per minute? Does it accommodate 100+ enrichment writes in a batch?
2. **Twenty's data model fit for enrichment fields.** Custom fields? JSON columns? Or do we adapt our schema to theirs?
3. **Auth between phonebooth and Twenty.** API key, OAuth, or something else? Where does the secret live?
4. **Twilio Voice JS SDK + Conference + AMD behavior.** Audio routing, kill-others timing, edge cases. Worth a spike before specing parallel dialing.
5. **Voicemail drop architecture.** High VM rate expected for this ICP. Script length, voice (Sean's recording vs AI-generated vs Twilio Polly), legal posture (still a "call" under FCC; rules apply).
6. **Federal DNC API integration.** Free tier, rate limits, scrub frequency.
7. **Where leads vs contacts vs companies vs opportunities live in Twenty.** A landscaping business is a company; the owner is a contact; the cold-call is an activity; a discovery booked is an opportunity. Need to confirm Twenty's standard objects fit this model before specing the schema.
