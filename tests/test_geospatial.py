import json
import unittest
from io import BytesIO
from unittest.mock import patch
from src.geospatial import REGIONS, validate_bbox, polygon_wkt, fetch_region, quality_summary

class TestGeospatial(unittest.TestCase):
    def test_bbox(self):
        self.assertEqual(validate_bbox((-70, -60, 20, 70)), (-70, -60, 20, 70))
        with self.assertRaises(ValueError):
            validate_bbox((20, 0, -20, 30))
        with self.assertRaises(ValueError):
            validate_bbox((float("nan"), 0, 20, 30))

    def test_polygon(self):
        self.assertTrue(polygon_wkt((-70, -60, 20, 70)).startswith("POLYGON(("))

    def test_pacific_two_windows(self):
        self.assertEqual(len(REGIONS["Pacific (approx.)"]), 2)

    def test_quality(self):
        q = quality_summary([{"scientific_name":"X", "event_date":None,
                              "dataset_id":None, "occurrence_id":None}])
        self.assertEqual(q["missing_event_date"], 1)

    @patch("src.geospatial.urlopen")
    def test_geographic_request_and_filter(self, mock_open):
        response = {"results": [
            {"decimalLatitude":10, "decimalLongitude":-40, "scientificName":"Species alpha"},
            {"decimalLatitude":10, "decimalLongitude":80, "scientificName":"Species beta"}]}
        mock_open.return_value.__enter__.return_value = BytesIO(json.dumps(response).encode())
        e = fetch_region("Atlantic (approx.)", 100, "alpha")
        self.assertEqual(len(e["records"]), 1)
        self.assertEqual(e["rejected_count"], 1)
        self.assertIn("geometry=", e["source_urls"][0])
        self.assertEqual(len(e["sha256"]), 64)

    def test_bad_region(self):
        with self.assertRaises(ValueError):
            fetch_region("Atlantis")
