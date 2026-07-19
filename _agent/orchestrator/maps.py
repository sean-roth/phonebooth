"""Google Maps Places API (New) — text search with contact + review fields.
Docs: https://developers.google.com/maps/documentation/places/web-service/text-search

Note: phone / website / reviews are higher-SKU fields but within the monthly
free credit at this volume. reviews.text is the priciest field in the mask;
drop it to cut cost (qualification then loses signal like owner names and
auto-shop tells)."""
import requests
from config import GOOGLE_MAPS_API_KEY

SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"

# Only the fields the pipeline actually uses.
FIELD_MASK = ",".join([
    "places.id",
    "places.displayName",
    "places.formattedAddress",
    "places.nationalPhoneNumber",
    "places.websiteUri",
    "places.rating",
    "places.userRatingCount",
    "places.types",
    "places.regularOpeningHours.weekdayDescriptions",
    "places.reviews.text",
])


def search(query: str, max_results: int = 10) -> list[dict]:
    """Return a list of normalized candidate place dicts for a text query."""
    if not GOOGLE_MAPS_API_KEY:
        raise RuntimeError("GOOGLE_MAPS_API_KEY not set")
    resp = requests.post(
        SEARCH_URL,
        headers={
            "Content-Type": "application/json",
            "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
            "X-Goog-FieldMask": FIELD_MASK,
        },
        json={"textQuery": query, "maxResultCount": min(max_results, 20)},
        timeout=30,
    )
    resp.raise_for_status()
    return [_normalize(p) for p in resp.json().get("places", [])]


def _normalize(p: dict) -> dict:
    """Flatten the Places response into the fields the pipeline uses."""
    reviews = [r.get("text", {}).get("text", "") for r in p.get("reviews", [])]
    hours = p.get("regularOpeningHours", {}).get("weekdayDescriptions", [])
    return {
        "place_id": p.get("id", ""),
        "name": p.get("displayName", {}).get("text", ""),
        "address": p.get("formattedAddress", ""),
        "phone": p.get("nationalPhoneNumber", ""),   # US format, e.g. "(630) 766-3121"
        "website": p.get("websiteUri", ""),
        "rating": p.get("rating"),
        "review_count": p.get("userRatingCount", 0),
        "types": p.get("types", []),
        "hours": hours,
        "reviews": [r for r in reviews if r][:5],
    }
