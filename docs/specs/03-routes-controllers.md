# 03 — Routes and Controllers

## Purpose of this document

Defines the HTTP surface of the Laravel app: every route, every controller method, every form field. The Engineer should be able to scaffold the entire application from this document plus the data model.

**Important:** Spec 10 (legal compliance) adds a recording consent disclosure to the cockpit page and a new disposition value. Read spec 10 alongside this document.

## Route map

All routes are unauthenticated in Phase 1 (single-user, local network).

```
GET   /                           → redirect to /leads
GET   /leads                      → LeadController@index
POST  /leads/import               → LeadController@import
GET   /leads/{lead}               → LeadController@show
PATCH /leads/{lead}               → LeadController@update
GET   /leads/{lead}/call          → CallController@create

POST  /calls                      → CallController@store
PATCH /calls/{call}               → CallController@update
GET   /calls/{call}               → CallController@show
GET   /calls/{call}/audio         → CallController@audio
POST  /calls/{call}/process       → CallController@process

POST  /webhooks/twilio/recording  → TwilioWebhookController@recording
POST  /webhooks/twilio/status     → TwilioWebhookController@status

GET   /api/twilio/token           → TwilioTokenController@generate
POST  /api/twilio/voice           → TwilioTokenController@voice
```

## CSRF protection

Laravel's CSRF middleware is on by default. Exempt only:

```php
protected $except = [
    'webhooks/twilio/*',
    'api/twilio/voice',
];
```

These are exempted because Twilio (not the browser) sends POST requests to them and Twilio doesn't include CSRF tokens. All other POST routes are browser-driven and keep CSRF protection.

## Controllers in detail

### `LeadController`

#### `index()` → GET /leads

Returns view `leads.index` with all leads, ordered by status. Filter buttons by status (`?status=new`). Each row: business_name, contact_name, neighborhood, industry, status badge, last_call_date, "Call" button.

#### `import(Request $request)` → POST /leads/import

Accepts CSV upload. Validates and creates leads.

Logic:
1. Validate file presence and `.csv` extension
2. Parse with `League\Csv` or `fgetcsv`
3. For each row: validate `business_name` and `phone` not empty, normalize phone (strip non-digits, prepend +1 if 10 digits, prepend + if 11 digits starting with 1, otherwise reject), skip duplicates by phone
4. Return to `/leads` with flash: "Imported {n}, skipped {m} duplicates, rejected {r} invalid"

#### `show(Lead $lead)` → GET /leads/{lead}

Lead detail with markdown editor for brief field. Lists past calls.

#### `update(Lead $lead, Request $request)` → PATCH /leads/{lead}

Updates lead fields. Phase 1: lead status transitions are manual.

### `CallController`

#### `create(Lead $lead)` → GET /leads/{lead}/call

Returns view `calls.create` — the cockpit. Four vertical sections (was three; added disclosure):

**Top — Recording disclosure (NEW per spec 10):**

```html
<section class="recording-disclosure" role="alert">
    <h3>READ FIRST — BEFORE ANY OTHER WORDS</h3>
    <p class="disclosure-script">
        "Hi, this is Sean Roth calling. Quick note before we start —
        I record my calls and have an AI transcribe them so I can review
        my conversations and improve. Is that okay with you?"
    </p>
    <p class="disclosure-instructions">
        Wait for an affirmative answer before continuing.
        If they decline or hang up, end the call and select "declined recording" below.
    </p>
</section>
```

This element is not collapsible. It is the legal gate for the rest of the call.

**Lead info:** business name (large heading), contact name, phone, website link, brief content (rendered markdown).

**Dialer:** status indicator, large Call button (with `data-phone` and `data-lead-id`), Hang Up button, live duration timer, audio device dropdown.

**Post-call form:** disabled until call ends. Fields:

- Disposition dropdown (required) with these options:
  - Voicemail left (`voicemail`)
  - No answer / disconnected (`no_answer`)
  - **Declined recording (`declined_recording`)** — NEW per spec 10
  - Not interested (`not_interested`)
  - Interested — follow up (`interested`)
  - Discovery call booked (`discovery_booked`)
  - Disqualified (`disqualified`)
  - Wrong number (`wrong_number`)
  - Bad number / dead line (`bad_number`)
- Pain points (textarea, REQUIRED unless disposition is `voicemail`, `no_answer`, `wrong_number`, `bad_number`, or `declined_recording`)
- Notes (textarea, optional)
- "Save and Next" — saves, loads next `new` lead
- "Save and Stay" — saves, returns to lead detail

Form submits via standard Blade form POST.

#### `store(Request $request)` → POST /calls

Creates a call row. Returns JSON.

Body: `{ "lead_id": 123 }`

