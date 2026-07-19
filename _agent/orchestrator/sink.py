"""Output: always write a dated CSV; optionally append to a Google Sheet.

The CSV is the reliable, reviewable artifact (paste into your tracker, same as
the manual batches). The Sheet append is opt-in (SHEETS_ENABLED=true) and needs
gspread + a service-account key."""
import csv
from datetime import date
from config import (OUTPUT_DIR, SHEETS_ENABLED, SHEETS_SPREADSHEET_ID,
                    SHEETS_WORKSHEET, SHEETS_REVIEW_WORKSHEET, GOOGLE_SA_JSON)

COLUMNS = ["Source", "Segment", "Company", "Phone", "Region", "Contact",
           "Status", "Last Touch", "Next Touch", "Hiring Cadence #",
           "Info Sent", "60-Day Re-dial", "Notes"]


def _row(lead: dict, verdict: dict) -> list:
    note = f"[{verdict['confidence']}] {lead.get('category', '')} · {verdict['note']}"
    return ["Places (mfg)", "Manufacturer", lead["name"], lead["phone"],
            lead.get("city_state", ""), "", "Not called", "", "", "", "", "", note]


def write_csv(keepers, review) -> str:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / f"leads-{date.today().isoformat()}.csv"
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(COLUMNS)
        for lead, verdict in keepers:
            w.writerow(_row(lead, verdict))
        if review:
            w.writerow([])
            w.writerow(["--- REVIEW (model unsure) ---"])
            for lead, verdict in review:
                w.writerow(_row(lead, verdict))
    return str(path)


def append_sheet(keepers, review):
    """Append to the live Google Sheet. No-op unless SHEETS_ENABLED."""
    if not SHEETS_ENABLED:
        return
    import gspread
    gc = gspread.service_account(filename=GOOGLE_SA_JSON)
    sh = gc.open_by_key(SHEETS_SPREADSHEET_ID)
    sh.worksheet(SHEETS_WORKSHEET).append_rows(
        [_row(l, v) for l, v in keepers], value_input_option="USER_ENTERED")
    if review:
        try:
            rev = sh.worksheet(SHEETS_REVIEW_WORKSHEET)
        except gspread.WorksheetNotFound:
            rev = sh.add_worksheet(SHEETS_REVIEW_WORKSHEET, rows=200, cols=len(COLUMNS))
            rev.append_row(COLUMNS)
        rev.append_rows([_row(l, v) for l, v in review], value_input_option="USER_ENTERED")
