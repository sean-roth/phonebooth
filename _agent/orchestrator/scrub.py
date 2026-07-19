"""Twilio Lookup v2 — flag invalid / disconnected numbers before dialing.

Honest limit: this catches invalid/unassigned numbers and reports line type,
but a valid-but-abandoned business line can still pass. It thins dead numbers;
it does not catch every one. Keep the 'no answer after 2 tries -> dead' habit."""
import re
import requests
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN

LOOKUP_URL = "https://lookups.twilio.com/v2/PhoneNumbers/{e164}"


def _e164(phone: str) -> str:
    d = re.sub(r"\D", "", phone or "")
    if len(d) == 10:
        return "+1" + d
    if len(d) == 11 and d.startswith("1"):
        return "+" + d
    return "+" + d


def check(phone: str) -> str:
    """Return 'valid', 'dead', or 'unknown' (unknown if Twilio is not configured)."""
    if not (TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN):
        return "unknown"
    try:
        resp = requests.get(
            LOOKUP_URL.format(e164=_e164(phone)),
            params={"Fields": "line_type_intelligence"},
            auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
            timeout=15,
        )
        if resp.status_code == 404:
            return "dead"                       # number not found / invalid
        resp.raise_for_status()
        return "dead" if resp.json().get("valid") is False else "valid"
    except requests.RequestException:
        return "unknown"
