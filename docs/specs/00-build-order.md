# 00 — Build Order

## Read this first if you're the Engineer

This document is the entry point. Read it, then read the specs in numerical order. Before writing any code, scan all seven specs end-to-end so the architecture makes sense as a whole.

## The mission

Get Sean to "first call placed through phonebooth" by Sunday night. Monday morning he picks up the dashboard cold and starts dialing.

## The specs

| # | Doc | What's in it |
|---|---|---|
| 00 | build-order.md | This file. Build sequence. |
| 01 | architecture.md | System overview, scope, data flow |
| 02 | data-model.md | SQLite schema for `leads` and `calls` |
| 03 | routes-controllers.md | Every HTTP route, every form, every controller method |
| 04 | twilio-integration.md | Browser softphone with code examples |
| 05 | whisper-claude-integration.md | Post-call processing pipeline with code examples |
| 06 | targeting-brief.md | Reference only — what Phase 1 is about (not for Engineer) |
| 07 | logging-and-events.md | Application logs + events table for traceback debugging |

The skill in `docs/skills/01-jeb-blount.md` is loaded at runtime by the coaching pipeline.

## Recommended build sequence

This sequence gets working software at the end of each step. Do not skip ahead — each step validates the previous before adding complexity.

### Step 1: Scaffold (1 hour)

```bash
laravel new phonebooth --git
cd phonebooth
composer require twilio/sdk
npm install @twilio/voice-sdk
```

Create directory structure: `scripts/`, `storage/app/recordings/`. Confirm `php artisan serve` works.

### Step 2: Data layer + logging foundation (1.5 hours)

Build migrations and Eloquent models per specs 02 and 07:
- `create_leads_table` (spec 02)
- `create_calls_table` (spec 02)
- `create_events_table` (spec 07)

Configure the three logging channels in `config/logging.php` per spec 07.

Create `app/Services/EventLogger.php` per spec 07.

Run `php artisan migrate`. Seed a few test leads with `php artisan db:seed`.

Validate: open `database/database.sqlite`, confirm tables exist. In tinker, `EventLogger::record('test', 'system', null, ['hello' => 'world'])` and verify the row appears in `events`.

### Step 3: Leads UI (2-3 hours)

Build LeadController with index/show/update + import. Build the views. Make CSV import work. No Twilio yet.

Don't add event logging here yet — leads are pre-call, not part of the critical traceback path. (Add later if useful.)

Validate: import a CSV, see leads in the list, click into one, edit the brief, save.

### Step 4: Twilio infrastructure (2 hours)

Set up Twilio account and ngrok per spec 04. Configure `.env`. Implement TwilioTokenController (with the call_id handling per spec 04). Build the cockpit page (calls.create) with the dialer JS.

Add EventLogger calls per spec 07:
- `call_initiated` in `CallController::store()`
- `twilio_call_connected` in `TwilioTokenController::voice()` after CallSid association

Add `Log::channel('phonebooth_calls')` info logs around the same operations.

Validate: load cockpit, click Call, talk to your own cell, hear yourself in headset, hang up. Then in tinker: `Event::orderBy('created_at', 'desc')->take(5)->get()` — should see `call_initiated` and `twilio_call_connected` rows. Watch logs for "Twilio Device registered" and the recording webhook firing.

### Step 5: Call data flow (1-2 hours)

Implement CallController store/update. Build the post-call form on the cockpit page. Implement the recording webhook with signature verification.

Add `twilio_recording_received` event in the webhook handler. Add `phonebooth_webhooks` log entry for every webhook arrival.

Validate: place a call, hang up, fill out the form (disposition + pain points + notes), click Save, see the call row in SQLite with `recording_url` populated. Query events for that call — should see initiated, connected, recording_received in order.

### Step 6: Whisper pipeline (2 hours)

Install faster-whisper:
```bash
pip install faster-whisper
python3 -c "from faster_whisper import WhisperModel; WhisperModel('small', device='cpu', compute_type='int8')"  # pre-pull model
```

Create `scripts/transcribe.py` per spec 05 (note: function definition above the loop, this was a v1 bug). Create RecordingDownloader and Transcriber services.

