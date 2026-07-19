"""One-time seeder: load hand-built tracker rows into the dedup store.

Before the agent's first real run, the seen-leads DB has never heard of the
hand-built batches — so the first sweep through an already-worked corridor
would re-source companies already in the tracker and append them as fresh
leads. Fix: export the tracker (File > Download > CSV in Google Sheets, one
tab or dated lead file at a time) and run this once per export:

    python seed.py path/to/tracker-export.csv [more.csv ...]

Safe to re-run: inserts are INSERT OR IGNORE, so already-known rows are
skipped. Rows without a phone are skipped too — phone is the primary dedup
key, and the tracker's Region column has no ZIP, so the name+ZIP fallback
cannot apply to seeded rows."""
import csv
import sys

import dedup

# Tracker columns we read (matched case-insensitively from the header row).
COMPANY, PHONE, REGION = "company", "phone", "region"


def _find_columns(header: list) -> dict:
    idx = {}
    for i, col in enumerate(header):
        key = (col or "").strip().lower()
        if key in (COMPANY, PHONE, REGION) and key not in idx:
            idx[key] = i
    missing = [k for k in (COMPANY, PHONE) if k not in idx]
    if missing:
        raise SystemExit(
            f"CSV header missing column(s): {', '.join(missing)}. "
            "Expected the tracker format (Company / Phone / Region).")
    return idx


def seed(paths: list):
    conn = dedup.connect()
    read = seeded = skipped = 0
    for path in paths:
        with open(path, newline="", encoding="utf-8-sig") as f:
            rows = csv.reader(f)
            header = next(rows, None)
            if header is None:
                continue
            idx = _find_columns(header)
            for row in rows:
                if not row or len(row) <= idx[PHONE]:
                    continue  # blank / separator rows in exports
                read += 1
                name = row[idx[COMPANY]].strip()
                phone = row[idx[PHONE]].strip()
                region = (row[idx[REGION]].strip()
                          if REGION in idx and len(row) > idx[REGION] else "")
                if not name or not any(ch.isdigit() for ch in phone):
                    skipped += 1
                    continue
                before = conn.total_changes
                dedup.record(conn,
                             {"phone": phone, "name": name, "address": region,
                              "city_state": region, "category": ""},
                             "seed:tracker", "seeded", "")
                if conn.total_changes > before:
                    seeded += 1
    print(f"Read {read} rows -> {seeded} seeded, {skipped} skipped (no "
          f"phone/name), {read - seeded - skipped} already known.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python seed.py <tracker-export.csv> [more.csv ...]")
    seed(sys.argv[1:])
