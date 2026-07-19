-- _agent/data/schema.sql
-- SQLite "seen leads" dedup store. The memory that makes repeated sweeps over
-- the same corridors survivable. Without it, duplicates drown the pipeline
-- within a few weeks.

CREATE TABLE IF NOT EXISTS seen_leads (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    phone_digits  TEXT,              -- normalized to digits only; primary dedup key
    name_key      TEXT,              -- lowercased company name (fallback match)
    zip           TEXT,              -- 5-digit ZIP (fallback match, paired with name_key)
    company       TEXT,              -- display name as sourced
    city_state    TEXT,
    category      TEXT,              -- the sweep category it came from
    slice         TEXT,              -- "metro x corridor x category"
    decision      TEXT,              -- keep | reject (from qualification)
    confidence    TEXT,              -- H | M | L
    number_status TEXT,              -- unknown | valid | dead (from lookup)
    first_seen    TEXT DEFAULT (date('now'))
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_seen_phone ON seen_leads(phone_digits);
CREATE INDEX IF NOT EXISTS idx_seen_namezip ON seen_leads(name_key, zip);

-- Log of which slices have been swept, so the human/agent knows what territory
-- is mined out.
CREATE TABLE IF NOT EXISTS swept_slices (
    slice       TEXT PRIMARY KEY,    -- "metro x corridor x category"
    last_swept  TEXT DEFAULT (date('now')),
    result      TEXT                 -- "productive" | "worked-out"
);
