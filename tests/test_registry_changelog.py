"""Tests for the append-only machine-readable registry changelog."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import generate_registry_changelog as CHANGELOG  # noqa: E402


def entry(
    transition_id: str,
    base_tag: str,
    base_commit: str,
    target_tag: str,
    target_commit: str,
) -> dict[str, object]:
    """Return one minimal valid changelog transition fixture."""

    return {
        "schema_version": 1,
        "transition_id": transition_id,
        "base": {
            "tag": base_tag,
            "commit": base_commit,
            "manifest_version": 7,
            "manifest_sha256": "a" * 64,
        },
        "target": {
            "tag": target_tag,
            "commit": target_commit,
            "manifest_version": 7,
            "manifest_sha256": "b" * 64,
        },
        "diff_schema_version": 1,
        "exactness": {
            "canonical": True,
            "consumers": True,
            "lifecycle": True,
            "provenance_debt": True,
            "metadata_schemas": True,
            "registry_client": True,
            "static_distribution": True,
            "notes": "",
        },
        "changes": {},
    }


class RegistryChangelogTests(unittest.TestCase):
    """Protect deterministic and append-only release history."""

    def test_committed_changelog_is_current(self) -> None:
        self.assertEqual(CHANGELOG.run(ROOT, write=False), [])

    def test_generation_is_deterministic(self) -> None:
        self.assertEqual(
            CHANGELOG.expected_outputs(ROOT),
            CHANGELOG.expected_outputs(ROOT),
        )

    def test_current_history_starts_from_published_phase8_snapshot(self) -> None:
        changelog = CHANGELOG.build_changelog(ROOT)

        self.assertEqual(changelog["schema_version"], 1)
        self.assertEqual(
            changelog["history_start"],
            {
                "tag": "snapshot-2026.10.07",
                "commit": "25bbf223bcf1ed00e62e5768b6de9a1d07b13ad9",
            },
        )
        self.assertEqual(len(changelog["entries"]), 1)
        transition = changelog["entries"][0]
        self.assertEqual(
            transition["transition_id"],
            "snapshot-2026.10.07__snapshot-2026.10.09",
        )
        self.assertEqual(
            transition["target"]["commit"],
            "caea1de8daec085b0af39525b9c5f8eb7ec5ce37",
        )

    def test_first_real_transition_records_phase9_changes(self) -> None:
        transition = CHANGELOG.build_changelog(ROOT)["entries"][0]
        changes = transition["changes"]

        self.assertEqual(changes["canonical"]["added"], [])
        self.assertEqual(changes["canonical"]["removed"], [])
        self.assertEqual(changes["canonical"]["changed"], [])
        self.assertEqual(changes["consumers"]["relationship_count"], [4, 4])
        self.assertEqual(
            changes["provenance_debt"]["total_debt"],
            [6, 9],
        )
        self.assertTrue(changes["registry_client"]["introduced"])
        self.assertTrue(changes["static_distribution"]["introduced"])
        self.assertFalse(transition["exactness"]["consumers"])
        self.assertFalse(transition["exactness"]["provenance_debt"])

    def test_contiguous_history_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            entries = root / "changelog" / "entries"
            entries.mkdir(parents=True)
            first = entry(
                "snapshot-2026.10.01__snapshot-2026.10.02",
                "snapshot-2026.10.01",
                "1" * 40,
                "snapshot-2026.10.02",
                "2" * 40,
            )
            second = entry(
                "snapshot-2026.10.02__snapshot-2026.10.03",
                "snapshot-2026.10.02",
                "2" * 40,
                "snapshot-2026.10.03",
                "3" * 40,
            )
            (entries / "01.json").write_text(
                json.dumps(first),
                encoding="utf-8",
            )
            (entries / "02.json").write_text(
                json.dumps(second),
                encoding="utf-8",
            )

            changelog = CHANGELOG.build_changelog(root)

            self.assertEqual(len(changelog["entries"]), 2)
            self.assertEqual(
                changelog["entries"][-1]["target"]["tag"],
                "snapshot-2026.10.03",
            )

    def test_non_contiguous_history_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            entries = root / "changelog" / "entries"
            entries.mkdir(parents=True)
            first = entry(
                "snapshot-2026.10.01__snapshot-2026.10.02",
                "snapshot-2026.10.01",
                "1" * 40,
                "snapshot-2026.10.02",
                "2" * 40,
            )
            second = entry(
                "snapshot-2026.10.03__snapshot-2026.10.04",
                "snapshot-2026.10.03",
                "3" * 40,
                "snapshot-2026.10.04",
                "4" * 40,
            )
            (entries / "01.json").write_text(
                json.dumps(first),
                encoding="utf-8",
            )
            (entries / "02.json").write_text(
                json.dumps(second),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                ValueError,
                "contiguous append-only history",
            ):
                CHANGELOG.build_changelog(root)

    def test_static_distribution_exposes_changelog(self) -> None:
        index = json.loads(
            (ROOT / "distribution" / "v1" / "index.json").read_text(
                encoding="utf-8"
            )
        )
        by_name = {item["name"]: item for item in index["artifacts"]}

        self.assertIn("changelog", by_name)
        self.assertEqual(
            by_name["changelog"]["source"],
            "reports/registry-changelog.json",
        )
        self.assertEqual(
            (ROOT / "distribution" / "v1" / "changelog.json").read_bytes(),
            (ROOT / "reports" / "registry-changelog.json").read_bytes(),
        )


if __name__ == "__main__":
    unittest.main()
