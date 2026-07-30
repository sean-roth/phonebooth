"""Site classification for the visibility skill's unlinked-site rule (see
../skills/visibility/SKILL.md). An empty Places websiteUri does not mean no
website — it means not linked to the profile, which is the highest-value
signal. This module finds that site by guessing domains from the business
name and a trade noun, then checking existence by HTTP status only."""
import requests

STOPWORDS = {"and", "the", "llc", "inc", "co", "company", "of"}

# Trade noun candidates per sweep-matrix.md trade. Business names rarely spell
# out the exact trade word ("Bud Chimney & Gutter" -> budchimneysweep.com) so
# these get appended to name-derived tokens as their own guess.
TRADE_NOUNS = {
    "chimney sweep": ["sweep", "chimneysweep"],
    "snow removal": ["snow", "snowplow", "plowing"],
    "gutters": ["gutter", "gutters"],
    "hvac": ["hvac", "heating", "cooling"],
    "garage doors": ["garage", "garagedoor"],
    "duct cleaning": ["duct", "ductcleaning"],
    "interior painting": ["painting", "painters"],
}


def _tokens(segment):
    return [t for t in "".join(ch if ch.isalnum() else " " for ch in segment.lower()).split()
            if t not in STOPWORDS]


def domain_candidates(name, trade=None):
    """Generate domain-guess candidates: primary-segment concat, primary+trade
    noun, full-name concat, hyphenated, possessive. Returns (candidate_str,
    source_label) pairs, most-likely first."""
    segments = [s for s in name.replace(" and ", " & ").split("&")]
    primary_tokens = _tokens(segments[0]) if segments else _tokens(name)
    all_tokens = _tokens(name)
    trade_nouns = TRADE_NOUNS.get(trade, []) if trade else []

    out = []
    if primary_tokens:
        base = "".join(primary_tokens)
        out.append((base, "primary segment"))
        out.append(("-".join(primary_tokens), "primary segment hyphenated"))
        for noun in trade_nouns:
            out.append((base + noun, f"primary segment + trade noun '{noun}'"))
        possessive = primary_tokens[0] + "s" + "".join(primary_tokens[1:])
        out.append((possessive, "possessive variant"))
    if all_tokens:
        out.append(("".join(all_tokens), "full name concatenated"))
    seen = set()
    deduped = []
    for base, label in out:
        if base and base not in seen:
            seen.add(base)
            deduped.append((base, label))
    return deduped


def domain_exists(base):
    """Existence check by HTTP status only — never parse body, never require
    200. ANY response (incl. 403/401/ROBOTS_DISALLOWED-style blocks) means the
    domain exists; only a connection failure/timeout means it doesn't."""
    for scheme in ("https://", "http://"):
        url = f"{scheme}{base}.com"
        try:
            r = requests.head(url, timeout=8, allow_redirects=True,
                               headers={"User-Agent": "Mozilla/5.0"})
            return r.url
        except requests.RequestException:
            try:
                r = requests.get(url, timeout=8, allow_redirects=True, stream=True,
                                  headers={"User-Agent": "Mozilla/5.0"})
                r.close()
                return r.url
            except requests.RequestException:
                continue
    return None


def guess_domain(name, trade=None, log=None):
    """Try each candidate in order; return the first URL that resolves.
    `log`, if given, collects (candidate, source_label, resolved_url) for
    every attempt — useful when a miss needs diagnosing."""
    for base, label in domain_candidates(name, trade):
        found = domain_exists(base)
        if log is not None:
            log.append((base, label, found))
        if found:
            return found
    return None


def classify_site(place, trade=None):
    """Return (site_class, site_url) for a normalized Places result dict
    (must have 'websiteUri' and 'displayName'.'text')."""
    site = place.get("websiteUri", "")
    name = place.get("displayName", {}).get("text", "")
    if site:
        if "facebook.com" in site or "instagram.com" in site:
            return "SOCIAL_ONLY", site
        return "SITE_LINKED", site
    guessed = guess_domain(name, trade=trade)
    if guessed:
        return "SITE_UNLINKED", guessed
    # No domain pattern resolved — the SKILL.md fallback is a phone-number web
    # search, which only a live agent session can run (WebSearch tool). This
    # module can't call it, so it surfaces the need rather than guessing NO_SITE.
    return "NEEDS_PHONE_SEARCH", ""
