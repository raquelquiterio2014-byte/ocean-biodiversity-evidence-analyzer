"""Validated OBIS marine species occurrence ingestion."""
import hashlib
import json
from datetime import datetime, timezone
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API = 'https://api.obis.org/v3/occurrence'

def validate_occurrence(record):
    """Return a normalized record or raise ValueError."""
    try:
        lat = float(record['decimalLatitude'])
        lon = float(record['decimalLongitude'])
    except (KeyError, ValueError, TypeError) as exc:
        raise ValueError('Missing or invalid coordinates') from exc
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError('Coordinates out of range')
    name = record.get('scientificName')
    if not isinstance(name, str) or not name.strip():
        raise ValueError('Missing scientific name')
    return {'scientific_name': name.strip(), 'latitude': lat, 'longitude': lon,
            'event_date': record.get('eventDate'), 'dataset_id': record.get('datasetID'),
            'occurrence_id': record.get('occurrenceID')}

def fetch_obis(size=100):
    """Fetch a bounded live sample; never fabricate a response."""
    if not isinstance(size, int) or not 1 <= size <= 300:
        raise ValueError('size must be between 1 and 300')
    url = API + '?' + urlencode({'size': size})
    req = Request(url, headers={'User-Agent': 'OceanBiodiversityEvidenceAnalyzer/1.0'})
    with urlopen(req, timeout=25) as response:
        payload = json.load(response)
    if not isinstance(payload.get('results'), list):
        raise ValueError('Unexpected OBIS response')
    valid, rejected = [], 0
    for item in payload['results']:
        try:
            valid.append(validate_occurrence(item))
        except (ValueError, TypeError):
            rejected += 1
    evidence = {'source_url': url, 'retrieved_at_utc': datetime.now(timezone.utc).isoformat(),
                'records': valid, 'rejected_count': rejected, 'source_type': 'obis_api',
                'data_status': 'real_observations'}
    canonical = json.dumps(evidence['records'], sort_keys=True, ensure_ascii=False)
    evidence['sha256'] = hashlib.sha256(canonical.encode('utf-8')).hexdigest()
    return evidence
