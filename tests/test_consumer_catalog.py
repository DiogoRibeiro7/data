"""Tests for the canonical consumer catalog generator."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import generate_consumer_catalog as CATALOG  # noqa: E402


class ConsumerCatalogTests(unittest.TestCase):
    """Exercise deterministic consumer catalog and dependency graph generation."""

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "consumers").mkdir()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def add_record(
        self,
        consumer_id: str,
        dataset_id: str,
        *,
        filename: str | None = None,
        status: str = "active",
        repository: str | None = None,
        canonical_path: str | None = None,
    ) -> Path:
        """Add one consumer relationship fixture."""

        directory = self.root / "consumers" / consumer_id
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / (filename or f"{dataset_id}.yaml")
        metadata = {
            "schema_version": 1,
            "status": status,
            "consumer_id": consumer_id,
            "consumer_repository": repository or f"DiogoRibeiro7/{consumer_id}",
            "dataset_id": dataset_id,
            "registry_layer": "canonical",
            "registry_repository": "DiogoRibeiro7/data",
            "registry_commit": "a" * 40,
            "path": canonical_path or f"datasets/{dataset_id}/raw/data.csv",
            "sha256": "b" * 64,
            "consumer_commit": "c" * 40,
            "evidence_url": f"https://example.test/{consumer_id}/{dataset_id}",
        }
        path.write_text(yaml.safe_dump(metadata, sort_keys=False), encoding="utf-8")
        return path

    def test_catalog_relationships_are_sorted(self) -> None:
        self.add_record("z-consumer", "b-dataset")
        self.add_record("a-consumer", "z-dataset")
        self.add_record("a-consumer", "a-dataset")

        catalog = CATALOG.build_catalog(self.root / "consumers")

        self.assertEqual(
            [
                (item["consumer_id"], item["dataset_id"])
                for item in catalog["relationships"]
            ],
            [
                ("a-consumer", "a-dataset"),
                ("a-consumer", "z-dataset"),
                ("z-consumer", "b-dataset"),
            ],
        )

    def test_dependency_graph_has_forward_and_reverse_views(self) -> None:
        self.add_record("consumer-one", "dataset-a")
        self.add_record("consumer-one", "dataset-b")
        self.add_record("consumer-two", "dataset-a")

        graph = CATALOG.build_dependency_graph(
            CATALOG.build_catalog(self.root / "consumers")
        )

        self.assertEqual(
            [item["dataset_id"] for item in graph["consumers"]["consumer-one"]["datasets"]],
            ["dataset-a", "dataset-b"],
        )
        self.assertEqual(
            [
                item["consumer_id"]
                for item in graph["datasets"]["dataset-a"]["consumers"]
            ],
            ["consumer-one", "consumer-two"],
        )

    def test_duplicate_relationships_fail(self) -> None:
        first = self.add_record("consumer", "dataset", filename="first.yaml")
        duplicate = first.parent / "second.yaml"
        duplicate.write_text(first.read_text(encoding="utf-8"), encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "duplicate consumer/dataset relationship"):
            CATALOG.build_catalog(self.root / "consumers")

    def test_conflicting_repository_for_same_consumer_fails(self) -> None:
        self.add_record("consumer", "dataset-a", repository="DiogoRibeiro7/one")
        self.add_record("consumer", "dataset-b", repository="DiogoRibeiro7/two")

        catalog = CATALOG.build_catalog(self.root / "consumers")

        with self.assertRaisesRegex(ValueError, "conflicting consumer_repository"):
            CATALOG.build_dependency_graph(catalog)

    def test_markdown_escapes_pipe_in_canonical_path(self) -> None:
        self.add_record(
            "consumer",
            "dataset",
            canonical_path="datasets/dataset/raw/a|b.csv",
        )

        rendered = CATALOG.render_markdown(
            CATALOG.build_catalog(self.root / "consumers")
        )

        self.assertIn("datasets/dataset/raw/a\\|b.csv", rendered)


    def test_markdown_contains_contract_and_evidence(self) -> None:
        self.add_record("consumer", "dataset")
        rendered = CATALOG.render_markdown(
            CATALOG.build_catalog(self.root / "consumers")
        )

        self.assertIn("DiogoRibeiro7/consumer", rendered)
        self.assertIn("datasets/dataset/raw/data.csv", rendered)
        self.assertIn("[evidence](https://example.test/consumer/dataset)", rendered)

    def test_write_then_check_is_current(self) -> None:
        self.add_record("consumer", "dataset")

        self.assertEqual(CATALOG.run(self.root, write=True), [])
        self.assertEqual(CATALOG.run(self.root, write=False), [])

        catalog = json.loads(
            (self.root / "consumers" / "catalog.json").read_text(encoding="utf-8")
        )
        graph = json.loads(
            (self.root / "consumers" / "dependency-graph.json").read_text(encoding="utf-8")
        )
        self.assertEqual(catalog["relationships"][0]["dataset_id"], "dataset")
        self.assertIn("dataset", graph["datasets"])

    def test_stale_artifact_is_reported(self) -> None:
        self.add_record("consumer", "dataset")
        CATALOG.run(self.root, write=True)
        (self.root / "consumers" / "CATALOG.md").write_text("stale\n", encoding="utf-8")

        errors = CATALOG.run(self.root, write=False)

        self.assertTrue(any("consumer artifact is stale" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
