"""Tests for checksum-verified fetch through RegistryClient."""

from __future__ import annotations

import hashlib
import http.server
import socketserver
import tempfile
import threading
import unittest
from functools import partial
from pathlib import Path

import yaml

from data_registry import FetchResult, RegistryClient, RegistryError


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler without noisy test output."""

    def log_message(self, format: str, *args: object) -> None:
        """Suppress request logs."""


class RegistryClientFetchTests(unittest.TestCase):
    """Exercise immutable fetch through the packaged client API."""

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.payload = b"a,b\n1,2\n"
        self.checksum = hashlib.sha256(self.payload).hexdigest()
        dataset = self.root / "datasets" / "example"
        (dataset / "raw").mkdir(parents=True)
        metadata = {
            "schema_version": 1,
            "id": "example",
            "title": "Example",
            "description": "Fetch fixture.",
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
                    "sha256": self.checksum,
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

    def serve(self, payload: bytes):
        """Create a local immutable raw-content fixture."""

        server_temp = tempfile.TemporaryDirectory()
        server_root = Path(server_temp.name)
        commit = "a" * 40
        source = (
            server_root
            / "owner"
            / "repo"
            / commit
            / "datasets"
            / "example"
            / "raw"
        )
        source.mkdir(parents=True)
        (source / "example.csv").write_bytes(payload)

        handler = partial(QuietHandler, directory=server_root)
        server = socketserver.TCPServer(("127.0.0.1", 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        return server_temp, server, thread, commit

    def test_fetch_rejects_floating_commit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(RegistryError, "40-character"):
                self.client.fetch(
                    "example",
                    "raw/example.csv",
                    commit="main",
                    output=Path(directory) / "example.csv",
                )

    def test_fetch_downloads_and_verifies_metadata_checksum(self) -> None:
        server_temp, server, thread, commit = self.serve(self.payload)
        try:
            with tempfile.TemporaryDirectory() as directory:
                result = self.client.fetch(
                    "example",
                    "raw/example.csv",
                    commit=commit,
                    output=Path(directory) / "example.csv",
                    repository="owner/repo",
                    base_url=f"http://127.0.0.1:{server.server_address[1]}",
                )

                self.assertIsInstance(result, FetchResult)
                self.assertEqual(result.dataset_id, "example")
                self.assertEqual(result.commit, commit)
                self.assertEqual(
                    result.path,
                    "datasets/example/raw/example.csv",
                )
                self.assertEqual(result.sha256, self.checksum)
                self.assertEqual(result.output.read_bytes(), self.payload)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
            server_temp.cleanup()

    def test_fetch_checksum_mismatch_is_fatal(self) -> None:
        server_temp, server, thread, commit = self.serve(b"wrong bytes\n")
        try:
            with tempfile.TemporaryDirectory() as directory:
                output = Path(directory) / "example.csv"
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
                        base_url=f"http://127.0.0.1:{server.server_address[1]}",
                    )
                self.assertFalse(output.exists())
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
            server_temp.cleanup()

    def test_verified_local_copy_satisfies_offline_rerun(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "example.csv"
            output.write_bytes(self.payload)

            result = self.client.fetch(
                "example",
                "raw/example.csv",
                commit="b" * 40,
                output=output,
                repository="owner/repo",
                base_url="http://127.0.0.1:1",
            )

            self.assertEqual(result.output, output)
            self.assertEqual(result.output.read_bytes(), self.payload)


if __name__ == "__main__":
    unittest.main()
