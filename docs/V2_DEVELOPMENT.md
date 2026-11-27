# V2.0 — Global Geospatial Explorer (development branch)

**Status:** V2.0 locally validated on 2026-11-27 (11 unit tests passed; live Pacific OBIS export and SHA-256 audit verified). See [V2 validation audit](V2_VALIDATION_AUDIT_2026-11-27.md). Other regions and provider licensing are not comprehensively certified.

## Scope
- Choose an approximate ocean search window: Global, Atlantic, Pacific, Indian, Arctic, Southern Ocean.
- Request OBIS records using WKT polygon `geometry` parameters for non-global windows.
- Pacific uses two rectangles to avoid dateline-crossing WKT complexity.
- Optional case-insensitive scientific-name substring filter applies **only to the returned sample**, not the full OBIS database.
- Display interactive map, table, missing-field counts, taxon reference photos and their credits, and SHA-256 evidence JSON.
- Retain V1.0 in `app.py`; V2.0 adds `app_v2.py` without replacing the V1 entry point.

## Run on Windows PowerShell
```powershell
git fetch origin
git switch feature/v2-global-geospatial-explorer
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m streamlit run app_v2.py
```

## Scientific limitations
- Rectangular search windows overlap and are **not authoritative ocean boundaries**.
- The returned rows are bounded **samples** and may change between API requests.
- Counts are not biodiversity, species richness or abundance estimates.
- Invalid/outside-window rows are counted as rejected; name-filtered rows are excluded without being called invalid.
- OBIS records are real scientific occurrence records; photos are separate taxon reference images.
- No satellite, physical sensor, drone, ROV, AUV or AI integration is implemented.
- Pacific approximate two-window live query was verified with 200 exported records. Other region requests require further coverage checks.

## Manual acceptance checks
1. Run all V1 and V2 tests without failures.
2. Query Atlantic, Pacific and Global; inspect query URLs and map coordinates.
3. Confirm empty name search is handled without fabricated records.
4. Toggle reference photos; inspect source credits and licenses.
5. Export JSON and recompute SHA-256 over `records` using `json.dumps(records, sort_keys=True, ensure_ascii=False)`.
6. Confirm V1.0 `app.py` remains runnable and hardware studies remain untouched.
