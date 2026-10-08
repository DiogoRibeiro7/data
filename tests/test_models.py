"""Tests for strict typed public registry models."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml

from data_registry.models import (
    CanonicalDataset,
    ConsumerRelationship,
    ExternalRecord,
    LifecycleDataset,
    ProvenanceDebtItem,
    RegistryModelError,
)

ROOT = Path(__file__).resolve().parents[1]


class RegistryModelTests(unittest.TestCase):
    """Exercise representative production records and strict failures."""

    def test_canonical_model_round_trips_production_metadata(self) -> None:
        path = ROOT / "datasets" / "online-retail-ii" / "metadata.yaml"
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))

        model = CanonicalDataset.from_mapping(raw)

        self.assertEqual(model.id, "online-retail-ii")
        self.assertEqual(model.lifecycle_status, "active")
        self.assertEqual(model.redistribution, "allowed")
        self.assertEqual(model.to_mapping(), raw)

    def test_external_model_round_trips_production_metadata(self) -> None:
        path = ROOT / "external" / "medium-crawlfeeds-corpus" / "metadata.yaml"
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))

        model = ExternalRecord.from_mapping(raw)

        self.assertEqual(model.id, "medium-crawlfeeds-corpus")
        self.assertEqual(model.to_mapping(), raw)

    def test_consumer_model_round_trips_production_metadata(self) -> None:
        path = (
            ROOT
            / "consumers"
            / "displacement-risk-lab-dynamodb"
            / "unhcr-refugee-population-2024.yaml"
        )
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))

        model = ConsumerRelationship.from_mapping(raw)

        self.assertEqual(model.status, "active")
        self.assertEqual(model.dataset_id, "unhcr-refugee-population-2024")
        self.assertIsNone(model.migration_status)
        self.assertEqual(model.to_mapping(), raw)

    def test_debt_model_round_trips_production_item(self) -> None:
        report = json.loads(
            (ROOT / "reports" / "provenance-debt.json").read_text(encoding="utf-8")
        )
        raw = report["items"][0]

        model = ProvenanceDebtItem.from_mapping(raw)

        self.assertIn(model.layer, {"external", "legacy"})
        self.assertEqual(model.to_mapping(), raw)

    def test_lifecycle_model_round_trips_production_item(self) -> None:
        report = json.loads(
            (ROOT / "reports" / "lifecycle.json").read_text(encoding="utf-8")
        )
        raw = report["datasets"][0]

        model = LifecycleDataset.from_mapping(raw)

        self.assertEqual(model.status, "active")
        self.assertEqual(model.replacement_chain, (model.id,))
        self.assertEqual(model.to_mapping(), raw)

    def test_canonical_model_rejects_unsupported_schema_version(self) -> None:
        path = ROOT / "datasets" / "online-retail-ii" / "metadata.yaml"
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        raw["schema_version"] = 2

        with self.assertRaisesRegex(
            RegistryModelError,
            "canonical.schema_version must be 1",
        ):
            CanonicalDataset.from_mapping(raw)

    def test_consumer_model_rejects_invalid_migration_state(self) -> None:
        path = (
            ROOT
            / "consumers"
            / "displacement-risk-lab-dynamodb"
            / "unhcr-refugee-population-2024.yaml"
        )
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        raw["migration"] = {"status": "maybe"}

        with self.assertRaisesRegex(
            RegistryModelError,
            "consumer.migration.status must be one of",
        ):
            ConsumerRelationship.from_mapping(raw)

    def test_lifecycle_model_rejects_malformed_replacement_chain(self) -> None:
        report = json.loads(
            (ROOT / "reports" / "lifecycle.json").read_text(encoding="utf-8")
        )
        raw = dict(report["datasets"][0])
        raw["replacement_chain"] = "not-a-list"

        with self.assertRaisesRegex(
            RegistryModelError,
            "lifecycle.replacement_chain must be a list",
        ):
            LifecycleDataset.from_mapping(raw)

    def test_to_mapping_returns_a_detached_mutable_copy(self) -> None:
        path = ROOT / "datasets" / "online-retail-ii" / "metadata.yaml"
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        model = CanonicalDataset.from_mapping(raw)

        restored = model.to_mapping()
        restored["id"] = "changed"

        self.assertEqual(model.id, "online-retail-ii")
        self.assertEqual(model.to_mapping()["id"], "online-retail-ii")


if __name__ == "__main__":
    unittest.main()
