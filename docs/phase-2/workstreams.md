# Phase 2 — Workstreams and Open Questions

## How to use this doc

The running backlog of Phase 2 work, organized by tier. Each tier maps to a user-facing milestone, not an architectural layer.

Reference items by ID (e.g. "let's work on T1.3") in future conversations. Items move between tiers, get split, or get retired as the picture sharpens.

For settled decisions, see `decisions-log.md`. This document is for what's still open.

---

## The priority lens

The constraint is runway. Every component in Phase 2 either directly increases conversations with right-fit prospects, or it doesn't. The honest priority isn't P0/P1/P2 — it's *"does this get me on the phone with more right-fit contractors faster, or does it feel productive while delaying the conversation?"*

Through that lens, five things matter most for Phase 2:

1. **Lead enrichment quality** — a great list of 100 beats a mediocre list of 1,000
2. **Cockpit functioning end-to-end with Twenty** — so dialing actually happens
3. **Pre-call brief content** — changes what gets said when they pick up
4. **The opener** — single biggest determinant of pickup-to-conversation
5. **Fast disposition capture** — fuels follow-up, which compounds

Everything else is downstream of these or operational.

---

## A meta-warning

Phase 2 architecture work is itself at risk of being the productivity-feeling avoidance pattern Sean has flagged before — build tasks instead of dial tasks, dressed up as essential infrastructure. The architecture is sound. The danger is treating this document as a checklist of work that justifies not picking up the phone.

The corrective is in the tier structure: build the smallest viable Tier 1 to resume calling, then dial 50–100 calls before specing Tier 2. Don't write Tier 2 specs until Tier 1 hurts.

---

## Tier 1 — First Dial Possible

The minimum to resume calling with the new Twenty-integrated cockpit. Single-line dialing only — parallel can wait.

### T1.1 Stand up Twenty on joi
Docker compose + Postgres + admin login. ~1 day. Pin a stable version; don't track main.

### T1.2 Validate Twenty data model
Hands-on poking through UI + GraphQL. Confirm custom field types, character limits, JSON column behavior, relation patterns. ~2–3 hours. Blocks T1.3.

### T1.3 Lock enrichment field list
Decide which fields are standard / custom Twenty fields / JSON, on Companies and People. ~1–2 hours of conversation. Blocked by T1.2. *This is where the next conversation goes.*

### T1.4 Decide MCP server vs direct GraphQL
For the enrichment sidecar AND for phonebooth. MCP is more ergonomic; GraphQL is more proven. Could split — MCP for sidecar, GraphQL for phonebooth. ~1 hour decision. Blocks T1.5–T1.7. Depends on S1.

### T1.5 Auth pattern phonebooth ↔ Twenty
API key, OAuth, or other. ~1 hour. Blocked by T1.4.

### T1.6 Build minimal enrichment sidecar (v0)
Claude Code orchestrator: Maps query → 20–50 cleaned leads in Twenty. Simple linear scoring. No fancy review analysis yet. ~1 day. Blocked by T1.3, T1.4.

### T1.7 Phonebooth reads call queue from Twenty
Cockpit fetches today's leads, displays as queue. ~half-day. Blocked by T1.5.

### T1.8 Pre-call brief renders in cockpit
Lead loads → Claude API generates 60-second brief → display in panel. ~half-day. Blocked by T1.7. Brief content is F1.

### T1.9 Disposition push to Twenty
Post-call form writes a Conversation record (or Note — depends on T1.3) attached to the Person. ~half-day. Blocked by T1.5.

### T1.10 First dial test
Sean places 10 calls using the integrated system end-to-end. Reveals friction. 90 minutes. Blocked by T1.6–T1.9.

---

## Tier 2 — Productive Calling at Volume

What gets added once Tier 1 has been exercised on 50–100 real dials. Don't spec until Tier 1 hurts.

### T2.1 Twilio Conference + AMD spike
2–3 hour proof-of-concept. Document quirks. Blocks T2.2.

### T2.2 Parallel dialing spec
Full spec for 3-line parallel via Conference + AMD. ~4 hours writing. Blocked by T2.1.

### T2.3 Parallel dialing build
Implementation. ~2–3 days. Blocked by T2.2.

### T2.4 Number rotation strategy
Round-robin across 3 Chicago numbers (312, 773, 708 or similar). Per-number dial-count tracking. Logic for retiring flagged numbers. ~half-day. Blocked by T2.3.

### T2.5 AMD failure mode UX
What happens when AMD is wrong. Override button? Audio cue? ~half-day. Blocked by T2.3.

### T2.6 Voicemail drop infrastructure
Pre-recorded VM dropped on AMD-detected voicemails. Tracks `vm_dropped` disposition. ~half-day. Blocked by T2.3. Script in F2.

