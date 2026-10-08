"""Public compatibility/versioning constants for the registry client."""

from __future__ import annotations

from typing import Final

PACKAGE_API_VERSION: Final[int] = 1
STATIC_DISTRIBUTION_VERSION: Final[int] = 1
SUPPORTED_SNAPSHOT_MANIFEST_VERSIONS: Final[tuple[int, ...]] = (1, 2, 3, 4, 5)

__all__ = [
    "PACKAGE_API_VERSION",
    "STATIC_DISTRIBUTION_VERSION",
    "SUPPORTED_SNAPSHOT_MANIFEST_VERSIONS",
]
