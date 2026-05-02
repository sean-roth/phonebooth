# 07 — Logging and Events

## Purpose of this document

Phonebooth has many moving parts that fail in non-obvious ways: Twilio lifecycle events fire in unexpected orders, Whisper subprocesses time out, Claude API calls return surprising responses, ngrok tunnels rotate. This document specifies the two-layer observability that makes those failures debuggable instead of mysterious.

## Two layers, two jobs

**Layer 1: Laravel application logs.** Text logs in `storage/logs/`, rotated daily. For ops debugging — stack traces, exception details, the "why did this throw" question. Cheap to write everywhere. Read with `tail -f` or `grep`.

**Layer 2: Events table.** Structured rows in SQLite with timestamped JSON payloads. For decision-level traceback — "what happened to call 123 in order, with what data." Queryable with SQL, per-subject addressable, durable across log rotation.

Both layers are built day one. They're complementary, not redundant.

The events table is also the substrate for Phase 2's audit log (hash chain on top of these rows) and Phase 2's cost tracking dashboard (sum of cost-bearing events). Build the foundation now.

## Layer 1: Laravel logging

### Channels

In `config/logging.php`, define three channels for phonebooth-specific logging:

```php
'channels' => [
    // ... existing channels (stack, single, daily, etc.)

    'phonebooth_calls' => [
        'driver' => 'daily',
        'path' => storage_path('logs/phonebooth-calls.log'),
        'level' => env('LOG_LEVEL', 'debug'),
        'days' => 14,
    ],

    'phonebooth_processing' => [
        'driver' => 'daily',
        'path' => storage_path('logs/phonebooth-processing.log'),
        'level' => env('LOG_LEVEL', 'debug'),
        'days' => 14,
    ],

    'phonebooth_webhooks' => [
        'driver' => 'daily',
        'path' => storage_path('logs/phonebooth-webhooks.log'),
        'level' => env('LOG_LEVEL', 'debug'),
        'days' => 14,
    ],
],
```

Three separate files because Twilio webhook noise should not bury Whisper crashes. Daily rotation, 14-day retention.

### Usage patterns

Use structured context, not formatted strings:

```php
// Good: structured, queryable
Log::channel('phonebooth_calls')->info('Call initiated', [
    'call_id' => $call->id,
    'lead_id' => $lead->id,
    'to_number' => $lead->phone,
]);

// Bad: hard to grep meaningfully
Log::channel('phonebooth_calls')->info("Call to {$lead->phone} initiated for call {$call->id}");
```

### What to log where

**`phonebooth_calls`:**
- Call row created
- Voice TwiML returned
- CallSid associated with call row
- Status callbacks received (info)
- Errors related to call placement (error)

**`phonebooth_processing`:**
- Recording download started/completed/failed
- Whisper subprocess started/completed/failed (with timing)
- Claude API request/response (info, with token counts; not full prompt or response — too noisy)
- Coaching saved
- Process Call orchestration errors

**`phonebooth_webhooks`:**
- Every webhook arrival (info, with CallSid)
- Signature verification failures (warning)
- Webhooks for unknown CallSid (warning)
- Webhook handler errors (error)

### Log levels

- `debug` — verbose detail, only useful when actively debugging
- `info` — normal operations (call placed, recording received, transcript saved)
- `warning` — abnormal but non-fatal (unknown CallSid, missing field, retry triggered)
- `error` — operation failed, needs attention (Whisper crashed, Claude API rejected, signature invalid)

In production, set `LOG_LEVEL=info` to skip debug noise. During development on the OptiPlex, keep it at `debug`.

## Layer 2: Events table

### Schema

Add a new migration `create_events_table`:

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER | Primary key |
| `event_type` | TEXT | Required. From the catalog below. |
| `subject_type` | TEXT | Required. `call`, `lead`, or `system`. |
| `subject_id` | INTEGER | Nullable (for `system` events). FK-like reference; not enforced because subject can be either calls or leads. |
| `payload` | TEXT | JSON object. Schema varies by event_type. |
| `created_at` | TIMESTAMP | Required. Use database default `CURRENT_TIMESTAMP`. |

**Indexes:**
- `(subject_type, subject_id, created_at)` — primary debugging query
- `(event_type, created_at)` — for "all coaching_generated events today" type queries
- `(created_at)` — for general timeline browsing

**Note: no `updated_at`.** Events are append-only by design. Once written, never modified. This makes the table forward-compatible with the Phase 2 hash chain audit (mutations would break the chain).

### Eloquent model

