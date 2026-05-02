# Handoff Notes

This document is for the next Claude conversation that picks up phonebooth — whether Designer (continuing spec work, evaluating field testing) or Engineer (doing the actual build on the OptiPlex). Read this first to get oriented.

## What phonebooth is

A sales cockpit for Sean to cold-call Chicago small businesses. Browser-based softphone (Twilio Voice JS SDK) + lead management + automatic call recording + local transcription (faster-whisper) + Claude-powered coaching feedback against sales frameworks. All in one Laravel dashboard running on Sean's OptiPlex 9020.

It exists because Sean is learning sales under runway pressure. He has anxiety about cold calling. The system removes every form of friction except picking up the phone, and produces structured coaching after every call. The pain-points field on every call is also doing customer discovery — patterns across 50+ calls reveal what to productize.

Phase 1 scope is deliberately small: leads list, cockpit (one call at a time), call detail with transcript and coaching. No Twenty CRM yet (Phase 2). One sales framework (Jeb Blount). Manual lead briefs. Pay-as-you-go costs (~$5-25/month at Phase 1 volume).

## Where things are

```
phonebooth/
├── README.md
├── docs/
│   ├── handoff.md                              ← you are here
│   ├── specs/
│   │   ├── 00-build-order.md                   ← Engineer entry point
│   │   ├── 01-architecture.md                  ← system overview
│   │   ├── 02-data-model.md                    ← SQLite schema (leads, calls)
│   │   ├── 03-routes-controllers.md            ← every HTTP route + form
│   │   ├── 04-twilio-integration.md            ← softphone + recording
│   │   ├── 05-whisper-claude-integration.md    ← post-call pipeline
│   │   ├── 06-targeting-brief.md               ← Phase 1 sales brief
│   │   ├── 07-logging-and-events.md            ← logs + events table
│   │   └── 08-verification-checklist.md        ← MUST READ before relying on 04/05
│   └── skills/
│       └── 01-jeb-blount.md                    ← v1 coaching skill prompt
```

## Project state at handoff

**Built:** nothing. The repo is spec-only. No Laravel app exists yet.

**Spec'd:** the entire Phase 1 system, end-to-end. Architecture, data model, routes, integrations (Twilio + Whisper + Claude), logging, and the v1 coaching skill. Three review passes caught and fixed real bugs (orchestrator non-idempotency, call_id race condition, audio playback misconfiguration, etc.).

**Verified against current docs:** very little. The Designer Claude wrote specs 04 and 05 from training-data memory. **Spec 08 lists every memory-derived detail that needs verification** — the Engineer should work through it during the relevant build steps.

**Open decisions:**
- Sales framework: locked to Jeb Blount for v1. The other five frameworks (SPIN, Sandler, Challenger, Hormozi, etc.) are roadmap.
- Industries to target: retailers + (something). Sean said "experiment, lead with web work as the wedge." First-sprint pick is open.
- Lead source: Google Maps Places API, manual list-building for Phase 0.

## The verification gap (most important context)

The Designer Claude was writing from memory, not from current docs, throughout the design conversation. This came up at the end. By that point, web access wasn't available in the conversation, so the gap was documented in spec 08 instead of fixed.

What this means concretely: specs 04 and 05 contain code samples that are *probably* correct but haven't been confirmed against current Twilio, Anthropic, or faster-whisper docs. The architecture is sound; specific class names, parameter shapes, model identifiers, and pricing figures may be stale.

The Engineer's first job in build steps 4, 6, and 7 is to work through spec 08 and verify before relying on the code. If anything is wrong, fix it in the spec and commit.

## How Sean works (collaboration notes)

Sean has a memory profile that captures most of this, but worth restating in case you don't have access:

- **Building is regulation.** Sean has explicitly said building is how he processes nervous energy and emotion. Don't try to talk him out of building things — but do help him see when a particular build is scope creep vs. genuine value.
- **He has explicitly asked Claude to push back when grounded in fact.** Don't just defer. Disagree honestly when the position holds up.
- **Runway is exhausted.** Every dollar matters. He's job-searching (W-2 primary) in a separate conversation while building this. Don't hint at expensive solutions casually.
- **Pattern: treats every good idea as something to build immediately.** Worth flagging when the conversation drifts toward "and we could also..." territory. The Phase 2 / Phase 3 framing is load-bearing — keep the urge to add scope channeled into roadmap items, not Phase 1 work.
- **He's planning a move to Chicago.** That's why phonebooth targets Chicago specifically — building geographic familiarity for the move alongside revenue.
- **Background:** ESL teacher (8500+ classes), screenwriter (MA in Creative Writing), runs SOPs Nobody Reads (compliance training platform on Laravel with cryptographic audit trails). Strong technical chops, but specifically asked for spec-led handoff to Engineer Claude rather than building everything himself.

## Working pattern: Designer → Engineer

We've been operating Designer→Engineer split:

