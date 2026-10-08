"""Tests for the stable typed programmatic registry API."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml

from data_registry.api import RegistryClient
from data_registry.core import RegistryError
from data_registry.models import (
    CanonicalDataset,
    ConsumerRelationship,
    ExternalRecord,
    LegacyRecord,
    LifecycleDataset,
    ProvenanceDebtItem,
)

ROOT = Path(__file__).resolve().parents[1]


class RegistryApiTests(unittest.TestCase):
    """Exercise the public offline RegistryClient surface."""

    def setUp(self) -> None:
        self.client = RegistryClient(ROOT)

    def test_client_accepts_string_root(self) -> None:
        client = RegistryClient(str(ROOT))

        self.assertEqual(client.root, ROOT.resolve())
        self.assertEqual(client.canonical("online-retail-ii").id, "online-retail-ii")

    def test_list_returns_typed_records_in_deterministic_order(self) -> None:
        records = self.client.list()
        keys = [
            (
                "canonical"
                if isinstance(item, CanonicalDataset)
                else "external"
                if isinstance(item, ExternalRecord)
                else "legacy",
                item.id,
            )
            for item in records
        ]

        self.assertEqual(keys, sorted(keys, key=lambda item: (
            {"canonical": 0, "external": 1, "legacy": 2}[item[0]],
            item[1],
        )))
        self.assertTrue(any(isinstance(item, CanonicalDataset) for item in records))
        self.assertTrue(any(isinstance(item, ExternalRecord) for item in records))
        self.assertTrue(any(isinstance(item, LegacyRecord) for item in records))

    def test_canonical_lookup_returns_typed_dataset(self) -> None:
        dataset = self.client.canonical("online-retail-ii")

        self.assertIsInstance(dataset, CanonicalDataset)
        self.assertEqual(dataset.id, "online-retail-ii")

    def test_search_returns_typed_results(self) -> None:
        results = self.client.search("refugee")

        self.assertTrue(results)
        self.assertTrue(
            all(
                isinstance(
                    item,
                    (CanonicalDataset, ExternalRecord, LegacyRecord),
                )
                for item in results
            )
        )

    def test_consumer_lookups_return_typed_relationships(self) -> None:
        relationships = self.client.consumer("displacement-risk-lab-dynamodb")

        self.assertTrue(relationships)
        self.assertTrue(
            all(isinstance(item, ConsumerRelationship) for item in relationships)
        )
        self.assertEqual(
            [item.dataset_id for item in relationships],
            sorted(item.dataset_id for item in relationships),
        )

        reverse = self.client.consumers_for_dataset(
            "unhcr-refugee-population-2024"
        )
        self.assertEqual(
            [item.consumer_id for item in reverse],
            ["displacement-risk-lab-dynamodb"],
        )

    def test_provenance_debt_api_returns_typed_sorted_items(self) -> None:
        items = self.client.provenance_debt()

        self.assertTrue(items)
        self.assertTrue(
            all(isinstance(item, ProvenanceDebtItem) for item in items)
        )
        self.assertEqual(
            [(item.layer, item.id) for item in items],
            sorted((item.layer, item.id) for item in items),
        )

        exact = self.client.provenance_debt_item(items[0].id)
        self.assertIsInstance(exact, ProvenanceDebtItem)
        self.assertEqual(exact.id, items[0].id)

    def test_lifecycle_and_replacement_are_typed(self) -> None:
        lifecycle = self.client.lifecycle("online-retail-ii")
        preferred = self.client.preferred_replacement("online-retail-ii")

        self.assertIsInstance(lifecycle, LifecycleDataset)
        self.assertIsInstance(preferred, LifecycleDataset)
        self.assertEqual(preferred.id, "online-retail-ii")
        self.assertEqual(
            self.client.superseded_by("online-retail-ii"),
            (),
        )

    def test_unknown_ids_fail_explicitly(self) -> None:
        with self.assertRaisesRegex(RegistryError, "unknown registry id"):
            self.client.canonical("missing-dataset")

        with self.assertRaisesRegex(RegistryError, "unknown consumer id"):
            self.client.consumer("missing-consumer")

        with self.assertRaisesRegex(RegistryError, "unknown provenance debt id"):
            self.client.provenance_debt_item("missing-debt")

        with self.assertRaisesRegex(RegistryError, "unknown lifecycle dataset id"):
            self.client.lifecycle("missing-dataset")

    def test_ambiguous_id_fails_like_cli_core_semantics(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            canonical = root / "datasets" / "same-id"
            external = root / "external" / "same-id"
            canonical.mkdir(parents=True)
            external.mkdir(parents=True)

            (canonical / "metadata.yaml").write_text(
                yaml.safe_dump(
                    {"id": "same-id", "title": "Canonical"},
                    sort_keys=False,
                ),
                encoding="utf-8",
            )
            (external / "metadata.yaml").write_text(
                yaml.safe_dump(
                    {"id": "same-id", "title": "External"},
                    sort_keys=False,
                ),
                encoding="utf-8",
            )

            client = RegistryClient(root)
            with self.assertRaisesRegex(RegistryError, "ambiguous across layers"):
                client.get("same-id")

    def test_invalid_layer_fails_explicitly(self) -> None:
        with self.assertRaisesRegex(RegistryError, "unknown registry layer"):
            self.client.list(layer="made-up")

        with self.assertRaisesRegex(RegistryError, "unknown registry layer"):
            self.client.search("data", layer="made-up")

    def test_read_api_never_opens_network_connections(self) -> None:
        with patch(
            "urllib.request.urlopen",
            side_effect=AssertionError("network access is forbidden"),
        ):
            self.client.list(layer="canonical")
            self.client.search("retail")
            self.client.canonical("online-retail-ii")
            self.client.consumer("medium-blog")
            self.client.consumers_for_dataset("online-retail-ii")
            self.client.provenance_debt()
            self.client.lifecycle("online-retail-ii")
            self.client.preferred_replacement("online-retail-ii")
            self.client.superseded_by("online-retail-ii")


if __name__ == "__main__":
    unittest.main()
