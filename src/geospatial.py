"""V2 experimental OBIS geographic querying. Ocean boxes are approximate."""
import hashlib
import json
import math
from datetime import datetime, timezone
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from src.core import API, validate_occurrence

# Approximate geographic search windows, NOT scientific ocean boundaries.
# Dateline-crossing Pacific is split into two query windows.
REGIONS = {
    "Global": [(-180, -90, 180, 90)],
    "Atlantic (approx.)": [(-70, -60, 20, 70)],
    "Pacific (approx.)": [(120, -60, 180, 65), (-180, -60, -70, 65)],
    "Indian (approx.)": [(20, -60, 120, 30)],
    "Arctic (approx.)": [(-180, 66, 180, 90)],
    "Southern Ocean (approx.)": [(-180, -90, 180, -60)],
}

def validate_bbox(bbox):
    if len(bbox) != 4:
        raise ValueError("Bounding box must contain west, south, east, north")
    west, south, east, north = (float(x) for x in bbox)
    if not all(math.isfinite(x) for x in (west, south, east, north)):
        raise ValueError("Coordinates must be finite")
    if not (-180 <= west < east <= 180 and -90 <= south < north <= 90):
        raise ValueError("Invalid bounding box")
    return west, south, east, north

def polygon_wkt(bbox):
    w, s, e, n = validate_bbox(bbox)
    return f"POLYGON(({w} {s},{e} {s},{e} {n},{w} {n},{w} {s}))"

def inside_bbox(record, bbox):
    w, s, e, n = validate_bbox(bbox)
    return w <= record["longitude"] <= e and s <= record["latitude"] <= n

def quality_summary(records):
    fields = ("event_date", "dataset_id", "occurrence_id")
    return {"records": len(records), **{
        "missing_" + key: sum(not r.get(key) for r in records) for key in fields
    }, "distinct_scientific_names": len({r["scientific_name"] for r in records})}

def fetch_region(region="Global", size=100, scientific_name=""):
    """Request geographically bounded samples from OBIS; no synthetic fallback.

    size is a per-window cap. A Pacific request can retrieve up to 2*size.
    Name search is a transparent local filter on the bounded sample, not an
    exhaustive taxon search or a global abundance estimate.
    """
    if region not in REGIONS:
        raise ValueError("Unknown region")
    if type(size) is not int or not 1 <= size <= 300:
        raise ValueError("size must be 1..300")
    name_filter = scientific_name.strip().casefold()
    if len(name_filter) > 120:
        raise ValueError("Scientific name filter too long")
    records, rejected, urls, seen = [], 0, [], set()
    for bbox in REGIONS[region]:
        params = {"size": size}
        if region != "Global":
            params["geometry"] = polygon_wkt(bbox)
        url = API + "?" + urlencode(params)
        urls.append(url)
        req = Request(url, headers={"User-Agent": "OceanBiodiversityEvidenceAnalyzer/2.0", "Accept": "application/json"})
        with urlopen(req, timeout=25) as response:
            payload = json.load(response)
        if not isinstance(payload, dict) or not isinstance(payload.get("results"), list):
            raise ValueError("Unexpected OBIS response")
        for item in payload["results"]:
            try:
                normalized = validate_occurrence(item)
                if region != "Global" and not inside_bbox(normalized, bbox):
                    rejected += 1
                    continue
                if name_filter and name_filter not in normalized["scientific_name"].casefold():
                    continue
                key = (normalized.get("occurrence_id") or "", normalized["scientific_name"],
                       normalized["latitude"], normalized["longitude"], normalized.get("event_date"))
                if key not in seen:
                    seen.add(key)
                    records.append(normalized)
            except (ValueError, TypeError):
                rejected += 1
    evidence = {
        "source_type": "obis_api", "data_status": "real_observations",
        "region": region, "region_boundaries": "approximate_rectangles_not_official_ocean_boundaries",
        "requested_per_window": size, "scientific_name_filter": scientific_name.strip(),
        "name_filter_scope": "client_side_within_returned_sample",
        "source_urls": urls, "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "records": records, "rejected_count": rejected,
        "quality": quality_summary(records),
    }
    canonical = json.dumps(records, sort_keys=True, ensure_ascii=False)
    evidence["sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return evidence
