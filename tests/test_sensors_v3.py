import tempfile
import unittest
from pathlib import Path
from src.sensors_v3 import SPECS, generate_observation, validate_observation, checksum
from src.api_v3 import store_observation, recent_observations

class TestSensorsV3(unittest.TestCase):
    def test_five_synthetic_measurements(self):
        for name in SPECS:
            with self.subTest(name=name):
                obs = generate_observation(name)
                self.assertEqual(obs["source_type"], "synthetic_simulator")
                self.assertEqual(obs["quality_flag"], "synthetic_demo")
                self.assertEqual(len(checksum(obs)), 64)

    def test_invalid_unit(self):
        obs = generate_observation("water_temperature")
        obs["unit"] = "mg/L"
        with self.assertRaises(ValueError):
            validate_observation(obs)

    def test_reject_physical_claim(self):
        obs = generate_observation("ph")
        obs["source_type"] = "physical_device_verified"
        with self.assertRaises(ValueError):
            validate_observation(obs)

    def test_invalid_coordinate(self):
        obs = generate_observation("salinity")
        obs["latitude"] = 100
        with self.assertRaises(ValueError):
            validate_observation(obs)

    def test_missing_timestamp(self):
        obs = generate_observation("pressure")
        del obs["observed_at_utc"]
        with self.assertRaises(ValueError):
            validate_observation(obs)

    def test_sqlite_duplicate_protection(self):
        with tempfile.TemporaryDirectory() as d:
            db = Path(d) / "observations.sqlite3"
            obs = generate_observation("dissolved_oxygen")
            self.assertTrue(store_observation(obs, db)["stored"])
            self.assertFalse(store_observation(obs, db)["stored"])
            self.assertEqual(len(recent_observations(db)), 1)
