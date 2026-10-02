"""Validate repository citation and archival metadata."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


class CitationMetadataTests(unittest.TestCase):
    def test_citation_cff_has_required_registry_identity(self) -> None:
        data = yaml.safe_load((ROOT / "CITATION.cff").read_text(encoding="utf-8"))
        self.assertEqual(data["cff-version"], "1.2.0")
        self.assertEqual(data["title"], "Data Registry")
        self.assertEqual(data["type"], "software")
        self.assertEqual(data["repository-code"], "https://github.com/DiogoRibeiro7/data")
        self.assertEqual(data["license"], "MIT")
        self.assertEqual(
            data["authors"],
            [{"family-names": "Ribeiro", "given-names": "Diogo"}],
        )
        self.assertIn("upstream datasets", data["message"])

    def test_codemeta_matches_citation_identity(self) -> None:
        data = json.loads((ROOT / "codemeta.json").read_text(encoding="utf-8"))
        self.assertEqual(data["@context"], "https://w3id.org/codemeta/3.1")
        self.assertEqual(data["@type"], "SoftwareSourceCode")
        self.assertEqual(data["name"], "Data Registry")
        self.assertEqual(
            data["codeRepository"],
            "https://github.com/DiogoRibeiro7/data",
        )
        self.assertEqual(data["license"], "https://spdx.org/licenses/MIT.html")
        self.assertEqual(
            data["author"],
            [{
                "@type": "Person",
                "givenName": "Diogo",
                "familyName": "Ribeiro",
            }],
        )

    def test_citation_guide_requires_tag_commit_and_upstream_citation(self) -> None:
        guide = (ROOT / "docs" / "CITATION.md").read_text(encoding="utf-8")
        self.assertIn("exact immutable snapshot tag", guide)
        self.assertIn("exact 40-character Git commit SHA", guide)
        self.assertIn("Do not substitute a floating branch name", guide)
        self.assertIn("cite the **upstream dataset/publisher**", guide)
        self.assertIn("not a replacement for upstream attribution", guide)

    def test_registry_citation_does_not_claim_dataset_mit_licensing(self) -> None:
        guide = (ROOT / "docs" / "CITATION.md").read_text(encoding="utf-8")
        self.assertIn(
            "do not claim that all datasets in this repository are MIT-licensed",
            guide,
        )


if __name__ == "__main__":
    unittest.main()
