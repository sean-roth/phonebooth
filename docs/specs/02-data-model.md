# 02 — Data Model

## Purpose of this document

The SQLite schema. Two main tables (leads, calls), one events table for audit/debugging.

Phase 1 uses SQLite (single-file local database). Phase 2 may migrate to Postgres for the Twenty CRM integration.

## leads table

```sql
CREATE TABLE leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Identity
    business_name VARCHAR(255) NOT NULL,
    contact_name VARCHAR(255),
    phone VARCHAR(20) NOT NULL UNIQUE,
    email VARCHAR(255),
    website VARCHAR(255),

    -- Categorization
    industry VARCHAR(100),
    neighborhood VARCHAR(100),
    address VARCHAR(255),

    -- Brief and notes
    brief TEXT,                   -- markdown, manual prep notes for the call
    source VARCHAR(50),           -- where this lead came from ('csv_import', 'manual', etc.)

    -- Status tracking
    status VARCHAR(30) DEFAULT 'new',
    last_call_date TIMESTAMP,

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_leads_status ON leads(status);
CREATE INDEX idx_leads_phone ON leads(phone);
```

### Status enum (string column, validated in Laravel)

- `new` — never called
- `called` — called but no decision yet
- `interested` — wants follow-up
- `discovery_booked` — discovery call scheduled
- `disqualified` — won't pursue
- `not_interested` — declined offer
- `dead` — wrong number, out of business, never reaching

Status transitions are manual in Phase 1.

## calls table

```sql
CREATE TABLE calls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Foreign key
    lead_id INTEGER NOT NULL,

    -- Twilio identifiers
    twilio_call_sid VARCHAR(50),
    twilio_recording_sid VARCHAR(50),  -- captured from recording webhook for deletion API

    -- Recording
    recording_url TEXT,                 -- Twilio's URL (with .mp3 appended)
    recording_local_path VARCHAR(255),  -- path on OptiPlex after download

    -- Transcript (cached for fast display; canonical version is in coaching/transcripts/{id}.md)
    transcript TEXT,

    -- Call metadata
    duration_seconds INTEGER,
    started_at TIMESTAMP,
    ended_at TIMESTAMP,

    -- Outcome
    disposition VARCHAR(30),
    pain_points TEXT,
    notes TEXT,

    -- Pipeline status
    processed_at TIMESTAMP,             -- set when transcription completes

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (lead_id) REFERENCES leads(id)
);

CREATE INDEX idx_calls_lead_id ON calls(lead_id);
CREATE INDEX idx_calls_twilio_call_sid ON calls(twilio_call_sid);
CREATE INDEX idx_calls_disposition ON calls(disposition);
CREATE INDEX idx_calls_started_at ON calls(started_at);
```

### Disposition enum (string column, validated in Laravel)

Per spec 03 and spec 10:

- `voicemail` — Voicemail left
- `no_answer` — No answer / disconnected
- `declined_recording` — Lead declined recording disclosure (recording auto-deleted)
- `not_interested` — Not interested
- `interested` — Interested, follow up
- `discovery_booked` — Discovery call booked
- `disqualified` — Disqualified
- `wrong_number` — Wrong number
- `bad_number` — Bad number / dead line

### Notes on the calls schema

**No `coaching_feedback` or `coaching_framework` columns.** Coaching feedback lives in the filesystem at `storage/app/coaching/feedback/{call_id}.md`, written by Claude Desktop via filesystem MCP (spec 09). The dashboard reads these files at display time. The schema does not duplicate this content.

This was a late architectural change. An earlier draft of this schema had `coaching_feedback TEXT` and `coaching_framework VARCHAR(50)` columns intended for storing API-generated coaching. Those columns were removed when the architecture pivoted to Claude Desktop.

**`twilio_recording_sid` exists for deletion.** When a lead declines recording (`disposition === 'declined_recording'`), spec 03's CallController calls Twilio's DELETE endpoint to remove the recording from their servers. That call requires the recording SID, captured from the webhook. See spec 04's webhook handler.

**`transcript` is cached.** The canonical transcript is the markdown file in `storage/app/coaching/transcripts/{call_id}.md` (with frontmatter, used by Claude Desktop). The DB column is a fast-read cache for the call detail page.

## events table

For traceback debugging. Append-only audit log of significant pipeline events. See spec 07 for full details.

```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type VARCHAR(50) NOT NULL,
    subject_type VARCHAR(20) NOT NULL,    -- 'call', 'lead', 'system'
    subject_id INTEGER,                    -- nullable for system events
    payload TEXT,                          -- JSON
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_events_subject ON events(subject_type, subject_id);
CREATE INDEX idx_events_event_type ON events(event_type);
CREATE INDEX idx_events_created_at ON events(created_at);
```

Event types used in Phase 1 (per spec 07 and spec 10):

- `call_initiated` — user clicked Call
- `twilio_call_connected` — Twilio's voice endpoint fired and we associated CallSid
- `twilio_recording_received` — recording webhook fired
- `recording_downloaded` — local file saved
- `transcript_generated` — Whisper completed
- `call_processed` — full pipeline succeeded
- `consent_declined` — lead declined recording disclosure (per spec 10)
- `recording_deleted` — recording removed from local disk and Twilio (per spec 10)
- `error` — any pipeline failure

## Migrations

Laravel migrations should be one-per-table:

```
database/migrations/
├── 2026_05_01_000001_create_leads_table.php
├── 2026_05_01_000002_create_calls_table.php
└── 2026_05_01_000003_create_events_table.php
```

The Engineer should not add `coaching_feedback` or `coaching_framework` columns to the calls migration. Those are intentionally absent — coaching is filesystem-based.

## Eloquent models

`app/Models/Lead.php`:

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Lead extends Model
{
    protected $fillable = [
        'business_name', 'contact_name', 'phone', 'email', 'website',
        'industry', 'neighborhood', 'address', 'brief', 'source', 'status',
    ];

    protected $casts = [
        'last_call_date' => 'datetime',
    ];

    public function calls(): HasMany
    {
        return $this->hasMany(Call::class);
    }
}
```

`app/Models/Call.php`:

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Call extends Model
{
    protected $fillable = [
        'lead_id',
        'twilio_call_sid', 'twilio_recording_sid',
        'recording_url', 'recording_local_path',
        'transcript', 'duration_seconds',
        'started_at', 'ended_at',
        'disposition', 'pain_points', 'notes',
        'processed_at',
    ];

    protected $casts = [
        'started_at' => 'datetime',
        'ended_at' => 'datetime',
        'processed_at' => 'datetime',
    ];

    public function lead(): BelongsTo
    {
        return $this->belongsTo(Lead::class);
    }
}
```

`app/Models/Event.php`:

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Event extends Model
{
    protected $fillable = ['event_type', 'subject_type', 'subject_id', 'payload'];

    protected $casts = [
        'payload' => 'array',
    ];

    public $timestamps = false;  // only created_at

    protected $dates = ['created_at'];
}
```

## Out of scope for Phase 1

- Foreign-key enforcement on `events.subject_id` (intentional — events table is loose audit log)
- Soft deletes on leads or calls (would conflict with the auto-delete-on-decline behavior for declined_recording)
- Lead deduplication beyond unique phone constraint
- Multi-tenant scoping
- Encryption at rest
- Connection to Twenty CRM (Phase 2 — will require lead schema additions or sync mechanism)
