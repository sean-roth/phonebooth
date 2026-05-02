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
POST  /calls/{call}/process       → CallController@process     (trigger Whisper + Claude pipeline)

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

The **other** POST routes (`/leads/import`, `/calls`, `/calls/{call}/process`, etc.) are browser-driven and keep CSRF protection. Forms include `@csrf` Blade directive; AJAX requests include the token via `X-CSRF-TOKEN` header (see spec 04 for the JS pattern).

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

#### `update(Lead $lead, Request $request)` → PATCH /leads/{lead}
Updates lead fields. Mass-assignable via `$lead->update($request->validated())`. Used for brief editing and status changes.

**Lead status transitions in Phase 1: manual.** When a call is saved with disposition `discovery_booked`, the user can manually update the lead's status to `discovery_booked` via the lead detail page. Phase 2 can automate this transition based on call disposition. Don't build the auto-transition now — it's an opinion that needs user-tested.

### `CallController`

#### `create(Lead $lead)` → GET /leads/{lead}/call
Returns view `calls.create` — the cockpit. Three vertical sections:

**Top section: Lead info**
- Business name (large heading)
- Contact name, phone number (clickable to verify)
- Website link (opens new tab)
- Brief content (rendered markdown, scrollable)

**Middle section: Dialer**
- Status indicator (idle / connecting / on-call / wrapping-up)
- "Call" button (large, green, prominent) — has `data-phone` and `data-lead-id` attributes
- Phone number display (read-only, set from lead)
- "Hang Up" button (visible only during call, large red)
- Live duration timer when call is active
- A small "device select" dropdown for browser audio device (microphone selection — defaults to system default)

This section is JS-heavy. See spec 04 for the Voice JS SDK wiring.

**Bottom section: Post-call form**
- Disabled until call ends
- Disposition dropdown (required) with these options:
  - Voicemail left
  - No answer / disconnected
  - Not interested
  - Interested — follow up
  - Discovery call booked
  - Disqualified
  - Wrong number
  - Bad number (disconnect, dead line)
- Pain points (textarea, REQUIRED — even one sentence; cannot save with empty pain points unless disposition is "Voicemail left", "No answer", "Wrong number", or "Bad number")
- Notes (textarea, optional)
- "Save and Next" button — saves the call, then loads the next lead in `new` status
- "Save and Stay" button — saves the call, returns to this lead's detail page

The form submits via standard Blade form POST (with `@csrf`), not fetch.

Note: "Process Call" is NOT on the cockpit page. It lives on the call detail page (`/calls/{call}`). The cockpit is for placing calls; the detail page is for reviewing them.

#### `store(Request $request)` → POST /calls
Creates a call row when the user clicks "Call" in the cockpit. Returns JSON.

Body:
```json
{
  "lead_id": 123
}
```

Logic:
1. Validate lead exists
2. Create call row with `lead_id`, `started_at = now()`, all other fields null
3. Return the new call's `id` (the JS will pass this through to Twilio's voice endpoint)

Response:
```json
{
  "call_id": 456,
  "to_number": "+13125551234"
}
```

#### `update(Call $call, Request $request)` → PATCH /calls/{call}
Updates call from the post-call form.

Validation:
- `disposition` required, must be one of the enum values
- `pain_points` required UNLESS disposition is voicemail / no_answer / wrong_number / bad_number
- `notes` optional, no max length

#### `show(Call $call)` → GET /calls/{call}
Returns view `calls.show` — the call detail page.

Layout:
- Lead info at top (smaller than on cockpit page)
- Call metadata (date, duration, disposition)
- Pain points and notes (rendered)
- Audio player (if `recording_url` present) — embed Twilio's recording URL in `<audio>` tag, OR provide a download link
- Transcript section:
  - If `transcript` is null and `recording_url` is null: "Recording not yet received from Twilio"
  - If `transcript` is null and `recording_url` is present: "Process Call" form button
  - If `transcript` is present: rendered transcript text (preserve line breaks)
- Coaching feedback section:
  - If `coaching_feedback` is null: empty or "Not yet processed"
  - If present: rendered as markdown

#### `process(Call $call)` → POST /calls/{call}/process
Triggers the Whisper + Claude pipeline for this call. Long-running (could take 60-90 seconds).

