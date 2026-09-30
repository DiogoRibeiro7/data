"""Tests for the external source catalog generator."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import generate_external_catalog as CATALOG  # noqa: E402


class ExternalCatalogTests(unittest.TestCase):
    """Exercise catalog normalization and freshness checks."""

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "external").mkdir()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def add_source(
        self,
        slug: str,
        *,
        license_data: dict[str, str] | None = None,
        storage: str | None = "authoritative-upstream",
        usage: dict[str, object] | None = None,
        consumers: list[str] | None = None,
    ) -> None:
        source = self.root / "external" / slug
        source.mkdir()
        metadata: dict[str, object] = {
            "schema_version": 1,
            "status": "external-reference",
            "id": slug,
            "title": f"Title {slug}",
            "publisher": f"Publisher {slug}",
            "source_url": f"https://example.test/{slug}",
        }
        if license_data is not None:
            metadata["license"] = license_data
        if storage is not None:
            metadata["storage"] = storage
        if usage is not None:
            metadata["usage"] = usage
        if consumers is not None:
            metadata["consumers"] = consumers
        (source / "metadata.yaml").write_text(
            yaml.safe_dump(metadata, sort_keys=False),
            encoding="utf-8",
        )

    def test_catalog_is_sorted_and_consumers_are_sorted(self) -> None:
        self.add_source("z-source", consumers=["b-project", "a-project"])
        self.add_source("a-source")
        catalog = CATALOG.build_catalog(self.root / "external")
        self.assertEqual([item["id"] for item in catalog["sources"]], ["a-source", "z-source"])
        self.assertEqual(catalog["sources"][1]["consumers"], ["a-project", "b-project"])

    def test_usage_shape_is_normalized(self) -> None:
        self.add_source(
            "usage-source",
            storage=None,
            usage={"storage": "authoritative-upstream", "redistribution": "series-dependent"},
        )
        item = CATALOG.build_catalog(self.root / "external")["sources"][0]
        self.assertEqual(item["storage"], "authoritative-upstream")
        self.assertEqual(item["redistribution"], "series-dependent")

    def test_missing_license_is_explicitly_unresolved(self) -> None:
        self.add_source("no-license")
        item = CATALOG.build_catalog(self.root / "external")["sources"][0]
        self.assertIsNone(item["license"])
        rendered = CATALOG.render_markdown({"schema_version": 1, "sources": [item]})
        self.assertIn("Unresolved", rendered)

    def test_duplicate_ids_fail(self) -> None:
        self.add_source("one")
        self.add_source("two")
        second = self.root / "external" / "two" / "metadata.yaml"
        metadata = yaml.safe_load(second.read_text(encoding="utf-8"))
        metadata["id"] = "one"
        second.write_text(yaml.safe_dump(metadata, sort_keys=False), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "duplicate external id"):
            CATALOG.build_catalog(self.root / "external")

    def test_write_then_check_is_current(self) -> None:
        self.add_source(
            "licensed",
            license_data={"name": "MIT", "url": "https://opensource.org/license/mit/"},
        )
        self.assertEqual(CATALOG.run(self.root, write=True), [])
        self.assertEqual(CATALOG.run(self.root, write=False), [])
        catalog = json.loads((self.root / "external" / "catalog.json").read_text(encoding="utf-8"))
        self.assertEqual(catalog["sources"][0]["id"], "licensed")

    def test_stale_catalog_is_reported(self) -> None:
        self.add_source("source")
        CATALOG.run(self.root, write=True)
        (self.root / "external" / "CATALOG.md").write_text("stale\n", encoding="utf-8")
        errors = CATALOG.run(self.root, write=False)
        self.assertTrue(any("catalog is stale" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
