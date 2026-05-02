# 03 — Routes and Controllers

## Purpose of this document

Defines the HTTP surface of the Laravel app: every route, every controller method, every form field. The Engineer should be able to scaffold the entire application from this document plus the data model.

## Route map

All routes are unauthenticated in Phase 1 (single-user, local network). All return Blade views unless noted.

```
GET   /                           → redirect to /leads
GET   /leads                      → LeadController@index       (list view)
POST  /leads/import               → LeadController@import      (CSV upload)
GET   /leads/{lead}               → LeadController@show        (lead detail + brief editor)
PATCH /leads/{lead}               → LeadController@update      (update lead fields including brief)
GET   /leads/{lead}/call          → CallController@create      (the cockpit page)

POST  /calls                      → CallController@store       (create call row when dial starts)
PATCH /calls/{call}               → CallController@update      (post-call form: disposition, pain points, notes)
GET   /calls/{call}               → CallController@show        (call detail with transcript + coaching)
GET   /calls/{call}/audio         → CallController@audio       (audio proxy — auth-handled stream)
POST  /calls/{call}/process       → CallController@process     (trigger Whisper pipeline; coaching is separate via Claude Desktop)

POST  /webhooks/twilio/recording  → TwilioWebhookController@recording   (Twilio fires this when recording is ready)
POST  /webhooks/twilio/status     → TwilioWebhookController@status      (call status updates)

GET   /api/twilio/token           → TwilioTokenController@generate      (returns capability token for browser SDK)
POST  /api/twilio/voice           → TwilioTokenController@voice         (TwiML response for outbound calls; called by Twilio, not browser)
```

## CSRF protection

Laravel's CSRF middleware is on by default. The following routes need to be **exempted** in `app/Http/Middleware/VerifyCsrfToken.php`:

```php
protected $except = [
    'webhooks/twilio/*',
    'api/twilio/voice',
];
```

These are exempted because Twilio (not the browser) sends POST requests to them and Twilio doesn't include CSRF tokens.

The **other** POST routes (`/leads/import`, `/calls`, `/calls/{call}/process`, etc.) are browser-driven and keep CSRF protection.

## Controllers in detail

### `LeadController`

#### `index()` → GET /leads
Returns view `leads.index` with:
- All leads, ordered by `status` (new first, then called/interested, then disqualified/dead at bottom)
- Filter buttons by status (use query string `?status=new`)
- An import button that opens a modal with file upload form
- A "Add Lead" button (manual single-lead entry — Phase 1 nice-to-have)

Each row shows: business_name, contact_name, neighborhood, industry, status badge, last_call_date, "Call" button.

#### `import(Request $request)` → POST /leads/import
Accepts a CSV upload. Validates and creates leads.

Form: `multipart/form-data` with field `csv_file`. Standard Blade form with `@csrf`.

Logic:
1. Validate file presence and `.csv` extension
2. Parse with `League\Csv` or just `fgetcsv`
3. For each row:
   - Validate `business_name` and `phone` not empty
   - **Normalize phone:**
     - Strip all non-digit characters
     - If 10 digits: prepend `+1`
     - If 11 digits and starts with `1`: prepend `+`
     - Otherwise: reject the row as invalid
   - Skip if phone already exists in DB
   - Create lead
4. Return to `/leads` with flash message: "Imported {n}, skipped {m} duplicates, rejected {r} invalid rows"

#### `show(Lead $lead)` → GET /leads/{lead}
Returns view `leads.show` with the lead's full record and a markdown editor for the brief field. Also lists past calls to this lead with links to call detail.

Brief editor is a plain `<textarea>` for Phase 1.

#### `update(Lead $lead, Request $request)` → PATCH /leads/{lead}
Updates lead fields. Mass-assignable via `$lead->update($request->validated())`.

**Lead status transitions in Phase 1: manual.** When a call is saved with disposition `discovery_booked`, the user can manually update the lead's status. Phase 2 can automate this transition.

### `CallController`

#### `create(Lead $lead)` → GET /leads/{lead}/call
Returns view `calls.create` — the cockpit. Three vertical sections:

**Top: Lead info** — business name, contact, phone, website link, brief content (rendered markdown).

**Middle: Dialer** — status indicator, large Call button (with `data-phone` and `data-lead-id`), Hang Up button, live duration timer, audio device dropdown.

**Bottom: Post-call form** — disabled until call ends. Fields:
- Disposition dropdown (required) — voicemail / no_answer / not_interested / interested / discovery_booked / disqualified / wrong_number / bad_number
- Pain points (textarea, REQUIRED unless disposition is voicemail/no_answer/wrong_number/bad_number)
- Notes (textarea, optional)
- "Save and Next" button — saves, loads next `new` lead
- "Save and Stay" button — saves, returns to lead detail

Form submits via standard Blade form POST.

Note: "Process Call" is NOT on the cockpit page. It lives on the call detail page.

#### `store(Request $request)` → POST /calls
Creates a call row when user clicks "Call". Returns JSON.

Body: `{ "lead_id": 123 }`

