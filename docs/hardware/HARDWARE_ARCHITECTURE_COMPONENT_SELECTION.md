# Hardware Architecture & Component Selection
## Global Ocean Observatory | Ocean & Biodiversity Evidence Analyzer
**Special Engineering Study 2 | COP31 AI Solutions Lab — Day 9**

**Status:** Proposed architecture and reference component selection; software-only project. No hardware has been acquired, assembled, connected, deployed, or tested. No device integration is claimed.

**Relationship to Study 1:** [Marine Monitoring Hardware Feasibility Study](HARDWARE_FEASIBILITY_STUDY.md). This document builds on its candidate matrix and constraints.

## 1. Architecture decision
Continue the validated OBIS-based V1.0 unchanged. Develop an **independent, optional ingestion subsystem** for future synthetic sensor streams and licensed external image/mission datasets. Never mix simulated measurements with real OBIS occurrence records.

**Primary selection criterion:** documented data interfaces that can be represented and validated in Python, not purchase price or presumed marine readiness.

## 2. Reference components and engineering rationale

| Function | Reference selection | Rationale for software study | Caveat / validation needed |
|---|---|---|---|
| Controller/gateway | Espressif ESP32-S3 | Well-documented I²C, UART, Wi-Fi; enables hypothetical device-to-HTTP adapter | Board/pinout, voltage levels, network security, timing and wiring not validated |
| Temperature | Encapsulated DS18B20 | Simple digital temperature schema and 1-Wire concept | Probe encapsulation and saltwater durability not established |
| Conductivity/salinity | Atlas Scientific EZO-EC + suitable probe | Documented digital interface and compensation concepts | Probe selection, calibration and conductivity-to-salinity assumptions |
| pH | Atlas Scientific EZO-pH + electrode | Digital pH readings and calibration metadata | Maintenance, buffers, electrode suitability |
| Dissolved oxygen | Atlas Scientific EZO-DO + probe | Digital DO data and environmental compensation metadata | Calibration, maintenance, correction factors |
| Pressure/depth | Blue Robotics Bar30 | Documented underwater pressure sensor for depth-related telemetry | Pressure reference, water density, deployment rating and I²C compatibility |
| Underwater camera + ROV | Blue Robotics BlueROV2 | Reference platform for underwater images and telemetry | Media export, API availability, tether/operations and licensing |
| Acoustic sensing | Blue Robotics Ping sonar family | Structured range/profile data and potential adapter boundary | Exact model and protocol differ; no integration tested |
| Coastal imagery | DJI Mavic 3 Multispectral | RGB/multispectral imagery and georeferencing for coastal analysis | Image processing, licensing, flight regulations, calibration |
| Autonomous survey | AUV category (no model selected) | Generic mission log and navigation schema | No specific vendor selected; underwater navigation is complex |

**Why not purchase:** The educational goal is to validate software contracts and evidence handling; hardware acquisition is unnecessary for the planned software tests.

## 3. Proposed system boundaries

```text
[OBIS API: real biodiversity records] --------------------------+
                                                                 |
[Synthetic environmental sensor simulator] -> HTTP JSON API ----+--> [Source-aware validation]
                                                                 |          |
[Licensed public camera/ROV imagery] -> File/metadata adapter ---+          v
                                                                 |    [Storage + audit trail]
[Licensed public drone/AUV missions] -> Import adapter ---------+          |
                                                                            v
                                                             [Streamlit map + tables]
```

All adapters are **proposed**, not implemented in V1.0. Sensor data and species occurrences are distinct entities. Imagery is never implicitly treated as a verified species observation.

## 4. Data contracts (proposed)

### 4.1 Environmental observation
Required: `schema_version`, `source_type`, `device_id`, `observed_at_utc`, `measurement`, `value`, `unit`, `quality_flag`.
Optional: `latitude`, `longitude`, `location_accuracy_m`, `depth_m`, `calibration_ref`, `source_ref`, `received_at_utc`, `raw_payload_sha256`.

Allowed source types (proposed): `synthetic_simulator`, `public_external_dataset`, `physical_device_unverified`, `physical_device_verified`. The last status must require documented evidence; it is never assigned by default.

Example **synthetic demonstration**:
```json
{
  "schema_version": "0.1-draft",
  "source_type": "synthetic_simulator",
  "device_id": "SIM-TEMP-001",
  "observed_at_utc": "2026-11-25T12:00:00Z",
  "measurement": "water_temperature",
  "value": 23.4,
  "unit": "degC",
  "quality_flag": "synthetic_demo",
  "calibration_ref": null
}
```

