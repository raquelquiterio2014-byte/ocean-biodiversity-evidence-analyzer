# Marine Monitoring Hardware Feasibility Study
## Global Ocean Observatory | Ocean & Biodiversity Evidence Analyzer
**Special Engineering Study 1 | COP31 AI Solutions Lab — Day 9**

**Status:** Desk-based feasibility assessment; **no hardware purchased, connected, deployed, or physically validated**.  
**Project emphasis:** Software engineering, reproducible integration contracts, scientific provenance, and human review.  
**Baseline:** V1.0 retrieves real marine occurrence records from OBIS. These are not live water-sensor measurements.

## 1. Purpose and scope
Evaluate candidate instruments and platforms that *could* supply future environmental observations, imagery and robotic telemetry to the Python application. This is **not** a purchasing recommendation, compatibility certification, field deployment plan, or claim that hardware integrations exist.

Assessment criteria: measured variable; environmental suitability (salt water, pressure, corrosion, fouling); calibration and maintenance; data interfaces; time and geolocation; power and connectivity; access to documentation; cost and integration effort; provenance and uncertainty.

## 2. Measurement-to-hardware matrix

| Observation / data | Candidate reference | Expected output | Key engineering constraints | Software ingestion concept |
|---|---|---|---|---|
| Water temperature | Waterproof-encapsulated DS18B20 probe | °C | Encapsulation is not automatically seawater-rated; corrosion, calibration and immersion lifetime need checking | 1-Wire through microcontroller → timestamped JSON |
| Conductivity / salinity | Atlas Scientific EZO-EC circuit + appropriate conductivity probe | Conductivity; calculated salinity where supported | Probe cell constant, calibration, temperature compensation, marine suitability | UART/I²C via controller → JSON |
| Water pH | Atlas Scientific EZO-pH + compatible electrode | pH | Calibration buffers, drift, electrode storage and maintenance | UART/I²C → JSON |
| Dissolved oxygen | Atlas Scientific EZO-DO + compatible probe | Dissolved oxygen, with units and compensation metadata | Calibration, membrane/probe maintenance; temperature, salinity and pressure corrections | UART/I²C → JSON |
| Depth / pressure | Blue Robotics Bar30 | Pressure; depth derived with assumptions | Operating limits, water ingress, marine lifetime, pressure-to-depth conversion | I²C → telemetry |
| Underwater range / obstacle detection | Blue Robotics Ping sonar family | Acoustic range / profile (model-dependent) | Turbidity, acoustic conditions, mounting and platform integration | Vendor protocol → structured messages |
| Position / mission trajectory | Platform GNSS (surface/aerial) or underwater navigation system | Lat/lon, time, track; uncertainty | GNSS generally unavailable underwater; underwater location needs dedicated method | GPS/mission logs → GeoJSON/JSON |
| Underwater stills/video | BlueROV2 camera system (reference) | Image/video and capture metadata | Lighting, turbidity, color attenuation, depth rating and licensing | Media files + sidecar metadata |
| Coastal aerial RGB/multispectral | DJI Mavic 3 Multispectral (reference) | RGB/multispectral imagery and georeferencing | Flight rules, coastal lighting, calibration, water glare, no underwater measurement | Image/metadata import |
| Robotic inspection | Blue Robotics BlueROV2 (ROV) | Video, depth, vehicle status and mission telemetry | Tether, power, operator, safety, software interfaces | BlueOS/ArduSub-compatible export or adapter |
| Autonomous underwater survey | AUV category; model to be selected in a later study | Mission logs, position estimates, sensor streams | High cost/complexity; navigation and safety; no candidate validated here | Offline mission-data adapter |

**Measurement interpretation:** Conductivity is measured; salinity may be calculated using assumptions. Depth is inferred from pressure with reference and density assumptions. A photograph does not itself establish species abundance or environmental quality. An aerial multispectral sensor is not a substitute for underwater sensing.

## 3. Candidate platforms and imaging systems
- **Microcontroller:** ESP32-S3 for a possible local Wi-Fi / USB laboratory gateway. It has no built-in cellular or satellite modem. This is a reference only; no board was purchased.
- **Underwater camera / ROV:** BlueROV2 as a documented remotely operated underwater platform. Camera imagery and vehicle telemetry would be distinct data products.
- **Aerial drone:** DJI Mavic 3 Multispectral as a reference for coastal vegetation and land–sea interface surveys, not for measuring submerged chemistry.
- **AUV:** A class of autonomous underwater platforms, not a selected specific model. Mission exports and sensor schemas require separate evaluation.
- **Sonar:** Blue Robotics Ping family as an example of acoustic sensing; sonar outputs are not equivalent to optical photographs.

## 4. Feasibility matrix
Qualitative, preliminary assessments—not vendor-certified ratings.

