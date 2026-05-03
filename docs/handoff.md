# Handoff Notes

This document is for the next Claude conversation that picks up phonebooth — whether Designer (continuing spec work, evaluating field testing) or Engineer (doing the actual build on the OptiPlex). Read this first to get oriented.

## What phonebooth is

A sales cockpit for Sean to cold-call Chicago small businesses. Browser-based softphone (Twilio Voice JS SDK) + lead management + recording disclosure workflow + automatic call recording + dual-channel local transcription (faster-whisper) + Claude Desktop coaching via filesystem MCP. All in one Laravel dashboard running on Sean's OptiPlex 9020.

It exists because Sean is learning sales under runway pressure. He has anxiety about cold calling. The system removes every form of friction except picking up the phone, captures the work as data, and stays inside Illinois recording-consent law.

Phase 1 scope: leads list, cockpit (one call at a time, with mandatory disclosure script displayed), call detail with attributed transcript and coaching display. No Twenty CRM yet (Phase 2). One sales framework (Jeb Blount). Manual lead briefs. Pay-as-you-go costs (~$5-25/month, only Twilio).

## Where things are

```
phonebooth/
├── README.md
├── docs/
│   ├── handoff.md                              ← you are here
│   ├── specs/
│   │   ├── 00-build-order.md                   ← Engineer entry point
│   │   ├── 01-architecture.md
│   │   ├── 02-data-model.md
│   │   ├── 03-routes-controllers.md
│   │   ├── 04-twilio-integration.md
│   │   ├── 05-whisper-claude-integration.md    ← dual-channel transcription
│   │   ├── 06-targeting-brief.md
│   │   ├── 07-logging-and-events.md
│   │   ├── 08-verification-checklist.md        ← MUST READ before relying on 04
│   │   ├── 09-claude-desktop-coaching.md       ← Sean reads this for MCP setup
│   │   └── 10-legal-compliance.md              ← Illinois consent — non-optional
│   └── skills/
│       └── 01-jeb-blount.md                    ← v1 coaching skill (loaded by Claude Desktop)
```

## Project state at handoff

**Built:** nothing. The repo is spec-only.

**Spec'd:** the entire Phase 1 system. Eleven specs (00-10) plus the Jeb Blount skill. Architecture, data model, routes, integrations, logging, coaching workflow, legal compliance.

**Architecture (final):**

- Cockpit displays disclosure script at the top of every call (legal requirement per spec 10)
- Dashboard handles calls and recording; recording auto-deletes if lead declines disclosure
- Dashboard splits stereo recordings into two mono files (ffmpeg) and runs Whisper twice — once per channel
- Merges segments by timestamp into an attributed transcript: `[00:14] SEAN: ...` / `[00:18] LEAD: ...`
- Writes transcript markdown to `storage/app/coaching/transcripts/{call_id}.md`
- Sean uses Claude Desktop separately with filesystem MCP to read transcripts and write coaching to `storage/app/coaching/feedback/{call_id}.md`
- Dashboard reads coaching feedback files at display time

**Verified against current docs:**

- Illinois recording law (verified via web search this session — confirms all-party consent, AI transcription needs disclosure)
- Twilio + faster-whisper + ngrok details — NOT verified, see spec 08

The Engineer's first job in build steps 4 and 6 is to work through spec 08 and verify before relying on the code samples in specs 04 and 05.

## The full design history at this handoff

This system went through several design corrections that future Claudes should know about:

1. **Original:** dashboard hits Anthropic API for coaching (rejected — cost, complexity)
2. **Pivot 1 (mid-conversation):** dashboard writes transcripts; Claude Desktop reads via MCP and writes feedback (current architecture)
3. **Late catch:** dual-channel mixing to mono was discarding speaker attribution. Coaching quality would have been generic. Fixed in spec 05 — channels split and processed separately.
4. **Late catch:** Illinois all-party consent law was never addressed in the original design. Recording without disclosure is a felony. Added spec 10 with disclosure script, declined_recording disposition, and auto-delete-on-decline.

The repo's commit history shows the evolution. If specs disagree with each other on details, the higher-numbered or later-committed spec should generally win — design corrections came late.

## How Sean works (collaboration notes)

- **Building is regulation.** Sean processes nervous energy by building. Don't try to talk him out of building things — but flag scope creep.
- **Push back when grounded in fact.** Sean has explicitly asked for this. Don't just defer.
- **Runway is exhausted.** Every dollar matters. He's job-searching W-2 in a separate conversation.
- **Pattern: treats every good idea as something to build immediately.** Worth flagging when conversation drifts toward "we could also..." territory.
- **Planning a move to Chicago.** That's why phonebooth targets Chicago specifically.
- **Background:** ESL teacher (8500+ classes), screenwriter (MA in Creative Writing), runs SOPs Nobody Reads. Strong technical chops; specifically asked for spec-led handoff.
- **Working style:** Sean prefers stripped-down systems where the system itself is observable. The phonebooth's many tabs and features were a step away from this — future iterations may push back toward simpler.

## Working pattern: Designer → Engineer

- **Designer:** spec-level work in markdown
- **Engineer:** implementation, reads specs, writes code

