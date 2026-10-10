"""Tests for the versioned static registry distribution."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import generate_static_distribution as DIST  # noqa: E402


class StaticDistributionTests(unittest.TestCase):
    """Protect deterministic distribution generation and integrity."""

    def test_committed_distribution_is_current(self) -> None:
        self.assertEqual(DIST.run(ROOT, write=False), [])

    def test_distribution_generation_is_deterministic(self) -> None:
        self.assertEqual(
            DIST.expected_outputs(ROOT),
            DIST.expected_outputs(ROOT),
        )

    def test_source_artifacts_are_copied_byte_for_byte(self) -> None:
        outputs = DIST.expected_outputs(ROOT)
        for name, source_path in DIST.SOURCE_ARTIFACTS.items():
            self.assertEqual(
                outputs[f"{name}.json"],
                (ROOT / source_path).read_text(encoding="utf-8"),
            )

    def test_legacy_catalog_contains_all_legacy_records(self) -> None:
        legacy = json.loads(
            (ROOT / "distribution" / "v1" / "legacy.json").read_text(
                encoding="utf-8"
            )
        )
        ids = [item["id"] for item in legacy["records"]]
        self.assertTrue(
            all("metadata" not in item for item in legacy["records"])
        )
        expected = sorted(
            path.name
            for path in (ROOT / "legacy").iterdir()
            if path.is_dir() and (path / "metadata.yaml").is_file()
        )
        self.assertEqual(ids, expected)

    def test_index_describes_versioned_artifact_sources(self) -> None:
        distribution = ROOT / "distribution" / "v1"
        index = json.loads((distribution / "index.json").read_text(encoding="utf-8"))
        self.assertEqual(index["distribution_version"], 1)
        self.assertEqual(index["repository"], "DiogoRibeiro7/data")

        names = [artifact["name"] for artifact in index["artifacts"]]
        self.assertEqual(names, sorted(names))
        self.assertIn("changelog", names)
        for artifact in index["artifacts"]:
            self.assertTrue((distribution / artifact["path"]).is_file())
            self.assertEqual(artifact["schema_version"], 1)
            self.assertTrue(artifact["source"])


if __name__ == "__main__":
    unittest.main()
