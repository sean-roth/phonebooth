# 07 — Logging and Events

## Purpose of this document

How phonebooth records what happened, so debugging at 9 AM Monday is fast.

Two parallel systems:

1. **Laravel logs** — three named channels for tracing pipeline behavior, debugging errors
2. **events table** — append-only structured audit log of significant pipeline events, queryable via tinker

Both have the same purpose (knowing what happened) at different fidelity. Logs capture the gory detail; events table captures the timeline.

When something breaks, the events table tells you *where* in the pipeline it died. The logs tell you *why*.

## Logging channels

`config/logging.php`:

```php
'channels' => [
    // ... default Laravel channels (stack, daily, etc.)

    'phonebooth_calls' => [
        'driver' => 'daily',
        'path' => storage_path('logs/phonebooth_calls.log'),
        'level' => 'debug',
        'days' => 14,
    ],

    'phonebooth_webhooks' => [
        'driver' => 'daily',
        'path' => storage_path('logs/phonebooth_webhooks.log'),
        'level' => 'debug',
        'days' => 14,
    ],

    'phonebooth_pipeline' => [
        'driver' => 'daily',
        'path' => storage_path('logs/phonebooth_pipeline.log'),
        'level' => 'debug',
        'days' => 14,
    ],
],
```

### Channel purposes

**`phonebooth_calls`** — call lifecycle (initiate, connect, hangup, save). Used by CallController and the cockpit JS-driven endpoints. When a call mysteriously doesn't show up in the leads list, look here.

**`phonebooth_webhooks`** — every webhook arrival from Twilio (recording, status). The full payload is logged as JSON. When the recording webhook isn't matching a call, this is where you diff what Twilio sent vs. what we have.

**`phonebooth_pipeline`** — Whisper subprocess output, file paths, timing. Used by the Process Call orchestrator and its services. When transcription is slow or failing, look here.

Use them like this:

```php
Log::channel('phonebooth_calls')->info('Call initiated', [
    'lead_id' => $lead->id,
    'call_id' => $call->id,
    'phone' => $lead->phone,
]);
```

## Events table

The events table is the structured-data side of logging. Every significant pipeline event becomes a row.

Schema is in spec 02:

```sql
events (id, event_type, subject_type, subject_id, payload, created_at)
```

`payload` is JSON, allowing per-event-type structure without schema changes.

## EventLogger service

`app/Services/EventLogger.php`:

```php
<?php

namespace App\Services;

use App\Models\Event;

class EventLogger
{
    public function record(string $eventType, string $subjectType, ?int $subjectId, array $payload = []): Event
    {
        return Event::create([
            'event_type' => $eventType,
            'subject_type' => $subjectType,
            'subject_id' => $subjectId,
            'payload' => json_encode($payload),
        ]);
    }
}
```

