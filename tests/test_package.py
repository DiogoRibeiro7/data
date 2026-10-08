"""Tests for installable registry package metadata and resources."""

from __future__ import annotations

import tomllib
import unittest
from importlib import resources
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PackageMetadataTests(unittest.TestCase):
    """Protect distribution metadata and packaged resources."""

    def test_poetry_metadata_identifies_distribution(self) -> None:
        data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        poetry = data["tool"]["poetry"]

        self.assertEqual(poetry["name"], "diogo-data-registry")
        self.assertEqual(poetry["version"], "0.1.0")
        self.assertEqual(poetry["license"], "MIT")
        self.assertEqual(poetry["authors"], ["Diogo Ribeiro"])
        self.assertEqual(poetry["maintainers"], ["Diogo Ribeiro"])
        self.assertEqual(
            poetry["scripts"]["data-registry"],
            "data_registry.cli:entrypoint",
        )
        self.assertEqual(
            data["tool"]["poetry"]["dependencies"]["python"],
            ">=3.12,<3.15",
        )

    def test_packaged_validator_schemas_are_present(self) -> None:
        schema_root = resources.files("data_registry").joinpath("schemas")
        expected = {
            "canonical-metadata-v1.schema.json",
            "consumer-metadata-v1.schema.json",
            "external-metadata-v1.schema.json",
            "legacy-metadata-v0.schema.json",
        }

        self.assertEqual(
            {item.name for item in schema_root.iterdir() if item.name.endswith(".json")},
            expected,
        )


if __name__ == "__main__":
    unittest.main()
