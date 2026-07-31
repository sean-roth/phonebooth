"""Delivery for the visibility skill — appends to the live "Web Development
- Master" tab (see ../skills/visibility/output-format.md). Separate module
from sink.py deliberately: sink.py's COLUMNS/_row() are hardcoded to the
leads/ skill's manufacturer-lead schema (Source, Segment, Company, Phone,
Region, Contact...) and reusing them here would write the wrong shape of
row into the wrong tab.

OAuth: connects directly via the ~/.config/phonebooth/ credential files
(scoped to spreadsheets only) rather than through sink.py's
GSPREAD_CREDENTIALS/GSPREAD_TOKEN env vars — those are unset in .env, and
sink.py has no working default for this project (its own oauth_setup.py
currently imports a _gspread_client() that doesn't exist in the committed
sink.py). That's a pre-existing gap in the leads/ pipeline, out of scope
here; this module just uses the credential files that are actually on disk
and already authorized."""
import os
import re
from datetime import date

from config import SHEETS_SPREADSHEET_ID

WORKSHEET = "Web Development - Master"
REVIEW_WORKSHEET = "Review"

# Exactly the 29 columns through "Notes" in the real sheet's column order
# (verified against the live header row after the 2026-07-30 cleanup added
# ProfileScore/WebsiteScore/BuyerScore after Score). Everything from "Tier"
# onward is intentionally never included in a row we send — append_rows()
# then leaves those cells (human-owned columns, and the PSILink formula)
# untouched rather than risking a value landing in the wrong cell over an
# ambiguity further out in the sheet (Deposit/Balance/Retainer are three
# separate columns as of the same cleanup).
COLUMNS = [
    "Source", "Trade", "Company", "Phone", "Website", "Reviews", "Rating",
    "SiteStatus", "Platform", "PSI", "LCP", "MobileOK", "TapPhone", "HTTPS",
    "GBP", "Observation", "Score", "ProfileScore", "WebsiteScore", "BuyerScore",
    "Hook", "Contact", "Status", "Last Touch", "Next Touch", "Attempts",
    "Audit Sent", "60-Day Re-dial", "Notes",
]

# Positions in COLUMNS the human owns — left as "" even though they sit
# between agent-written columns, not all trailing.
_HUMAN_COLUMNS = {
    "SiteStatus", "Platform", "MobileOK", "TapPhone", "HTTPS", "Observation",
    "Contact", "Last Touch", "Next Touch", "Attempts", "Audit Sent",
    "60-Day Re-dial",
}


def _gbp_status(signals: dict) -> str:
    """Derive Complete/Thin from the confidently-known profile signals only
    — services_listed and posts_recent are permanently unknown (public API
    limitation, see qualification-prompt.md) and must never push this
    toward "Thin" just because they can't be determined. "Unclaimed" and
    "Missing" aren't derivable from Places data at all — never guessed."""
    concerning = {"generic", "absent"}
    keys = ["primary_category_specific", "photos_full", "business_description", "hours_set"]
    known = [signals.get(k) for k in keys if signals.get(k) not in (None, "unknown")]
    if not known:
        return "Thin"  # nothing confidently known — conservative default
    return "Thin" if any(v in concerning for v in known) else "Complete"


def _bare_lcp(value) -> str:
    """PSI/Lighthouse's displayValue for LCP is a string like "8.4 s" (with
    a non-breaking space). The sheet wants a bare number so it stays
    numeric/sortable — strip any trailing unit text rather than trusting
    the caller to have already extracted the number."""
    if value in (None, ""):
        return ""
    m = re.match(r"^\s*([\d.]+)", str(value))
    return m.group(1) if m else str(value)