`App\Models\Event`:

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Event extends Model
{
    public $timestamps = false;  // we manage created_at ourselves
    protected $fillable = ['event_type', 'subject_type', 'subject_id', 'payload', 'created_at'];
    protected $casts = [
        'payload' => 'array',
        'created_at' => 'datetime',
    ];

    public function subject()
    {
        if ($this->subject_type === 'call') {
            return Call::find($this->subject_id);
        }
        if ($this->subject_type === 'lead') {
            return Lead::find($this->subject_id);
        }
        return null;
    }
}
```

## Event types catalog

These are the eight event types Phase 1 records. Adding more is fine; not recording these is not.

### `call_initiated`
Recorded when the user clicks Call and the Call row is created.

Subject: `call`, the new call's id.

Payload:
```json
{
    "lead_id": 123,
    "to_number": "+13125551234",
    "lead_business_name": "Joe's HVAC"
}
```

### `twilio_call_connected`
Recorded when Twilio's voice TwiML endpoint runs and the CallSid is associated with the call row. This is the moment our internal call_id and Twilio's CallSid become linked.

Subject: `call`, the call's id.

Payload:
```json
{
    "twilio_call_sid": "CA1234567890abcdef",
    "from_number": "+13125550000",
    "to_number": "+13125551234"
}
```

### `twilio_recording_received`
Recorded when the recording webhook fires and we save the recording_url.

Subject: `call`, the call's id.

Payload:
```json
{
    "twilio_call_sid": "CA1234567890abcdef",
    "recording_url": "https://api.twilio.com/...",
    "duration_seconds": 287
}
```

### `recording_downloaded`
Recorded when we successfully download the audio from Twilio to local disk.

Subject: `call`, the call's id.

Payload:
```json
{
    "local_path": "/storage/app/recordings/456.mp3",
    "size_bytes": 1452300,
    "download_seconds": 3.2
}
```

### `transcript_generated`
Recorded when Whisper finishes transcription.

Subject: `call`, the call's id.

Payload:
```json
{
    "model": "small",
    "device": "cpu",
    "compute_type": "int8",
    "audio_duration_seconds": 287,
    "transcription_seconds": 52,
    "transcript_length_chars": 4823
}
```

### `coaching_generated`
Recorded after Claude returns coaching feedback. **Used for cost tracking.**

Subject: `call`, the call's id.

Payload:
```json
{
    "framework": "jeb_blount",
    "model": "claude-sonnet-4-6",
    "input_tokens": 3284,
    "output_tokens": 891,
    "cost_usd": 0.0234,
    "claude_seconds": 14.2,
    "feedback_length_chars": 3120
}
```

Cost calculation: at Sonnet pricing of $3/M input + $15/M output, the cost is `(input_tokens * 3 + output_tokens * 15) / 1_000_000`. Engineer should encode this in the EventLogger and update if pricing changes.

### `call_processed`
Recorded after the entire pipeline (download → transcribe → coach) completes successfully.

Subject: `call`, the call's id.

Payload:
```json
{
    "total_seconds": 78,
    "framework": "jeb_blount"
}
```

### `error`
Recorded when any operation fails. Don't lose errors.

Subject: usually `call` (the call being processed); can be `system` for tunnel/config issues.

Payload:
```json
{
    "operation": "transcribe",
    "error_class": "Symfony\\Component\\Process\\Exception\\ProcessFailedException",
    "message": "ffmpeg: command not found",
    "context": {
        "call_id": 456,
        "audio_path": "/storage/app/recordings/456.mp3"
    }
}
```

The `operation` field is a short identifier: `download_recording`, `transcribe`, `claude_api`, `webhook_signature`, `voice_twiml`, etc.

## Event recording API

Single helper service to keep call sites consistent.

`app/Services/EventLogger.php`:

```php
<?php

namespace App\Services;

use App\Models\Event;

class EventLogger
{
    /**
     * Record an event. Always succeeds (catches its own failures
     * to avoid event-recording errors masking the actual operation).
     */
    public function record(
        string $eventType,
        string $subjectType,
        ?int $subjectId,
        array $payload = []
    ): ?Event {
        try {
            return Event::create([
                'event_type' => $eventType,
                'subject_type' => $subjectType,
                'subject_id' => $subjectId,
                'payload' => $payload,
                'created_at' => now(),
            ]);
        } catch (\Throwable $e) {
            // Event logging must never break the calling code.
            \Log::error('EventLogger failed', [
                'event_type' => $eventType,
                'error' => $e->getMessage(),
            ]);
            return null;
        }
    }

    /**
     * Convenience: record a coaching_generated event with cost calculation.
     */
    public function recordCoaching(
        int $callId,
        string $framework,
        string $model,
        int $inputTokens,
        int $outputTokens,
        float $claudeSeconds,
        int $feedbackLengthChars
    ): ?Event {
        $cost = $this->calculateCost($model, $inputTokens, $outputTokens);

        return $this->record('coaching_generated', 'call', $callId, [
            'framework' => $framework,
            'model' => $model,
            'input_tokens' => $inputTokens,
            'output_tokens' => $outputTokens,
            'cost_usd' => $cost,
            'claude_seconds' => $claudeSeconds,
            'feedback_length_chars' => $feedbackLengthChars,
        ]);
    }

