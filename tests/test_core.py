import unittest
from unittest.mock import patch
from io import BytesIO
from src.core import validate_occurrence, fetch_obis

class TestCore(unittest.TestCase):
    def test_valid(self):
        r = validate_occurrence({'decimalLatitude': 1, 'decimalLongitude': -2, 'scientificName': 'Test species'})
        self.assertEqual(r['latitude'], 1.0)
    def test_invalid_latitude(self):
        with self.assertRaises(ValueError):
            validate_occurrence({'decimalLatitude': 100, 'decimalLongitude': 0, 'scientificName': 'X'})
    def test_missing_name(self):
        with self.assertRaises(ValueError):
            validate_occurrence({'decimalLatitude': 0, 'decimalLongitude': 0})
    def test_invalid_size(self):
        with self.assertRaises(ValueError):
            fetch_obis(301)
    @patch('src.core.urlopen')
    def test_fetch_mock(self, mock_open):
        mock_open.return_value.__enter__.return_value = BytesIO(b'{"results":[{"decimalLatitude":1,"decimalLongitude":2,"scientificName":"A"}]}')
        result = fetch_obis(1)
        self.assertEqual(len(result['records']), 1)
        self.assertEqual(len(result['sha256']), 64)

if __name__ == '__main__':
    unittest.main()