Add EventLogger calls:
- `recording_downloaded` in RecordingDownloader on success
- `transcript_generated` in Transcriber on success (capture timing — wrap with `microtime(true)` before/after)
- `error` events in any catch blocks

Validate: place a test call, click Process Call (form POST per spec 03/05), see transcript appear within ~60 seconds for a 5-min call. Query events: should see download + transcript events with payloads.

### Step 7: Coaching pipeline (1-2 hours)

Create CoachingGenerator service per spec 05. Wire to the same "Process Call" flow.

Use `EventLogger::recordCoaching()` (spec 07) which automatically calculates cost from token counts. This is the foundation for cost tracking.

Add `call_processed` event after the full pipeline succeeds.

Validate: place a test call, click Process Call, see coaching report. Query events:
```php
Event::where('subject_id', $callId)->where('subject_type', 'call')->orderBy('created_at')->get();
```
Should see all 5 events: initiated → connected → recording_received → downloaded → transcript_generated → coaching_generated → call_processed.

Bonus check: query today's spend:
```php
Event::where('event_type', 'coaching_generated')->whereDate('created_at', today())->get()->sum(fn($e) => $e->payload['cost_usd']);
```

### Step 8: Polish for Monday (1-2 hours)

- Make sure all error paths show useful messages AND record `error` events
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

13-17 hours of focused work. With breaks, Sat evening + Sunday should comfortably fit it. The events/logging additions add ~1.5 hours to the original estimate but pay for themselves the first time something breaks.

## Critical paths

These three things will eat time if they go wrong. Front-load them:

1. **Twilio account verification + number purchase.** Do this Saturday evening. Don't discover Sunday afternoon that the account needs ID verification.
2. **ngrok stability.** Free tier rotates URLs. Either pay for static URL ($8/mo) or accept the friction. Document the update process. **TUNNEL_URL must match exactly or signature verification fails.**
3. **faster-whisper model download.** ~460MB on first use. Pre-pull it Saturday so Sunday's transcription test isn't waiting on a download.

## Things that are fine to skip if time runs short

- Pretty styling (Tailwind defaults are fine)
- The "Add Lead" manual form (CSV import is enough)
- Webhook signature verification on local dev (add before any public exposure)
- Status webhook (just recording webhook is critical)
- Comprehensive error handling beyond the obvious cases

## Things that are NOT fine to skip

- Pain points field as required on calls with conversations (spec 03)
- Recording webhook (entire downstream depends on it)
- ngrok tunnel running for the recording webhook to reach Laravel
- The coaching skill at `docs/skills/01-jeb-blount.md` (the prompt content)
- Events table + EventLogger (spec 07) — debugging without it is brutal
- The eight required EventLogger call sites (spec 07)

## When to ask for help

If any single step takes more than 2x its estimate, stop and surface it. The system is designed so each step is independently validatable. If step 4 (Twilio) is going sideways at hour 4, that's a sign to either simplify (skip recording for now, just get calling working) or escalate.

## A note on the model string

Spec 05 uses `claude-sonnet-4-6` as the default model. This was correct at time of writing — verify against Anthropic's current docs (https://docs.claude.com) when you wire up the API client. The config-driven design means the model is one `.env` change to update.

The cost calculation in `EventLogger::recordCoaching()` (spec 07) has hardcoded pricing per model. If pricing changes, update that map.

## A note on the events table

When something breaks Monday morning — and something will — the first place to look is the events table, not the Laravel logs. Tinker query for the call's events shows the timeline; Laravel logs show why a specific step failed. Both are useful, the events table is faster for "where in the pipeline did it die."

See spec 07's "Sample debugging session" for the pattern.

## What success looks like Monday at 9 AM

Sean opens his laptop. He navigates to `localhost:8000/leads`. He sees 50 Chicago retailers and trades businesses. He clicks the first one. The brief is on the page. He puts on his headset. He clicks Call. His business number rings the lead's phone. He talks. He hangs up. He fills in disposition, pain points, notes. He clicks Save. He navigates to the call detail. He clicks Process Call. Whisper transcribes. Claude tells him what he could have done better. He reads it. He clicks the next lead.

Behind the scenes, the events table accumulates the timeline. Costs add up by row. Tomorrow's "where did Tuesday's $2.40 in API calls go" question has an answer.

That's the system. Build for that.
