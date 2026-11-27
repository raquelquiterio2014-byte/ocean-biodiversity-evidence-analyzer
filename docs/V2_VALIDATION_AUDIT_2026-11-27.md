# V2.0 validation and evidence audit — 2026-11-27

## Scope and evidence
Project: Ocean & Biodiversity Evidence Analyzer — Global Geospatial Explorer V2.0.
Evidence artifact: `obis_geospatial_evidence.json`, exported locally on 2026-11-27 at `2026-11-27T16:41:04.937895+00:00`.
The user ran `python -m unittest discover -s tests -v` on Windows PowerShell: **11 tests passed** (five core and six geospatial). Screenshots document a working Streamlit V2 interface, regional mapping, optional taxon reference photos, photo credits and licenses. These are user-observed local tests, not independent CI execution.

## Pacific live-query audit
- Source: OBIS occurrence API (`source_type=obis_api`, `data_status=real_observations`).
- Region: `Pacific (approx.)`; **two approximate rectangular windows**, not authoritative ocean boundaries.
- Requested: 100 occurrences per window, 200 records exported.
- Rejected/outside-window: 0.
- Distinct scientific names in sample: 145; **not a species-richness estimate**.
- Missing `event_date`: 3; `dataset_id`: 176; `occurrence_id`: 7.
- Exact duplicate normalized records in export: 0.
- No scientific-name substring filter was applied.
- Source query URLs and retrieval timestamp are embedded in the exported JSON.

## SHA-256 integrity check
The checksum was independently recalculated from the supplied JSON using the same canonicalization as `src/geospatial.py`:

```python
import hashlib, json
with open("obis_geospatial_evidence.json", encoding="utf-8") as f:
    evidence = json.load(f)
canonical = json.dumps(evidence["records"], sort_keys=True, ensure_ascii=False)
assert hashlib.sha256(canonical.encode("utf-8")).hexdigest() == evidence["sha256"]
```

Expected/verified SHA-256:
`52989b463c9dc40656e946f4fe1ae1789bece6cd293f4da3f05c2569948b78b4`

The checksum validates the integrity of the **normalized records** in this export; it does not authenticate OBIS or establish biological truth. Photo URLs and photo attribution are UI enrichment and are not added to `records` or included in their checksum.

## Preservation and acceptance
- V1.0 remains runnable through `app.py`; V2.0 runs separately through `app_v2.py`.
- The two pre-existing hardware feasibility/architecture studies are retained as documentation. No physical sensors, ROV, AUV, drones, satellite processing, or AI integration is claimed.
- Live Pacific query and exported JSON were checked; Atlantic and Global were visually demonstrated in user screenshots, but comprehensive region-by-region live regression and licensing review are not claimed.
- API responses can vary over time; record counts are bounded samples, not ocean abundance or coverage estimates.

## Reproduction (PowerShell)
```powershell
cd D:\ocean-biodiversity-evidence-analyzer
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m streamlit run app_v2.py
```
Select Pacific (approx.), 100 per window, blank name filter; query, inspect map and photo credits, export JSON and run the checksum verification above.
