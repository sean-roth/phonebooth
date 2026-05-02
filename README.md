# phonebooth

A sales cockpit for cold calling Chicago small businesses. One-person operation.

## What this is

A Laravel-based dashboard that combines:

- A browser-based softphone (Twilio Voice JS SDK)
- Lead management with manual CSV import
- Automatic call recording via Twilio
- Local transcription via Whisper
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

Early-stage. Phase 1 (Monday-ready cockpit) under active build. See `docs/specs/` for build documentation.

## Stack

- Laravel (backend, dashboard)
- SQLite (local storage)
- Twilio (telephony, recording)
- Whisper (local transcription, OpenAI's open-source model)
- Claude API (coaching feedback generation)

## Repository layout

```
phonebooth/
├── docs/
│   ├── specs/      # Build specifications (architecture, data model, integrations)
│   └── skills/     # Coaching skill prompts (one per sales framework)
├── app/            # Laravel application code (added during build)
├── resources/      # Frontend assets (added during build)
└── routes/         # Route definitions (added during build)
```

## License

Private. All rights reserved.