- **Designer (this conversation, and probably you):** spec-level work. Architecture decisions, data model, written specifications. Output is markdown docs in `docs/specs/`.
- **Engineer (a different Claude on the OptiPlex via Claude Code or similar):** implementation. Reads the specs, writes Laravel code, runs tests. Output is committed code.

The handoff is the spec. Designer doesn't write code into the repo (other than examples within spec docs). Engineer doesn't make architectural decisions — if something isn't covered, ask Designer.

This split has worked well so far. Don't break it without a good reason.

## What the next conversation should probably do

Depends on which Claude you are.

### If you're Designer continuing where we left off

Likely scenarios:
1. **Sean has questions before starting the build.** Answer them, refine specs as needed. Don't add new scope.
2. **Sean wants to continue the Phase 2 design.** Pull from the "out of scope for Phase 1" sections across specs. Twenty integration, multiple frameworks, the Settings tab with cost dashboard, the territory tab.
3. **Sean is post-field-testing and wants to redesign.** Listen to what he learned, throw out what doesn't match reality, redesign Phase 2 from the field data.

In all three: keep the verification gap front-of-mind. If web tools are available in your turn, the highest-leverage thing you can do is verify spec 08's open items against current docs and update specs 04/05 directly.

### If you're Engineer on the OptiPlex

Read in this order:
1. `README.md`
2. `docs/handoff.md` (this file)
3. `docs/specs/00-build-order.md`
4. `docs/specs/08-verification-checklist.md` — internalize this before touching specs 04 and 05
5. The rest of the specs in numerical order

Build sequence is in spec 00. Work through it. Where the code samples are confirmed against docs (most of specs 02, 03, 06, 07), use them as-is. Where they're memory-derived (most of specs 04 and 05), verify before adopting. Update specs when you find issues; commit your fixes.

If something fundamental is broken (e.g., Voice JS SDK doesn't pass custom params through to TwiML), pause and surface it — don't work around it. The architectural assumption needs to be revisited.

### If you're Designer post-field-testing

Sean said early on: "I'll probably want to rebuild this system next weekend after some field testing." So this scenario is likely.

Things worth asking:
- What actually got used? What didn't?
- What was painful? What was friction-y?
- What surprised you?
- What did you find yourself reaching for that wasn't there?
- Of the patterns in the pain-points field, what's emerging?
- Did the Jeb Blount coaching feedback actually help, or feel generic?

Then decide: refactor Phase 1 in place, or rebuild from scratch with a sharper Phase 1 scope. Sean was pre-committing to "rebuild is fine" — the Phase 1 system is intentionally cheap to throw away. Lean into that if the data warrants.

## Costs and operational reality

Phonebooth runs on Sean's OptiPlex 9020 (32GB RAM, no GPU, Linux). Self-hosted, local network only for Phase 1. Twilio webhooks reach the OptiPlex via ngrok (free tier with rotating URLs, or paid for static).

Monthly costs at projected Phase 1 volume (10 calls/day average):
- Twilio: ~$20 (number + minutes + recording)
- Anthropic: ~$5 (coaching feedback)
- ngrok: $0 (free tier acceptable for now)
- Hosting: $0 (OptiPlex)

At zero calls/day (a bad week): ~$1.15 (Twilio number rental).

The pay-as-you-go shape is intentional. Sean explicitly didn't want subscription costs that would punish bad days.

## What's deliberately not built

The "out of scope for Phase 1" lists across specs are deliberate, not oversights:

- Twenty CRM (Phase 2)
- Pre-call brief auto-generation (Phase 2)
- Multiple coaching frameworks (Phase 2)
- Cost tracking dashboard UI (Phase 2 — events table has the data)
- Audit hash chain (Phase 2)
- MCP server for Claude Desktop (Phase 2)
- Pretty UI (Phase 2)
- Apollo / Google Maps API integration (Phase 2)
- Territory tab with neighborhood context (Phase 2)
- Pain-points pattern recognition (Phase 2)
- Speaker diarization (Phase 2)
- Real-time transcription (out)
- Queue-based async processing (Phase 2)
- User accounts / auth (Phase 2 if ever needed)

Don't pull these forward into Phase 1 conversations. The whole point of the small Phase 1 scope is shipping by Monday.

## Repo etiquette

- Each meaningful spec change is its own commit with a descriptive message
- Commit messages have been descriptive ("Fix spec 04: pass call_id through TwiML for CallSid association") — keep that pattern
- Branch is `main`, no PR workflow for Phase 1 (single contributor)
- The repo is private; it has business logic and will eventually have lead data

## Final note

The Phase 1 system is good enough. It's not perfect — three review passes found real bugs, and the verification gap means specs 04 and 05 still need eyes-on. But Sean's stated criterion was "doesn't need to be perfect, I'll rebuild after field testing." Don't let perfectionism delay shipping.

The boulder is the calls themselves. Everything in this repo exists to make picking up the phone Monday morning easier than not picking it up. Keep that in mind when making tradeoff calls.

Build well.
