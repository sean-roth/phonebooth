"""SQLite dedup store. Schema in ../data/schema.sql.

The memory that keeps repeated sweeps over the same corridors survivable:
without it, duplicates drown the pipeline within a few weeks. Rejects are
remembered too, so the same non-fit shop is not re-qualified every run."""
import re
import sqlite3
from config import DB_PATH, SCHEMA_PATH, REVISIT_AFTER_DAYS


def _digits(phone: str) -> str:
    return re.sub(r"\D", "", phone or "")


def _zip_of(address: str) -> str:
    m = re.search(r"\b(\d{5})(?:-\d{4})?\b", address or "")
    return m.group(1) if m else ""


def _name_key(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (name or "").lower())


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA_PATH.read_text())  # CREATE ... IF NOT EXISTS (idempotent)
    return conn


def is_seen(conn, lead: dict) -> bool:
    pd, nk, zp = _digits(lead["phone"]), _name_key(lead["name"]), _zip_of(lead["address"])
    row = conn.execute(
        "SELECT 1 FROM seen_leads "
        "WHERE (phone_digits != '' AND phone_digits = ?) "
        "   OR (zip != '' AND name_key = ? AND zip = ?) LIMIT 1",
        (pd, nk, zp),
    ).fetchone()
    return row is not None


def record(conn, lead: dict, slice_id: str, decision: str, confidence: str):
    conn.execute(
        "INSERT OR IGNORE INTO seen_leads "
        "(phone_digits, name_key, zip, company, city_state, category, slice, "
        " decision, confidence, number_status) "
        "VALUES (?,?,?,?,?,?,?,?,?,'unknown')",
        (_digits(lead["phone"]), _name_key(lead["name"]), _zip_of(lead["address"]),
         lead["name"], lead.get("city_state", ""), lead.get("category", ""),
         slice_id, decision, confidence),
    )
    conn.commit()


def mark_number(conn, phone: str, status: str):
    conn.execute("UPDATE seen_leads SET number_status = ? WHERE phone_digits = ?",
                 (status, _digits(phone)))
    conn.commit()


def slice_done(conn, slice_id: str) -> bool:
    """True while a slice sits inside its rest window.

    Worked-out (mostly dupes/rejects) and empty (no Maps results) slices are
    skipped for REVISIT_AFTER_DAYS, then become eligible again — new shops
    appear, and the seen-leads store keeps old ones from re-listing."""
    return conn.execute(
        "SELECT 1 FROM swept_slices WHERE slice = ? "
        "AND result IN ('worked-out', 'empty') "
        "AND last_swept > date('now', '-' || ? || ' days')",
        (slice_id, REVISIT_AFTER_DAYS),
    ).fetchone() is not None


def mark_slice(conn, slice_id: str, result: str):
    conn.execute(
        "INSERT INTO swept_slices (slice, last_swept, result) VALUES (?, date('now'), ?) "
        "ON CONFLICT(slice) DO UPDATE SET last_swept = date('now'), result = excluded.result",
        (slice_id, result),
    )
    conn.commit()
