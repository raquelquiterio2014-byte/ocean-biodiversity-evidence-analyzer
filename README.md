# Ocean & Biodiversity Evidence Analyzer V1.0

COP31 AI Solutions Lab — Day 9 (17 November 2026)

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
Five offline unit tests pass using mocked API data. Live API and GUI testing remain pending.

## Evidence & limitations
- Source: https://api.obis.org/v3/occurrence
- Each export includes the source URL, UTC retrieval time, source type, rejection count and a SHA-256 checksum of normalized records.
- OBIS occurrence records are observations, **not** complete inventories, abundance estimates, or direct evidence of environmental change.
- Live API availability, response schema and data licenses should be reviewed before publication or redistribution.
- No satellite, drone, IoT, computer vision or generative AI integration is claimed in this build.
- A checksum detects changes in exported normalized records; it does not establish scientific truth or authenticate the provider.

## Roadmap
V1.1 is reserved for a later geospatial enhancement release. Satellite, drone/CV, marine IoT and AI evidence/human review are future planned stages.
