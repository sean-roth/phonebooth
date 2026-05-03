# 00 — Build Order

## Read this first if you're the Engineer

This document is the entry point. Read it, then read the specs in numerical order. Before writing any code, scan all twelve specs (00-11) end-to-end so the architecture makes sense as a whole.

**Critical: spec 08 lists every API detail in spec 04 that needs verification against current docs.** The Designer Claude wrote that spec from memory.

**Critical: there is no transcription, recording, or Anthropic API in Phase 1.** Spec 11 documents the architecture pivot that removed these. Cold calls are dialed and noted; discovery calls happen separately in Google Meet and are coached via Claude Desktop reading the Meet transcript.

**Critical: specs 05 (Whisper) and 10 (legal compliance) are now stubs.** They explain what was removed and why. Don't implement anything from earlier drafts of those specs.

## The mission

Get Sean to "first call placed through phonebooth" by Sunday night. Monday morning he picks up the dashboard cold and starts dialing. Coaching happens in Claude Desktop *after discovery calls*, not after cold calls.

## The specs

| # | Doc | What's in it |
|---|---|---|
| 00 | build-order.md | This file |
| 01 | architecture.md | System overview, scope, data flow |
| 02 | data-model.md | SQLite schema (simplified per spec 11) |
| 03 | routes-controllers.md | Every HTTP route, every form |
| 04 | twilio-integration.md | Browser softphone (verify against spec 08) |
| 05 | whisper-claude-integration.md | **STUB — pipeline removed per spec 11** |
| 06 | targeting-brief.md | Reference only — what Phase 1 is about |
| 07 | logging-and-events.md | Application logs + events table |
| 08 | verification-checklist.md | API details to verify before building |
| 09 | claude-desktop-coaching.md | Discovery-call coaching workflow |
| 10 | legal-compliance.md | **STUB — recording removed per spec 11** |
| 11 | recording-pivot.md | Documents the architecture change |

The skill in `docs/skills/01-jeb-blount.md` is loaded by Claude Desktop for cold-call mechanics review (Sean reviews his own notes against it). For discovery calls, consider adding `02-spin.md` or similar.

## Recommended build sequence

### Step 1: Scaffold (1 hour)

```bash
laravel new phonebooth --git
cd phonebooth
composer require twilio/sdk
npm install @twilio/voice-sdk
```

Create directories: `storage/app/coaching/discoveries/`, `storage/app/coaching/feedback/`. Confirm `php artisan serve` works.

Note: no `scripts/` directory needed (no Python). No `storage/app/recordings/` directory (no recording).

### Step 2: Data layer + logging foundation (1 hour)

Migrations and Eloquent models per specs 02 and 07:
- `create_leads_table` (spec 02)
- `create_calls_table` — note: **simplified schema per spec 11**, no recording columns
- `create_events_table` (spec 07)

Configure the three logging channels per spec 07. Create `app/Services/EventLogger.php`.

Run `php artisan migrate`. Seed test leads.

Validate: tables exist, EventLogger writes a test row.

### Step 3: Leads UI (2-3 hours)

LeadController with index/show/update + import. Views. CSV import.

Validate: import a CSV, click into a lead, edit the brief, save.

### Step 4: Twilio infrastructure (2-4 hours)

**Before writing code: work through spec 08.**

Set up Twilio account and ngrok per spec 04. Configure `.env`. Implement TwilioTokenController. Build the cockpit page (calls.create) — **no recording disclosure section** (removed per spec 11).

Disposition options per spec 03's enum (no `declined_recording`).

Add EventLogger calls per spec 07:
- `call_initiated` in `CallController::store()`
- `twilio_call_connected` in `TwilioTokenController::voice()`

Validate: load cockpit, click Call, talk to your own cell, hang up. Check events.

### Step 5: Call data flow (1 hour)

Implement CallController store/update. Build the post-call form. Implement the status webhook (no recording webhook).

Add `call_completed` event in CallController::update.

Validate: place a call, hang up, fill form, click Save. Tinker check on call row and events.

### ~~Step 6: Whisper pipeline~~ — REMOVED per spec 11

The original step 6 (Whisper installation, channel splitting, transcription) is gone. Skip directly from step 5 to what was step 7.

### Step 6 (was 7): Filesystem MCP setup for Claude Desktop (30 min - 1 hour)

