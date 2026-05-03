# Handoff Notes

This document is for the next Claude conversation that picks up phonebooth — whether Designer (continuing spec work, evaluating field testing) or Engineer (doing the actual build on the OptiPlex). Read this first to get oriented.

## What phonebooth is

A sales cockpit for Sean to cold-call Chicago small businesses. Browser-based softphone (Twilio Voice JS SDK) + lead management + post-call notes. All in one Laravel dashboard running on Sean's OptiPlex 9020.

The dashboard does not record cold calls. Discovery calls happen separately in Google Meet and are coached via Claude Desktop reading the Meet transcript.

It exists because Sean is learning sales under runway pressure. He has anxiety about cold calling. The system removes friction from the cold-call workflow and surfaces coaching where it matters most — the discovery calls that contain the actual sales substance.

Phase 1 scope: leads list, cockpit (one call at a time), simple post-call notes form. No recording, no transcription, no Twenty CRM, no API integrations. Pay-as-you-go costs (~$5-17/month, only Twilio).

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
│   │   ├── 05-whisper-claude-integration.md    ← STUB (pipeline removed)
│   │   ├── 06-targeting-brief.md
│   │   ├── 07-logging-and-events.md
│   │   ├── 08-verification-checklist.md
│   │   ├── 09-claude-desktop-coaching.md       ← discovery-call workflow
│   │   ├── 10-legal-compliance.md              ← STUB (recording removed)
│   │   └── 11-recording-pivot.md               ← documents the change
│   └── skills/
│       ├── 01-jeb-blount.md                    ← cold-call mechanics
│       └── qa-passes/SKILL.md                  ← QA review skill
```

## Project state at handoff

**Built:** nothing. The repo is spec-only.

**Spec'd:** the entire Phase 1 system. Twelve specs (00-11) plus the Jeb Blount skill and the qa-passes skill.

**Architecture (current):**

- Cockpit dials leads via Twilio Voice JS SDK (no recording)
- Post-call form captures Sean's own observations (disposition, pain points, notes)
- Discovery calls happen in Google Meet (Sean schedules with the lead via email)
- Sean exports Google Meet transcripts to `storage/app/coaching/discoveries/`
- Claude Desktop reads transcripts via filesystem MCP, generates coaching, writes to `storage/app/coaching/feedback/`
- Dashboard reads coaching feedback files at display time (or doesn't display them — discovery feedback is keyed by lead, not by call row)

**Verified against current docs:**

- Illinois recording law (verified earlier in the design conversation; subsequently rendered moot by the recording-pivot decision)
- Twilio details — NOT verified, see spec 08

The Engineer's first job in build step 4 is to work through spec 08 and verify Twilio details before relying on the code samples in spec 04.

## The full design history at this handoff

This system went through five design corrections that future Claudes should know about:

1. **Original:** dashboard hits Anthropic API for coaching (rejected — cost, complexity)
2. **Pivot 1:** dashboard writes transcripts; Claude Desktop reads via MCP (current coaching mechanism)
3. **Catch:** dual-channel mixing to mono was discarding speaker attribution. Fixed in spec 05 — channels split and processed separately. (Subsequently rendered moot by pivot 2.)
4. **Catch:** Illinois all-party consent law required disclosure-and-consent workflow. Added spec 10. (Subsequently rendered moot by pivot 2.)
5. **Pivot 2 (final):** stop recording cold calls entirely; coach discovery calls only. Spec 11 documents this. The Whisper pipeline (spec 05) and the legal compliance layer (spec 10) became stubs.

The repo's commit history shows the evolution. If specs disagree with each other on details, the higher-numbered or later-committed spec should generally win.

## How Sean works (collaboration notes)

- **Building is regulation.** Sean processes nervous energy by building. Don't try to talk him out of building things — but flag scope creep.
- **Push back when grounded in fact.** Sean has explicitly asked for this. Don't just defer.
- **Runway is exhausted.** Every dollar matters.
- **Pattern: treats every good idea as something to build immediately.** Worth flagging when conversation drifts toward "we could also..." territory.
- **Planning a move to Chicago.** That's why phonebooth targets Chicago specifically.
- **Background:** ESL teacher (8500+ classes), screenwriter (MA in Creative Writing), runs SOPs Nobody Reads. Strong technical chops; specifically asked for spec-led handoff.
- **Working style:** Sean prefers stripped-down systems where the system itself is observable. The phonebooth's earlier drafts (with recording, transcription, dual-channel splitting, disclosure UI, auto-delete logic) were a step away from this. Pivot 2 brought it back to a much simpler shape.

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

If web tools are available, the highest-leverage thing you can do is run the spec 08 verification checklist against current Twilio docs.

### If you're Engineer on the OptiPlex

Read in this order:

1. `README.md`
2. `docs/handoff.md` (this file)
3. `docs/specs/00-build-order.md`
4. `docs/specs/11-recording-pivot.md` — understand what was removed and why
5. `docs/specs/08-verification-checklist.md` — internalize before spec 04
6. `docs/specs/09-claude-desktop-coaching.md` — what Sean does for discovery-call coaching
7. The rest in numerical order

Build sequence in spec 00. Specs 05 and 10 are stubs — don't implement anything from earlier drafts of those.

If something fundamental seems broken, pause and surface it.

### If you're Designer post-field-testing

Sean has explicitly anticipated rebuilding. Likely scenario.

Ask:

- What got used? What didn't?
- Were the cold calls easier without the disclosure script?
- Did discovery calls happen? How many? How did Google Meet's transcript quality work out?
- Was Claude Desktop coaching of discovery calls useful?
- What did the pain_points data reveal across cold calls?
- What surprised you?

Then decide: refactor in place, rebuild with sharper Phase 1 scope, or reconsider the cold-call recording decision.

## Costs and operational reality

OptiPlex 9020, 32GB RAM, no GPU, Linux. Self-hosted, local network for Phase 1. Twilio webhooks reach via ngrok.

Monthly costs at Phase 1 volume:

- Twilio: ~$5-17 (number + outbound minutes only; no recording)
- Anthropic: $0
- Google Workspace: $0 incremental (existing — needed for Meet recording)
- Claude Desktop: $0 incremental (existing subscription)
- ngrok: $0 (free tier) or $8 (static URL)
- Hosting: $0 (OptiPlex)

## What's deliberately not built (Phase 1)

- Twenty CRM (Phase 2)
- Pre-call brief auto-generation (Phase 2)
- Multiple coaching frameworks managed by the dashboard (Phase 2)
- Cost tracking dashboard UI (Twilio costs visible in their console)
- Audit hash chain (Phase 2)
- Pretty UI (Phase 2)
- Apollo / Google Maps API integration (Phase 2)
- Territory tab (Phase 2)
- Auto pain-points pattern recognition (Sean does manually in Claude Desktop)
- Auto-import of Google Meet transcripts (Sean does manually)
- Cold-call recording / transcription / coaching (removed per spec 11)
- Recording disclosure UI (removed per spec 11)
- Legal-compliance auto-delete logic (removed per spec 11)
- Real-time anything (out)
- Queue-based async processing (Phase 2)
- User accounts / auth (Phase 2 if ever needed)
- DTMF support for navigating phone trees (Phase 2 if needed)
- Emotional scaffolding for the calling work itself (Sean handles via journaling separately)

## Things to watch for in the specs

The recording pivot (spec 11) removed a lot. Watch for residual references that didn't get cleaned up:

- Any mention of recording in specs other than 04, 05, 10, 11
- Any Whisper / faster-whisper / ffmpeg / transcribe references
- Any disclosure-script or declined_recording references
- Any coaching_feedback / coaching_framework column references
- Any /calls/{call}/audio or /calls/{call}/process route references
- Any Anthropic API references

If you find any, fix them and commit. The qa-passes skill (`docs/skills/qa-passes/SKILL.md`) has a "dead-code / stale-reference" pass type designed for exactly this work.

## Repo etiquette

- Each meaningful spec change is its own commit with a descriptive message
- Branch is `main`, no PR workflow for Phase 1
- The repo is private

## Final note

The Phase 1 system is much smaller than it was earlier in the design process. That's the right direction. Sean's stated criterion is "doesn't need to be perfect, I'll rebuild after field testing." That criterion is most apt for the simplest possible Phase 1.

The boulder is the calls themselves. Everything in this repo exists to make picking up the phone Monday morning easier than not picking it up.

Build well.
