# 01 — System Architecture

## Purpose of this document

Describes what phonebooth is, what it does, and how the pieces fit together. This is the doc the Engineer reads first to orient. Subsequent specs (data model, routes, integrations) elaborate on the boxes drawn here.

## Scope: Phase 1 (Monday-ready cockpit)

This document describes ONLY Phase 1. Phase 2+ exists conceptually but is not built. Phase 1 is deliberately minimal — the smallest system that supports a Monday morning calling sprint.

Phase 1 ships when these are working end-to-end:

1. Lead is loaded into the dashboard via CSV import
2. User opens the lead, reads the brief, clicks "Call"
3. Browser-based softphone connects to the lead's number via Twilio
4. User talks, hangs up
5. Twilio's recording webhook fires; recording URL is saved to the call row
6. User fills in disposition, pain points, notes; clicks Save
7. User clicks "Process Call" on the call detail page
8. Whisper transcribes the recording locally
9. Claude API generates coaching feedback against the chosen framework
10. Transcript and feedback display on the call detail page

That is the entire Phase 1 loop. Anything not on this list is out of scope for Monday.

## Explicitly out of scope for Phase 1

- Twenty CRM integration (all lead data lives in local SQLite for now)
- Pre-call brief auto-generation (briefs are written manually into the lead record)
- Multiple sales frameworks (one framework, one coaching skill, one button)
- Cost tracking dashboard
- Audit log / cryptographic chain
- MCP integration for Claude Desktop
- Authentication (runs on local network, single user)
- Pretty UI / styling beyond functional
- Apollo or Google Maps API integration (lead list is hand-built)
- Territory tab, Library tab, Settings tab — only Leads, Call, and Call Detail exist
- Voicemail handling, SMS, inbound calls

## High-level architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      User's laptop / OptiPlex                   │
│                                                                 │
│  ┌──────────────────┐         ┌────────────────────────────┐   │
│  │  Browser         │◄────────┤  Laravel app (port 8000)   │   │
│  │  - Leads list    │         │  - Routes & controllers    │   │
│  │  - Call page     │  HTTP   │  - SQLite database         │   │
│  │  - Call detail   │         │  - Whisper subprocess      │   │
│  │  - Voice JS SDK  │         │  - Claude API client       │   │
│  └────────┬─────────┘         └──────┬──────────┬──────────┘   │
│           │                          │          │              │
└───────────┼──────────────────────────┼──────────┼──────────────┘
            │                          │          │
            │ WebRTC                   │ HTTPS    │ HTTPS
            │ (audio)                  │ (API)    │ (webhooks)
            │                          │          │
            ▼                          ▼          │
   ┌────────────────┐         ┌─────────────────┐ │
   │   Twilio       │         │   Anthropic     │ │
   │   - Voice      │         │   - Claude API  │ │
   │   - Recording  │         └─────────────────┘ │
   │   - Webhooks   │─────────────────────────────┘
   └────────────────┘
