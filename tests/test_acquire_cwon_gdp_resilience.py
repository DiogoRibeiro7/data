"""Offline checks for the CWON acquisition contract."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

from scripts.acquire_cwon_gdp_resilience import (
    EXPECTED_SOURCE_DATE, INDICATORS, SOURCE_ID, acquire, check_indicator, check_source,
)


def envelope(records: list[dict], **extra: object) -> bytes:
    """Build a synthetic World Bank API response."""
    header = {"page": 1, "pages": 1, "total": len(records), **extra}
    return json.dumps([header, records]).encode()


def source_response(date: str = EXPECTED_SOURCE_DATE) -> bytes:
    """Synthetic metadata, never an actual source observation."""
    return envelope([{"id": SOURCE_ID, "name": "Wealth Accounts", "lastupdated": date}])


def indicator_response(indicator: str, name: str | None = None) -> bytes:
    """Synthetic indicator metadata."""
    return envelope([{
        "id": indicator, "source": {"id": SOURCE_ID},
        "name": name or f"{INDICATORS[indicator]} per capita (real chained 2019 US$)",
    }])


def observation_response(indicator: str) -> bytes:
    """Sparse fixture: two rows, one explicitly missing; all other cells absent."""
    return envelope([
        {"countryiso3code": "PRT", "date": "1995",
         "indicator": {"id": indicator}, "value": 1.0},
        {"countryiso3code": "PRT", "date": "1996",
         "indicator": {"id": indicator}, "value": None},
    ], sourceid=SOURCE_ID, lastupdated=EXPECTED_SOURCE_DATE)


def mock_request(url: str) -> bytes:
    """Dispatch synthetic source, indicator and observation requests."""
    parsed = urlparse(url)
    if "/source/" in parsed.path:
        return source_response()
    indicator = parsed.path.split("/")[-1]
    if "/country/" in parsed.path:
        assert parse_qs(parsed.query)["source"] == [SOURCE_ID]
        return observation_response(indicator)
    return indicator_response(indicator)


class TestCWONAcquisition(unittest.TestCase):
    def test_source_identity(self) -> None:
        self.assertEqual(check_source(source_response())["id"], SOURCE_ID)
        with self.assertRaisesRegex(ValueError, "vintage"):
            check_source(source_response("2025-01-01"))

    def test_nominal_series_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "indicator metadata"):
            check_indicator(indicator_response("NW.TOW.PC",
                "National comprehensive wealth per capita (current US$)"), "NW.TOW.PC")

    def test_renewable_nonrenewable_not_interchangeable(self) -> None:
        with self.assertRaisesRegex(ValueError, "indicator metadata"):
            check_indicator(indicator_response("NW.NCA.TOTL.PC",
                "Nonrenewable natural capital per capita (real chained 2019 US$)"),
                "NW.NCA.TOTL.PC")

    def test_candidate_manifest_and_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "candidate"
            with patch("scripts.acquire_cwon_gdp_resilience.request", side_effect=mock_request):
                result = acquire(output)
            self.assertEqual(len(result["files"]), 16)
            self.assertEqual(result["status"], "candidate_only")
            self.assertEqual(result["coverage"]["NW.TOW.PC"]["observed"], 1)
            self.assertEqual(result["coverage"]["NW.TOW.PC"]["explicit_nulls"], 1)
            self.assertEqual(result["coverage"]["NW.TOW.PC"]["absent_cells"], 856)
            self.assertEqual(result["coverage"]["NW.TOW.PC"]["complete_years"], [])
            self.assertTrue((output / "manifest.json").is_file())

    def test_wrong_vintage_fails_without_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "candidate"
            with patch("scripts.acquire_cwon_gdp_resilience.request",
                       return_value=source_response("2025-01-01")):
                with self.assertRaises(ValueError):
                    acquire(output)
            self.assertFalse((output / "manifest.json").exists())