**Important:** This endpoint should be invoked via a standard form POST (with `@csrf`), NOT a fetch/XHR request. Reasons:
- Browsers wait indefinitely on form submissions, with the spinner being the page navigation indicator
- Fetch/XHR has default timeouts (~60s in some browsers) that can fire before the pipeline completes
- A redirect-after-POST cleanly delivers the user to the call detail page when done

The form on the call detail page:
```html
<form method="POST" action="{{ route('calls.process', $call) }}">
    @csrf
    <button type="submit">Process Call</button>
</form>
```

See spec 05 for the full processing logic.

### `TwilioWebhookController`

#### `recording(Request $request)` → POST /webhooks/twilio/recording
Twilio calls this when a recording is ready (after the call ends). Public endpoint, no auth — but signature verification is REQUIRED via the `twilio.signature` middleware.

Twilio sends form-encoded POST data including:
- `CallSid` — the call's Twilio SID
- `RecordingSid`, `RecordingUrl`, `RecordingDuration`, `RecordingStatus`

Logic:
1. Find call row by `twilio_call_sid = CallSid`
2. If not found, log and return 200 (don't error — Twilio will retry forever on non-200)
3. Update call row with `recording_url` (with `.mp3` appended), `duration_seconds = RecordingDuration`, `ended_at = now()` if not set
4. Return 200 with empty body

#### `status(Request $request)` → POST /webhooks/twilio/status
Receives call status callbacks (initiated, ringing, answered, completed, failed). Used to update `started_at`, `ended_at`, and detect failures.

Less critical than recording webhook for Phase 1 — Twilio will fire it but we mostly care about the recording. Implement basic version: log every status callback, update timestamps where relevant. If short on time Sunday, this can be a no-op endpoint that returns 200.

### `TwilioTokenController`

See spec 04 for full code. Two methods:

- `generate()` — returns capability token for browser SDK
- `voice()` — returns TwiML for outbound calls; this is where the call_id passed from the browser gets associated with Twilio's CallSid

## Views to create

In `resources/views/`:

```
layouts/
  app.blade.php          — base layout with nav, includes csrf-token meta tag

leads/
  index.blade.php        — leads list
  show.blade.php         — lead detail with brief editor
  partials/
    import-modal.blade.php

calls/
  create.blade.php       — the cockpit (most complex view)
  show.blade.php         — call detail with transcript + coaching, includes Process Call form

components/
  status-badge.blade.php — reusable status pill
```

Use Tailwind CSS (Laravel default) for styling. Don't try to be pretty — use defaults, get to functional. A polish pass is Phase 2.

## JavaScript files

In `resources/js/`:

```
app.js                — entry point, mostly Laravel default
twilio-device.js      — wraps Twilio.Device, exposes simple API to cockpit page
cockpit.js            — wires the cockpit page (call/hangup buttons, timer, form enable/disable)
```

The `twilio-device.js` module is the only complex piece. See spec 04 for full code.

## Form validations summary

| Form | Field | Rule |
|---|---|---|
| CSV import | csv_file | required, file, mimes:csv,txt |
| Lead update | brief | optional, string |
| Lead update | status | optional, in:new,called,interested,discovery_booked,disqualified,not_interested,dead |
| Call store | lead_id | required, exists:leads,id |
| Call update | disposition | required, in:[enum values] |
| Call update | pain_points | required_unless:disposition,voicemail,no_answer,wrong_number,bad_number |
| Call update | notes | optional, string |

## Error handling expectations

- Twilio webhook signature failure → 403, log
- Whisper subprocess failure → flash error to user, leave transcript null, allow retry
- Claude API failure → flash error, leave coaching_feedback null, allow retry
- CSV parse error → return to form with error, no partial imports
- Twilio API failure during call initiation → JS shows error to user, no call row created (or call row created with error state — Engineer's call)

## Out of scope for Phase 1

- API endpoints for external consumers (everything is browser-driven)
- Pagination on leads list (50 leads doesn't need it; add when >100)
- Search on leads list (filter by status is enough)
- Batch operations (delete multiple, bulk-update status, etc.)
- Export to CSV
- User accounts, roles, permissions
- Auto-transition of lead status based on call disposition (deferred to Phase 2)
