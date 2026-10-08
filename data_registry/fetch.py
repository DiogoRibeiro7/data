"""Immutable canonical dataset fetch primitives."""

from __future__ import annotations

import hashlib
import os
import re
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Final

REPOSITORY_RE: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$"
)
COMMIT_RE: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{64}$")
DEFAULT_REPOSITORY: Final[str] = "DiogoRibeiro7/data"
DEFAULT_RAW_BASE_URL: Final[str] = "https://raw.githubusercontent.com"


@dataclass(frozen=True)
class DatasetReference:
    """Immutable reference to one canonical dataset file."""

    repository: str
    commit: str
    path: str
    sha256: str

    def __post_init__(self) -> None:
        """Validate repository, commit, path and checksum fields."""

        if not REPOSITORY_RE.fullmatch(self.repository):
            raise ValueError("repository must use GitHub owner/name form")
        if not COMMIT_RE.fullmatch(self.commit):
            raise ValueError("commit must be a full 40-character lowercase Git SHA")
        if not SHA256_RE.fullmatch(self.sha256):
            raise ValueError("sha256 must be 64 lowercase hexadecimal characters")
        pure_path = PurePosixPath(self.path)
        if pure_path.is_absolute() or ".." in pure_path.parts or self.path.endswith("/"):
            raise ValueError("path must be a relative repository file path")

    def url(self, *, base_url: str = DEFAULT_RAW_BASE_URL) -> str:
        """Build an immutable raw-content URL."""

        encoded = "/".join(
            urllib.parse.quote(part, safe="")
            for part in PurePosixPath(self.path).parts
        )
        return (
            f"{base_url.rstrip(chr(47))}/"
            f"{self.repository}/{self.commit}/{encoded}"
        )


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest for a local file."""

    if not isinstance(path, Path):
        raise TypeError("path must be pathlib.Path")
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def fetch_dataset_file(
    reference: DatasetReference,
    output: Path,
    *,
    base_url: str = DEFAULT_RAW_BASE_URL,
    timeout_seconds: float = 60.0,
    force: bool = False,
) -> Path:
    """Fetch a canonical file atomically and verify its checksum."""

    if not isinstance(reference, DatasetReference):
        raise TypeError("reference must be DatasetReference")
    if not isinstance(output, Path):
        raise TypeError("output must be pathlib.Path")
    if not isinstance(timeout_seconds, (int, float)) or timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")
    if not isinstance(force, bool):
        raise TypeError("force must be bool")

    if output.is_file() and sha256_file(output) == reference.sha256:
        return output
    if output.exists() and not force:
        raise FileExistsError(
            f"{output} exists with a different checksum; use --force to replace it"
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    temp_path: Path | None = None
    try:
        request = urllib.request.Request(
            reference.url(base_url=base_url),
            headers={"User-Agent": "data-repository-fetch/1"},
        )
        with urllib.request.urlopen(
            request,
            timeout=float(timeout_seconds),
        ) as response:
            with tempfile.NamedTemporaryFile(
                mode="wb",
                dir=output.parent,
                prefix=f".{output.name}.",
                suffix=".tmp",
                delete=False,
            ) as temp_file:
                temp_path = Path(temp_file.name)
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    temp_file.write(chunk)

        actual = sha256_file(temp_path)
        if actual != reference.sha256:
            raise RuntimeError(
                "downloaded checksum mismatch: "
                f"expected {reference.sha256}, got {actual}"
            )
        os.replace(temp_path, output)
        temp_path = None
        return output
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise RuntimeError(
            f"could not fetch {reference.url(base_url=base_url)}"
        ) from exc
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
