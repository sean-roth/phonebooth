# phonebooth

A sales cockpit for cold calling Chicago small businesses. One-person operation.

## What this is

A Laravel-based dashboard that combines:

- A browser-based softphone (Twilio Voice JS SDK)
- Lead management with manual CSV import
- Automatic call recording via Twilio
- Local transcription via faster-whisper
- Coaching feedback via Claude Desktop (filesystem MCP)
- Pain-points capture on every call (the underrated long-game data)

The goal is to make the moment of "I am about to pick up the phone" frictionless and the moment after "I just hung up" reflective.

## Why it exists

Sales is a learnable skill. The author is learning it under runway pressure and needs a system that:

1. Removes every form of friction except picking up the phone
2. Captures every call as data for self-coaching
3. Captures owner pain points as data for product discovery
4. Costs nothing on bad days (pay-as-you-go everything; coaching uses existing Claude subscription)

## Status

Early-stage. Phase 1 (Monday-ready cockpit) is fully designed but not yet built. See `docs/specs/00-build-order.md` to start the build.

**If you're a Claude conversation picking this up: read `docs/handoff.md` first.**

## Stack

- Laravel (backend, dashboard)
- SQLite (local storage)
- Twilio (telephony, recording)
- faster-whisper (local transcription, Python subprocess)
- Claude Desktop with filesystem MCP (coaching feedback — uses Sean's existing subscription, no API costs)

## Repository layout

```
phonebooth/
├── docs/
│   ├── handoff.md       # Read first if you're a Claude picking this up
│   ├── specs/           # Build specifications
│   │   ├── 00-build-order.md
│   │   ├── 01-architecture.md
│   │   ├── 02-data-model.md
│   │   ├── 03-routes-controllers.md
│   │   ├── 04-twilio-integration.md
│   │   ├── 05-whisper-claude-integration.md
│   │   ├── 06-targeting-brief.md
│   │   ├── 07-logging-and-events.md
│   │   ├── 08-verification-checklist.md   # Verify memory-derived API details
│   │   └── 09-claude-desktop-coaching.md   # How Sean configures Claude Desktop
│   └── skills/          # Coaching skill prompts (loaded by Claude Desktop)
│       └── 01-jeb-blount.md
├── app/                 # Laravel application code (added during build)
├── resources/           # Frontend assets (added during build)
└── routes/              # Route definitions (added during build)
```

## Architecture in one diagram

```
Browser (cockpit page)
   ↓ WebRTC
Twilio (telephony, recording)
   ↓ webhook
Laravel dashboard
   ├── stores call data in SQLite
   ├── downloads recording locally
   ├── transcribes via faster-whisper subprocess
   └── writes transcript markdown to storage/app/coaching/transcripts/

Sean opens Claude Desktop separately
   ├── reads transcripts via filesystem MCP
   ├── reads Jeb Blount skill from docs/skills/
   ├── generates coaching markdown
   └── writes to storage/app/coaching/feedback/

Dashboard reads feedback files at display time
```

## License

Private. All rights reserved.
