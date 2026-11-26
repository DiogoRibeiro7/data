"""Offline checks for candidate WDI acquisition."""
import json
import unittest

from scripts.acquire_wdi_gdp_resilience import parse_page, validate_rows


def row(year: int = 2020, value: float | None = 1.0) -> dict:
    return {"countryiso3code": "PRT", "date": str(year),
            "indicator": {"id": "GDP"}, "value": value}


class TestWdiCandidate(unittest.TestCase):
    def test_page(self) -> None:
        header = {"page": 1, "pages": 1, "total": 1}
        self.assertEqual(parse_page(json.dumps([header, [row()]]).encode(), 1),
                         (header, [row()]))

    def test_error_envelope(self) -> None:
        with self.assertRaises(ValueError):
            parse_page(b'[{"message": "error"}]', 1)

    def test_wrong_page(self) -> None:
        with self.assertRaises(ValueError):
            parse_page(b'[{"page": 2, "pages": 2}, []]', 1)

    def test_null_and_absent_are_distinct(self) -> None:
        result = validate_rows([row(), row(2021, None)], "GDP",
                               ("PRT",), 2020, 2022)
        self.assertEqual(result["explicit_nulls"], 1)
        self.assertEqual(result["absent_cells"], 1)
        self.assertEqual(result["complete_years"], [2020])

    def test_duplicate_rejected(self) -> None:
        with self.assertRaises(ValueError):
            validate_rows([row(), row()], "GDP", ("PRT",), 2020, 2020)

    def test_invalid_value_rejected(self) -> None:
        with self.assertRaises(ValueError):
            validate_rows([row(value=float("nan"))], "GDP", ("PRT",), 2020, 2020)

    def test_wrong_indicator_rejected(self) -> None:
        with self.assertRaises(ValueError):
            validate_rows([row()], "OTHER", ("PRT",), 2020, 2020)

    def test_wrong_country_rejected(self) -> None:
        with self.assertRaises(ValueError):
            validate_rows([row()], "GDP", ("ESP",), 2020, 2020)
