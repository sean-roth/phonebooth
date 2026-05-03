# 07 — Logging and Events

## Purpose of this document

How phonebooth records what happened, so debugging at 9 AM Monday is fast.

Two parallel systems:

1. **Laravel logs** — three named channels for tracing pipeline behavior
2. **events table** — append-only structured audit log of significant events, queryable via tinker

When something breaks, the events table tells you *where* in the pipeline it died. The logs tell you *why*.

**Note: this spec was simplified by spec 11 (recording pivot).** Earlier drafts had recording-related events (`twilio_recording_received`, `recording_downloaded`, `transcript_generated`, `consent_declined`, `recording_deleted`) and Anthropic API cost-tracking events. All removed; the system tracks call lifecycle only.

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

**`phonebooth_calls`** — call lifecycle (initiate, connect, hangup, save). Used by CallController and the cockpit JS-driven endpoints.

**`phonebooth_webhooks`** — webhook arrivals from Twilio (status callbacks). Full payload as JSON.

**`phonebooth_pipeline`** — kept for consistency with previous design even though the post-call processing pipeline was removed. Phase 2 may reintroduce a pipeline (e.g., for discovery-call coaching auto-import); this channel is the home for that work.

Use them like this:

```php
Log::channel('phonebooth_calls')->info('Call initiated', [
    'lead_id' => $lead->id,
    'call_id' => $call->id,
    'phone' => $lead->phone,
]);
```

## Events table

The structured-data side of logging. Every significant event becomes a row.

Schema is in spec 02:

```sql
events (id, event_type, subject_type, subject_id, payload, created_at)
```

`payload` is JSON.

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

## Required event call sites in Phase 1

Per spec 03 and spec 04, the Engineer should add these EventLogger calls:

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

3. **`call_completed`** — `CallController::update()` after Sean saves the post-call form
   ```php
   $events->record('call_completed', 'call', $call->id, [
       'disposition' => $call->disposition,
   ]);
   ```

4. **`error`** — every catch block
   ```php
   catch (\Exception $e) {
       $events->record('error', 'call', $call->id, [
           'step' => 'whichever_step_failed',
           'message' => $e->getMessage(),
           'trace' => $e->getTraceAsString(),
       ]);
       throw $e;
   }
   ```

That's it. Four event types in Phase 1. Earlier drafts had nine; the recording pipeline removal cut it down significantly.

## Sample debugging session

A call doesn't show up in the leads list. Sean opens tinker:

```php
$lead = Lead::where('business_name', 'like', 'Acme%')->first();
$call = Call::where('lead_id', $lead->id)->latest()->first();
echo $call?->id;  // 47

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
    { event_type: 'call_completed', created_at: '09:18:30' },
]
```

Pipeline succeeded. If a `call_completed` event were missing, the form save failed; if `twilio_call_connected` were missing, the call never connected through Twilio.

If an `error` event appears, the payload tells you which step:

```
{ event_type: 'error', payload: { step: 'twilio_voice', message: '...' } }
```

Then `tail storage/logs/phonebooth_calls-2026-05-04.log` shows the full stack.

## Useful queries

**Calls completed today:**
```php
Event::where('event_type', 'call_completed')
    ->whereDate('created_at', today())
    ->count();
```

**Disposition distribution this week:**
```php
Event::where('event_type', 'call_completed')
    ->where('created_at', '>=', now()->subWeek())
    ->get()
    ->groupBy(fn($e) => $e->payload['disposition'] ?? 'unknown')
    ->map->count();
```

**Errors by step:**
```php
Event::where('event_type', 'error')
    ->get()
    ->groupBy(fn($e) => $e->payload['step'] ?? 'unknown')
    ->map->count();
```

## What this is NOT

- A real-time monitoring system
- A cost tracking system (Phase 1 has no API costs to track; Twilio costs are visible in their console)
- A user activity log
- A replacement for Laravel's default error logging

## Out of scope for Phase 1

- Cost tracking events (no API; Twilio costs visible in their console)
- Hash-chain audit log (Phase 2)
- Event-driven side effects
- Streaming/tail UI for events
- Retention policy
- Discovery-call coaching events (Phase 1's discovery-call workflow is manual; if Phase 2 automates it, those events go here)
