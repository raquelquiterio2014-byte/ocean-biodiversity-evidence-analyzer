"""End-to-end localhost HTTP contract and export integrity tests."""
import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

from src.api_v3 import Handler
from src.evidence_v3 import export_evidence, verify_evidence
from src.sensors_v3 import generate_observation

class TestHTTPAndEvidenceV3(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name) / "test.sqlite3"
        self.db_patch = patch("src.api_v3.DB", self.db)
        self.db_patch.start()
        # Defaults are evaluated at function definition; patch those defaults too.
        import src.api_v3 as api
        self.original_defaults = (api.init_db.__defaults__, api.store_observation.__defaults__, api.recent_observations.__defaults__)
        api.init_db.__defaults__ = (self.db,)
        api.store_observation.__defaults__ = (self.db,)
        api.recent_observations.__defaults__ = (self.db, 100)
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = "http://127.0.0.1:" + str(self.server.server_port)

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)
        import src.api_v3 as api
        api.init_db.__defaults__, api.store_observation.__defaults__, api.recent_observations.__defaults__ = self.original_defaults
        self.db_patch.stop()
        self.temp.cleanup()

    def request(self, route, obj=None, raw=None):
        body = raw if raw is not None else (json.dumps(obj).encode() if obj is not None else None)
        req = urllib.request.Request(self.base + route, data=body, headers={"Content-Type": "application/json"}, method="POST" if body is not None else "GET")
        try:
            with urllib.request.urlopen(req, timeout=3) as res:
                return res.status, json.load(res)
        except urllib.error.HTTPError as exc:
            return exc.code, json.load(exc)

    def test_health(self):
        code, body = self.request("/health")
        self.assertEqual(code, 200)
        self.assertEqual(body["mode"], "synthetic_only")

    def test_post_get_duplicate(self):
        sample = generate_observation("water_temperature")
        code, body = self.request("/observations", sample)
        self.assertEqual(code, 201)
        self.assertTrue(body["stored"])
        code, body = self.request("/observations", sample)
        self.assertEqual(code, 200)
        self.assertFalse(body["stored"])
        code, body = self.request("/observations")
        self.assertEqual(code, 200)
        self.assertEqual(body["records"], [sample])

    def test_reject_invalid_measurement(self):
        sample = generate_observation("ph")
        sample["unit"] = "degC"
        self.assertEqual(self.request("/observations", sample)[0], 400)

    def test_reject_malformed_json(self):
        self.assertEqual(self.request("/observations", raw=b"{bad json")[0], 400)

    def test_unknown_route(self):
        self.assertEqual(self.request("/missing")[0], 404)

    def test_export_integrity_and_tampering(self):
        records = [generate_observation("salinity")]
        evidence = export_evidence(records)
        self.assertTrue(verify_evidence(evidence))
        serialized = json.loads(json.dumps(evidence))
        serialized["records"][0]["value"] += 1
        self.assertFalse(verify_evidence(serialized))
        self.assertEqual(evidence["record_count"], 1)

if __name__ == "__main__":
    unittest.main()
