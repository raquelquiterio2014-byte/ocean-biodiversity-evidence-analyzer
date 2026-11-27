"""V3: deterministic synthetic marine sensor observations; NEVER field data."""
import hashlib
import json
import math
import random
from datetime import datetime, timezone

SPECS = {
    "water_temperature": ("degC", -2.5, 40.0, 22.0, 3.0),
    "ph": ("pH", 0.0, 14.0, 8.1, 0.15),
    "salinity": ("PSU", 0.0, 45.0, 35.0, 1.2),
    "dissolved_oxygen": ("mg/L", 0.0, 20.0, 7.0, 1.5),
    "pressure": ("dbar", 0.0, 12000.0, 20.0, 5.0),
}

def validate_observation(obs):
    if not isinstance(obs, dict):
        raise ValueError("Observation must be a JSON object")
    required = ("schema_version", "source_type", "device_id", "observed_at_utc",
                "measurement", "value", "unit", "quality_flag")
    if any(k not in obs for k in required):
        raise ValueError("Missing required field")
    if obs["schema_version"] != "1.0" or obs["source_type"] != "synthetic_simulator":
        raise ValueError("Only V3 synthetic simulator observations are accepted")
    if not isinstance(obs["device_id"], str) or not obs["device_id"].startswith("SIM-") or len(obs["device_id"]) > 80:
        raise ValueError("Invalid synthetic device ID")
    if obs["quality_flag"] != "synthetic_demo":
        raise ValueError("Invalid quality flag")
    try:
        timestamp = datetime.fromisoformat(obs["observed_at_utc"].replace("Z", "+00:00"))
    except (ValueError, AttributeError) as exc:
        raise ValueError("Invalid timestamp") from exc
    if timestamp.tzinfo is None or timestamp.utcoffset().total_seconds() != 0:
        raise ValueError("Timestamp must be UTC")
    spec = SPECS.get(obs["measurement"])
    if spec is None or obs["unit"] != spec[0]:
        raise ValueError("Unknown measurement or incompatible unit")
    value = obs["value"]
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError("Value must be a finite number")
    if not spec[1] <= value <= spec[2]:
        raise ValueError("Value outside prototype validation range")
    for field, lo, hi in (("latitude", -90, 90), ("longitude", -180, 180)):
        if field in obs and obs[field] is not None:
            x = obs[field]
            if isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) or not lo <= x <= hi:
                raise ValueError("Invalid " + field)
    return obs

def generate_observation(measurement, index=0, seed=42):
    if measurement not in SPECS:
        raise ValueError("Unknown measurement")
    if type(index) is not int or not 0 <= index <= 1000000:
        raise ValueError("Invalid sample index")
    unit, low, high, center, spread = SPECS[measurement]
    rng = random.Random(f"{seed}:{measurement}:{index}")
    value = round(max(low, min(high, center + rng.uniform(-spread, spread))), 3)
    obs = {
        "schema_version": "1.0", "source_type": "synthetic_simulator",
        "device_id": "SIM-" + measurement.upper().replace("_", "-"),
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "measurement": measurement, "value": value, "unit": unit,
        "quality_flag": "synthetic_demo", "calibration_ref": None
    }
    return validate_observation(obs)

def checksum(observation):
    return hashlib.sha256(json.dumps(observation, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
