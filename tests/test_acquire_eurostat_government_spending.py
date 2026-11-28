"""Offline tests for the Eurostat candidate acquisition contract."""
import sys
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from acquire_eurostat_government_spending import COUNTRIES, FISCAL_ITEMS, QUERIES, request_url, validate_payload


class AcquisitionTests(unittest.TestCase):
    def test_query_filters(self) -> None:
        dataset, filters = QUERIES["fiscal.json"]
        parsed = parse_qs(urlparse(request_url(dataset, filters)).query)
        self.assertEqual(set(parsed["geo"]), set(COUNTRIES))
        self.assertEqual(len(parsed["geo"]), 27)
        self.assertEqual(set(parsed["na_item"]), set(FISCAL_ITEMS))
        self.assertEqual(parsed["unit"], ["PC_GDP"])
        self.assertEqual(parsed["sinceTimePeriod"], ["1995"])
        self.assertEqual(parsed["untilTimePeriod"], ["2025"])

    def test_reject_error_payload(self) -> None:
        with self.assertRaises(ValueError):
            validate_payload({"error": "failed"}, {})

    def test_validate_and_reject_wrong_unit(self) -> None:
        dimensions = {name: {"category": {"index": {key: i for i, key in enumerate(keys)}}}
                      for name, keys in {"unit": ["PC_GDP"], "geo": COUNTRIES, "time": ["2025"]}.items()}
        payload = {"class": "dataset", "value": {"0": 57.2}, "dimension": dimensions}
        validate_payload(payload, {"unit": "PC_GDP"})
        with self.assertRaises(ValueError):
            validate_payload(payload, {"unit": "CP_MEUR"})
