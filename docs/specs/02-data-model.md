# 02 — Data Model

## Purpose of this document

The SQLite schema. Two main tables (leads, calls), one events table for audit/debugging.

Phase 1 uses SQLite. Phase 2 may migrate to Postgres for Twenty CRM integration.

**Note: this spec was substantially simplified by spec 11 (recording pivot).** Earlier drafts had recording-related columns (`recording_url`, `recording_local_path`, `transcript`, `processed_at`, `twilio_recording_sid`) that were removed when the architecture stopped recording cold calls. The current schema reflects a calls-only-with-notes design.

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
- `discovery_completed` — discovery call done (Phase 1 may not need this; Sean can check past calls table)
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

    -- Twilio identifier (for the call leg, not for any recording)
    twilio_call_sid VARCHAR(50),

    -- Call metadata
    duration_seconds INTEGER,
    started_at TIMESTAMP,
    ended_at TIMESTAMP,

    -- Outcome — Sean's own observations replace AI-generated transcripts
    disposition VARCHAR(30),
    pain_points TEXT,
    notes TEXT,

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

- `voicemail` — Voicemail left
- `no_answer` — No answer / disconnected
- `not_interested` — Not interested
- `interested` — Interested, follow up
- `discovery_booked` — Discovery call booked
- `disqualified` — Disqualified
- `wrong_number` — Wrong number
- `bad_number` — Bad number / dead line

`declined_recording` was removed when the recording pipeline was removed (spec 11).

### Notes on the calls schema

**No recording columns.** Per spec 11, cold calls are not recorded. There is no `recording_url`, `recording_local_path`, `transcript`, `twilio_recording_sid`, or `processed_at` column. The dashboard tracks the call's existence and Sean's observations; that's it.

**No `coaching_feedback` or `coaching_framework` columns.** Coaching for *discovery calls* (not cold calls) lives in the filesystem at `storage/app/coaching/feedback/discovery-{filename}.md`, written by Claude Desktop via filesystem MCP. The schema does not duplicate this content. See spec 09.

**Sean's pain_points and notes are the cold-call coaching data.** Without transcripts, Sean's own real-time observations *are* the data. The pain_points field captures what the lead complained about; the notes field captures Sean's reflection on the call itself ("opened too fast," "good rapport," "should have asked X"). Phase 2 might add a structured "self-coaching" form; Phase 1 keeps it as free text.

## events table

For traceback debugging. Append-only audit log of significant pipeline events. See spec 07.

```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type VARCHAR(50) NOT NULL,
    subject_type VARCHAR(20) NOT NULL,
    subject_id INTEGER,
    payload TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_events_subject ON events(subject_type, subject_id);
CREATE INDEX idx_events_event_type ON events(event_type);
CREATE INDEX idx_events_created_at ON events(created_at);
```

Event types used in Phase 1 (per spec 07, simplified from earlier draft per spec 11):

- `call_initiated` — user clicked Call
- `twilio_call_connected` — Twilio's voice endpoint fired and we associated CallSid
- `call_completed` — call ended, Sean saved the post-call form
- `error` — any pipeline failure

Recording-related events (`twilio_recording_received`, `recording_downloaded`, `transcript_generated`, `consent_declined`, `recording_deleted`) are removed.

## Migrations

```
database/migrations/
├── 2026_05_01_000001_create_leads_table.php
├── 2026_05_01_000002_create_calls_table.php
└── 2026_05_01_000003_create_events_table.php
```

The Engineer should not add `coaching_feedback`, `coaching_framework`, `recording_url`, `recording_local_path`, `transcript`, `twilio_recording_sid`, or `processed_at` columns to the calls migration. Those are intentionally absent.

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
        'twilio_call_sid',
        'duration_seconds',
        'started_at', 'ended_at',
        'disposition', 'pain_points', 'notes',
    ];

    protected $casts = [
        'started_at' => 'datetime',
        'ended_at' => 'datetime',
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

    public $timestamps = false;

    protected $casts = [
        'payload' => 'array',
        'created_at' => 'datetime',
    ];
}
```

## Out of scope for Phase 1

- Foreign-key enforcement on `events.subject_id` (intentional)
- Soft deletes on leads or calls
- Lead deduplication beyond unique phone constraint
- Multi-tenant scoping
- Encryption at rest
- Connection to Twenty CRM (Phase 2)
- Discovery call records as separate entity (Phase 1: discovery calls are tracked via lead status updates, not as DB records)
