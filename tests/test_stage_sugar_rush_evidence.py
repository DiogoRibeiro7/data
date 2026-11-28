"""Checks for the published evidence transcription and staging contract."""
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import yaml

from scripts.stage_sugar_rush_evidence import EFFECTS, REFERENCES, SLUG, STUDIES, stage, validate_tables


class SugarEvidenceTests(unittest.TestCase):
    def test_published_inventory(self) -> None:
        validate_tables()
        self.assertEqual(len(STUDIES), 9)
        self.assertEqual(sum(row[6] for row in STUDIES), 461109)
        self.assertEqual(len(EFFECTS), 10)

    def test_duplicate_effect_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            validate_tables(effects=EFFECTS[:-1] + (EFFECTS[0],))

    def test_invalid_interval_rejected(self) -> None:
        first = list(EFFECTS[0])
        first[3] = 2.0
        with self.assertRaisesRegex(ValueError, "interval"):
            validate_tables(effects=(tuple(first),) + EFFECTS[1:])

    def test_missing_stratum_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "Expected"):
            validate_tables(effects=EFFECTS[:-1])

    def test_staged_bytes_and_no_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "reports").mkdir()
            (root / "reports" / "canonical-adoption-policy.json").write_text(
                json.dumps({"exemptions": []}), encoding="utf-8")
            stage(root)
            target = root / "datasets" / SLUG
            metadata = yaml.safe_load((target / "metadata.yaml").read_text(encoding="utf-8"))
            self.assertEqual(metadata["license"]["redistribution"], "allowed")
            for entry in metadata["files"]:
                self.assertEqual(hashlib.sha256((target / entry["path"]).read_bytes()).hexdigest(),
                                 entry["sha256"])
            for slug, *_ in REFERENCES:
                self.assertEqual({p.name for p in (root / "external" / slug).iterdir()},
                                 {"metadata.yaml", "README.md"})
            policy = json.loads((root / "reports" / "canonical-adoption-policy.json").read_text())
            self.assertEqual(policy["exemptions"][0]["dataset_id"], SLUG)
            with self.assertRaisesRegex(ValueError, "refusing overwrite"):
                stage(root)


if __name__ == "__main__":
    unittest.main()
