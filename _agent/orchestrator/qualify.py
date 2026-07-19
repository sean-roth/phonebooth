"""Per-lead qualification with Sonnet, using the committed system prompt.

The system prompt is loaded from ../skills/leads/qualification-prompt.md so the
prompt file stays the single source of truth — edit it there to change behavior."""
import json
import re
from anthropic import Anthropic
from config import ANTHROPIC_API_KEY, QUALIFY_MODEL, PROMPT_PATH

_client = Anthropic(api_key=ANTHROPIC_API_KEY)


def _load_system_prompt() -> str:
    """The prompt file wraps the system prompt between --- fences; take that block."""
    text = PROMPT_PATH.read_text()
    parts = text.split("\n---\n")
    return (parts[1] if len(parts) >= 2 else text).strip()


SYSTEM = _load_system_prompt()


def qualify(lead: dict) -> dict:
    """Return {'decision': keep|reject|review, 'confidence': H|M|L, 'note': str}."""
    reviews = lead.get("reviews", []) or ["(none)"]
    user = (
        "Qualify this company. Return ONLY the JSON object.\n\n"
        f"name: {lead['name']}\n"
        f"types: {', '.join(lead.get('types', []))}\n"
        f"address: {lead['address']}\n"
        f"phone: {lead['phone']}\n"
        f"website: {lead.get('website', '')}\n"
        f"rating: {lead.get('rating')}\n"
        f"review_count: {lead.get('review_count', 0)}\n"
        f"hours: {'; '.join(lead.get('hours', []))}\n"
        "reviews:\n- " + "\n- ".join(reviews)
    )
    resp = _client.messages.create(
        model=QUALIFY_MODEL,
        max_tokens=200,
        system=SYSTEM,
        messages=[{"role": "user", "content": user}],
    )
    raw = "".join(b.text for b in resp.content if b.type == "text").strip()
    return _parse(raw)


def _parse(raw: str) -> dict:
    """Extract the JSON object; if it won't parse, send the lead to review."""
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    try:
        obj = json.loads(m.group(0)) if m else {}
    except json.JSONDecodeError:
        obj = {}
    decision = obj.get("decision", "review")
    if decision not in ("keep", "reject"):
        decision = "review"
    return {
        "decision": decision,
        "confidence": obj.get("confidence", "L"),
        "note": obj.get("note", "unparsed model output - check"),
    }
