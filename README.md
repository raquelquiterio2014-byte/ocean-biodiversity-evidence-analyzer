# Ocean & Biodiversity Evidence Analyzer — V1.0 and V2.0

COP31 AI Solutions Lab — Day 9 (17 November 2026)

## Versions
- **V1.0 — Biodiversity Evidence Foundation:** run `app.py`; original bounded OBIS occurrence sampling and evidence export preserved.
- **V2.0 — Global Geospatial Explorer:** run `app_v2.py`; approximate ocean-region windows, optional name filtering within returned samples, map, optional iNaturalist taxon reference photos with credits, and SHA-256 evidence export.
- **Hardware studies:** two published feasibility/architecture studies are documentation only; no physical integration is claimed.
- **Validation:** 11 offline unit tests passed locally; a Pacific live-query JSON export of 200 records was audited and its SHA-256 verified on 2026-11-27. See [V2 validation audit](docs/V2_VALIDATION_AUDIT_2026-11-27.md).

## Purpose
An educational, evidence-first marine biodiversity monitoring prototype. This initial build fetches a bounded sample of real marine species occurrence records from the Ocean Biodiversity Information System (OBIS), validates coordinates and scientific names, maps records, and exports evidence with a SHA-256 checksum.

## Requirements
Python 3.11+; internet access for live data.

## Run in PyCharm terminal
```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

## Tests
```bash
python -m unittest discover -s tests -v
```
Eleven offline unit tests passed locally (five V1 and six V2). V1 and V2 interfaces were observed in local screenshots; the V2 Pacific live OBIS export and checksum were audited. See the validation audit for exact scope and remaining limitations.

## Evidence & limitations
- Source: https://api.obis.org/v3/occurrence
- Each export includes the source URL, UTC retrieval time, source type, rejection count and a SHA-256 checksum of normalized records.
- OBIS occurrence records are observations, **not** complete inventories, abundance estimates, or direct evidence of environmental change.
- Live API availability, response schema and data licenses should be reviewed before publication or redistribution.
- No satellite, drone, IoT, computer vision or generative AI integration is claimed in this build.
- A checksum detects changes in exported normalized records; it does not establish scientific truth or authenticate the provider.

## Roadmap
V2.0 adds geospatial exploration as a separate entry point. Satellite, drone/CV, marine IoT, physical hardware integration and AI evidence/human review remain future planned stages.
