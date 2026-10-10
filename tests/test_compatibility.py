"""Tests for public compatibility and versioning contracts."""

from __future__ import annotations

import json
import re
import tomllib
import unittest
from pathlib import Path

from data_registry import (
    CURRENT_SNAPSHOT_MANIFEST_VERSION,
    PACKAGE_VERSION,
    PRE_1_DEPRECATION_MIN_MINOR_RELEASES,
    PUBLIC_API_VERSION,
    STATIC_DISTRIBUTION_VERSION,
    SUPPORTED_METADATA_SCHEMA_VERSIONS,
    SUPPORTED_SNAPSHOT_MANIFEST_VERSIONS,
    supports_metadata_schema,
    supports_snapshot_manifest,
)

ROOT = Path(__file__).resolve().parents[1]


class CompatibilityPolicyTests(unittest.TestCase):
    """Protect compatibility constants and documented version contracts."""

    def test_public_api_version_is_v1(self) -> None:
        self.assertEqual(PUBLIC_API_VERSION, 1)

    def test_static_distribution_version_matches_committed_index(self) -> None:
        index = json.loads(
            (ROOT / "distribution" / "v1" / "index.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(index["distribution_version"], STATIC_DISTRIBUTION_VERSION)
        self.assertEqual(STATIC_DISTRIBUTION_VERSION, 1)

    def test_current_snapshot_manifest_is_supported(self) -> None:
        text = (ROOT / "scripts" / "create_snapshot.py").read_text(encoding="utf-8")
        match = re.search(r'"manifest_version":\s*(\d+)', text)
        self.assertIsNotNone(match)
        assert match is not None
        current = int(match.group(1))

        self.assertEqual(current, CURRENT_SNAPSHOT_MANIFEST_VERSION)
        self.assertTrue(supports_snapshot_manifest(current))
        self.assertEqual(current, 7)

    def test_historical_snapshot_manifest_versions_remain_supported(self) -> None:
        self.assertEqual(
            SUPPORTED_SNAPSHOT_MANIFEST_VERSIONS,
            (1, 2, 3, 4, 5, 6, 7),
        )

    def test_package_metadata_matches_initial_semver_line(self) -> None:
        data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        version = data["tool"]["poetry"]["version"]

        self.assertEqual(version, PACKAGE_VERSION)
        self.assertEqual(version, "0.1.0")
        self.assertRegex(version, r"^\d+\.\d+\.\d+$")

    def test_supported_metadata_schema_versions_are_explicit(self) -> None:
        self.assertEqual(
            SUPPORTED_METADATA_SCHEMA_VERSIONS,
            {
                "canonical": (1,),
                "consumer": (1,),
                "external": (1,),
                "legacy": (0,),
            },
        )
        self.assertTrue(supports_metadata_schema("canonical", 1))
        self.assertFalse(supports_metadata_schema("canonical", 2))
        self.assertFalse(supports_metadata_schema("unknown", 1))

    def test_pre_one_deprecation_window_is_one_minor_release(self) -> None:
        self.assertEqual(PRE_1_DEPRECATION_MIN_MINOR_RELEASES, 1)

    def test_deprecation_window_is_documented(self) -> None:
        policy = (ROOT / "docs" / "COMPATIBILITY.md").read_text(encoding="utf-8")

        self.assertIn(
            "remain functional for at least one subsequent package minor release",
            policy,
        )
        self.assertIn("Unknown future versions must be rejected", policy)


if __name__ == "__main__":
    unittest.main()
