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
from datetime import date

from config import SHEETS_SPREADSHEET_ID

WORKSHEET = "Web Development - Master"

# Exactly the 26 columns through "Notes" in the real sheet's column order
# (verified against the live header row). Everything from "Tier" onward is
# intentionally never included in a row we send — append_rows() then leaves
# those cells (human-owned columns, and the PSILink formula) untouched
# rather than risking a value landing in the wrong cell over an ambiguity
# further out in the sheet (Deposit/Balance/Retainer render as what appears
# to be a single merged column live, though output-format.md documents three).
COLUMNS = [
    "Source", "Trade", "Company", "Phone", "Website", "Reviews", "Rating",
    "SiteStatus", "Platform", "PSI", "LCP", "MobileOK", "TapPhone", "HTTPS",
    "GBP", "Observation", "Score", "Hook", "Contact", "Status", "Last Touch",
    "Next Touch", "Attempts", "Audit Sent", "60-Day Re-dial", "Notes",
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
        "LCP": (lead.get("psi") or {}).get("lcp", ""),
        "GBP": _gbp_status(q.get("signals", {})),
        "Score": q.get("score", ""),
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


def append_leads(leads: list, corridor: str, trade: str) -> int:
    """Append leads (each a dict with a populated 'qualification' key) to
    the Web Development - Master tab, highest score first. Returns the
    number of rows written."""
    ordered = sorted(leads, key=lambda l: l["qualification"].get("score", 0), reverse=True)
    rows = [_row(lead, corridor, trade) for lead in ordered]
    gc = _gspread_client()
    sh = gc.open_by_key(SHEETS_SPREADSHEET_ID)
    ws = sh.worksheet(WORKSHEET)
    ws.append_rows(rows, value_input_option="USER_ENTERED")
    return len(rows)
