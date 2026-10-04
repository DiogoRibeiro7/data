"""Tests for the local data registry CLI."""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import sys
import tempfile
import threading
import unittest
from functools import partial
from http.server import SimpleHTTPRequestHandler
from pathlib import Path
from socketserver import TCPServer

import yaml

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import registry as REGISTRY  # noqa: E402


class QuietHandler(SimpleHTTPRequestHandler):
    """HTTP handler without request log noise."""

    def log_message(self, format: str, *args: object) -> None:
        pass


class RegistryFixture:
    """Build a minimal three-layer registry fixture."""

    def __init__(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "datasets").mkdir()
        (self.root / "external").mkdir()
        (self.root / "legacy").mkdir()

    def add_consumer_graph(self) -> None:
        """Add a deterministic generated consumer dependency graph."""

        consumers = self.root / "consumers"
        consumers.mkdir()
        graph = {
            "schema_version": 1,
            "consumers": {
                "consumer-one": {
                    "repository": "DiogoRibeiro7/consumer-one",
                    "datasets": [
                        {
                            "dataset_id": "dataset-a",
                            "status": "active",
                            "registry_commit": "a" * 40,
                            "path": "datasets/dataset-a/raw/example.csv",
                            "sha256": "b" * 64,
                        },
                        {
                            "dataset_id": "dataset-b",
                            "status": "deprecated",
                            "registry_commit": "c" * 40,
                            "path": "datasets/dataset-b/raw/example.csv",
                            "sha256": "d" * 64,
                        },
                    ],
                },
                "consumer-two": {
                    "repository": "DiogoRibeiro7/consumer-two",
                    "datasets": [
                        {
                            "dataset_id": "dataset-a",
                            "status": "active",
                            "registry_commit": "e" * 40,
                            "path": "datasets/dataset-a/raw/example.csv",
                            "sha256": "f" * 64,
                        }
                    ],
                },
            },
            "datasets": {
                "dataset-a": {
                    "consumers": [
                        {
                            "consumer_id": "consumer-one",
                            "consumer_repository": "DiogoRibeiro7/consumer-one",
                            "status": "active",
                            "registry_commit": "a" * 40,
                            "path": "datasets/dataset-a/raw/example.csv",
                            "sha256": "b" * 64,
                        },
                        {
                            "consumer_id": "consumer-two",
                            "consumer_repository": "DiogoRibeiro7/consumer-two",
                            "status": "active",
                            "registry_commit": "e" * 40,
                            "path": "datasets/dataset-a/raw/example.csv",
                            "sha256": "f" * 64,
                        },
                    ]
                },
                "dataset-b": {
                    "consumers": [
                        {
                            "consumer_id": "consumer-one",
                            "consumer_repository": "DiogoRibeiro7/consumer-one",
                            "status": "deprecated",
                            "registry_commit": "c" * 40,
                            "path": "datasets/dataset-b/raw/example.csv",
                            "sha256": "d" * 64,
                        }
                    ]
                },
            },
        }
        (consumers / "dependency-graph.json").write_text(
            json.dumps(graph, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )


    def close(self) -> None:
        self.temp.cleanup()

    def add_canonical(self, slug: str, data: bytes = b"a,b\n1,2\n") -> str:
        dataset = self.root / "datasets" / slug
        raw = dataset / "raw"
        raw.mkdir(parents=True)
        (dataset / "README.md").write_text(f"# {slug}\n", encoding="utf-8")
        path = raw / "example.csv"
        path.write_bytes(data)
        sha = hashlib.sha256(data).hexdigest()
        metadata = {
            "schema_version": 1,
            "id": slug,
            "title": f"Canonical {slug}",
            "description": "Climate and testing example.",
            "domain": ["climate", "testing"],
            "source": {
                "publisher": "Canonical Publisher",
                "url": "https://example.test/canonical",
                "retrieved_at": "2026-09-30",
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
                "sha256": sha,
            }],
            "lineage": [],
        }
        (dataset / "metadata.yaml").write_text(
            yaml.safe_dump(metadata, sort_keys=False), encoding="utf-8"
        )
        return sha

    def add_external(self, slug: str) -> None:
        source = self.root / "external" / slug
        source.mkdir()
        (source / "README.md").write_text(f"# {slug}\n", encoding="utf-8")
        metadata = {
            "schema_version": 1,
            "status": "external-reference",
            "id": slug,
            "title": f"External {slug}",
            "publisher": "Climate Publisher",
            "source_url": "https://example.test/external",
            "storage": "authoritative-upstream",
        }
        (source / "metadata.yaml").write_text(
            yaml.safe_dump(metadata, sort_keys=False), encoding="utf-8"
        )

    def add_legacy(self, slug: str) -> None:
        group = self.root / "legacy" / slug
        raw = group / "raw"
        raw.mkdir(parents=True)
        payload = b"x\n1\n"
        path = raw / "legacy.csv"
        path.write_bytes(payload)
        (group / "README.md").write_text(f"# {slug}\n", encoding="utf-8")
        header = f"blob {len(payload)}\0".encode("ascii")
        git_sha = hashlib.sha1(header + payload, usedforsecurity=False).hexdigest()
        metadata = {
            "schema_version": 0,
            "status": "legacy-quarantine",
            "id": slug,
            "title": f"Legacy {slug}",
            "source": {"publisher": "unknown", "url": None},
            "license": {"name": "unknown", "redistribution": "unknown"},
            "files": [{
                "original_path": "legacy.csv",
                "path": "raw/legacy.csv",
                "size_bytes": len(payload),
                "git_blob_sha": git_sha,
            }],
        }
        (group / "metadata.yaml").write_text(
            yaml.safe_dump(metadata, sort_keys=False), encoding="utf-8"
        )


class RegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = RegistryFixture()

    def tearDown(self) -> None:
        self.fixture.close()

    def test_load_and_search_across_layers(self) -> None:
        self.fixture.add_canonical("weather-data")
        self.fixture.add_external("climate-source")
        self.fixture.add_legacy("old-weather")
        entries = REGISTRY.load_registry(self.fixture.root)
        self.assertEqual([entry.layer for entry in entries], ["canonical", "external", "legacy"])
        climate = REGISTRY.search_entries(entries, "climate")
        self.assertEqual({entry.id for entry in climate}, {"weather-data", "climate-source"})

    def test_find_entry_requires_layer_for_duplicate_id(self) -> None:
        self.fixture.add_canonical("same-id")
        self.fixture.add_external("same-id")
        entries = REGISTRY.load_registry(self.fixture.root)
        with self.assertRaisesRegex(REGISTRY.RegistryError, "ambiguous"):
            REGISTRY.find_entry(entries, "same-id")
        found = REGISTRY.find_entry(entries, "same-id", layer="external")
        self.assertEqual(found.layer, "external")

    def test_json_list_output_is_machine_readable(self) -> None:
        self.fixture.add_external("source")
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            code = REGISTRY.main(["--root", str(self.fixture.root), "list", "--json"])
        self.assertEqual(code, 0)
        payload = json.loads(stream.getvalue())
        self.assertEqual(payload[0]["id"], "source")

    def test_verify_valid_legacy_entry(self) -> None:
        self.fixture.add_legacy("legacy-data")
        entry = REGISTRY.find_entry(REGISTRY.load_registry(self.fixture.root), "legacy-data")
        self.assertEqual(REGISTRY.verify_entry(self.fixture.root, entry), [])

    def test_consumers_command_lists_registered_consumers_as_json(self) -> None:
        self.fixture.add_consumer_graph()
        stream = io.StringIO()

        with contextlib.redirect_stdout(stream):
            code = REGISTRY.main(
                ["--root", str(self.fixture.root), "consumers", "--json"]
            )

        self.assertEqual(code, 0)
        payload = json.loads(stream.getvalue())
        self.assertEqual(
            [item["consumer_id"] for item in payload],
            ["consumer-one", "consumer-two"],
        )
        self.assertEqual(payload[0]["dataset_count"], 2)

    def test_consumer_command_shows_one_consumer(self) -> None:
        self.fixture.add_consumer_graph()
        stream = io.StringIO()

        with contextlib.redirect_stdout(stream):
            code = REGISTRY.main(
                ["--root", str(self.fixture.root), "consumer", "consumer-one", "--json"]
            )

        self.assertEqual(code, 0)
        payload = json.loads(stream.getvalue())
        self.assertEqual(payload["consumer_id"], "consumer-one")
        self.assertEqual(
            [item["dataset_id"] for item in payload["datasets"]],
            ["dataset-a", "dataset-b"],
        )

    def test_used_by_returns_reverse_dataset_consumers(self) -> None:
        self.fixture.add_consumer_graph()
        stream = io.StringIO()

        with contextlib.redirect_stdout(stream):
            code = REGISTRY.main(
                ["--root", str(self.fixture.root), "used-by", "dataset-a", "--json"]
            )

        self.assertEqual(code, 0)
        payload = json.loads(stream.getvalue())
        self.assertEqual(
            [item["consumer_id"] for item in payload],
            ["consumer-one", "consumer-two"],
        )

    def test_uses_returns_consumer_datasets(self) -> None:
        self.fixture.add_consumer_graph()
        stream = io.StringIO()

        with contextlib.redirect_stdout(stream):
            code = REGISTRY.main(
                ["--root", str(self.fixture.root), "uses", "consumer-one", "--json"]
            )

        self.assertEqual(code, 0)
        payload = json.loads(stream.getvalue())
        self.assertEqual(
            [item["dataset_id"] for item in payload],
            ["dataset-a", "dataset-b"],
        )

    def test_unknown_consumer_id_is_a_clear_error(self) -> None:
        self.fixture.add_consumer_graph()
        stderr = io.StringIO()

        with contextlib.redirect_stderr(stderr):
            code = REGISTRY.main(
                ["--root", str(self.fixture.root), "consumer", "missing"]
            )

        self.assertEqual(code, 1)
        self.assertIn("unknown consumer id 'missing'", stderr.getvalue())

    def test_unknown_used_by_dataset_is_a_clear_error(self) -> None:
        self.fixture.add_consumer_graph()
        stderr = io.StringIO()

        with contextlib.redirect_stderr(stderr):
            code = REGISTRY.main(
                ["--root", str(self.fixture.root), "used-by", "missing"]
            )

        self.assertEqual(code, 1)
        self.assertIn("unknown consumer dataset id 'missing'", stderr.getvalue())

    def test_consumer_human_output_is_tabular(self) -> None:
        self.fixture.add_consumer_graph()
        stream = io.StringIO()

        with contextlib.redirect_stdout(stream):
            code = REGISTRY.main(
                ["--root", str(self.fixture.root), "consumers"]
            )

        self.assertEqual(code, 0)
        rendered = stream.getvalue()
        self.assertIn("CONSUMER", rendered)
        self.assertIn("consumer-one", rendered)
        self.assertIn("dataset-a, dataset-b", rendered)


    def test_fetch_uses_metadata_checksum_and_exact_commit(self) -> None:
        payload = b"a,b\n1,2\n"
        checksum = self.fixture.add_canonical("dataset", payload)
        entry = REGISTRY.find_entry(REGISTRY.load_registry(self.fixture.root), "dataset")

        commit = "a" * 40
        with tempfile.TemporaryDirectory() as server_dir, tempfile.TemporaryDirectory() as out_dir:
            source = (
                Path(server_dir) / "owner" / "repo" / commit / "datasets" / "dataset" / "raw"
            )
            source.mkdir(parents=True)
            (source / "example.csv").write_bytes(payload)
            handler = partial(QuietHandler, directory=server_dir)
            with TCPServer(("127.0.0.1", 0), handler) as server:
                port = server.server_address[1]
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                try:
                    output = Path(out_dir) / "example.csv"
                    result, repo_path, returned_sha = REGISTRY.fetch_entry_file(
                        entry,
                        "raw/example.csv",
                        commit=commit,
                        output=output,
                        repository="owner/repo",
                        base_url=f"http://127.0.0.1:{port}",
                    )
                    self.assertEqual(result.read_bytes(), payload)
                    self.assertEqual(returned_sha, checksum)
                    self.assertEqual(repo_path, "datasets/dataset/raw/example.csv")
                finally:
                    server.shutdown()
                    thread.join(timeout=5)

    def test_fetch_rejects_branch_name(self) -> None:
        self.fixture.add_canonical("dataset")
        entry = REGISTRY.find_entry(REGISTRY.load_registry(self.fixture.root), "dataset")
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(REGISTRY.RegistryError, "40-character"):
                REGISTRY.fetch_entry_file(
                    entry,
                    "raw/example.csv",
                    commit="main",
                    output=Path(directory) / "out.csv",
                )


if __name__ == "__main__":
    unittest.main()
