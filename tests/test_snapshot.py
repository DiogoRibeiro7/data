"""Tests for deterministic registry snapshot generation."""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

import yaml
import jsonschema

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import create_snapshot as SNAPSHOT  # noqa: E402


class SnapshotFixture:
    """Build a minimal repository layout for snapshot tests."""

    def __init__(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "datasets").mkdir()
        (self.root / "external").mkdir()
        (self.root / "consumers").mkdir()
        (self.root / "schemas").mkdir()
        (self.root / "legacy").mkdir()
        (self.root / "reports").mkdir()
        (self.root / "distribution" / "v1").mkdir(parents=True)
        (self.root / "preservation").mkdir()
        (self.root / "archive").mkdir()
        (self.root / "scripts").mkdir()
        (self.root / ".github" / "workflows").mkdir(parents=True)
        (self.root / "scripts" / "create_snapshot.py").write_text(
            "# fixture snapshot generator\n",
            encoding="utf-8",
        )
        (self.root / ".github" / "workflows" / "snapshot-release.yml").write_text(
            "jobs:\n"
            "  release:\n"
            "    uses: DiogoRibeiro7/git-actions-collection/.github/workflows/"
            "snapshot-release.yml@6c68c76f3cec5b61552d24aa724fbd3398c33dbd\n",
            encoding="utf-8",
        )
        (self.root / "pyproject.toml").write_text(
            """[tool.poetry]
name = "diogo-data-registry"
version = "0.1.0"

[tool.poetry.dependencies]
python = ">=3.12,<3.15"

[tool.poetry.scripts]
data-registry = "data_registry.cli:entrypoint"
""",
            encoding="utf-8",
        )
        (self.root / "distribution" / "v1" / "index.json").write_text(
            json.dumps(
                {
                    "distribution_version": 1,
                    "repository": "DiogoRibeiro7/data",
                    "artifacts": [
                        {
                            "name": "canonical",
                            "path": "canonical.json",
                            "schema_version": 1,
                            "source": "datasets/catalog.json",
                        }
                    ],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )

        (self.root / "reports" / "canonical-adoption-policy.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "baseline": {
                        "snapshot": "snapshot-2026.10.05",
                        "dataset_ids": [],
                    },
                    "exemptions": [],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        (self.root / "reports" / "registry-quality.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "canonical_expansion": {
                        "baseline_snapshot": "snapshot-2026.10.05",
                        "baseline_dataset_count": 0,
                        "current_dataset_count": 0,
                        "datasets_added_since_baseline": [],
                        "datasets_removed_since_baseline": [],
                        "added_datasets_with_consumers": [],
                        "added_datasets_exempted": [],
                        "exemptions": {},
                        "uncovered_datasets": [],
                    },
                    "consumers": {
                        "active_relationship_count": 0,
                        "pinned_contract_count": 0,
                        "pinned_contract_coverage": 1.0,
                        "canonical_dataset_adoption_coverage": 1.0,
                    },
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        (self.root / "reports" / "lifecycle.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "summary": {
                        "canonical_dataset_count": 0,
                        "active_count": 0,
                        "deprecated_count": 0,
                        "superseded_count": 0,
                        "replacement_edge_count": 0,
                        "active_consumer_relationship_count": 0,
                        "current_consumer_relationship_count": 0,
                        "migration_required_count": 0,
                        "migration_planned_count": 0,
                        "migration_retained_count": 0,
                        "migrated_relationship_count": 0,
                        "migration_needed_count": 0,
                        "migration_resolution_coverage": 1.0,
                    },
                    "preferred_replacements": {},
                    "datasets": [],
                    "consumer_migrations": [],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        (self.root / "preservation" / "policy-v1.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "policy_version": 1,
                    "archive_profiles": {
                        "release-metadata": {},
                        "eligible-canonical-bytes": {},
                    },
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        (
            self.root
            / "preservation"
            / "external-disappearance-policy-v1.json"
        ).write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "repository": "DiogoRibeiro7/data",
                    "states": {
                        "live": {},
                        "transient-outage": {},
                        "moved": {},
                        "permanently-unavailable": {},
                        "legal-withdrawal": {},
                    },
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        (self.root / "archive" / "identifiers.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "repository": "DiogoRibeiro7/data",
                    "entries": [],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        (self.root / "reports" / "preservation-eligibility.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "summary": {
                        "canonical_dataset_count": 0,
                        "canonical_byte_archive_eligible_count": 0,
                        "canonical_metadata_only_count": 0,
                        "external_source_count": 0,
                        "external_metadata_only_count": 0,
                        "legacy_package_count": 0,
                        "legacy_metadata_only_count": 0,
                    },
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )

        (self.root / "reports" / "provenance-debt.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "age_reference_date": "2026-10-05",
                    "summary": {
                        "total_debt": 2,
                        "external_count": 1,
                        "legacy_count": 1,
                        "structured_count": 2,
                        "unstructured_count": 0,
                        "actionable_count": 0,
                        "terminal_count": 2,
                        "by_blocker_category": {
                            "redistribution-rights": 1,
                            "historical-export-route": 1,
                        },
                    },
                    "items": [],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )

        (self.root / "datasets" / "catalog.json").write_text(
            json.dumps({"schema_version": 1, "datasets": []}, indent=2) + "\n",
            encoding="utf-8",
        )
        (self.root / "external" / "catalog.json").write_text(
            json.dumps({"schema_version": 1, "sources": []}, indent=2) + "\n",
            encoding="utf-8",
        )
        (self.root / "consumers" / "catalog.json").write_text(
            json.dumps({"schema_version": 1, "relationships": []}, indent=2) + "\n",
            encoding="utf-8",
        )
        (self.root / "consumers" / "dependency-graph.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "consumers": {},
                    "datasets": {},
                },
                indent=2,
            ) + "\n",
            encoding="utf-8",
        )
        schemas = {
            "canonical-metadata-v1.schema.json": 1,
            "consumer-metadata-v1.schema.json": 1,
            "external-metadata-v1.schema.json": 1,
            "legacy-metadata-v0.schema.json": 0,
        }
        for name, version in schemas.items():
            (self.root / "schemas" / name).write_text(
                json.dumps(
                    {
                        "$schema": "https://json-schema.org/draft/2020-12/schema",
                        "type": "object",
                        "properties": {"schema_version": {"const": version}},
                    },
                    indent=2,
                ) + "\n",
                encoding="utf-8",
            )

    def close(self) -> None:
        self.temp.cleanup()

    def add_canonical(
        self,
        slug: str,
        payload: bytes = b"a,b\n1,2\n",
        *,
        lifecycle: dict[str, object] | None = None,
    ) -> str:
        dataset = self.root / "datasets" / slug
        raw = dataset / "raw"
        raw.mkdir(parents=True)
        data_path = raw / "example.csv"
        data_path.write_bytes(payload)
        checksum = hashlib.sha256(payload).hexdigest()
        metadata = {
            "schema_version": 1,
            "id": slug,
            "title": slug,
            "description": "fixture",
            "domain": ["testing"],
            "source": {
                "publisher": "Fixture",
                "url": "https://example.test/data",
                "retrieved_at": "2026-10-01",
                "snapshot": "v1",
            },
            "license": {
                "name": "CC0-1.0",
                "url": "https://creativecommons.org/publicdomain/zero/1.0/",
                "redistribution": "allowed",
            },
            "citation": None,
            "files": [{
                "path": "raw/example.csv",
                "role": "raw",
                "format": "csv",
                "sha256": checksum,
            }],
            "lineage": [],
        }
        if lifecycle is not None:
            metadata["lifecycle"] = lifecycle
        (dataset / "metadata.yaml").write_text(
            yaml.safe_dump(metadata, sort_keys=False),
            encoding="utf-8",
        )
        return checksum

    def add_consumer(
        self,
        consumer_id: str,
        dataset_id: str,
        *,
        repository: str = "DiogoRibeiro7/example-consumer",
        status: str = "active",
    ) -> None:
        """Add one consumer relationship and regenerate fixture artifacts."""

        directory = self.root / "consumers" / consumer_id
        directory.mkdir(parents=True, exist_ok=True)
        metadata = {
            "schema_version": 1,
            "status": status,
            "consumer_id": consumer_id,
            "consumer_repository": repository,
            "dataset_id": dataset_id,
            "registry_layer": "canonical",
            "registry_repository": "DiogoRibeiro7/data",
            "registry_commit": "e" * 40,
            "path": f"datasets/{dataset_id}/raw/example.csv",
            "sha256": "f" * 64,
            "consumer_commit": "a" * 40,
        }
        (directory / f"{dataset_id}.yaml").write_text(
            yaml.safe_dump(metadata, sort_keys=False),
            encoding="utf-8",
        )

        catalog = {
            "schema_version": 1,
            "relationships": [
                {
                    "consumer_id": consumer_id,
                    "consumer_repository": repository,
                    "dataset_id": dataset_id,
                    "status": status,
                    "registry_repository": "DiogoRibeiro7/data",
                    "registry_commit": "e" * 40,
                    "path": f"datasets/{dataset_id}/raw/example.csv",
                    "sha256": "f" * 64,
                    "consumer_commit": "a" * 40,
                }
            ],
        }
        (self.root / "consumers" / "catalog.json").write_text(
            json.dumps(catalog, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        graph = {
            "schema_version": 1,
            "consumers": {
                consumer_id: {
                    "repository": repository,
                    "datasets": [
                        {
                            "dataset_id": dataset_id,
                            "status": status,
                            "registry_commit": "e" * 40,
                            "path": f"datasets/{dataset_id}/raw/example.csv",
                            "sha256": "f" * 64,
                        }
                    ],
                }
            },
            "datasets": {
                dataset_id: {
                    "consumers": [
                        {
                            "consumer_id": consumer_id,
                            "consumer_repository": repository,
                            "status": status,
                            "registry_commit": "e" * 40,
                            "path": f"datasets/{dataset_id}/raw/example.csv",
                            "sha256": "f" * 64,
                        }
                    ]
                }
            },
        }
        (self.root / "consumers" / "dependency-graph.json").write_text(
            json.dumps(graph, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )


class SnapshotTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = SnapshotFixture()

    def tearDown(self) -> None:
        self.fixture.close()

    def test_valid_snapshot_tags(self) -> None:
        for tag in ("snapshot-2026.10.01", "snapshot-2026.10.01.2"):
            SNAPSHOT.validate_snapshot_tag(tag)

    def test_invalid_snapshot_tag_or_date_fails(self) -> None:
        for tag in ("v1.0.0", "snapshot-2026-10-01", "snapshot-2026.02.30", "snapshot-2026.10.01.0"):
            with self.subTest(tag=tag):
                with self.assertRaises(ValueError):
                    SNAPSHOT.validate_snapshot_tag(tag)

    def test_commit_must_be_full_lowercase_sha(self) -> None:
        for commit in ("main", "a" * 7, "A" * 40):
            with self.subTest(commit=commit):
                with self.assertRaises(ValueError):
                    SNAPSHOT.validate_commit(commit)

    def test_manifest_contains_catalog_and_schema_digests(self) -> None:
        manifest = SNAPSHOT.build_manifest(
            self.fixture.root,
            tag="snapshot-2026.10.01",
            commit="a" * 40,
        )
        self.assertEqual(manifest["manifest_version"], 8)
        self.assertEqual(manifest["commit"], "a" * 40)
        self.assertEqual(manifest["catalogs"]["canonical"]["schema_version"], 1)
        self.assertEqual(manifest["metadata_schemas"]["legacy"]["schema_version"], 0)
        self.assertEqual(manifest["metadata_schemas"]["consumer"]["schema_version"], 1)
        self.assertEqual(manifest["catalogs"]["consumer"]["schema_version"], 1)
        self.assertEqual(len(manifest["catalogs"]["external"]["sha256"]), 64)
        self.assertEqual(len(manifest["consumer_registry"]["sha256"]), 64)
        self.assertEqual(len(manifest["provenance_debt"]["sha256"]), 64)
        self.assertEqual(manifest["provenance_debt"]["terminal_count"], 2)
        self.assertEqual(manifest["provenance_debt"]["unstructured_count"], 0)
        self.assertEqual(manifest["provenance_debt"]["items"], [])
        self.assertEqual(
            manifest["canonical_expansion"]["baseline_snapshot"],
            "snapshot-2026.10.05",
        )
        self.assertEqual(
            len(manifest["canonical_expansion"]["quality_report_sha256"]),
            64,
        )
        self.assertEqual(
            len(manifest["canonical_expansion"]["adoption_policy_sha256"]),
            64,
        )
        self.assertEqual(
            len(manifest["canonical_lifecycle"]["sha256"]),
            64,
        )
        self.assertEqual(manifest["canonical_lifecycle"]["active_count"], 0)
        self.assertEqual(
            manifest["canonical_lifecycle"]["migration_resolution_coverage"],
            1.0,
        )

    def test_consumer_relationships_are_recorded(self) -> None:
        self.fixture.add_consumer(
            "example-consumer",
            "dataset",
            repository="DiogoRibeiro7/example-consumer",
        )
        manifest = SNAPSHOT.build_manifest(
            self.fixture.root,
            tag="snapshot-2026.10.01",
            commit="e" * 40,
        )

        consumer = manifest["consumer_registry"]
        self.assertEqual(consumer["consumer_count"], 1)
        self.assertEqual(consumer["repository_count"], 1)
        self.assertEqual(consumer["dataset_count"], 1)
        self.assertEqual(consumer["relationship_count"], 1)
        self.assertEqual(consumer["active_relationship_count"], 1)
        self.assertEqual(consumer["deprecated_relationship_count"], 0)
        self.assertEqual(len(consumer["relationships"]), 1)
        self.assertEqual(
            consumer["relationships"][0]["consumer_id"],
            "example-consumer",
        )

    def test_snapshot_summary_includes_consumer_registry(self) -> None:
        self.fixture.add_consumer("example-consumer", "dataset")
        manifest = SNAPSHOT.build_manifest(
            self.fixture.root,
            tag="snapshot-2026.10.01",
            commit="e" * 40,
        )

        summary = SNAPSHOT.render_summary(manifest)

        self.assertIn("## Consumer registry", summary)
        self.assertIn("Active canonical consumer relationships: **1**", summary)
        self.assertIn("Distinct repositories: **1**", summary)
        self.assertIn("consumers/dependency-graph.json", summary)


    def test_snapshot_summary_includes_provenance_debt(self) -> None:
        manifest = SNAPSHOT.build_manifest(
            self.fixture.root,
            tag="snapshot-2026.10.05",
            commit="e" * 40,
        )

        summary = SNAPSHOT.render_summary(manifest)

        self.assertIn("## Provenance and licensing debt", summary)
        self.assertIn("Terminal debt items: **2**", summary)
        self.assertIn("Actionable debt items: **0**", summary)
        self.assertIn("reports/provenance-debt.json", summary)

    def test_provenance_debt_summary_must_be_well_formed(self) -> None:
        path = self.fixture.root / "reports" / "provenance-debt.json"
        path.write_text('{"schema_version": 1, "summary": {}}\n', encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "summary.total_debt"):
            SNAPSHOT.build_manifest(
                self.fixture.root,
                tag="snapshot-2026.10.05",
                commit="f" * 40,
            )

    def test_snapshot_summary_includes_canonical_expansion_state(self) -> None:
        quality_path = self.fixture.root / "reports" / "registry-quality.json"
        quality = json.loads(quality_path.read_text(encoding="utf-8"))
        quality["canonical_expansion"].update(
            {
                "baseline_dataset_count": 2,
                "current_dataset_count": 4,
                "datasets_added_since_baseline": ["ons", "unhcr"],
                "added_datasets_with_consumers": ["ons", "unhcr"],
            }
        )
        quality["consumers"].update(
            {
                "active_relationship_count": 4,
                "pinned_contract_count": 4,
                "pinned_contract_coverage": 1.0,
                "canonical_dataset_adoption_coverage": 1.0,
            }
        )
        quality_path.write_text(
            json.dumps(quality, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        manifest = SNAPSHOT.build_manifest(
            self.fixture.root,
            tag="snapshot-2026.10.06",
            commit="a" * 40,
        )
        summary = SNAPSHOT.render_summary(manifest)

        self.assertIn("## Canonical expansion and adoption", summary)
        self.assertIn("Baseline / current canonical datasets: **2 / 4**", summary)
        self.assertIn("ons", summary)
        self.assertIn("unhcr", summary)
        self.assertIn("Uncovered canonical datasets: **0**", summary)

    def test_snapshot_records_phase10_preservation_trust_state(self) -> None:
        manifest = SNAPSHOT.build_manifest(
            self.fixture.root,
            tag="snapshot-2026.10.10",
            commit="a" * 40,
        )

        self.assertEqual(manifest["manifest_version"], 8)
        preservation = manifest["preservation_trust"]
        self.assertEqual(
            preservation["preservation_eligibility"][
                "canonical_byte_archive_eligible_count"
            ],
            0,
        )
        self.assertEqual(
            preservation["external_disappearance_policy"]["states"],
            [
                "legal-withdrawal",
                "live",
                "moved",
                "permanently-unavailable",
                "transient-outage",
            ],
        )
        self.assertTrue(
            preservation["release_trust"]["offline_bundle_verification"]
        )
        self.assertTrue(
            preservation["release_trust"]["github_artifact_attestations"]
        )

    def test_snapshot_summary_includes_phase10_preservation_trust(self) -> None:
        manifest = SNAPSHOT.build_manifest(
            self.fixture.root,
            tag="snapshot-2026.10.10",
            commit="b" * 40,
        )
        summary = SNAPSHOT.render_summary(manifest)

        self.assertIn("## Preservation, citation, and release trust", summary)
        self.assertIn("Offline bundle verification: **enabled**", summary)
        self.assertIn("GitHub artifact attestations: **enabled**", summary)

    def test_snapshot_records_registry_client_state(self) -> None:
        manifest = SNAPSHOT.build_manifest(
            self.fixture.root,
            tag="snapshot-2026.10.09",
            commit="a" * 40,
        )

        client = manifest["registry_client"]
        self.assertEqual(client["name"], "diogo-data-registry")
        self.assertEqual(client["version"], "0.1.0")
        self.assertEqual(client["public_api_version"], 1)
        self.assertEqual(client["python"], ">=3.12,<3.15")
        self.assertEqual(
            client["console_entry"],
            "data_registry.cli:entrypoint",
        )
        self.assertEqual(len(client["sha256"]), 64)

    def test_snapshot_records_static_distribution_state(self) -> None:
        manifest = SNAPSHOT.build_manifest(
            self.fixture.root,
            tag="snapshot-2026.10.09",
            commit="b" * 40,
        )

        distribution = manifest["static_distribution"]
        self.assertEqual(distribution["distribution_version"], 1)
        self.assertEqual(distribution["repository"], "DiogoRibeiro7/data")
        self.assertEqual(len(distribution["sha256"]), 64)
        self.assertEqual(
            distribution["artifacts"],
            [
                {
                    "name": "canonical",
                    "path": "canonical.json",
                    "schema_version": 1,
                    "source": "datasets/catalog.json",
                }
            ],
        )

    def test_snapshot_summary_includes_client_distribution_state(self) -> None:
        manifest = SNAPSHOT.build_manifest(
            self.fixture.root,
            tag="snapshot-2026.10.09",
            commit="c" * 40,
        )

        summary = SNAPSHOT.render_summary(manifest)

        self.assertIn("## Registry client and static distribution", summary)
        self.assertIn("diogo-data-registry 0.1.0", summary)
        self.assertIn("Static distribution version: **v1**", summary)

    def test_snapshot_summary_includes_lifecycle_state(self) -> None:
        manifest = SNAPSHOT.build_manifest(
            self.fixture.root,
            tag="snapshot-2026.10.07",
            commit="a" * 40,
        )

        summary = SNAPSHOT.render_summary(manifest)

        self.assertIn("## Canonical lifecycle and supersession", summary)
        self.assertIn("Migration resolution coverage: **100%**", summary)
        self.assertIn("Replacement chains:", summary)

    def test_lifecycle_snapshot_projection_records_replacement_chain(self) -> None:
        report_path = self.fixture.root / "reports" / "lifecycle.json"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        report["summary"].update(
            {
                "canonical_dataset_count": 2,
                "active_count": 1,
                "superseded_count": 1,
                "replacement_edge_count": 1,
                "active_consumer_relationship_count": 1,
                "current_consumer_relationship_count": 0,
                "migration_required_count": 1,
                "migration_needed_count": 1,
                "migration_resolution_coverage": 0.0,
            }
        )
        report["preferred_replacements"] = {"old": "new"}
        report["datasets"] = [
            {
                "id": "new",
                "status": "active",
                "deprecated_at": None,
                "direct_replacement": None,
                "preferred_dataset_id": "new",
                "replacement_chain": ["new"],
                "active_consumer_count": 0,
                "migration_needed_consumer_count": 0,
                "migration_note": None,
            },
            {
                "id": "old",
                "status": "superseded",
                "deprecated_at": "2026-10-07",
                "direct_replacement": "new",
                "preferred_dataset_id": "new",
                "replacement_chain": ["old", "new"],
                "active_consumer_count": 1,
                "migration_needed_consumer_count": 1,
                "migration_note": "Move to new.",
            },
        ]
        report_path.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        manifest = SNAPSHOT.build_manifest(
            self.fixture.root,
            tag="snapshot-2026.10.07",
            commit="b" * 40,
        )

        lifecycle = manifest["canonical_lifecycle"]
        self.assertEqual(lifecycle["preferred_replacements"], {"old": "new"})
        old = next(item for item in lifecycle["datasets"] if item["id"] == "old")
        self.assertEqual(old["replacement_chain"], ["old", "new"])
        self.assertEqual(old["preferred_dataset_id"], "new")

    def test_canonical_dataset_record_embeds_lifecycle_metadata(self) -> None:
        self.fixture.add_canonical(
            "old",
            lifecycle={
                "status": "superseded",
                "superseded_by": "new",
                "deprecated_at": "2026-10-07",
                "migration_note": "Use new.",
            },
        )
        self.fixture.add_canonical(
            "new",
            payload=b"x\n2\n",
            lifecycle={
                "status": "active",
                "supersedes": ["old"],
            },
        )

        manifest = SNAPSHOT.build_manifest(
            self.fixture.root,
            tag="snapshot-2026.10.07",
            commit="c" * 40,
        )

        by_id = {item["id"]: item for item in manifest["canonical_datasets"]}
        self.assertEqual(by_id["old"]["lifecycle"]["status"], "superseded")
        self.assertEqual(by_id["old"]["lifecycle"]["superseded_by"], "new")
        self.assertEqual(by_id["new"]["lifecycle"]["supersedes"], ["old"])
    def test_unquoted_yaml_date_is_serialized_as_iso_string(self) -> None:
        self.fixture.add_canonical("dataset")
        metadata_path = self.fixture.root / "datasets" / "dataset" / "metadata.yaml"
        lines = metadata_path.read_text(encoding="utf-8").splitlines()
        rewritten = [
            "  retrieved_at: 2026-10-01"
            if line.lstrip().startswith("retrieved_at:")
            else line
            for line in lines
        ]
        metadata_path.write_text("\n".join(rewritten) + "\n", encoding="utf-8")

        manifest = SNAPSHOT.build_manifest(
            self.fixture.root,
            tag="snapshot-2026.10.06",
            commit="b" * 40,
        )

        retrieved_at = manifest["canonical_datasets"][0]["source"]["retrieved_at"]
        self.assertEqual(retrieved_at, "2026-10-01")
        json.dumps(manifest)
    def test_canonical_source_identity_is_recorded(self) -> None:
        self.fixture.add_canonical("dataset")
        manifest = SNAPSHOT.build_manifest(
            self.fixture.root,
            tag="snapshot-2026.10.06",
            commit="b" * 40,
        )

        item = manifest["canonical_datasets"][0]
        self.assertEqual(item["source"]["publisher"], "Fixture")
        self.assertEqual(item["source"]["snapshot"], "v1")
        self.assertEqual(item["license"]["redistribution"], "allowed")
    def test_canonical_file_checksums_are_recorded(self) -> None:
        checksum = self.fixture.add_canonical("dataset")
        manifest = SNAPSHOT.build_manifest(
            self.fixture.root,
            tag="snapshot-2026.10.01",
            commit="b" * 40,
        )
        item = manifest["canonical_datasets"][0]
        self.assertEqual(item["id"], "dataset")
        self.assertEqual(item["files"][0]["sha256"], checksum)

    def test_canonical_checksum_mismatch_fails(self) -> None:
        self.fixture.add_canonical("dataset")
        metadata_path = self.fixture.root / "datasets" / "dataset" / "metadata.yaml"
        metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
        metadata["files"][0]["sha256"] = "0" * 64
        metadata_path.write_text(yaml.safe_dump(metadata, sort_keys=False), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            SNAPSHOT.build_manifest(
                self.fixture.root,
                tag="snapshot-2026.10.01",
                commit="c" * 40,
            )

    def test_snapshot_provenance_binds_manifest_and_summary(self) -> None:
        self.fixture.add_canonical("dataset")
        with tempfile.TemporaryDirectory() as directory:
            manifest_path, summary_path, provenance_path = (
                SNAPSHOT.write_release_material(
                    self.fixture.root,
                    tag="snapshot-2026.10.10",
                    commit="a" * 40,
                    output_dir=Path(directory),
                )
            )

            provenance = json.loads(
                provenance_path.read_text(encoding="utf-8")
            )

            self.assertEqual(provenance["schema_version"], 1)
            self.assertEqual(
                provenance["snapshot"],
                {
                    "tag": "snapshot-2026.10.10",
                    "commit": "a" * 40,
                },
            )
            self.assertEqual(
                provenance["artifacts"]["manifest"]["sha256"],
                hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
            )
            self.assertEqual(
                provenance["artifacts"]["summary"]["sha256"],
                hashlib.sha256(summary_path.read_bytes()).hexdigest(),
            )

    def test_snapshot_provenance_matches_public_schema(self) -> None:
        self.fixture.add_canonical("dataset")
        with tempfile.TemporaryDirectory() as directory:
            _, _, provenance_path = SNAPSHOT.write_release_material(
                self.fixture.root,
                tag="snapshot-2026.10.10",
                commit="e" * 40,
                output_dir=Path(directory),
            )

            provenance = json.loads(
                provenance_path.read_text(encoding="utf-8")
            )
            schema = json.loads(
                (
                    Path(__file__).resolve().parents[1]
                    / "schemas"
                    / "snapshot-provenance-v1.schema.json"
                ).read_text(encoding="utf-8")
            )
            jsonschema.Draft202012Validator(schema).validate(provenance)

    def test_snapshot_provenance_records_exact_producer_identity(self) -> None:
        self.fixture.add_canonical("dataset")
        manifest = SNAPSHOT.build_manifest(
            self.fixture.root,
            tag="snapshot-2026.10.10",
            commit="b" * 40,
        )
        manifest_text = (
            json.dumps(
                manifest,
                indent=2,
                ensure_ascii=False,
                sort_keys=True,
            )
            + "\n"
        )
        summary_text = SNAPSHOT.render_summary(manifest)

        provenance = SNAPSHOT.build_snapshot_provenance(
            self.fixture.root,
            manifest=manifest,
            manifest_text=manifest_text,
            summary_text=summary_text,
        )

        self.assertEqual(
            provenance["producer"]["reusable_publisher"]["ref"],
            "6c68c76f3cec5b61552d24aa724fbd3398c33dbd",
        )
        self.assertEqual(
            provenance["interfaces"]["snapshot_manifest_version"],
            manifest["manifest_version"],
        )
        self.assertEqual(
            provenance["interfaces"]["package_version"],
            "0.1.0",
        )
        self.assertEqual(
            provenance["interfaces"]["public_api_version"],
            1,
        )
        self.assertEqual(
            provenance["interfaces"]["static_distribution_version"],
            1,
        )

    def test_snapshot_provenance_contains_only_deterministic_assertions(self) -> None:
        self.fixture.add_canonical("dataset")
        manifest = SNAPSHOT.build_manifest(
            self.fixture.root,
            tag="snapshot-2026.10.10",
            commit="c" * 40,
        )
        manifest_text = json.dumps(
            manifest,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        ) + "\n"
        provenance = SNAPSHOT.build_snapshot_provenance(
            self.fixture.root,
            manifest=manifest,
            manifest_text=manifest_text,
            summary_text=SNAPSHOT.render_summary(manifest),
        )

        self.assertTrue(provenance["assertions"])
        self.assertTrue(
            all(
                item["result"] == "pass"
                for item in provenance["assertions"]
            )
        )
        serialized = json.dumps(provenance, sort_keys=True)
        for forbidden in ("run_id", "timestamp", "actor", "created_at"):
            self.assertNotIn(forbidden, serialized)

    def test_snapshot_provenance_requires_exact_reusable_publisher_ref(self) -> None:
        self.fixture.add_canonical("dataset")
        workflow = (
            self.fixture.root
            / ".github"
            / "workflows"
            / "snapshot-release.yml"
        )
        workflow.write_text(
            "jobs:\n  release:\n"
            "    uses: DiogoRibeiro7/git-actions-collection/"
            ".github/workflows/snapshot-release.yml@v1\n",
            encoding="utf-8",
        )
        manifest = SNAPSHOT.build_manifest(
            self.fixture.root,
            tag="snapshot-2026.10.10",
            commit="d" * 40,
        )
        with self.assertRaisesRegex(
            ValueError,
            "exact reusable snapshot publisher ref not found",
        ):
            SNAPSHOT.build_snapshot_provenance(
                self.fixture.root,
                manifest=manifest,
                manifest_text=json.dumps(manifest),
                summary_text=SNAPSHOT.render_summary(manifest),
            )

    def test_release_material_is_byte_deterministic(self) -> None:
        self.fixture.add_canonical("dataset")
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            first_json, first_md, first_provenance = SNAPSHOT.write_release_material(
                self.fixture.root,
                tag="snapshot-2026.10.01.3",
                commit="d" * 40,
                output_dir=Path(first),
            )
            second_json, second_md, second_provenance = SNAPSHOT.write_release_material(
                self.fixture.root,
                tag="snapshot-2026.10.01.3",
                commit="d" * 40,
                output_dir=Path(second),
            )
            self.assertEqual(first_json.read_bytes(), second_json.read_bytes())
            self.assertEqual(first_md.read_bytes(), second_md.read_bytes())
            self.assertEqual(
                first_provenance.read_bytes(),
                second_provenance.read_bytes(),
            )


if __name__ == "__main__":
    unittest.main()
