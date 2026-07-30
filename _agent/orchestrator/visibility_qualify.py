"""Per-lead qualification for the visibility skill, using the committed
system prompt at ../skills/visibility/qualification-prompt.md.

Thinking is explicitly disabled: this is rubric application against fixed
gates, not a reasoning task, and adaptive thinking's token spend was
truncating output before the JSON closed (~20% of calls in testing). A
malformed/truncated response is retried once; if it still won't parse, the
lead is routed to review with a parse_failure flag rather than dropped."""
import json
import re
from anthropic import Anthropic
from config import ANTHROPIC_API_KEY, QUALIFY_MODEL, VISIBILITY_PROMPT_PATH

_client = Anthropic(api_key=ANTHROPIC_API_KEY)


def _load_system_prompt() -> str:
    text = VISIBILITY_PROMPT_PATH.read_text(encoding="utf-8")
    parts = text.split("\n---\n")
    return (parts[1] if len(parts) >= 2 else text).strip()


SYSTEM = _load_system_prompt()


def _qualify_once(user: str):
    resp = _client.messages.create(
        model=QUALIFY_MODEL,
        max_tokens=1024,
        thinking={"type": "disabled"},
        system=SYSTEM,
        messages=[{"role": "user", "content": user}],
    )
    raw = "".join(b.text for b in resp.content if b.type == "text").strip()
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


def _enforce_score_cap(parsed: dict) -> dict:
    """The website-subscore cap (min(website_subscore_raw, 20)) is structural
    per qualification-prompt.md — don't trust the model's own arithmetic to
    apply it. Recompute `score` deterministically whenever all three
    subscores are present; this has caught real model arithmetic slips where
    the reported subscores were correct but the summed score wasn't."""
    profile = parsed.get("profile_subscore")
    website = parsed.get("website_subscore_raw")
    buyer = parsed.get("buyer_subscore")
    if all(isinstance(v, (int, float)) for v in (profile, website, buyer)):
        correct = profile + min(website, 20) + buyer
        if correct != parsed.get("score"):
            parsed.setdefault("flags", []).append(
                f"score_recomputed: model said {parsed.get('score')}, formula gives {correct}"
            )
            parsed["score"] = correct
    return parsed


def _field_or_unreturned(lead: dict, key: str) -> str:
    """Render a field as its value, or explicitly 'not returned by Places'
    when absent — never just omit the line. The model can only declare a
    signals entry `unknown` (qualification-prompt.md) instead of guessing
    `absent` if the payload tells it, per field, whether Places actually
    returned that data."""
    val = lead.get(key)
    if val in (None, "", [], {}):
        return "not returned by Places"
    if isinstance(val, (list, tuple)):
        return ", ".join(str(v) for v in val)
    return str(val)


def _description_status(lead: dict) -> str:
    """Three states, not two. A caller that fetched editorialSummary and got
    nothing back must set lead['description'] = "" explicitly — that is
    itself scoreable profile-completeness information ('Places confirms no
    description exists', the business_description `absent` signal) and is
    not the same fact as a caller that never fetched the field at all (key
    omitted or None, the `unknown` signal). Collapsing these two into one
    'not returned by Places' string is what caused business_description to
    be misjudged inconsistently in testing — the model had no way to tell
    a confirmed-empty field from a never-asked one."""
    if "description" not in lead or lead["description"] is None:
        return "not requested from Places"
    if lead["description"] == "":
        return "requested from Places — confirmed no description present"
    return str(lead["description"])


def qualify(lead: dict) -> dict:
    """Return the qualification JSON (verdict/score/subscores/signals/
    site_class/hook/note/flags) for one lead dict — expects name, phone,
    rating, reviews, types, site_class, site_url, and psi ({'score', 'lcp'}
    or None/error). Also reads primary_type, photos, services, description,
    hours, recent_posts when the caller has them — primary_type in
    particular carries the heaviest single profile-scoring weight (35 of
    ~105 points) and must never be inferred from the generic `types` list.

    `description` has a three-state contract, not the omit-or-value pattern
    the other fields use: omit the key (or pass None) when it was never
    fetched; pass "" explicitly when editorialSummary was fetched and came
    back empty (Places confirms no description — this is itself a scoreable
    fact); pass the real text otherwise. See _description_status()."""
    psi = lead.get("psi") or {}
    user = (
        "Qualify this company. Return ONLY the JSON object.\n\n"
        f"name: {lead['name']}\n"
        f"primary_type: {_field_or_unreturned(lead, 'primary_type')}\n"
        f"types: {_field_or_unreturned(lead, 'types')}\n"
        f"phone: {lead['phone']}\n"
        f"rating: {lead.get('rating')}\n"
        f"review_count: {lead.get('reviews', 0)}\n"
        f"site_class: {lead.get('site_class')}\n"
        f"website: {lead.get('site_url', '')}\n"
        f"psi_mobile_score: {psi.get('score', 'not tested')}\n"
        f"psi_lcp: {psi.get('lcp', 'not tested')}\n"
        f"photos: {_field_or_unreturned(lead, 'photos')}\n"
        f"services: {_field_or_unreturned(lead, 'services')}\n"
        f"business_description: {_description_status(lead)}\n"
        f"hours: {_field_or_unreturned(lead, 'hours')}\n"
        f"posts_last_90_days: {_field_or_unreturned(lead, 'recent_posts')}\n"
    )
    for _ in range(2):
        parsed = _qualify_once(user)
        if parsed is not None:
            return _enforce_score_cap(parsed)
    return {
        "verdict": "review",
        "score": 0,
        "site_class": lead.get("site_class"),
        "hook": "",
        "note": "qualification response failed to parse twice",
        "flags": ["parse_failure"],
    }
