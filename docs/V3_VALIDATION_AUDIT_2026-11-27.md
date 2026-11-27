# V3.0 — Local Validation & Export Audit (2026-11-27)

**Status:** User-validated local prototype on Windows, pending final release review.

## Evidence from local execution
- Python unittest suite: **17/17 passed** (V1 + V2 + V3).
- HTTP `GET /health`: `{"status":"ok","mode":"synthetic_only"}`.
- HTTP `POST /observations`: response confirmed `stored: true` and `source_type: synthetic_simulator`.
- HTTP `GET /observations`: returned persisted water temperature sample, **24.127 degC**.
- Streamlit `app_v3.py`: screenshot confirmed local API connection, history table and temperature/DO chart display.
- Export file `v3_synthetic_observations.json` was supplied and inspected separately.

## JSON audit results
- 9 exported synthetic observations, spanning 5 measurements.
- Temperature: 2 records, 24.127 and 23.464 degC.
- pH: 1 record, 8.126 pH.
- Salinity: 1 record, 36.012 PSU.
- Dissolved oxygen: 3 records, each 7.363 mg/L.
- Pressure: 2 records, each 16.408 dbar.
- All nine timestamps parsed as UTC, with `source_type=synthetic_simulator`, `quality_flag=synthetic_demo`, and null calibration references.
- 9 unique complete record payloads. Repeated measurement values have distinct timestamps and are not byte-identical record duplicates.
- SHA-256 of **the uploaded export file bytes**: `e68bd9ea5efc047b82216359c7f639ca987088d2ec6849ef3b76ba78cd191e6b`.

## Scope and caveats
This validates the local educational prototype and exported file structure, not physical instrumentation, calibration, field conditions, oceanographic accuracy, or production deployment. File SHA-256 was computed independently from the uploaded export; no independent byte-for-byte comparison with the user's SQLite database has been performed. Streamlit chart display was observed, but full HTTP error-path integration tests and release review remain future hardening work. V1/V2 OBIS records remain separate from synthetic sensor data.
