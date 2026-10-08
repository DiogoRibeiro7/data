"""Tests for packaged checksum-verified registry fetch."""

from __future__ import annotations

import hashlib
import http.server
import socketserver
import tempfile
import threading
import unittest
from functools import partial
from pathlib import Path
from unittest.mock import patch

import yaml

from data_registry import FetchResult, RegistryClient
from data_registry.core import RegistryError


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler without test log noise."""

    def log_message(self, format: str, *args: object) -> None:
        """Suppress request logs."""


class RegistryFetchApiTests(unittest.TestCase):
    """Exercise immutable fetch through the packaged client API."""

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        dataset = self.root / "datasets" / "example"
        raw = dataset / "raw"
        raw.mkdir(parents=True)
        payload = b"a,b\n1,2\n"
        self.payload = payload
        self.sha256 = hashlib.sha256(payload).hexdigest()
        metadata = {
            "schema_version": 1,
            "id": "example",
            "title": "Example",
            "description": "Fixture",
            "domain": ["testing"],
            "source": {
                "publisher": "Fixture",
                "url": "https://example.test/data",
                "retrieved_at": "2026-10-08",
                "snapshot": "v1",
            },
            "license": {
                "name": "CC0-1.0",
                "url": "https://creativecommons.org/publicdomain/zero/1.0/",
                "redistribution": "allowed",
            },
            "citation": None,
            "files": [
                {
                    "path": "raw/example.csv",
                    "role": "raw",
                    "format": "csv",
                    "sha256": self.sha256,
                }
            ],
            "lineage": [],
        }
        (dataset / "metadata.yaml").write_text(
            yaml.safe_dump(metadata, sort_keys=False),
            encoding="utf-8",
        )
        self.client = RegistryClient(self.root)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_branch_name_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(RegistryError, "40-character"):
                self.client.fetch(
                    "example",
                    "raw/example.csv",
                    commit="main",
                    output=Path(directory) / "example.csv",
                )

    def test_unknown_canonical_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(RegistryError, "not declared in metadata"):
                self.client.fetch(
                    "example",
                    "raw/missing.csv",
                    commit="a" * 40,
                    output=Path(directory) / "missing.csv",
                )

    def test_verified_local_copy_avoids_network(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "example.csv"
            output.write_bytes(self.payload)

            with patch(
                "urllib.request.urlopen",
                side_effect=AssertionError("network should not be used"),
            ):
                result = self.client.fetch(
                    "example",
                    "raw/example.csv",
                    commit="a" * 40,
                    output=output,
                    base_url="http://127.0.0.1:1",
                )

            self.assertIsInstance(result, FetchResult)
            self.assertEqual(result.sha256, self.sha256)
            self.assertEqual(result.path, "datasets/example/raw/example.csv")
            self.assertEqual(result.output.read_bytes(), self.payload)

    def test_download_verifies_registry_checksum(self) -> None:
        commit = "a" * 40
        with tempfile.TemporaryDirectory() as server_dir, tempfile.TemporaryDirectory() as out_dir:
            source = (
                Path(server_dir)
                / "owner"
                / "repo"
                / commit
                / "datasets"
                / "example"
                / "raw"
            )
            source.mkdir(parents=True)
            (source / "example.csv").write_bytes(self.payload)

            handler = partial(QuietHandler, directory=server_dir)
            with socketserver.TCPServer(("127.0.0.1", 0), handler) as server:
                port = server.server_address[1]
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                try:
                    output = Path(out_dir) / "example.csv"
                    result = self.client.fetch(
                        "example",
                        "raw/example.csv",
                        commit=commit,
                        output=output,
                        repository="owner/repo",
                        base_url=f"http://127.0.0.1:{port}",
                    )
                finally:
                    server.shutdown()
                    thread.join(timeout=5)

            self.assertEqual(result.output.read_bytes(), self.payload)
            self.assertEqual(result.sha256, self.sha256)
            self.assertEqual(result.commit, commit)
            self.assertEqual(result.repository, "owner/repo")

    def test_mismatched_existing_file_requires_force(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "example.csv"
            output.write_bytes(b"stale\n")

            with self.assertRaisesRegex(RegistryError, "use --force"):
                self.client.fetch(
                    "example",
                    "raw/example.csv",
                    commit="a" * 40,
                    output=output,
                    base_url="http://127.0.0.1:1",
                )

            self.assertEqual(output.read_bytes(), b"stale\n")

    def test_force_replaces_mismatched_existing_file_after_verification(self) -> None:
        commit = "c" * 40
        with tempfile.TemporaryDirectory() as server_dir, tempfile.TemporaryDirectory() as out_dir:
            source = (
                Path(server_dir)
                / "owner"
                / "repo"
                / commit
                / "datasets"
                / "example"
                / "raw"
            )
            source.mkdir(parents=True)
            (source / "example.csv").write_bytes(self.payload)

            output = Path(out_dir) / "example.csv"
            output.write_bytes(b"stale\n")

            handler = partial(QuietHandler, directory=server_dir)
            with socketserver.TCPServer(("127.0.0.1", 0), handler) as server:
                port = server.server_address[1]
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                try:
                    result = self.client.fetch(
                        "example",
                        "raw/example.csv",
                        commit=commit,
                        output=output,
                        repository="owner/repo",
                        base_url=f"http://127.0.0.1:{port}",
                        force=True,
                    )
                finally:
                    server.shutdown()
                    thread.join(timeout=5)

            self.assertEqual(result.output.read_bytes(), self.payload)

    def test_checksum_mismatch_is_fatal(self) -> None:
        commit = "b" * 40
        bad_payload = b"wrong bytes\n"

        with tempfile.TemporaryDirectory() as server_dir, tempfile.TemporaryDirectory() as out_dir:
            source = (
                Path(server_dir)
                / "owner"
                / "repo"
                / commit
                / "datasets"
                / "example"
                / "raw"
            )
            source.mkdir(parents=True)
            (source / "example.csv").write_bytes(bad_payload)

            handler = partial(QuietHandler, directory=server_dir)
            with socketserver.TCPServer(("127.0.0.1", 0), handler) as server:
                port = server.server_address[1]
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                try:
                    output = Path(out_dir) / "example.csv"
                    with self.assertRaisesRegex(
                        RegistryError,
                        "downloaded checksum mismatch",
                    ):
                        self.client.fetch(
                            "example",
                            "raw/example.csv",
                            commit=commit,
                            output=output,
                            repository="owner/repo",
                            base_url=f"http://127.0.0.1:{port}",
                        )
                    self.assertFalse(output.exists())
                finally:
                    server.shutdown()
                    thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