### T2.7 Federal DNC scrub integration
Pre-dial DNC check. Block + flag in Twenty. ~half-day.

### T2.8 Stats dashboard v1
Three panels (today / week / month). Conversation count + meetings booked as headline metrics. ~1 day. Blocked by T1.9.

---

## Tier 3 — Sustainable Operation

What's needed by the time Sean is delivering for client #1 and dialing for client #2.

### T3.1 AI-drafted follow-up email
Post-hangup, Claude generates email draft from dispo notes. Sean copies into Gmail. ~half-day. Blocked by T1.9.

### T3.2 LinkedIn message draft
Same as T3.1 for LinkedIn connect + follow-up. ~2 hours. Blocked by T1.9.

### T3.3 Disposition-based callback scheduling
Auto-create Task in Twenty for the right cadence (3 days for soft yes, 2 weeks for "send info," 90 days for "stay in touch"). Cockpit queue surfaces due callbacks alongside new leads. ~half-day. Blocked by T1.9.

### T3.4 Discovery booking → calendar handoff
When dispo = `discovery_booked`: Calendly link in follow-up email? Google Calendar API call to create the meeting? Manual entry? Decide. ~half-day depending on choice.

### T3.5 Voicemail voice decision
Sean recorded vs Twilio Polly. Sean's voice is more authentic but pricier to iterate. ~2 hours including recording. Blocked by F2.

### T3.6 Twenty backup strategy
Postgres backup cadence + offsite copy + restore drill. ~half-day. Blocked by T1.1.

### T3.7 Twenty version pinning policy
Document production version + upgrade procedure. Twenty moves fast at v0.x; uncontrolled upgrades break integrations. ~1 hour. Blocked by T1.1.

### T3.8 Phonebooth → Twenty rate-limit handling
What does phonebooth do if Twenty's API rate-limits us? Queue + retry? Probably irrelevant at solo volume; address only if hit.

---

## Tier 4 — Deferred

Explicitly not now. Documented so we don't relitigate.

### T4.1 Multi-user auth
Defer until first sales hire.

### T4.2 Email send automation
Manual Gmail copy-paste works fine at solo volume. Direct send introduces deliverability + compliance complexity.

### T4.3 Apollo integration
Wrong ICP for current Phase 2 target. Re-enters for office-staffed contractors or property managers.

### T4.4 Lead scoring sophistication
Linear weighted scoring is enough. Don't ML-ify until 1000+ dialed leads with conversion data.

---

## Parallel content workstreams

These are content questions, not architecture. Often run concurrently through the Researcher → Analyst → Engineer flow.

### F1 Pre-call brief generation prompt
The Claude prompt that turns enrichment into the 60-second brief. Sections, tone, hooks. ~2 hours design + iteration. Concurrent with T1.7. Worth iterating after first 50 calls based on which hooks actually convert.

### F2 Voicemail drop script
18-second VM content for contractor ICP. Hook + value prop + callback ask. ~1 hour. Concurrent with T2.6.

### F3 The cold call opener
10–15 second opener for when an electrician/plumber/landscaper picks up. The thing said first. Single biggest determinant of pickup-to-conversation rate. Iterative — workshop content, test, refine. **Status unknown:** confirm whether this is happening through Researcher/Analyst flow or surfaces here as a workstream.

### F4 Disposition vocabulary
The standard list of call dispositions phonebooth tracks (`no_answer`, `voicemail`, `gatekeeper`, `wrong_number`, `callback_requested`, `interested`, `not_interested`, `do_not_call`, `discovery_booked`, etc.). Phase 1 likely already has a vocab; needs review and Twenty mapping. ~30 minutes.

---

## Spikes still needed

Small investigations before specing dependent workstreams.

### S1 Twenty MCP server maturity check
How stable is it? Active dev? Real-world use? 30 minutes of reading + a quick install. Blocks T1.4.

### S2 Twilio Conference + AMD WebRTC behavior
See T2.1 — same investigation. Listed here for visibility.

### S3 Two-party consent ambiguity
Get a clearer read on whether non-persistent real-time STT genuinely violates IL Eavesdropping Act, or if there's case law making whisper-coach more workable than was framed earlier in this conversation. Not blocking; noted for honesty. If TPC is more workable than feared, whisper-coach re-enters the architectural conversation as a future option (probably Tier 4-equivalent). Effort: 1 hour reading or eventual 30-minute attorney consult.

---

## Status legend (for future reference)

When a workstream gets started, edit this doc with status. Suggested:

- **Not started** — default; no work begun
- **Spike in progress** — investigation underway
- **Spec in progress** — written design happening
- **Built** — code merged, in use
- **Retired** — cancelled or absorbed into another item; document why
