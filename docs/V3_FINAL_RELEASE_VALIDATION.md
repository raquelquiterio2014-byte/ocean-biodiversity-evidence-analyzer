# V3.0 — Final Release Validation

Date: 2026-11-27

## Validation evidence
- Windows Python unittest: **23 tests passed, 0 failures**, including V1/V2 regression checks.
- Local HTTP integration tests: health 200, first POST 201, duplicate POST 200, GET 200, invalid unit 400, malformed JSON 400, missing route 404.
- User demonstrated Streamlit dashboard, SQLite history and synthetic charts.
- User-provided final JSON export: **9 records, 5 measurement types**.
- Export's declared `record_count=9` matches the actual record count.
- Independently recalculated SHA-256 of canonical JSON records: `b2aaa602083cc7abdc8d92f2c0d740f44b43d50bb738df697df086bd8b1e56b8`, matching the `records_sha256` manifest field.
- All exported records have `source_type=synthetic_simulator`, `quality_flag=synthetic_demo` and valid UTC timestamps.
- SHA-256 of uploaded export **file bytes** (distinct from canonical-record digest): `2e74c49e0b9570241def17b98d66a66a3bf24fe5d9e8c5c3d189775cd8a2d6a8`.

## Limits
The prototype runs locally on 127.0.0.1; there are no connected physical devices or field measurements. Synthetic readings are not scientific ocean observations. Hashes detect content changes relative to a trusted digest, but do not prove origin, calibration, scientific correctness, or independently reconcile the user's SQLite database. The system is an educational prototype, not production telemetry infrastructure.

## Release scope
- `app_v3.py`: Streamlit monitoring and JSON evidence export.
- `src/sensors_v3.py`: five synthetic measurement types.
- `src/api_v3.py`: localhost HTTP API and SQLite.
- `src/evidence_v3.py`: canonical-record SHA-256 manifest and verification.
- `tests/test_sensors_v3.py`, `tests/test_http_evidence_v3.py`: tests.
- Prior V1 and V2 apps remain available independently.