    private function calculateCost(string $model, int $inputTokens, int $outputTokens): float
    {
        // Pricing per 1M tokens. Update when Anthropic pricing changes.
        $pricing = [
            'claude-sonnet-4-6' => ['input' => 3.0, 'output' => 15.0],
            'claude-opus-4-7'   => ['input' => 15.0, 'output' => 75.0],
            'claude-haiku-4-5'  => ['input' => 1.0, 'output' => 5.0],
        ];

        $rates = $pricing[$model] ?? ['input' => 3.0, 'output' => 15.0];

        return round(
            ($inputTokens * $rates['input'] + $outputTokens * $rates['output']) / 1_000_000,
            6
        );
    }
}
```

## Where to record events

Inject `EventLogger` into the controllers and services that perform the operations. Specific call sites:

| Where | Event type |
|---|---|
| `CallController::store()` after creating call row | `call_initiated` |
| `TwilioTokenController::voice()` after associating CallSid | `twilio_call_connected` |
| `TwilioWebhookController::recording()` after saving URL | `twilio_recording_received` |
| `RecordingDownloader::download()` on success | `recording_downloaded` |
| `Transcriber::transcribe()` on success (with timing) | `transcript_generated` |
| `CoachingGenerator::generate()` on success | `coaching_generated` (use `recordCoaching()`) |
| `CallController::process()` on overall success | `call_processed` |
| Any catch block in the pipeline | `error` |

Each service should accept `EventLogger` via constructor injection (Laravel's service container resolves it). No need to add EventLogger to every method signature — it's a service.

## Querying events for debugging

### Show timeline for a specific call

```sql
SELECT event_type, payload, created_at
FROM events
WHERE subject_type = 'call' AND subject_id = 456
ORDER BY created_at;
```

Or in Tinker:
```php
Event::where('subject_type', 'call')->where('subject_id', 456)->orderBy('created_at')->get();
```

### Show all errors today

```php
Event::where('event_type', 'error')
    ->whereDate('created_at', today())
    ->get();
```

### Today's Claude API spend

```php
Event::where('event_type', 'coaching_generated')
    ->whereDate('created_at', today())
    ->get()
    ->sum(fn($e) => $e->payload['cost_usd']);
```

### Calls that started but never completed processing

```sql
SELECT call_id FROM events WHERE event_type = 'call_initiated'
EXCEPT
SELECT subject_id FROM events WHERE event_type = 'call_processed';
```

### Average Whisper transcription time

```php
Event::where('event_type', 'transcript_generated')
    ->get()
    ->avg(fn($e) => $e->payload['transcription_seconds']);
```

## Phase 1 access pattern

There is no UI for browsing events in Phase 1. Access is via `php artisan tinker` or direct SQL through a SQLite client. This is fine — the events are there to be queried when something goes wrong, not browsed casually.

Phase 2 will add a Settings tab with:
- Today's call cost (Twilio + Claude)
- This month's running total
- Recent errors
- Per-call event timeline (clickable from any call's detail page)

## Sample debugging session

Imagine: Sean made a call Monday morning. The cockpit showed "call ended" but no recording ever arrived in the call detail page. He opens tinker.

```php
> $call = Call::find(456);
> $call->recording_url
=> null  // confirmed: no recording on the row

> Event::where('subject_id', 456)->where('subject_type', 'call')->orderBy('created_at')->get(['event_type', 'created_at', 'payload']);
=> [
    { event_type: 'call_initiated',          created_at: '09:14:32', payload: {...} },
    { event_type: 'twilio_call_connected',   created_at: '09:14:33', payload: { twilio_call_sid: 'CAabc' } },
    // nothing after this
   ]
```

Pattern: call connected, but no `twilio_recording_received`. Either Twilio never fired the webhook, or it failed signature verification, or our endpoint errored.

```php
> Event::where('event_type', 'error')->where('created_at', '>=', '09:14:00')->get();
=> [
    { event_type: 'error', payload: { operation: 'webhook_signature', message: 'Invalid Twilio signature', call_sid: 'CAabc' } }
   ]
```

Found it. Signature verification failed — probably the ngrok URL rotated and TUNNEL_URL is stale. Fix the env, restart, retry.

This whole investigation took 30 seconds because the events table told the story in order. Without it, Sean would have been grepping through three log files looking for needles.

## What's deferred to Phase 2 / 3

- **Hash chain audit log:** add a `prev_hash` and `content_hash` column to events; each event references the previous event's hash. SHA-256 over the JSON payload + prev_hash. This makes the events table tamper-evident.
- **OpenTimestamps anchoring:** periodic Bitcoin-anchored proofs of the chain's state.
- **Web UI for browsing events:** the Settings tab event browser.
- **Retention policies:** decide what events to archive vs delete after N days.
- **Cost dashboard:** real-time today/month/year breakdowns by source (Twilio, Claude, etc.).
- **Alerts:** email/SMS when error rate spikes or when cost exceeds a threshold.

These are the SOPs Nobody Reads audit pattern, generalized. The Phase 1 events table is the seed.

## Implementation checklist

- [ ] Add `events` migration
- [ ] Add `Event` model
- [ ] Add `EventLogger` service
- [ ] Add three logging channels in `config/logging.php`
- [ ] Sprinkle `EventLogger::record()` calls at the eight required locations
- [ ] Add structured `Log::channel(...)->info()` calls at appropriate operations
- [ ] Verify after a test call: query the events table and see the full timeline

Total estimated time: ~1.5 hours added to the Phase 1 build. Worth it.
