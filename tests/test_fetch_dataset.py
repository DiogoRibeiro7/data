"""Tests for the pinned canonical dataset fetch helper."""

from __future__ import annotations

import hashlib
import http.server
import socketserver
import sys
import tempfile
import threading
import unittest
from functools import partial
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from fetch_dataset import DatasetReference, fetch_dataset_file  # noqa: E402


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler without noisy test logs."""

    def log_message(self, format: str, *args: object) -> None:
        """Suppress request logs."""


class FetchDatasetTests(unittest.TestCase):
    """Test immutable references and checksum enforcement."""

    def test_rejects_branch_name(self) -> None:
        with self.assertRaises(ValueError):
            DatasetReference("DiogoRibeiro7/data", "main", "datasets/x/raw/a.csv", "0" * 64)

    def test_rejects_path_traversal(self) -> None:
        with self.assertRaises(ValueError):
            DatasetReference("DiogoRibeiro7/data", "a" * 40, "../a.csv", "0" * 64)

    def test_existing_verified_file_avoids_network(self) -> None:
        payload = b"a,b\n1,2\n"
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "data.csv"
            output.write_bytes(payload)
            ref = DatasetReference(
                "DiogoRibeiro7/data", "a" * 40, "datasets/x/raw/a.csv",
                hashlib.sha256(payload).hexdigest(),
            )
            result = fetch_dataset_file(ref, output, base_url="http://127.0.0.1:1")
            self.assertEqual(result.read_bytes(), payload)

    def test_download_verifies_checksum(self) -> None:
        payload = b"x,y\n3,4\n"
        with tempfile.TemporaryDirectory() as server_dir, tempfile.TemporaryDirectory() as out_dir:
            nested = Path(server_dir) / "owner" / "repo" / ("a" * 40) / "datasets" / "x" / "raw"
            nested.mkdir(parents=True)
            (nested / "data.csv").write_bytes(payload)
            handler = partial(QuietHandler, directory=server_dir)
            with socketserver.TCPServer(("127.0.0.1", 0), handler) as server:
                port = server.server_address[1]
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                try:
                    ref = DatasetReference(
                        "owner/repo", "a" * 40, "datasets/x/raw/data.csv",
                        hashlib.sha256(payload).hexdigest(),
                    )
                    output = Path(out_dir) / "data.csv"
                    fetch_dataset_file(ref, output, base_url=f"http://127.0.0.1:{port}")
                finally:
                    server.shutdown()
                    thread.join(timeout=5)
            self.assertEqual(output.read_bytes(), payload)


if __name__ == "__main__":
    unittest.main()
