# V3.0 — Sensor Simulation & HTTP API

**Status:** First implementation on development branch. Tests and API behavior must be verified on the user's Windows environment before release.

## Implemented initial scope
- Five **synthetic** measurements: water temperature (degC), pH, salinity (PSU), dissolved oxygen (mg/L), and pressure (dbar).
- Standard-library Python HTTP server bound to **127.0.0.1:8766**, with `GET /health`, `GET /observations`, and `POST /observations`.
- Validation of units, values, UTC timestamps, coordinates, provenance labels and simulated device IDs.
- Local SQLite storage with duplicate protection using SHA-256.
- Offline unit tests; no new Python dependencies.

**Important:** Validation ranges are prototype input guards, not calibrated marine science thresholds. Synthetic measurements are never OBIS occurrences and must not be presented as real field measurements. No ESP32, ROV, AUV, drone, underwater camera, or physical sensor has been connected.

## Run in Windows PowerShell
```powershell
cd D:\ocean-biodiversity-evidence-analyzer
git fetch origin
git switch feature/v3-sensor-simulation-http-api
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m src.api_v3
```

In a **second** PowerShell window, generate and send one synthetic sample:

```powershell
cd D:\ocean-biodiversity-evidence-analyzer
.\.venv\Scripts\python.exe -c "import json,urllib.request; from src.sensors_v3 import generate_observation; payload=json.dumps(generate_observation('water_temperature')).encode(); req=urllib.request.Request('http://127.0.0.1:8766/observations',data=payload,headers={'Content-Type':'application/json'},method='POST'); print(urllib.request.urlopen(req).read().decode())"
```

Then open `http://127.0.0.1:8766/observations` in the browser to inspect stored synthetic records. Stop the server with Ctrl+C.

## Next implementation milestones
- Streamlit V3 dashboard and historical charts.
- Export of stored evidence with integrity checks.
- HTTP-level integration tests and invalid-payload tests.
- Preserve V1.0 and V2.0 apps and the two hardware studies unchanged.

## Architecture
Synthetic simulator → localhost HTTP JSON API → validation → SQLite → future Streamlit V3 dashboard.

**Security boundary:** local educational API only. Do not expose port 8766 to the internet or treat this prototype as a production telemetry service.
