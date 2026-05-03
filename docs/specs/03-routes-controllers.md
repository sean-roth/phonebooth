# 03 — Routes and Controllers

## Purpose of this document

Defines the HTTP surface of the Laravel app: every route, every controller method, every form field.

**Note: this spec was substantially simplified by spec 11 (recording pivot).** Earlier drafts had a recording disclosure section on the cockpit, an audio proxy route, a Process Call route triggering Whisper transcription, and auto-delete-on-decline logic in CallController::update. All of that was removed when the architecture stopped recording cold calls.

## Route map

All routes are unauthenticated in Phase 1.

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

POST  /webhooks/twilio/status     → TwilioWebhookController@status

GET   /api/twilio/token           → TwilioTokenController@generate
POST  /api/twilio/voice           → TwilioTokenController@voice
```

Removed compared to earlier drafts:

- `POST /webhooks/twilio/recording` (no recording webhook needed)
- `GET /calls/{call}/audio` (no audio to serve)
- `POST /calls/{call}/process` (no transcription pipeline)

## CSRF protection

```php
protected $except = [
    'webhooks/twilio/*',
    'api/twilio/voice',
];
```

Twilio doesn't send CSRF tokens; everything else (browser-driven) keeps protection.

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

Updates lead fields. Status transitions are manual in Phase 1.

### `CallController`

#### `create(Lead $lead)` → GET /leads/{lead}/call

Returns view `calls.create` — the cockpit. Three vertical sections (no recording disclosure; that section was removed per spec 11):

**Lead info:** business name (large heading), contact name, phone, website link, brief content (rendered markdown).

**Dialer:** status indicator, large Call button (with `data-phone` and `data-lead-id`), Hang Up button, live duration timer, audio device dropdown.

**Post-call form:** disabled until call ends. Fields:

- Disposition dropdown (required) with these options:
  - Voicemail left (`voicemail`)
  - No answer / disconnected (`no_answer`)
  - Not interested (`not_interested`)
  - Interested — follow up (`interested`)
  - Discovery call booked (`discovery_booked`)
  - Disqualified (`disqualified`)
  - Wrong number (`wrong_number`)
  - Bad number / dead line (`bad_number`)
- Pain points (textarea, REQUIRED unless disposition is `voicemail`, `no_answer`, `wrong_number`, `bad_number`)
- Notes (textarea, optional) — Sean's reflection on the call itself ("opened too fast," "good rapport," "should have asked X")
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
- `pain_points` required UNLESS disposition is `voicemail`, `no_answer`, `wrong_number`, `bad_number`
- `notes` optional

Records `call_completed` event after save. No recording cleanup (no recording exists).

```php
public function update(Call $call, Request $request, EventLogger $events)
{
    $validated = $request->validate([
        'disposition' => 'required|in:voicemail,no_answer,not_interested,interested,discovery_booked,disqualified,wrong_number,bad_number',
        'pain_points' => 'required_unless:disposition,voicemail,no_answer,wrong_number,bad_number',
        'notes' => 'nullable|string',
    ]);

    $call->update($validated + ['ended_at' => now()]);

    $events->record('call_completed', 'call', $call->id, [
        'disposition' => $call->disposition,
    ]);

    if ($request->input('action') === 'next') {
        $nextLead = Lead::where('status', 'new')
            ->where('id', '!=', $call->lead_id)
            ->orderBy('id')
            ->first();

        return $nextLead
            ? redirect()->route('calls.create', $nextLead)
            : redirect()->route('leads.index')->with('info', 'No more new leads. Nice work.');
    }

    return redirect()->route('leads.show', $call->lead);
}
```

#### `show(Call $call)` → GET /calls/{call}

Call detail page. Simple — just metadata and Sean's notes. No transcript section, no coaching section, no audio player.

```blade
<h1>Call with {{ $call->lead->business_name }}</h1>
<p>{{ $call->started_at->format('M j, Y g:ia') }} ({{ $call->duration_seconds }}s)</p>

<h2>Disposition</h2>
<p>{{ $call->disposition }}</p>

@if($call->pain_points)
    <h2>Pain points captured</h2>
    {!! Str::markdown($call->pain_points) !!}
@endif

@if($call->notes)
    <h2>Sean's notes</h2>
    {!! Str::markdown($call->notes) !!}
@endif
```

For discovery-call coaching feedback (after the lead's status moves to `discovery_completed`), see spec 09's discovery-call coaching workflow. That feedback lives outside the calls table — it's keyed to the lead, not the call.

### `TwilioWebhookController`

#### `status(Request $request)` → POST /webhooks/twilio/status

Receives call status callbacks (initiated, ringing, answered, completed, failed). Used to update `started_at`, `ended_at`, and detect failures.

Implement basic version: log every status callback, update timestamps where relevant. Return 200.

The recording webhook handler that existed in earlier drafts (`recording()`) has been removed per spec 11.

### `TwilioTokenController`

See spec 04 for full code. Two methods: `generate()` returns a capability token; `voice()` returns TwiML for outbound calls without recording attributes.

## Views to create

```
layouts/
  app.blade.php          — base layout with nav, csrf-token meta tag

leads/
  index.blade.php
  show.blade.php
  partials/import-modal.blade.php

calls/
  create.blade.php       — the cockpit (no disclosure section)
  show.blade.php         — call detail (just metadata + notes)

components/
  status-badge.blade.php
```

Use Tailwind CSS defaults.

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
| Call update | disposition | required, in:voicemail,no_answer,not_interested,interested,discovery_booked,disqualified,wrong_number,bad_number |
| Call update | pain_points | required_unless:disposition,voicemail,no_answer,wrong_number,bad_number |
| Call update | notes | optional, string |

## Error handling expectations

- Twilio webhook signature failure → 403, log
- CSV parse error → return to form with error, no partial imports
- Twilio API failure during call initiation → JS shows error, no call row created

## Out of scope for Phase 1

- API endpoints for external consumers
- Pagination on leads list
- Search on leads list
- Batch operations
- Export to CSV
- User accounts, roles, permissions
- Auto-transition of lead status based on call disposition
- Lead deletion UI
- Audio proxy route (no recording)
- Process Call / transcription route (no transcription)
- Recording disclosure UI (no recording)
- Recording auto-delete logic (no recording)
- Discovery call records as separate routes/controllers (lead status update is enough)
