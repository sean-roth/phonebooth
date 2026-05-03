# phonebooth

A sales cockpit for cold calling Chicago small businesses. One-person operation.

## What this is

A Laravel-based dashboard that combines:

- A browser-based softphone (Twilio Voice JS SDK)
- Lead management with manual CSV import
- Post-call notes capture (disposition, pain points, observations)

Discovery calls happen separately in Google Meet and are coached via Claude Desktop reading the Meet transcripts. The dashboard does not record cold calls.

## Why it exists

Sales is a learnable skill. The author is learning it under runway pressure and needs a system that:

1. Removes friction from picking up the phone (no disclosure script, no recording overhead)
2. Captures cold calls as Sean's own observations (the data that matters at the cold-call stage)
3. Captures discovery calls as Google Meet transcripts that Claude Desktop coaches against (the substantive conversations)
4. Costs nothing on bad days

## Status

Early-stage. Phase 1 (Monday-ready cockpit) is fully designed but not yet built. See `docs/specs/00-build-order.md` to start the build.

**If you're a Claude conversation picking this up: read `docs/handoff.md` first.**

## Stack

- Laravel (backend, dashboard)
- SQLite (local storage)
- Twilio (telephony only — no recording in Phase 1)
- Google Meet (discovery call hosting + recording, handled outside phonebooth)
- Claude Desktop with filesystem MCP (discovery-call coaching feedback)

## Repository layout

```
phonebooth/
├── docs/
│   ├── handoff.md       # Read first if you're a Claude picking this up
│   ├── specs/           # Build specifications (12 specs total, 00-11)
│   │   ├── 00-build-order.md
│   │   ├── 01-architecture.md
│   │   ├── 02-data-model.md
│   │   ├── 03-routes-controllers.md
│   │   ├── 04-twilio-integration.md
│   │   ├── 05-whisper-claude-integration.md   # STUB — pipeline removed per spec 11
│   │   ├── 06-targeting-brief.md
│   │   ├── 07-logging-and-events.md
│   │   ├── 08-verification-checklist.md
│   │   ├── 09-claude-desktop-coaching.md       # Discovery-call coaching workflow
│   │   ├── 10-legal-compliance.md              # STUB — recording removed per spec 11
│   │   └── 11-recording-pivot.md               # Documents the architecture change
│   └── skills/
│       ├── 01-jeb-blount.md                    # Cold-call mechanics
│       └── qa-passes/SKILL.md                  # QA review skill (installable in Claude Desktop)
├── app/                 # Laravel application code (added during build)
├── resources/           # Frontend assets (added during build)
└── routes/              # Route definitions (added during build)
```

## Architecture in one diagram

```
Cold call workflow:
  Browser cockpit → WebRTC → Twilio → lead's phone
  After hangup: Sean writes notes (disposition, pain points)

Discovery call workflow:
  Google Meet → recording handled by platform → transcript exported
  Sean saves transcript → Claude Desktop reads via filesystem MCP
  Claude generates coaching → writes feedback file
  Sean reads feedback → refines for next call
```

## License

Private. All rights reserved.
