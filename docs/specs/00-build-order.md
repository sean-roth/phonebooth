# 00 — Build Order

## Read this first if you're the Engineer

This document is the entry point. Read it, then read the specs in numerical order. Before writing any code, scan all six specs end-to-end so the architecture makes sense as a whole.

## The mission

Get Sean to "first call placed through phonebooth" by Sunday night. Monday morning he picks up the dashboard cold and starts dialing.

## The specs

| # | Doc | What's in it |
|---|---|---|
| 01 | architecture.md | System overview, scope, data flow |
| 02 | data-model.md | SQLite schema for `leads` and `calls` |
| 03 | routes-controllers.md | Every HTTP route, every form, every controller method |
| 04 | twilio-integration.md | Browser softphone with code examples |
| 05 | whisper-claude-integration.md | Post-call processing pipeline with code examples |
| 06 | targeting-brief.md | Reference only — what Phase 1 is about (not for Engineer) |

The skill in `docs/skills/01-jeb-blount.md` is loaded at runtime by the coaching pipeline.

## Recommended build sequence

This sequence gets working software at the end of each step. Do not skip ahead — each step validates the previous before adding complexity.

### Step 1: Scaffold (1 hour)

```bash
laravel new phonebooth --git
cd phonebooth
composer require twilio/sdk anthropic-php/anthropic-php
npm install @twilio/voice-sdk
```

Create directory structure: `scripts/`, `storage/app/recordings/`. Confirm `php artisan serve` works.

### Step 2: Data layer (1 hour)

Build migrations and Eloquent models per spec 02. Run `php artisan migrate`. Seed a few test leads with `php artisan db:seed`.

Validate: open `database/database.sqlite` in a browser tool, confirm tables exist with correct columns.

### Step 3: Leads UI (2-3 hours)

Build LeadController with index/show/update + import. Build the views. Make CSV import work. No Twilio yet.

Validate: import a CSV, see leads in the list, click into one, edit the brief, save.

### Step 4: Twilio infrastructure (2 hours)

Set up Twilio account and ngrok per spec 04. Configure `.env`. Implement TwilioTokenController. Build the cockpit page (calls.create) with the dialer JS. **Don't worry about the post-call form yet.**

Validate: load cockpit, click Call, talk to your own cell, hear yourself in headset, hang up. Watch logs for "Twilio Device registered" and the recording webhook firing.

### Step 5: Call data flow (1-2 hours)

Implement CallController store/update. Build the post-call form on the cockpit page. Implement the recording webhook with signature verification.

Validate: place a call, hang up, fill out the form (disposition + pain points + notes), click Save, see the call row in SQLite with `recording_url` populated.

### Step 6: Whisper pipeline (2 hours)

Install faster-whisper:
```bash
pip install faster-whisper
python3 -c "from faster_whisper import WhisperModel; WhisperModel('small', device='cpu', compute_type='int8')"  # pre-pull model
```

Create `scripts/transcribe.py` per spec 05. Create RecordingDownloader and Transcriber services. Wire to a "Transcribe" button on call detail.

Validate: place a test call, click Transcribe, see transcript appear within ~60 seconds for a 5-min call.

### Step 7: Coaching pipeline (1-2 hours)

Create CoachingGenerator service per spec 05. Wire to the same "Process Call" flow (download → transcribe → coach all in one button). Display the markdown feedback on call detail page.

Validate: place a test call, click Process Call, see a real coaching report from Claude based on the transcript.

### Step 8: Polish for Monday (1-2 hours)

- Make sure all error paths show useful messages
- Test CSV import with a few weird rows (missing fields, bad phones)
- Confirm ngrok URL is stable; document how to update if it changes
- Place 3-4 test calls end-to-end to make sure the whole flow works
- Take notes on anything that surprised you

### Step 9: Pre-Monday (Sunday evening)

- Sean populates the leads CSV with 50 Chicago small businesses
- Imports them into phonebooth
- Writes briefs for the first 10 leads (the Monday morning cohort)
- Goes to bed

## Total estimated time

12-16 hours of focused work. With breaks, Sat evening + Sunday should comfortably fit it.

## Critical paths

These three things will eat time if they go wrong. Front-load them:

1. **Twilio account verification + number purchase.** Do this Saturday evening. Don't discover Sunday afternoon that the account needs ID verification.
2. **ngrok stability.** Free tier rotates URLs. Either pay for static URL ($8/mo) or accept the friction. Document the update process.
3. **faster-whisper model download.** ~460MB on first use. Pre-pull it Saturday so Sunday's transcription test isn't waiting on a download.

## Things that are fine to skip if time runs short

- Pretty styling (Tailwind defaults are fine)
- The "Add Lead" manual form (CSV import is enough)
- Webhook signature verification on local dev (add before production exposure)
- Status webhook (just recording webhook is critical)
- Comprehensive error handling (catch the obvious cases)

## Things that are NOT fine to skip

- Pain points field as required on calls with conversations (spec 03)
- Recording webhook (entire downstream depends on it)
- ngrok tunnel running for the recording webhook to reach Laravel
- The coaching skill at `docs/skills/01-jeb-blount.md` (the prompt content)

## When to ask for help

If any single step takes more than 2x its estimate, stop and surface it. The system is designed so each step is independently validatable. If step 4 (Twilio) is going sideways at hour 4, that's a sign to either simplify (skip recording for now, just get calling working) or escalate.

## A note on the model string

Spec 05 references `claude-sonnet-4-7` as the default model. This may not be the current model identifier — verify against Anthropic's current docs (https://docs.claude.com) when you wire up the API client. The config-driven design means the model is one `.env` change to update.

## What success looks like Monday at 9 AM

Sean opens his laptop. He navigates to `localhost:8000/leads`. He sees 50 Chicago retailers and trades businesses. He clicks the first one. The brief is on the page. He puts on his headset. He clicks Call. His business number rings the lead's phone. He talks. He hangs up. He fills in disposition, pain points, notes. He clicks Save and Process. Whisper transcribes. Claude tells him what he could have done better. He reads it. He clicks the next lead.

That's the system. Build for that.