### 4.2 Image/media asset
`asset_id`, `source_type`, `source_ref`, `captured_at_utc`, `media_type`, `file_sha256`, `license`, `attribution`, optional geolocation/uncertainty and human-review status.

### 4.3 Mission/telemetry
`mission_id`, `platform_type` (`rov`/`auv`/`drone`), `source_type`, `timestamp_utc`, optional position/depth/attitude with uncertainty and source reference.

## 5. Interface and processing choices
- **Python HTTP endpoint:** preferred first software adapter; local simulator sends JSON, server validates and persists.
- **Streamlit:** presentation layer, not the device communication protocol; ingestion should run independently of UI reruns.
- **SQLite:** candidate for local prototype storage, with separate tables for observations, media, missions, sources and audit events.
- **JSON/CSV/GeoJSON:** interoperable interchange formats where suitable; media files are stored separately with metadata.
- **SHA-256:** reproducible integrity checks for normalized evidence and media, not proof of scientific correctness.
- **I²C/UART/1-Wire:** hardware-facing interface concepts only; physical wiring and electrical compatibility remain unverified.
- **Wi-Fi:** local laboratory reference only; not an offshore or underwater networking solution.

## 6. Data quality and scientific safeguards
1. Validate field types, units and measurement-specific ranges; preserve raw values.
2. Flag missing, stale or inconsistent timestamps; do not silently fabricate coordinates.
3. Record calibration status and uncertainty; reject unsupported precision claims.
4. Prevent duplicates using source IDs plus timestamps and payload hashes as appropriate.
5. Separate real OBIS occurrences, taxon reference photographs, synthetic sensor readings and external licensed media.
6. Record license and attribution for every imported media asset.
7. Require human review before ecological interpretation, species identification or operational alerts.

## 7. Planned software verification
| Test | Input | Expected outcome |
|---|---|---|
| Valid synthetic temperature | Complete JSON | Accepted, marked synthetic |
| Invalid latitude | Out-of-range coordinate | Rejected/flagged with reason |
| Invalid unit | DO value labelled as temperature | Rejected/flagged |
| Missing timestamp | No observation time | Rejected/flagged |
| Duplicate payload | Repeated ID + time | Deduplicated or flagged |
| Offline API | OBIS/network unavailable | Error shown; no fabricated observations |
| Media without license | Public photo with missing license metadata | Restricted/flagged for review |
| Integrity verification | Tampered exported JSON/media | Hash mismatch detected |
| Provenance isolation | Synthetic record alongside OBIS record | Separate source labels and storage |
| UI regression | Existing OBIS workflow | V1.0 map, photos, export remain unchanged |

**All tests above are plans**, not executed results.

## 8. Proposed implementation sequence
1. V1.1 geospatial exploration remains the next software version.
2. V1.2 introduces local synthetic device simulator and HTTP ingestion.
3. Add storage, validation, quality flags and automated tests.
4. Add optional media/mission imports from licensed public datasets.
5. Keep physical integration as a future *possibility*, not a scheduled deliverable or prerequisite.

## 9. Decision record
**ADR-HW-002: Software-first, hardware-aware architecture**
- **Decision:** use documented reference components to design source-aware software adapters; purchase no devices.
- **Benefits:** reproducible tests, low cost, compatibility with modest notebook resources, auditable evidence.
- **Tradeoffs:** no claims about electrical compatibility, calibration, real-time field performance, marine reliability, or sensor accuracy.
- **Status:** Proposed design; not implemented or physically validated.

## 10. Technical references
- Study 1: [Hardware Feasibility Study](HARDWARE_FEASIBILITY_STUDY.md)
- OBIS: https://obis.org/ and https://api.obis.org/
- Espressif ESP32-S3: https://www.espressif.com/en/products/socs/esp32-s3
- Atlas Scientific EC: https://atlas-scientific.com/embedded-solutions/ezo-conductivity-circuit/
- Atlas Scientific pH: https://atlas-scientific.com/embedded-solutions/ezo-ph-circuit/
- Atlas Scientific DO: https://atlas-scientific.com/embedded-solutions/ezo-dissolved-oxygen-circuit/
- Blue Robotics Bar30: https://bluerobotics.com/store/sensors-cameras/sensors/bar-depth-pressure-sensor/
- Blue Robotics BlueROV2: https://bluerobotics.com/store/rov/bluerov2/
- Blue Robotics Ping sonar: https://bluerobotics.com/store/sensors-cameras/sonar/ping-sonar-r2-rp/
- BlueOS: https://blueos.cloud/
- DJI Mavic 3 Multispectral: https://enterprise.dji.com/mavic-3-m/specs

**Evidence boundary:** Desk-based engineering selection, not an independently verified product compatibility assessment or procurement specification.