```

## Components

### Laravel app
The single backend service. Runs on the OptiPlex on port 8000. Serves the dashboard HTML/JS, handles all backend logic, talks to SQLite, calls out to Whisper as a local subprocess, and calls the Claude API for coaching.

Why Laravel: it's home turf for the user, who already runs a Laravel platform. No new framework to learn.

### Browser dashboard
Single-user web UI served by Laravel. Three pages:
- **Leads list** (`/leads`) — table of all leads, CSV import, click row to enter Call page
- **Call page** (`/leads/{id}/call`) — lead info + brief on top, dialer in middle, post-call form on bottom. The cockpit.
- **Call detail** (`/calls/{id}`) — view a past call's transcript and coaching feedback

Built with whatever Laravel ships by default (Blade + Livewire if the engineer prefers, or vanilla Blade + JS). Voice JS SDK is loaded on the Call page.

### SQLite
Lives at `database/database.sqlite`. Two tables in Phase 1: `leads` and `calls`. See `02-data-model.md` for schema.

### Twilio
External service. Provides:
- A purchased Chicago phone number (312 or 773 area code)
- Voice JS SDK that turns the browser into a softphone
- Automatic call recording (configured via TwiML or REST API)
- Webhooks that fire on call events (especially `recording-status-callback`)

### Whisper
OpenAI's open-source speech-to-text model. Runs locally on the OptiPlex. Invoked as a subprocess from Laravel when the user clicks "Process Call." Input is an audio file downloaded from Twilio's recording URL; output is a text transcript.

Engineer should use the `whisper` Python CLI for Phase 1 simplicity. If GPU acceleration is unavailable, the `base` or `small` model is the right tradeoff for speed/quality on the OptiPlex 9020 MT.

### Claude API
External service. Called once per "Process Call" action. Receives the transcript plus the coaching skill prompt; returns markdown coaching feedback. Saved to the call row.

Model: `claude-sonnet-4-7` (current best, per the Anthropic SDK conventions). Engineer should pull this from a config value, not hardcode, so the model can be upgraded.

## Data flow: a single call, end to end

1. User imports CSV → leads created in `leads` table
2. User clicks lead → Call page loads with brief
3. User clicks "Call" → browser uses Voice JS SDK to initiate WebRTC call via Twilio
4. Twilio dials the lead's number, bridges audio
5. Conversation happens
6. User clicks "Hang Up" → Twilio ends call, generates recording
7. Twilio fires `recording-status-callback` webhook to Laravel
8. Laravel creates row in `calls` table with `twilio_call_sid`, `recording_url`, `started_at`, `duration_seconds`
9. User fills in disposition, pain points, notes → form POST updates the call row
10. User clicks "Process Call" on call detail page
11. Laravel downloads the recording from Twilio's URL → saves to `storage/recordings/{call_id}.mp3`
12. Laravel invokes Whisper subprocess on the file → captures stdout transcript
13. Laravel saves transcript to call row
14. Laravel sends transcript + coaching skill prompt to Claude API
15. Laravel saves coaching markdown to call row
16. Page refreshes → user sees transcript and coaching feedback

## Configuration / secrets

The Laravel `.env` file holds:

- `TWILIO_ACCOUNT_SID` — from Twilio console
- `TWILIO_AUTH_TOKEN` — from Twilio console
- `TWILIO_API_KEY_SID` — for Voice JS SDK token generation
- `TWILIO_API_KEY_SECRET` — for Voice JS SDK token generation
- `TWILIO_TWIML_APP_SID` — TwiML app for outbound calls
- `TWILIO_PHONE_NUMBER` — the purchased Chicago number
- `ANTHROPIC_API_KEY` — for coaching feedback generation
- `CLAUDE_MODEL` — defaults to `claude-sonnet-4-7`
- `WHISPER_MODEL` — defaults to `base`
- `WHISPER_PATH` — path to the `whisper` CLI binary

`.env.example` should be committed with all these keys present but values blank.

## Deployment / operating model

This runs on the OptiPlex 9020 MT on the user's home network. The user accesses it via browser at `http://localhost:8000` (or `http://optiplex.local:8000` from the laptop, if Bonjour/mDNS resolves).

For Phase 1: no auth, no SSL, no public exposure. The Twilio webhooks for recording-status-callback are the one inbound that needs to reach the OptiPlex from the public internet — solve this in Phase 1 with `ngrok` or `cloudflared` tunneling. The webhook URL goes into Twilio's recording-callback config. When the tunnel changes (free ngrok URLs rotate), update Twilio.

Production-grade tunneling, SSL, and dynamic DNS can be solved in Phase 2 if/when the system matures.

## Phase 2+ (out of scope, for context only)

- Twenty CRM stood up via Docker Compose; lead data migrates into Twenty; SQLite keeps coaching data only
- Multiple coaching frameworks selectable per call
- Pre-call brief auto-generation skill
- Settings tab with cost tracking, system health
- Audit log with hash chain
- Pretty UI pass
- MCP server exposing transcripts and feedback to Claude Desktop
- Territory tab with Google Maps + Firecrawl + neighborhood context
- Pain-points pattern recognition skill (Sunday review ritual)

These are roadmap. They are not Monday.