def _row(lead: dict, corridor: str, trade: str) -> list:
    q = lead["qualification"]
    values = {
        "Source": f"Places {corridor} {trade} {date.today().isoformat()}",
        "Trade": trade,
        "Company": lead["name"],
        "Phone": lead["phone"],
        "Website": lead.get("site_url", ""),
        "Reviews": lead.get("reviews", ""),
        "Rating": lead.get("rating", ""),
        "PSI": (lead.get("psi") or {}).get("score", ""),
        "LCP": _bare_lcp((lead.get("psi") or {}).get("lcp", "")),
        "GBP": _gbp_status(q.get("signals", {})),
        "Score": q.get("score", ""),
        "ProfileScore": q.get("profile_subscore", ""),
        # Capped, not raw: WebsiteScore must satisfy
        # ProfileScore + WebsiteScore + BuyerScore == Score by direct sheet
        # arithmetic, with no mental min(x, 20) required to audit it.
        "WebsiteScore": (
            min(q["website_subscore_raw"], 20)
            if isinstance(q.get("website_subscore_raw"), (int, float)) else ""
        ),
        "BuyerScore": q.get("buyer_subscore", ""),
        "Hook": q.get("hook", ""),
        "Status": "Not called",
        "Notes": f"[{lead.get('site_class', '')}] {q.get('note', '')}".strip(),
    }
    return [values.get(col, "") if col not in _HUMAN_COLUMNS else "" for col in COLUMNS]


def _gspread_client():
    import gspread
    cfg = os.path.join(os.path.expanduser("~"), ".config", "phonebooth")
    return gspread.oauth(
        credentials_filename=os.path.join(cfg, "oauth-client.json"),
        authorized_user_filename=os.path.join(cfg, "authorized_user.json"),
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )


def _write_rows(ws, rows: list) -> int:
    """Write rows to the given worksheet, highest score already sorted by
    the caller. Does NOT use append_rows()/values.append, even with
    table_range. PSILink (column AJ) holds a formula in every real row,
    well to the right of Notes (column AC) with the blank
    Tier/Price/Deposit/... columns in between -- a second, disjoint block
    at the same row-depth as the real A:AC data. Google's table-detection
    follows that block regardless of table_range (confirmed live:
    table_range="A1:AC1" still returned tableRange 'A1:AJ5' and wrote to
    row 6, because a row with nothing but an AJ formula still counts as
    part of "the table" once any column is considered). table_range
    constrains where values land, not how the next row is found -- it does
    not fix this.

    Compute the target row directly instead: the last row where Company (a
    required field on every real lead) actually has a value, plus one. This
    is immune to whatever is sitting in columns further right, and applies
    equally to any tab built on this same column layout (Web Development -
    Master, Review, and any future duplicate of either)."""
    import gspread
    company_col = ws.col_values(3)
    last_real_row = 1
    for i, v in enumerate(company_col, start=1):
        if v.strip():
            last_real_row = i
    next_row = last_real_row + 1

    last_col_a1 = gspread.utils.rowcol_to_a1(1, len(COLUMNS)).rstrip("0123456789")
    target_range = f"A{next_row}:{last_col_a1}{next_row + len(rows) - 1}"
    ws.update(target_range, rows, value_input_option="USER_ENTERED")
    return len(rows)


def append_leads(leads: list, corridor: str, trade: str) -> int:
    """Append leads (each a dict with a populated 'qualification' key) to
    the Web Development - Master tab, highest score first. Returns the
    number of rows written."""
    ordered = sorted(leads, key=lambda l: l["qualification"].get("score", 0), reverse=True)
    rows = [_row(lead, corridor, trade) for lead in ordered]
    gc = _gspread_client()
    sh = gc.open_by_key(SHEETS_SPREADSHEET_ID)
    ws = sh.worksheet(WORKSHEET)
    return _write_rows(ws, rows)


def append_review_leads(leads: list, corridor: str, trade: str) -> int:
    """Same as append_leads(), but for the 'Review' tab -- ambiguous
    verdicts (ties, suspicious rating patterns, unresolved multi-location
    flags) that a human should eyeball before either calling or discarding.
    Same row shape as the main tab; the Review tab is a duplicate of it, so
    the columns line up."""
    ordered = sorted(leads, key=lambda l: l["qualification"].get("score", 0), reverse=True)
    rows = [_row(lead, corridor, trade) for lead in ordered]
    gc = _gspread_client()
    sh = gc.open_by_key(SHEETS_SPREADSHEET_ID)
    ws = sh.worksheet(REVIEW_WORKSHEET)
    return _write_rows(ws, rows)
