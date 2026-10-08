"""Tests for the reusable registry core module boundary."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import fetch_dataset as FETCH_SCRIPT  # noqa: E402
import registry as REGISTRY_SCRIPT  # noqa: E402

from data_registry import core as CORE  # noqa: E402
from data_registry import fetch as FETCH  # noqa: E402


class RegistryCoreTests(unittest.TestCase):
    """Protect the shared-core/compatibility-wrapper boundary."""

    def test_fetch_script_reexports_shared_implementation(self) -> None:
        self.assertIs(FETCH_SCRIPT.DatasetReference, FETCH.DatasetReference)
        self.assertIs(FETCH_SCRIPT.fetch_dataset_file, FETCH.fetch_dataset_file)
        self.assertIs(FETCH_SCRIPT.sha256_file, FETCH.sha256_file)

    def test_registry_script_delegates_lookup_functions_to_shared_core(self) -> None:
        self.assertIs(REGISTRY_SCRIPT.RegistryEntry, CORE.RegistryEntry)
        self.assertIs(REGISTRY_SCRIPT.RegistryError, CORE.RegistryError)
        self.assertIs(REGISTRY_SCRIPT.load_registry, CORE.load_registry)
        self.assertIs(REGISTRY_SCRIPT.find_entry, CORE.find_entry)
        self.assertIs(REGISTRY_SCRIPT.search_entries, CORE.search_entries)
        self.assertIs(
            REGISTRY_SCRIPT.load_consumer_graph,
            CORE.load_consumer_graph,
        )
        self.assertIs(
            REGISTRY_SCRIPT.load_lifecycle_report,
            CORE.load_lifecycle_report,
        )
        self.assertIs(
            REGISTRY_SCRIPT.fetch_entry_file,
            CORE.fetch_entry_file,
        )

    def test_shared_core_import_has_no_cli_side_effects(self) -> None:
        self.assertTrue(callable(CORE.load_registry))
        self.assertTrue(callable(FETCH.fetch_dataset_file))

    def test_shared_core_reads_registry_without_script_imports(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            dataset = root / "datasets" / "example"
            dataset.mkdir(parents=True)
            metadata = {
                "schema_version": 1,
                "id": "example",
                "title": "Example",
                "description": "Fixture",
                "domain": ["testing"],
                "source": {
                    "publisher": "Fixture",
                    "url": "https://example.test/data",
                },
                "files": [],
            }
            (dataset / "metadata.yaml").write_text(
                yaml.safe_dump(metadata, sort_keys=False),
                encoding="utf-8",
            )

            entries = CORE.load_registry(root)

        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].id, "example")
        self.assertEqual(entries[0].layer, "canonical")

    def test_shared_core_reads_committed_report_shapes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "reports").mkdir()
            (root / "consumers").mkdir()

            (root / "reports" / "provenance-debt.json").write_text(
                json.dumps({"items": []}) + "\n",
                encoding="utf-8",
            )
            (root / "reports" / "lifecycle.json").write_text(
                json.dumps({"datasets": []}) + "\n",
                encoding="utf-8",
            )
            (root / "consumers" / "dependency-graph.json").write_text(
                json.dumps({"consumers": {}, "datasets": {}}) + "\n",
                encoding="utf-8",
            )

            self.assertEqual(CORE.load_provenance_debt(root)["items"], [])
            self.assertEqual(CORE.load_lifecycle_report(root)["datasets"], [])
            self.assertEqual(
                CORE.load_consumer_graph(root),
                {"consumers": {}, "datasets": {}},
            )


if __name__ == "__main__":
    unittest.main()
