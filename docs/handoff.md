# Handoff Notes

This document is for the next Claude conversation that picks up phonebooth — whether Designer (continuing spec work, evaluating field testing) or Engineer (doing the actual build on the OptiPlex). Read this first to get oriented.

## What phonebooth is

A sales cockpit for Sean to cold-call Chicago small businesses. Browser-based softphone (Twilio Voice JS SDK) + lead management + automatic call recording + local transcription (faster-whisper) + Claude Desktop coaching via filesystem MCP. All in one Laravel dashboard running on Sean's OptiPlex 9020.

It exists because Sean is learning sales under runway pressure. He has anxiety about cold calling. The system removes every form of friction except picking up the phone, and produces structured coaching after every call (in Claude Desktop, not auto-generated). The pain-points field on every call is also doing customer discovery — patterns across 50+ calls reveal what to productize.

Phase 1 scope is deliberately small: leads list, cockpit (one call at a time), call detail with transcript and coaching display. No Twenty CRM yet (Phase 2). One sales framework (Jeb Blount). Manual lead briefs. Pay-as-you-go costs (~$5-25/month at Phase 1 volume — only Twilio, no API costs).

## Where things are

```
phonebooth/
├── README.md
├── docs/
│   ├── handoff.md                              ← you are here
│   ├── specs/
│   │   ├── 00-build-order.md                   ← Engineer entry point
│   │   ├── 01-architecture.md                  ← system overview
│   │   ├── 02-data-model.md                    ← SQLite schema (leads, calls, events)
│   │   ├── 03-routes-controllers.md            ← every HTTP route + form
│   │   ├── 04-twilio-integration.md            ← softphone + recording
│   │   ├── 05-whisper-claude-integration.md    ← Whisper pipeline (writes transcript files)
│   │   ├── 06-targeting-brief.md               ← Phase 1 sales brief
│   │   ├── 07-logging-and-events.md            ← logs + events table
│   │   ├── 08-verification-checklist.md        ← MUST READ before relying on 04
│   │   └── 09-claude-desktop-coaching.md       ← Claude Desktop MCP setup (Sean reads this)
│   └── skills/
│       └── 01-jeb-blount.md                    ← v1 coaching skill (loaded by Claude Desktop)
```

## Project state at handoff

**Built:** nothing. The repo is spec-only. No Laravel app exists yet.

**Spec'd:** the entire Phase 1 system, end-to-end. Architecture, data model, routes, integrations (Twilio + Whisper), logging, the v1 coaching skill, and the Claude Desktop coaching workflow.

**Architecture (final):**
- Dashboard handles calls, recording, transcription
- Dashboard writes transcript markdown to `storage/app/coaching/transcripts/{call_id}.md`
- Sean uses Claude Desktop (separately) with filesystem MCP to read transcripts and write coaching markdown to `storage/app/coaching/feedback/{call_id}.md`
- Dashboard reads coaching feedback files at display time

**Verified against current docs:** very little. The Designer Claude wrote specs 04 and 05 from training-data memory. **Spec 08 lists every memory-derived detail that needs verification** during build steps 4 and 6.

**Open decisions:**
- Sales framework: locked to Jeb Blount for v1. Other frameworks are roadmap.
- Industries to target: retailers + trades. Specific first-sprint pick is open.
- Lead source: Google Maps Places API (Phase 2), manual list-building for Phase 0.

## The verification gap

The Designer Claude was writing from memory throughout the design conversation. This came up at the end. By that point, web access wasn't available, so the gap was documented in spec 08 instead of fixed.

Specs 04 (Twilio) and 05 (Whisper) contain code samples that are *probably* correct but haven't been confirmed against current docs. The architecture is sound; specific class names, parameter shapes, and library APIs may be stale.

The Engineer's first job in build steps 4 and 6 is to work through spec 08 and verify before relying on the code. If anything is wrong, fix it in the spec and commit.

**Note: spec 08 used to also have an Anthropic API verification section. That's been removed because the architecture changed mid-design — the dashboard no longer integrates with Claude API. Coaching is done in Claude Desktop via filesystem MCP (spec 09). Spec 08 may still contain stale Anthropic content depending on whether it's been cleaned up.**

## The Claude API → Claude Desktop pivot

Late in the design conversation, Sean caught a regression. Earlier discussions had established that coaching would happen in Claude Desktop via MCP — but the spec had drifted into an Anthropic API integration in the dashboard.