Logic: validate lead exists, create call row with `lead_id`, `started_at = now()`. Return `{ "call_id": 456, "to_number": "+13125551234" }`.

#### `update(Call $call, Request $request)` → PATCH /calls/{call}

Updates call from post-call form.

Validation:
- `disposition` required, must be one of the enum values
- `pain_points` required UNLESS disposition is `voicemail`, `no_answer`, `wrong_number`, `bad_number`, or `declined_recording`
- `notes` optional

**After save:** if disposition is `declined_recording`, delete the recording per spec 10:

```php
public function update(Call $call, Request $request, EventLogger $events)
{
    $validated = $request->validate([...]);
    $call->update($validated);

    if ($call->disposition === 'declined_recording') {
        $this->deleteRecording($call);
        $events->record('recording_deleted', 'call', $call->id, [
            'reason' => 'declined_recording',
        ]);
    }

    $events->record('consent_declined', 'call', $call->id, [])
        ->when($call->disposition === 'declined_recording');

    return redirect()->route(/* ... */);
}

private function deleteRecording(Call $call): void
{
    // Delete local file
    if ($call->recording_local_path && file_exists($call->recording_local_path)) {
        unlink($call->recording_local_path);
    }

    // Delete from Twilio
    if ($call->twilio_recording_sid) {
        $accountSid = config('services.twilio.account_sid');
        $authToken = config('services.twilio.auth_token');
        $url = "https://api.twilio.com/2010-04-01/Accounts/{$accountSid}/Recordings/{$call->twilio_recording_sid}.json";

        \Illuminate\Support\Facades\Http::withBasicAuth($accountSid, $authToken)
            ->delete($url);
    }

    $call->update([
        'recording_url' => null,
        'recording_local_path' => null,
    ]);
}
```

Note: `twilio_recording_sid` needs to be added to the calls table — captured in the recording webhook (it arrives as `RecordingSid`). See spec 02 for schema update.

#### `show(Call $call)` → GET /calls/{call}

Call detail page.