Inject it into controllers and services that need to record events. (Or use Laravel's facade pattern if preferred — keep it simple.)

## Required event call sites in Phase 1

Per spec 03, spec 04, and spec 10, the Engineer should add these EventLogger calls:

1. **`call_initiated`** — `CallController::store()` after creating the call row
   ```php
   $events->record('call_initiated', 'call', $call->id, [
       'lead_id' => $lead->id,
       'phone' => $lead->phone,
   ]);
   ```

2. **`twilio_call_connected`** — `TwilioTokenController::voice()` after associating the CallSid
   ```php
   $events->record('twilio_call_connected', 'call', $callId, [
       'twilio_call_sid' => $twilioCallSid,
   ]);
   ```

3. **`twilio_recording_received`** — `TwilioWebhookController::recording()` after the call row update succeeds
   ```php
   $events->record('twilio_recording_received', 'call', $call->id, [
       'twilio_call_sid' => $callSid,
       'twilio_recording_sid' => $recordingSid,
       'recording_url' => $call->recording_url,
       'duration_seconds' => (int) $duration,
   ]);
   ```

4. **`recording_downloaded`** — `RecordingDownloader::download()` on success
   ```php
   $events->record('recording_downloaded', 'call', $call->id, [
       'local_path' => $path,
       'size_bytes' => filesize($path),
   ]);
   ```

5. **`transcript_generated`** — `Transcriber::transcribe()` on success, capturing timing
   ```php
   $start = microtime(true);
   // ... transcribe both channels ...
   $duration = microtime(true) - $start;
   $events->record('transcript_generated', 'call', $call->id, [
       'transcript_length' => strlen($transcript),
       'transcribe_seconds' => round($duration, 2),
       'left_segments' => count($leftSegments),
       'right_segments' => count($rightSegments),
   ]);
   ```

6. **`call_processed`** — `CallController::process()` after the full pipeline succeeds
   ```php
   $events->record('call_processed', 'call', $call->id, []);
   ```

7. **`consent_declined`** — `CallController::update()` when disposition is set to `declined_recording` (per spec 10)
   ```php
   if ($call->disposition === 'declined_recording') {
       $events->record('consent_declined', 'call', $call->id, []);
   }
   ```

8. **`recording_deleted`** — also in `CallController::update()` after the recording is deleted (per spec 10)
   ```php
   $events->record('recording_deleted', 'call', $call->id, [
       'reason' => 'declined_recording',
   ]);
   ```

9. **`error`** — every catch block in the pipeline
   ```php
   catch (\Exception $e) {
       $events->record('error', 'call', $call->id, [
           'step' => 'transcribe',  // or whichever step failed
           'message' => $e->getMessage(),
           'trace' => $e->getTraceAsString(),  // include for Phase 1 debugging
       ]);
       throw $e;  // re-throw after logging
   }
   ```

## Sample debugging session

Monday at 9:30 AM, a call doesn't show coaching feedback in the dashboard. Sean opens tinker:

```php
// Find the call
$call = Call::latest()->first();
echo $call->id;  // 47

// Get its event timeline
Event::where('subject_type', 'call')
    ->where('subject_id', 47)
    ->orderBy('created_at')
    ->get(['event_type', 'created_at', 'payload']);
```

Output:

```
[
    { event_type: 'call_initiated', created_at: '09:14:22' },
    { event_type: 'twilio_call_connected', created_at: '09:14:25' },
    { event_type: 'twilio_recording_received', created_at: '09:18:12' },
    { event_type: 'recording_downloaded', created_at: '09:19:01' },
    { event_type: 'transcript_generated', created_at: '09:20:14' },
    { event_type: 'call_processed', created_at: '09:20:14' },
]
```

Pipeline succeeded. Coaching is missing because Sean hasn't run Claude Desktop yet — that's not a bug, that's the workflow per spec 09.

If instead an `error` event appeared, the payload tells you which step failed:

```
{ event_type: 'error', payload: { step: 'transcribe', message: 'ffmpeg subprocess failed: ...' } }
```

Then `tail storage/logs/phonebooth_pipeline-2026-05-04.log` shows the full stack and what ffmpeg said.

## Useful queries

**Calls processed today:**
```php
Event::where('event_type', 'call_processed')
    ->whereDate('created_at', today())
    ->count();
```

**Decline rate (per spec 10 — for tuning the disclosure script):**
```php
$calls = Event::where('event_type', 'call_initiated')->count();
$declines = Event::where('event_type', 'consent_declined')->count();
echo $declines / max($calls, 1);  // ratio
```

**Transcription performance distribution:**
```php
Event::where('event_type', 'transcript_generated')
    ->get()
    ->pluck('payload.transcribe_seconds')
    ->avg();
```

**Errors by step:**
```php
Event::where('event_type', 'error')
    ->get()
    ->groupBy(fn($e) => $e->payload['step'] ?? 'unknown')
    ->map->count();
```

## What this is NOT

- A real-time monitoring system (no dashboards, no alerting)
- A cost tracking system (Phase 1 has no API costs to track; Twilio costs are visible in their console)
- A user activity log (events are about pipeline behavior, not "Sean clicked X at Y")
- A replacement for Laravel's default error logging (still want exception traces, just not exclusively in logs)

## Out of scope for Phase 1

- Cost tracking events (no Anthropic API; no per-call cost to track)
- Token counting (no LLM inference happens in the dashboard)
- Hash-chain audit log (Phase 2 — could derive from events table)
- Event-driven side effects (events are recorded, never trigger work — they're logs)
- Streaming/tail UI for events (Phase 2 — useful for live debugging)
- Retention policy (events accumulate; truncate manually as needed)
