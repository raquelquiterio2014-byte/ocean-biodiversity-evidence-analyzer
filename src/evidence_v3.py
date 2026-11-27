"""Integrity manifest for exported synthetic observations."""
import hashlib
import json

def canonical_records(records):
    return json.dumps(records, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")

def export_evidence(records):
    if not isinstance(records, list) or any(not isinstance(r, dict) or r.get("source_type") != "synthetic_simulator" for r in records):
        raise ValueError("Export accepts synthetic records only")
    return {
        "schema_version": "1.0",
        "source_type": "synthetic_simulator",
        "record_count": len(records),
        "records_sha256": hashlib.sha256(canonical_records(records)).hexdigest(),
        "hash_scope": "canonical_json_records_only",
        "records": records,
    }

def verify_evidence(export):
    if not isinstance(export, dict) or export.get("source_type") != "synthetic_simulator":
        return False
    records = export.get("records")
    if not isinstance(records, list) or any(not isinstance(r, dict) or r.get("source_type") != "synthetic_simulator" for r in records):
        return False
    if export.get("record_count") != len(records):
        return False
    try:
        return hashlib.sha256(canonical_records(records)).hexdigest() == export.get("records_sha256")
    except (ValueError, TypeError):
        return False