Logic:
1. Validate lead exists
2. Create call row with `lead_id`, `started_at = now()`
3. Return new call's `id`

Response: `{ "call_id": 456, "to_number": "+13125551234" }`

#### `update(Call $call, Request $request)` → PATCH /calls/{call}
Updates call from the post-call form.

Validation:
- `disposition` required
- `pain_points` required UNLESS disposition is voicemail / no_answer / wrong_number / bad_number
- `notes` optional

#### `show(Call $call)` → GET /calls/{call}
Returns view `calls.show` — the call detail page.

Layout:
- Lead info at top (smaller than cockpit)
- Call metadata (date, duration, disposition)
- Pain points and notes (rendered)
- **Audio player** — uses audio proxy route
- Transcript section — see logic below
- Coaching feedback section — see logic below

**Reading the transcript:** stored in `calls.transcript` column after Process Call runs.

**Reading the coaching feedback:** read from filesystem at `storage/app/coaching/feedback/{call_id}.md`. The dashboard does NOT generate coaching itself — that happens via Claude Desktop (see spec 09).

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
@if($call->transcript)
    {{-- transcript display --}}
@elseif($call->recording_url)
    <p>Recording received but not yet transcribed.</p>
    <form method="POST" action="{{ route('calls.process', $call) }}">@csrf<button>Process Call</button></form>
@else
    <p>Recording not yet received from Twilio.</p>
@endif

<section class="coaching">
    <h2>Coaching Feedback</h2>
    @if($coachingFeedback)
        {!! Str::markdown($coachingFeedback) !!}
    @else
        <p>Not yet coached. Open Claude Desktop and ask it to coach call #{{ $call->id }}. See <code>docs/specs/09-claude-desktop-coaching.md</code>.</p>
    @endif
</section>
```

#### `audio(Call $call)` → GET /calls/{call}/audio
Returns the call's audio as a streamable MP3.

**Why this route exists:** Twilio recording URLs require HTTP Basic Auth. Browsers don't include credentials in `<audio>` src attributes. We proxy through Laravel.

Logic:
1. If `recording_local_path` is set AND file exists, serve local file via `response()->file()`
2. Otherwise fetch from Twilio with basic auth, stream body back with `Content-Type: audio/mpeg`
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

In Blade:
```blade
@if($call->recording_url || $call->recording_local_path)
    <audio controls src="{{ route('calls.audio', $call) }}"></audio>
@endif
```

#### `process(Call $call)` → POST /calls/{call}/process
Triggers the Whisper transcription pipeline. Long-running (60-90 seconds for a 5-minute call).

**This is transcription only — no coaching.** Coaching happens separately in Claude Desktop after this completes (see spec 09).

```php
public function process(Call $call, RecordingDownloader $downloader, Transcriber $transcriber)
{
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

The form on the call detail page:
```html
<form method="POST" action="{{ route('calls.process', $call) }}">
    @csrf
    <button type="submit">Process Call (Transcribe)</button>
</form>
```

See spec 05 for the full Transcriber implementation.

### `TwilioWebhookController`

#### `recording(Request $request)` → POST /webhooks/twilio/recording
Twilio calls this when a recording is ready. Public endpoint, no auth, but signature verification REQUIRED via `twilio.signature` middleware.

Twilio sends form-encoded POST data including `CallSid`, `RecordingSid`, `RecordingUrl`, `RecordingDuration`, `RecordingStatus`.

Logic:
1. Find call row by `twilio_call_sid = CallSid`
2. If not found, log and return 200 (don't error — Twilio retries forever on non-200)
3. Update call row with `recording_url` (with `.mp3` appended), `duration_seconds`, `ended_at = now()` if not set
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
  index.blade.php        — leads list
  show.blade.php         — lead detail with brief editor
  partials/
    import-modal.blade.php

calls/
  create.blade.php       — the cockpit
  show.blade.php         — call detail with transcript + coaching display, audio player, Process Call form

components/
  status-badge.blade.php
```

Use Tailwind CSS defaults. Polish is Phase 2.

## JavaScript files

```
app.js                — entry point
twilio-device.js      — Twilio.Device wrapper
cockpit.js            — wires the cockpit page
```

The `twilio-device.js` is the only complex piece. See spec 04.

## Form validations summary

| Form | Field | Rule |
|---|---|---|
| CSV import | csv_file | required, file, mimes:csv,txt |
| Lead update | brief | optional, string |
| Lead update | status | optional, in:[enum values] |
| Call store | lead_id | required, exists:leads,id |
| Call update | disposition | required, in:[enum values] |
| Call update | pain_points | required_unless:disposition,voicemail,no_answer,wrong_number,bad_number |
| Call update | notes | optional, string |

## Error handling expectations

- Twilio webhook signature failure → 403, log
- Whisper subprocess failure → flash error, leave transcript null, allow retry
- CSV parse error → return to form with error, no partial imports
- Twilio API failure during call initiation → JS shows error, no call row created
- Audio proxy fetch failure → 404 with message

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
