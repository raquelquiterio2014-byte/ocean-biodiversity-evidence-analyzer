"""Optional taxon reference photos from iNaturalist (not occurrence photographs)."""
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen

TAXA_API = "https://api.inaturalist.org/v1/taxa/autocomplete"

def reference_photo(scientific_name):
    """Return a species-level taxon photo with attribution, or None.

    A photo represents the taxon, not the specific OBIS observation.
    Network failures never block the primary biodiversity workflow.
    """
    if not isinstance(scientific_name, str) or not scientific_name.strip():
        return None
    name = scientific_name.strip()
    # Avoid assigning a species photograph to higher taxa or ambiguous names.
    if len(name.split()) != 2:
        return None
    url = TAXA_API + "?" + urlencode({"q": name, "per_page": 10})
    request = Request(url, headers={"User-Agent": "OceanBiodiversityEvidenceAnalyzer/1.0", "Accept": "application/json"})
    try:
        with urlopen(request, timeout=8) as response:
            results = json.load(response).get("results", [])
    except (OSError, ValueError, TypeError, AttributeError):
        return None
    for taxon in results:
        if taxon.get("name", "").casefold() != name.casefold() or taxon.get("rank") != "species":
            continue
        photo = taxon.get("default_photo") or {}
        image_url = photo.get("medium_url") or photo.get("url")
        taxon_id = taxon.get("id")
        if not image_url or not image_url.startswith("https://") or not taxon_id:
            continue
        return {
            "image_url": image_url,
            "taxon_url": "https://www.inaturalist.org/taxa/" + str(taxon_id),
            "attribution": photo.get("attribution") or "See iNaturalist taxon page for photo credits",
            "license_code": photo.get("license_code") or "unspecified",
            "source": "iNaturalist taxon reference photo",
        }
    return None
