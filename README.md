# phonebooth

A sales cockpit for cold calling Chicago small businesses. One-person operation.

## What this is

A Laravel-based dashboard that combines:

- A browser-based softphone (Twilio Voice JS SDK)
- Lead management with manual CSV import
- Automatic call recording via Twilio
- Local transcription via faster-whisper
- Claude-powered coaching feedback against sales frameworks
- Pain-points capture on every call (the underrated long-game data)

The goal is to make the moment of "I am about to pick up the phone" frictionless and the moment after "I just hung up" reflective.

## Why it exists

Sales is a learnable skill. The author is learning it under runway pressure and needs a system that:

1. Removes every form of friction except picking up the phone
2. Captures every call as data for self-coaching
3. Captures owner pain points as data for product discovery
4. Costs nothing on bad days (pay-as-you-go everything)

## Status

Early-stage. Phase 1 (Monday-ready cockpit) is fully designed but not yet built. See `docs/specs/00-build-order.md` to start the build.

**If you're a Claude conversation picking this up: read `docs/handoff.md` first.**

## Stack

- Laravel (backend, dashboard)
- SQLite (local storage)
- Twilio (telephony, recording)
- faster-whisper (local transcription, Python subprocess)
- Claude API (coaching feedback generation)

## Repository layout

```
phonebooth/
├── docs/
│   ├── handoff.md       # Read first if you're a Claude picking this up
│   ├── specs/           # Build specifications (architecture, data model, integrations)
│   │   ├── 00-build-order.md
│   │   ├── 01-architecture.md
│   │   ├── 02-data-model.md
│   │   ├── 03-routes-controllers.md
│   │   ├── 04-twilio-integration.md
│   │   ├── 05-whisper-claude-integration.md
│   │   ├── 06-targeting-brief.md
│   │   ├── 07-logging-and-events.md
│   │   └── 08-verification-checklist.md   # Verify memory-derived API details
│   └── skills/          # Coaching skill prompts (one per sales framework)
│       └── 01-jeb-blount.md
├── app/                 # Laravel application code (added during build)
├── resources/           # Frontend assets (added during build)
└── routes/              # Route definitions (added during build)
```

## License

Private. All rights reserved.
