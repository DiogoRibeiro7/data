"""Offline WEO schema and status tests; no IMF observations or network calls."""
from __future__ import annotations

import unittest

from scripts.inspect_imf_weo_gdp import (
    END, INDICATORS, START, inspect_rows, number, observation_status, year_value,
)


def header() -> tuple:
    """Synthetic WEO headers matching the documented modern workbook format."""
    return ("COUNTRY.ID", "INDICATOR.ID", "UNIT", "SCALE",
            "LATEST_ACTUAL_ANNUAL_DATA", *range(START, END + 1))


def series(code: str, cutoff: int | None = 2024) -> tuple:
    """Use invented values exclusively, not real WEO data."""
    return ("PRT", code, "synthetic unit", "Billions", cutoff,
            *(None if year == 1995 else 1.0 for year in range(START, END + 1)))


class TestWEOInspection(unittest.TestCase):
    def test_year_labels(self) -> None:
        self.assertEqual(year_value("2024"), 2024)
        self.assertEqual(year_value(2024.0), 2024)
        self.assertIsNone(year_value("2024-01-01"))

    def test_missing_values(self) -> None:
        self.assertIsNone(number("--"))
        self.assertIsNone(number(None))
        self.assertEqual(number(0), 0)
        with self.assertRaises(ValueError):
            number("unexpected")

    def test_actual_cutoff(self) -> None:
        self.assertEqual(observation_status(2024, 2024), "through_reported_actual_cutoff")
        self.assertEqual(observation_status(2025, 2024), "estimate_or_projection")
        self.assertEqual(observation_status(2027, 2024), "projection")
        self.assertEqual(observation_status(2020, None), "unknown_actual_status")

    def test_coverage(self) -> None:
        result = inspect_rows([("Synthetic fixture",), header(),
                               *(series(code) for code in INDICATORS)])
        self.assertEqual(result["matched_series"], 3)
        self.assertEqual(result["expected_series"], 99)
        self.assertEqual(len(result["absent_series"]), 96)
        info = result["coverage"]["NGDPD"]["PRT"]["years_by_status"]
        self.assertEqual(info["missing"], [1995])
        self.assertIn(2025, info["estimate_or_projection"])
        self.assertIn(2031, info["projection"])

    def test_duplicates_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "Duplicate country/indicator"):
            inspect_rows([header(), series("NGDPD"), series("NGDPD")])

    def test_wrong_horizon(self) -> None:
        with self.assertRaisesRegex(ValueError, "annual columns"):
            inspect_rows([header()[:-1], series("NGDPD")])

    def test_unknown_cutoff(self) -> None:
        result = inspect_rows([header(), *(series(code, None) for code in INDICATORS)])
        info = result["coverage"]["NGDPD"]["PRT"]["years_by_status"]
        self.assertIn(2024, info["unknown_actual_status"])
        self.assertIn(2027, info["projection"])