Layout: lead info, call metadata, pain points and notes, audio player (only if recording exists — won't for declined), transcript section, coaching feedback section.

**Transcript:** stored in `calls.transcript` column after Process Call runs. Won't exist for `declined_recording` calls.

**Coaching feedback:** read from filesystem at `storage/app/coaching/feedback/{call_id}.md`. Dashboard does NOT generate coaching — that happens via Claude Desktop (spec 09).

```php
public function show(Call $call)
{
    $feedbackPath = storage_path('app/coaching/feedback/' . $call->id . '.md');
    $coachingFeedback = file_exists($feedbackPath) ? file_get_contents($feedbackPath) : null;

    return view('calls.show', [
        'call' => $call,
        'coachingFeedback' => $coachingFeedback,
    ]);
}
```

In the Blade view:

```blade
@if($call->disposition === 'declined_recording')
    <p>Lead declined recording. No transcript or coaching available.</p>
@elseif($call->transcript)
    {{-- transcript display --}}
@elseif($call->recording_url)
    <p>Recording received but not yet transcribed.</p>
    <form method="POST" action="{{ route('calls.process', $call) }}">
        @csrf
        <button>Process Call (Transcribe)</button>
    </form>
@else
    <p>Recording not yet received from Twilio.</p>
@endif

<section class="coaching">
    <h2>Coaching Feedback</h2>
    @if($call->disposition === 'declined_recording')
        {{-- intentionally empty --}}
    @elseif($coachingFeedback)
        {!! Str::markdown($coachingFeedback) !!}
    @else
        <p>Not yet coached. Open Claude Desktop and ask it to coach call #{{ $call->id }}. See <code>docs/specs/09-claude-desktop-coaching.md</code>.</p>
    @endif
</section>
```

#### `audio(Call $call)` → GET /calls/{call}/audio

Returns the call's audio as streamable MP3.

Twilio recording URLs require HTTP Basic Auth; browsers don't include credentials in `<audio>` src attributes, so we proxy through Laravel.

Logic:
1. If `recording_local_path` is set AND file exists, serve local file
2. Otherwise fetch from Twilio with basic auth, stream body back
3. Otherwise 404

```php
public function audio(Call $call)
{
    if ($call->recording_local_path && file_exists($call->recording_local_path)) {
        return response()->file($call->recording_local_path, ['Content-Type' => 'audio/mpeg']);
    }

    if (!$call->recording_url) {
        abort(404, 'No recording available for this call.');
    }

    $accountSid = config('services.twilio.account_sid');
    $authToken = config('services.twilio.auth_token');

    $response = \Illuminate\Support\Facades\Http::withBasicAuth($accountSid, $authToken)
        ->timeout(60)
        ->get($call->recording_url);

    if (!$response->successful()) {
        abort(404, 'Recording could not be retrieved from Twilio.');
    }

    return response($response->body(), 200, ['Content-Type' => 'audio/mpeg']);
}
```

#### `process(Call $call)` → POST /calls/{call}/process

Triggers the Whisper transcription pipeline. Long-running (60-90 seconds).

Transcription only — no coaching. Coaching happens in Claude Desktop (spec 09).

```php
public function process(Call $call, RecordingDownloader $downloader, Transcriber $transcriber)
{
    // Don't process declined-recording calls (no recording to process)
    if ($call->disposition === 'declined_recording') {
        return redirect()->route('calls.show', $call)
            ->with('error', 'Cannot process: lead declined recording.');
    }

    try {
        // Idempotent: each step skipped if already done
        if (!$call->recording_local_path) {
            $downloader->download($call);
            $call->refresh();
        }

        if (!$call->transcript) {
            $transcriber->transcribe($call);
            $call->refresh();
        }

        if (!$call->processed_at) {
            $call->update(['processed_at' => now()]);
        }

        return redirect()->route('calls.show', $call)
            ->with('success', 'Call transcribed. Open Claude Desktop to coach.');

    } catch (\Exception $e) {
        \Log::error('Process call failed', ['call_id' => $call->id, 'error' => $e->getMessage()]);
        return redirect()->route('calls.show', $call)
            ->with('error', 'Processing failed: ' . $e->getMessage());
    }
}
```

The Process Call form on call detail page:

```html
<form method="POST" action="{{ route('calls.process', $call) }}">
    @csrf
    <button type="submit">Process Call (Transcribe)</button>
</form>
```

See spec 05 for full Transcriber implementation.

### `TwilioWebhookController`

#### `recording(Request $request)` → POST /webhooks/twilio/recording

Twilio calls this when a recording is ready. Public endpoint, no auth, but signature verification REQUIRED.

Twilio sends form-encoded POST data including `CallSid`, `RecordingSid`, `RecordingUrl`, `RecordingDuration`, `RecordingStatus`.

Logic:
1. Find call by `twilio_call_sid = CallSid`
2. If not found, log and return 200 (Twilio retries forever on non-200)
3. Update call: `recording_url` (with `.mp3`), `recording_sid = RecordingSid`, `duration_seconds`, `ended_at = now()` if not set
4. Record `twilio_recording_received` event
5. Return 200

Full code in spec 04.

#### `status(Request $request)` → POST /webhooks/twilio/status

Receives call status callbacks. Less critical for Phase 1 — implement basic version that logs and returns 200.

### `TwilioTokenController`

See spec 04 for full code. Two methods: `generate()` and `voice()`.

## Views to create

```
layouts/
  app.blade.php          — base layout with nav, csrf-token meta tag

leads/
  index.blade.php
  show.blade.php
  partials/import-modal.blade.php

calls/
  create.blade.php       — the cockpit (disclosure section at top)
  show.blade.php         — call detail with transcript + coaching display

components/
  status-badge.blade.php
```

Use Tailwind CSS defaults. The disclosure section should be visually prominent — large text, attention-grabbing border, NOT subtle.

## JavaScript files

```
app.js
twilio-device.js       — Twilio.Device wrapper
cockpit.js             — wires the cockpit
```

See spec 04 for the Twilio JS.

## Form validations summary

| Form | Field | Rule |
|---|---|---|
| CSV import | csv_file | required, file, mimes:csv,txt |
| Lead update | brief | optional, string |
| Lead update | status | optional, in:[enum values] |
| Call store | lead_id | required, exists:leads,id |
| Call update | disposition | required, in:voicemail,no_answer,declined_recording,not_interested,interested,discovery_booked,disqualified,wrong_number,bad_number |
| Call update | pain_points | required_unless:disposition,voicemail,no_answer,wrong_number,bad_number,declined_recording |
| Call update | notes | optional, string |

## Error handling expectations

- Twilio webhook signature failure → 403, log
- Whisper subprocess failure → flash error, leave transcript null, allow retry
- CSV parse error → return to form with error, no partial imports
- Twilio API failure during call initiation → JS shows error, no call row created
- Audio proxy fetch failure → 404 with message
- Recording deletion failure (Twilio API down) → log error, but don't fail the call save

## Out of scope for Phase 1

- API endpoints for external consumers
- Pagination on leads list
- Search on leads list
- Batch operations
- Export to CSV
- User accounts, roles, permissions
- Auto-transition of lead status based on call disposition
- Lead deletion UI
- Streamed audio response
- Auto-coaching (Claude Desktop is a separate manual step)
- Multi-state legal compliance (Phase 1 is Illinois only)