| Candidate group | Software integration feasibility | Physical deployment difficulty | Priority for software-only study |
|---|---|---|---|
| Temperature / pH / EC / DO sensor JSON schemas | High with documented interfaces | Medium to high for marine use | High |
| Pressure/depth telemetry | High with an adapter | Medium to high | High |
| Underwater camera media + metadata | High for file ingestion | High | High |
| ROV mission logs | Medium; depends on export/API | High | Medium |
| Aerial georeferenced imagery | Medium to high; processing required | High | Medium |
| AUV mission telemetry | Medium to low; vendor-specific | Very high | Later |
| Live long-range buoy communications | Medium; connectivity-dependent | Very high | Later |

## 5. Software-first integration design
1. **Keep sources separate:** OBIS biodiversity occurrences, synthetic device samples, public external datasets, and verified physical observations must never share an unqualified “real-time” label.
2. **Define an ingestion contract:** `source_type`, `device_id`, `observed_at_utc`, `received_at_utc`, `latitude`, `longitude`, `location_accuracy_m`, `measurement`, `value`, `unit`, `quality_flag`, `calibration_ref`, `source_ref`.
3. **Validate:** data types, units, permissible ranges, timestamps, duplicates, missing location, calibration state and source identity.
4. **Preserve evidence:** raw payload, normalized record, software version, retrieval metadata, hash, and review outcome. SHA-256 supports integrity checking, **not scientific accuracy**.
5. **Support images and missions:** separate media assets, attribution/license, capture metadata, geospatial references and human review; do not infer species from photos without a validated model and expert assessment.
6. **Build without devices:** local Python simulator → HTTP endpoint → persistent records → Streamlit dashboard → automated tests. Public image or mission datasets may be added only with provenance and license checks.

Example **synthetic** measurement (illustrative, not from a real device):

```json
{
  "source_type": "synthetic_simulator",
  "device_id": "SIM-DO-001",
  "observed_at_utc": "2026-11-25T12:00:00Z",
  "measurement": "dissolved_oxygen",
  "value": 6.8,
  "unit": "mg/L",
  "quality_flag": "synthetic_demo",
  "calibration_ref": null
}
```

## 6. Risks, constraints, and verification needs
- **Marine survivability:** waterproof labels alone do not prove long-term saltwater resistance; check pressure rating, galvanic corrosion, biofouling and maintenance.
- **Scientific validity:** calibration, traceability, drift, uncertainty, reference methods and appropriate compensation are required before interpreting sensor readings.
- **Geospatial accuracy:** surface GNSS does not solve underwater navigation; timestamp and location quality must be explicit.
- **Data provenance:** images, taxonomic reference photos, OBIS records and simulated readings have different evidence statuses.
- **Connectivity:** Wi-Fi is a laboratory starting point, not a solution for offshore underwater transmission.
- **Regulatory/operational:** aerial and marine operations may require permits, trained operators and safety review; no deployment is planned.

## 7. Conclusion and next study
**Decision:** No hardware acquisition. Continue software development with simulator-based ingestion, validation, documented adapters and traceable external datasets. This study identifies candidate technologies only; it does not verify cross-vendor compatibility or claim field readiness.

**Next:** *Hardware Architecture & Component Selection* — justify reference components, define interface boundaries, data contracts, test strategy and integration architecture.

## 8. Manufacturer and scientific references
Access dates and exact model revisions should be recorded before a future procurement or deployment decision.

1. OBIS — Ocean Biodiversity Information System: https://obis.org/ ; API: https://api.obis.org/
2. Espressif — ESP32-S3: https://www.espressif.com/en/products/socs/esp32-s3
3. Atlas Scientific — EZO EC: https://atlas-scientific.com/embedded-solutions/ezo-conductivity-circuit/
4. Atlas Scientific — EZO pH: https://atlas-scientific.com/embedded-solutions/ezo-ph-circuit/
5. Atlas Scientific — EZO DO: https://atlas-scientific.com/embedded-solutions/ezo-dissolved-oxygen-circuit/
6. Blue Robotics — Bar30 pressure sensor: https://bluerobotics.com/store/sensors-cameras/sensors/bar-depth-pressure-sensor/
7. Blue Robotics — BlueROV2: https://bluerobotics.com/store/rov/bluerov2/
8. Blue Robotics — Ping sonar: https://bluerobotics.com/store/sensors-cameras/sonar/ping-sonar-r2-rp/
9. Blue Robotics — BlueOS documentation: https://blueos.cloud/
10. DJI Enterprise — Mavic 3 Multispectral: https://enterprise.dji.com/mavic-3-m/specs

**Evidence classification:** The candidate list and architecture are a desk study based on publicly documented product families. No hands-on compatibility, performance or seawater-resistance testing was performed.
