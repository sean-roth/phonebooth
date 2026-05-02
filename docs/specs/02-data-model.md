# 02 — Data Model

## Purpose of this document

Defines the SQLite schema for Phase 1. Three tables: `leads`, `calls`, and `events`. Designed to be extended in Phase 2 without migration pain (Phase 2 will add Twenty integration, more frameworks, hash-chained audit log, etc., but won't need to restructure these core tables).

The `events` table is documented in detail in spec 07 (logging-and-events), not here. This document covers `leads` and `calls`. Both are part of the day-one schema.

## Engineering notes

- SQLite via Laravel's default `database/database.sqlite`
- Migrations live in `database/migrations/`
- Use Laravel's standard `id`, `created_at`, `updated_at` conventions on every table (except `events`, which is append-only — see spec 07)
- Soft deletes are NOT used in Phase 1 (keep it simple)
- Foreign keys enforced (SQLite supports this with `PRAGMA foreign_keys=ON`)

## Table: `leads`

A lead is a business to potentially call. One row per business, even if multiple people work there. (In Phase 2 when Twenty arrives, leads here become Companies in Twenty and contact people become a separate concept. For Phase 1, owner-operated small businesses mean the business and the contact are effectively the same entity.)

### Columns

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER | Primary key, auto-increment |
| `business_name` | TEXT | Required. The business name. |
| `contact_name` | TEXT | Nullable. Owner's name if known. |
| `phone` | TEXT | Required. Stored in E.164 format (`+13125551234`). Validation on import. |
| `website` | TEXT | Nullable. Full URL with scheme. |
| `address` | TEXT | Nullable. Free-text address. |
| `neighborhood` | TEXT | Nullable. Chicago neighborhood name (Logan Square, Wicker Park, etc.). For grouping in the leads list. |
| `industry` | TEXT | Nullable. Free-text industry tag. |
| `brief` | TEXT | Nullable. Markdown. The pre-call brief. Manually written for Phase 1. |
| `status` | TEXT | Required. Default `'new'`. Enum-like: `new`, `called`, `interested`, `discovery_booked`, `disqualified`, `not_interested`, `dead`. |
| `source` | TEXT | Nullable. Where this lead came from (`google_maps`, `manual_search`, `referral`, etc.). |
| `notes` | TEXT | Nullable. Free-text notes about the lead (not call-specific). |
| `created_at` | TIMESTAMP | Standard Laravel. |
| `updated_at` | TIMESTAMP | Standard Laravel. |

### Indexes
- `phone` — unique. Prevents accidental duplicate imports.
- `status` — non-unique. Used for filtering the leads list.

### Constraints
- `business_name` and `phone` are NOT NULL.
- `phone` must validate as E.164. Use a Laravel form request validator on import; reject bad rows.

## Table: `calls`

A call is one attempt to reach a lead. One row per dialing attempt, regardless of outcome (voicemail, no answer, conversation, etc.).

### Columns

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER | Primary key. |
| `lead_id` | INTEGER | Required. FK to `leads.id`. ON DELETE RESTRICT (don't let leads with calls be deleted). |
| `twilio_call_sid` | TEXT | Required after Twilio confirms the call. Twilio's unique ID for the call. Set by the voice TwiML endpoint. |
| `started_at` | TIMESTAMP | When the call connected (or attempt began). |
| `ended_at` | TIMESTAMP | Nullable. When the call ended. |
| `duration_seconds` | INTEGER | Nullable. Twilio reports this in the recording webhook. |
| `recording_url` | TEXT | Nullable. Twilio's recording URL with `.mp3` appended. Saved when recording webhook fires. |
| `recording_local_path` | TEXT | Nullable. Path on disk if we've downloaded it for Whisper. |
| `transcript` | TEXT | Nullable. Plain text. Whisper output. |
| `coaching_feedback` | TEXT | Nullable. Markdown. Claude API output. |
| `coaching_framework` | TEXT | Nullable. Which framework was used (`spin`, `jeb_blount`, etc.). For Phase 1, only one will be used; column exists so Phase 2 doesn't need migration. |
| `disposition` | TEXT | Nullable. Set after call by user. Enum-like: `voicemail`, `no_answer`, `not_interested`, `interested_followup`, `discovery_booked`, `disqualified`, `wrong_number`, `bad_number`. |
| `pain_points` | TEXT | Nullable. Free-text. **The single most important data field for long-term value.** What the lead complained about, what eats their time, what they wish they had. Captured even when call is "no" or voicemail (in voicemail case, this is empty; for "not interested" calls, sometimes the user gets a sentence of pain before the hangup — capture it). |
| `notes` | TEXT | Nullable. Free-text notes about the call itself. |
| `processed_at` | TIMESTAMP | Nullable. When "Process Call" was run (transcript + coaching generated). NULL means not yet processed. |
| `created_at` | TIMESTAMP | Standard. |
| `updated_at` | TIMESTAMP | Standard. |

### Indexes
- `lead_id` — for "show me all calls to this lead"
- `twilio_call_sid` — unique. Used by the webhook handler to find the right call row.
- `created_at` — for chronological listing.

### Constraints
- `lead_id` NOT NULL.
- `twilio_call_sid` unique, can be NULL briefly during call creation but must be set before the call ends.

## Table: `events`

The events table captures structured, timestamped, queryable records of every meaningful state transition in the system. It is the substrate for traceback debugging, cost tracking, and (Phase 2) the cryptographic audit log.

**Full schema and event types catalog: see spec 07 (logging-and-events.md).**

The events table is part of the day-one Phase 1 build. Do not skip it — it pays for itself the first time something breaks in production.

## Lifecycle of a call row

1. **Row created** when user clicks "Call" — `lead_id` set, `started_at` set to now, `twilio_call_sid` NULL initially. Event recorded: `call_initiated`.
2. **CallSid assigned** when Twilio's voice TwiML endpoint runs — `twilio_call_sid` set. Event recorded: `twilio_call_connected`.
3. **Recording arrives** via webhook — `recording_url`, `duration_seconds`, `ended_at` populated. Event recorded: `twilio_recording_received`.
4. **User completes form** post-call — `disposition`, `pain_points`, `notes` populated.
5. **User clicks "Process Call"** — `recording_local_path`, `transcript`, `coaching_feedback`, `coaching_framework`, `processed_at` populated. Multiple events recorded along the way (see spec 07).

A call row in any of these states is valid. The UI handles displaying partial data gracefully ("Recording not yet received" / "Not yet processed").

## CSV import format for leads

When the user imports leads via the leads page, the expected CSV format is:

```csv
business_name,contact_name,phone,website,address,neighborhood,industry,source,notes
"Joe's HVAC","Joe Smith","+13125551234","https://joeshvac.com","123 Main St, Chicago IL 60622","Logan Square","HVAC","manual_search","Has online quote form already, may be tech-forward"
```

- Header row is required.
- `business_name` and `phone` are mandatory. Bad rows are rejected with an error message; the rest of the file imports successfully.
- `phone` is normalized: strip non-digits, prepend `+1` if 10 digits, prepend `+` if 11 digits starting with `1`, otherwise reject. (See spec 03 for full rules.)
- Duplicate phone numbers are skipped (with a count of skipped rows shown to the user).
- `source` defaults to `csv_import` if blank.
- `status` is set to `new` for all imported leads (cannot be specified in CSV).

## Migrations to write

Three migration files are needed:

1. `create_leads_table` — all columns above.
2. `create_calls_table` — all columns above, with FK to leads.
3. `create_events_table` — see spec 07 for schema.

The Engineer should run `php artisan migrate` on a fresh SQLite database after creating these. Provide a `php artisan db:seed` command with a few test leads for development.

## Eloquent models

### `App\Models\Lead`
- `$fillable`: all non-id, non-timestamp columns
- `$casts`: none needed initially
- Relationship: `calls()` — hasMany `Call`

### `App\Models\Call`
- `$fillable`: all non-id, non-timestamp columns
- `$casts`: `started_at`, `ended_at`, `processed_at` to `datetime`
- Relationship: `lead()` — belongsTo `Lead`
- Helper methods:
  - `hasRecording()`: returns true if `recording_url` is not null
  - `isProcessed()`: returns true if `processed_at` is not null
  - `framework()`: returns `coaching_framework` or fallback to default

### `App\Models\Event`
See spec 07.

## What's deferred to Phase 2

- A `companies` and `contacts` split (Twenty's data model when migrated)
- A `frameworks` table or seed data — for Phase 1, framework is just a string column
- Hash-chain columns on `events` (`prev_hash`, `content_hash`) — adding these later doesn't require migrating the existing rows; they just won't have hashes
- A `costs` denormalized table for tracking Twilio + Claude API spend per call (the events table already has this data; a denormalized table is just for query speed)
- Tags, custom fields, anything resembling Twenty's metadata model

These are intentionally not built. The current schema is forward-compatible: when Twenty arrives, `leads` becomes a sync target, not a replacement; coaching data stays here; events stay here.
