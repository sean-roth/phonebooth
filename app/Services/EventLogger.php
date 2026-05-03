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
            'payload' => $payload,
            'created_at' => now(),
        ]);
    }
}