The pivot back to MCP for coaching:
- **Saves money** (uses subscription, not API)
- **Simpler** (no API integration, no key management, no token counting, no cost tracking)
- **Better UX** (interactive coaching with follow-up questions, pattern recognition across calls)
- **Original mental model** (Sean's "Claude Desktop as second viewpoint" intuition was the right one)

This affected specs 05, 03, 00, README, handoff (this doc), and required a new spec 09. Specs 01, 02, 07, 08 may still have stale references to the API path that should be cleaned up during build (or left alone if not breaking — the engineer can use judgment).

## How Sean works (collaboration notes)

Sean has a memory profile that captures most of this, but worth restating:

- **Building is regulation.** Sean has explicitly said building is how he processes nervous energy and emotion.
- **He has explicitly asked Claude to push back when grounded in fact.** Don't just defer.
- **Runway is exhausted.** Every dollar matters. He's job-searching W-2 in a separate conversation.
- **Pattern: treats every good idea as something to build immediately.** Worth flagging when conversation drifts toward scope creep.
- **Planning a move to Chicago.** That's why phonebooth targets Chicago specifically.
- **Background:** ESL teacher (8500+ classes), screenwriter (MA in Creative Writing), runs SOPs Nobody Reads (compliance training platform on Laravel with cryptographic audit trails). Strong technical chops; specifically asked for spec-led handoff.

## Working pattern: Designer → Engineer

We've been operating Designer → Engineer split:

- **Designer:** spec-level work in markdown
- **Engineer:** implementation, reads specs, writes code

The handoff is the spec. Designer doesn't write code into the repo (other than examples within spec docs). Engineer doesn't make architectural decisions — if something isn't covered, ask Designer.

## What the next conversation should probably do

Depends on which Claude you are.

### If you're Designer continuing where we left off

Likely scenarios:
1. **Sean has questions before starting the build.** Answer them, refine specs.
2. **Sean wants to continue Phase 2 design.** Pull from "out of scope for Phase 1" sections.
3. **Sean is post-field-testing and wants to redesign.** Listen to what he learned.

In all three: keep the verification gap front-of-mind. If web tools are available, the highest-leverage thing you can do is verify spec 08's open items against current docs.

Also: if you notice stale references to "Claude API" or "Anthropic API" or "CoachingGenerator" in specs 01, 02, 07, or 08, those should be cleaned up. The architecture changed mid-design and not all specs were updated.

### If you're Engineer on the OptiPlex

Read in this order:
1. `README.md`
2. `docs/handoff.md` (this file)
3. `docs/specs/00-build-order.md`
4. `docs/specs/08-verification-checklist.md` — internalize before touching specs 04 and 05
5. `docs/specs/09-claude-desktop-coaching.md` — what Sean does with Claude Desktop
6. The rest of the specs in numerical order

Build sequence in spec 00. Step 7 is filesystem MCP setup for Claude Desktop (configuration, not code). Steps 4 and 6 require spec 08 verification first.

If something fundamental is broken (e.g., Voice JS SDK doesn't pass custom params through to TwiML), pause and surface it.

### If you're Designer post-field-testing

Sean said early: "I'll probably want to rebuild this system next weekend after some field testing." Likely scenario.

Ask:
- What got used? What didn't?
- Was the Claude Desktop coaching workflow actually used, or did Sean skip it?
- What did the pain_points data reveal?
- What surprised you?

Then decide: refactor in place or rebuild with sharper Phase 1 scope.

## Costs and operational reality

Phonebooth runs on Sean's OptiPlex 9020 (32GB RAM, no GPU, Linux). Self-hosted, local network for Phase 1. Twilio webhooks reach the OptiPlex via ngrok.

Monthly costs at projected Phase 1 volume:
- Twilio: ~$20 (number + minutes + recording)
- Anthropic: $0 (no API integration; coaching uses Sean's Claude Desktop subscription)
- ngrok: $0 (free tier)
- Hosting: $0 (OptiPlex)

The pay-as-you-go shape is intentional — no subscription costs that punish bad days.

## What's deliberately not built (Phase 1)

- Twenty CRM (Phase 2)
- Pre-call brief auto-generation (Phase 2)
- Multiple coaching frameworks via Claude Desktop project switching (Phase 2)
- Cost tracking dashboard UI (no API costs to track in Phase 1)
- Audit hash chain (Phase 2)
- Pretty UI (Phase 2)
- Apollo / Google Maps API integration (Phase 2)
- Territory tab with neighborhood context (Phase 2)
- Pain-points pattern recognition automation (Phase 2 — Sean does this manually in Claude Desktop for now)
- Speaker diarization (Phase 2)
- Real-time transcription (out)
- Auto-coaching trigger when transcript appears (Phase 2)
- Queue-based async processing (Phase 2)
- User accounts / auth (Phase 2 if ever needed)

Don't pull these forward into Phase 1 conversations.

## Repo etiquette

- Each meaningful spec change is its own commit with a descriptive message
- Branch is `main`, no PR workflow for Phase 1
- The repo is private

## Final note

The Phase 1 system is good enough. It's not perfect — three review passes found real bugs, the verification gap means specs 04 and 05 still need eyes-on, and the late-stage MCP pivot may have left stale references in specs 01, 02, 07, 08.

But Sean's stated criterion was "doesn't need to be perfect, I'll rebuild after field testing." Don't let perfectionism delay shipping.

The boulder is the calls themselves. Everything in this repo exists to make picking up the phone Monday morning easier than not picking it up.

Build well.
