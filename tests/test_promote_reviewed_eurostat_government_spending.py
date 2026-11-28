"""Offline integrity tests for the pinned Eurostat promotion."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from promote_reviewed_eurostat_government_spending import MANIFEST_SHA, SOURCE_FILES, digest, verify_candidate


class PromotionTests(unittest.TestCase):
    def test_digest(self) -> None:
        self.assertEqual(digest(b"abc"), "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")

    def test_reviewed_contract(self) -> None:
        self.assertEqual(len(MANIFEST_SHA), 64)
        self.assertEqual(sum(v[2] for v in SOURCE_FILES.values()), 10849)
        self.assertEqual(len(SOURCE_FILES), 3)

    def test_reject_substituted_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            candidate = Path(tmp)
            (candidate / "manifest.json").write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Not the reviewed"):
                verify_candidate(candidate)
