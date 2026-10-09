"""Public compatibility/versioning constants for the registry client."""

from __future__ import annotations

from typing import Final

PACKAGE_VERSION: Final[str] = "0.1.0"
PUBLIC_API_VERSION: Final[int] = 1
STATIC_DISTRIBUTION_VERSION: Final[int] = 1
CURRENT_SNAPSHOT_MANIFEST_VERSION: Final[int] = 6
SUPPORTED_SNAPSHOT_MANIFEST_VERSIONS: Final[tuple[int, ...]] = (1, 2, 3, 4, 5, 6)
SUPPORTED_METADATA_SCHEMA_VERSIONS: Final[dict[str, tuple[int, ...]]] = {
    "canonical": (1,),
    "consumer": (1,),
    "external": (1,),
    "legacy": (0,),
}
PRE_1_DEPRECATION_MIN_MINOR_RELEASES: Final[int] = 1


def supports_snapshot_manifest(version: int) -> bool:
    """Return whether the client policy supports one snapshot manifest version."""

    return version in SUPPORTED_SNAPSHOT_MANIFEST_VERSIONS


def supports_metadata_schema(layer: str, version: int) -> bool:
    """Return whether the client policy supports one metadata schema version."""

    return version in SUPPORTED_METADATA_SCHEMA_VERSIONS.get(layer, ())


__all__ = [
    "CURRENT_SNAPSHOT_MANIFEST_VERSION",
    "PACKAGE_VERSION",
    "PRE_1_DEPRECATION_MIN_MINOR_RELEASES",
    "PUBLIC_API_VERSION",
    "STATIC_DISTRIBUTION_VERSION",
    "SUPPORTED_METADATA_SCHEMA_VERSIONS",
    "SUPPORTED_SNAPSHOT_MANIFEST_VERSIONS",
    "supports_metadata_schema",
    "supports_snapshot_manifest",
]
