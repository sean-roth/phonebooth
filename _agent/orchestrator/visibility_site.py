"""Site classification for the visibility skill's unlinked-site rule (see
../skills/visibility/SKILL.md). An empty Places websiteUri does not mean no
website — it means not linked to the profile, which is the highest-value
signal. This module finds that site by guessing domains from the business
name and a trade noun, then checking existence by HTTP status only."""
from urllib.parse import urlparse

import requests

STOPWORDS = {"and", "the", "llc", "inc", "co", "company", "of"}

# Domain marketplaces / parking services. A guessed domain that redirects to
# one of these isn't a real business site — it's an expired or never-owned
# domain being resold or squatted. Caught by hostname only, never body
# content: domain_exists() already follows redirects and reports the final
# URL, so this is a lookup against that URL's host, not a fetch of anything
# new.
PARKING_HOSTS = {
    "buydomains.com", "hugedomains.com", "dan.com", "sedo.com",
    "afternic.com", "domainmarket.com", "undeveloped.com", "above.com",
    "bodis.com", "parkingcrew.net", "sedoparking.com", "godaddy.com",
    "networksolutions.com", "namecheap.com",
}

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
    # Strip apostrophes rather than treating them as separators — "Ivan's"
    # must tokenize to "ivans", not split into "ivan" + a stray "s" token
    # (which corrupts the hyphenated/possessive variants downstream even
    # though straight concatenation happens to hide the damage).
    segment = segment.replace("'", "").replace("’", "")
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


def _host(url):
    h = (urlparse(url).hostname or "").lower()
    return h[4:] if h.startswith("www.") else h


def _is_parking_host(hostname):
    return any(hostname == p or hostname.endswith("." + p) for p in PARKING_HOSTS)


def domain_exists(base):
    """Existence check by HTTP status only — never parse body, never require
    200. ANY response (incl. 403/401/ROBOTS_DISALLOWED-style blocks) means the
    domain exists; only a connection failure/timeout means it doesn't.

    Returns None, or a dict {'url', 'domain_mismatch'}. A known parking/
    marketplace host (the guessed domain redirects to a for-sale lander, not
    a real site) is treated as not-existing — try the next candidate. Any
    OTHER final host that doesn't match the guessed domain is still returned
    (it may be a legitimate forwarding/rebrand), but flagged via
    domain_mismatch so a human double-checks before trusting SITE_UNLINKED."""
    guessed_host = f"{base}.com"
    for scheme in ("https://", "http://"):
        url = f"{scheme}{base}.com"
        try:
            r = requests.head(url, timeout=8, allow_redirects=True,
                               headers={"User-Agent": "Mozilla/5.0"})
        except requests.RequestException:
            try:
                r = requests.get(url, timeout=8, allow_redirects=True, stream=True,
                                  headers={"User-Agent": "Mozilla/5.0"})
                r.close()
            except requests.RequestException:
                continue
        final_host = _host(r.url)
        if not final_host or _is_parking_host(final_host):
            continue
        return {"url": r.url, "domain_mismatch": final_host != guessed_host}
    return None


def guess_domain(name, trade=None, log=None):
    """Try each candidate in order; return the first result dict that
    resolves ({'url', 'domain_mismatch'}), or None. `log`, if given, collects
    (candidate, source_label, resolved_result) for every attempt — useful
    when a miss needs diagnosing."""
    for base, label in domain_candidates(name, trade):
        found = domain_exists(base)
        if log is not None:
            log.append((base, label, found))
        if found:
            return found
    return None


def classify_site(place, trade=None):
    """Return (site_class, site_url, flags) for a normalized Places result
    dict (must have 'websiteUri' and 'displayName'.'text'). `flags` is a
    list of strings, non-empty only when something about the classification
    needs a human's attention before it's trusted."""
    site = place.get("websiteUri", "")
    name = place.get("displayName", {}).get("text", "")
    if site:
        if "facebook.com" in site or "instagram.com" in site:
            return "SOCIAL_ONLY", site, []
        return "SITE_LINKED", site, []
    guessed = guess_domain(name, trade=trade)
    if guessed:
        flags = []
        if guessed["domain_mismatch"]:
            flags.append(
                f"domain_mismatch: guessed domain resolved to a different "
                f"registrable domain ({guessed['url']}) — verify this is a real "
                f"forwarding/rebrand and not a parked or unrelated site before "
                f"treating as SITE_UNLINKED"
            )
        return "SITE_UNLINKED", guessed["url"], flags
    # No domain pattern resolved — the SKILL.md fallback is a phone-number web
    # search, which only a live agent session can run (WebSearch tool). This
    # module can't call it, so it surfaces the need rather than guessing NO_SITE.
    return "NEEDS_PHONE_SEARCH", "", []