Designer doesn't write code into the repo. Engineer doesn't make architectural decisions — if something isn't covered, ask Designer.

## What the next conversation should probably do

### If you're Designer continuing where we left off

Likely scenarios:

1. **Sean has questions before starting the build.** Answer them. Don't add new scope.
2. **Sean wants to continue Phase 2 design.** Pull from "out of scope for Phase 1" sections.
3. **Sean is post-field-testing and wants to redesign.** Listen to what he learned.
4. **Sean wants to design a different system entirely.** That's fine — phonebooth is meant to be throwable.

In any scenario: if web tools are available, the highest-leverage thing you can do is run the spec 08 verification checklist against current Twilio and faster-whisper docs.

A future skill that might be worth building: structured QA passes with named pass types (consistency, traceability, dead code, drift detection). The vague "review again" instruction tends to produce vague review. Sean has flagged this as a pattern worth addressing.

### If you're Engineer on the OptiPlex

Read in this order:

1. `README.md`
2. `docs/handoff.md` (this file)
3. `docs/specs/00-build-order.md`
4. `docs/specs/10-legal-compliance.md` — internalize before any code
5. `docs/specs/08-verification-checklist.md` — internalize before specs 04 and 05
6. `docs/specs/09-claude-desktop-coaching.md` — what Sean does with Claude Desktop
7. The rest in numerical order

Build sequence in spec 00. Spec 10's disclosure section on the cockpit and the auto-delete-on-decline behavior are non-negotiable; build them in step 4-5. Spec 05's dual-channel splitting is non-negotiable; build it in step 6.

If something fundamental seems broken, pause and surface it. Don't work around legal-compliance gaps or speaker-attribution gaps; those affect what the system fundamentally is.

### If you're Designer post-field-testing

Sean has explicitly anticipated rebuilding. Likely scenario.

Ask:

- What got used? What didn't?
- Was the disclosure script natural to deliver? What was the decline rate?
- Was the dual-channel attribution actually useful? Did Claude Desktop coaching produce better feedback because of it?
- What did the pain_points data reveal?
- What surprised you?
- Did Twilio recording quality match what was expected? Any odd dropouts or distortions?
- Was Twenty CRM-ish features missed, or was the simple leads list enough?

Then decide: refactor in place or rebuild with sharper Phase 1 scope.

## Costs and operational reality

OptiPlex 9020, 32GB RAM, no GPU, Linux. Self-hosted, local network for Phase 1. Twilio webhooks reach via ngrok.

Monthly costs at Phase 1 volume:

- Twilio: ~$5-25 (number + minutes + recording)
- Anthropic: $0 (no API integration; coaching uses Claude Desktop subscription)
- ngrok: $0 (free tier) or $8 (static URL)
- Hosting: $0 (OptiPlex)

## What's deliberately not built (Phase 1)

- Twenty CRM (Phase 2)
- Pre-call brief auto-generation (Phase 2)
- Multiple coaching frameworks (Phase 2)
- Cost tracking dashboard UI (no API costs to track)
- Audit hash chain (Phase 2)
- Pretty UI (Phase 2)
- Apollo / Google Maps API integration (Phase 2)
- Territory tab (Phase 2)
- Auto pain-points pattern recognition (Phase 2 — Sean does manually in Claude Desktop)
- Speaker diarization beyond channel splitting (current handles 95% case)
- Real-time transcription (out)
- Auto-coaching trigger (Phase 2)
- Queue-based async processing (Phase 2)
- User accounts / auth (Phase 2 if ever needed)
- Pre-call automated TwiML disclosure message (Sean reads it himself in Phase 1)
- Multi-state legal compliance (Illinois only)
- Lead deletion UI (tinker for Phase 1)
- DTMF support for navigating phone trees (Phase 2 if needed)
- Emotional scaffolding for the calling work itself (Sean handles via journaling separately)

## What changed late and may have residual inconsistencies

Several specs were updated near the end of design to accommodate the Claude Desktop pivot, the dual-channel fix, and the legal compliance addition. The visible inconsistencies were caught and fixed in this round, but the engineer should be alert for:

- References to `coaching_feedback` or `coaching_framework` columns (should be removed everywhere — coaching is filesystem-based)
- References to "all eight specs" or "all nine specs" (should now read "all eleven specs" — 00-10)
- Claude API token counting in event payloads (removed; events table no longer tracks API costs)
- Cost tracking UI mentions (no API costs to track)

If you spot any of the above, fix them and commit.

## Repo etiquette

- Each meaningful spec change is its own commit with a descriptive message
- Branch is `main`, no PR workflow for Phase 1
- The repo is private

## Final note

The Phase 1 system is good enough. It's not perfect, but it's grounded in:

- Real legal verification (web search this session confirmed Illinois consent law)
- Architectural correction (Claude API → Claude Desktop MCP)
- Coaching quality fix (mono → dual-channel attribution)
- Legal protection (disclosure script + auto-delete)

Sean's stated criterion is "doesn't need to be perfect, I'll rebuild after field testing." That criterion is even more apt now that field testing will reveal real legal/UX/quality questions the design phase couldn't.

The boulder is the calls themselves. Everything in this repo exists to make picking up the phone Monday morning easier than not picking it up — and to keep that activity legal.

Build well.