**This is configuration on Sean's machine, not Engineer code.**

Engineer's job: confirm directory structure (`storage/app/coaching/discoveries/` and `storage/app/coaching/feedback/` exist), document the absolute paths Sean needs.

Sean's job (per spec 09):
1. Configure filesystem MCP in `claude_desktop_config.json` pointing at:
   - `storage/app/coaching/`
   - `docs/skills/`
2. Create "Phonebooth Coaching" Project in Claude Desktop
3. Add cold-call skill (Jeb Blount) and discovery-call skill (SPIN or similar) as project knowledge
4. Add the workflow note as system prompt
5. Test by saving a sample discovery transcript and asking Claude to coach it

Validate: Sean places a (test) cold call, marks disposition. Then separately, saves a fake discovery transcript to `storage/app/coaching/discoveries/test.md`, asks Claude Desktop to coach it, confirms feedback file appears in `feedback/`.

### Step 7 (was 8): Polish for Monday (1-2 hours)

- All error paths show useful messages AND record `error` events
- Test CSV import with weird rows
- Confirm ngrok URL is stable
- Place 3-4 test calls end-to-end

### Step 8 (was 9): Pre-Monday (Sunday evening)

- Sean populates ten-lead CSV (per spec 06)
- Imports them
- Writes brief for the first lead
- Goes to bed

## Total estimated time

11-15 hours of focused work. The recording pivot cut ~3-4 hours from the previous estimate.

## Critical paths

1. **Twilio account verification + number purchase.** Saturday evening.
2. **ngrok stability.** Free tier rotates URLs.
3. **Claude Desktop filesystem MCP setup.** Sean does Saturday or Sunday.

No more faster-whisper model download, no ffmpeg verification, no attorney consult required for cold-call recording compliance.

## Things fine to skip if time runs short

- Pretty styling
- "Add Lead" manual form
- Webhook signature verification on local dev
- Status webhook (just no-op endpoint that returns 200)
- Comprehensive error handling beyond obvious cases

## Things NOT fine to skip

- Spec 08 verification of API details before step 4
- Pain points field as required (spec 03)
- ngrok tunnel running
- Events table + EventLogger (spec 07)
- The four required EventLogger call sites (spec 07)

## When to ask for help

If any single step takes more than 2x its estimate, stop and surface it.

If spec 08's verification reveals something fundamentally broken architecturally, pause before working around it.

## A note on what changed

This build is much smaller than earlier drafts. The recording pivot (spec 11) removed:

- Whisper installation and channel splitting
- ffmpeg dual-channel verification
- Recording webhook handler and signature verification
- Audio proxy route
- Process Call orchestrator
- Recording disclosure UI
- Auto-delete-on-decline logic
- Twilio recording deletion API call
- Anthropic API integration

What's left is a clean dialer with notes. Discovery-call coaching is layered on separately via Google Meet + Claude Desktop, requiring no dashboard changes.

## A note on the Claude integration

There is no Claude API in this build. Spec 09 documents how Sean uses his Claude Desktop subscription via filesystem MCP for *discovery-call* coaching (not cold-call coaching).

## A note on the events table

When something breaks Monday morning, the first place to look is the events table. Tinker query for the call's events shows the timeline; Laravel logs show why a specific step failed.

## What success looks like Monday at 9 AM

Sean opens his laptop. He navigates to `localhost:8000/leads`. He sees ten Chicago retailers and trades. He clicks the first one. The brief is on the page. He puts on his headset.

The cockpit page loads. **No disclosure script** — just the lead's info and the dialer.

He clicks Call. The phone rings. Someone picks up.

Sean opens with his pitch directly: "Hi, this is Sean Roth, I do small AI and web projects for Chicago businesses..."

He talks. He hangs up. He fills in disposition, pain points, notes — his own observations, since there's no transcript. He clicks Save and Next.

Some calls book discovery calls. Sean schedules those in Google Meet for later in the week.

Later in the week, after a discovery call: Sean downloads the Google Meet transcript, saves it to `storage/app/coaching/discoveries/{lead-name}-{date}.md`, opens Claude Desktop, asks for coaching. Reads it. Refines.

Tomorrow's "what worked, what didn't" question gets answered for cold calls via Sean's own notes, and for discovery calls via Claude Desktop's framework-aware coaching.

That's the system. Build for that.
