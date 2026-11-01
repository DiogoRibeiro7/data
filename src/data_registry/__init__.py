"""Reusable core for the DiogoRibeiro7 data registry.

Installable client core for the DiogoRibeiro7 data registry.

The Git repository remains the source of truth; package reads are deterministic
and offline unless an explicit immutable fetch is requested.
"""

from .api import FetchResult, RegistryClient, RegistryRecord
from .archive_verification import (
    ArchiveVerificationError,
    ArchiveVerificationResult,
    verify_archive_bundle,
)
from .compatibility import (
    CURRENT_SNAPSHOT_MANIFEST_VERSION,
    PACKAGE_VERSION,
    PRE_1_DEPRECATION_MIN_MINOR_RELEASES,
    PUBLIC_API_VERSION,
    STATIC_DISTRIBUTION_VERSION,
    SUPPORTED_METADATA_SCHEMA_VERSIONS,
    SUPPORTED_SNAPSHOT_MANIFEST_VERSIONS,
    supports_metadata_schema,
    supports_snapshot_manifest,
)
from .core import RegistryEntry, RegistryError, load_registry
from .fetch import DatasetReference, fetch_dataset_file
from .handoff import HandoffManifest, HandoffObject, build_handoff_manifest
from .handoff_verification import (
    HandoffVerificationError,
    HandoffVerificationResult,
    verify_handoff_manifest,
)
from .release_verification import (
    ReleaseVerificationError,
    ReleaseVerificationResult,
    verify_release_bundle,
)
from .models import (
    CanonicalDataset,
    ConsumerRelationship,
    ExternalRecord,
    LegacyRecord,
    LifecycleDataset,
    ProvenanceDebtItem,
    RegistryModelError,
)

__all__ = [
    "CURRENT_SNAPSHOT_MANIFEST_VERSION",
    "PACKAGE_VERSION",
    "PUBLIC_API_VERSION",
    "SUPPORTED_METADATA_SCHEMA_VERSIONS",
    "supports_metadata_schema",
    "supports_snapshot_manifest",
    "CanonicalDataset",
    "ArchiveVerificationError",
    "ArchiveVerificationResult",
    "verify_archive_bundle",
    "ConsumerRelationship",
    "ExternalRecord",
    "FetchResult",
    "HandoffManifest",
    "HandoffObject",
    "HandoffVerificationError",
    "HandoffVerificationResult",
    "verify_handoff_manifest",
    "LegacyRecord",
    "LifecycleDataset",
    "ProvenanceDebtItem",
    "RegistryModelError",
    "verify_release_bundle",
    "ReleaseVerificationResult",
    "ReleaseVerificationError",
    "PRE_1_DEPRECATION_MIN_MINOR_RELEASES",
    "SUPPORTED_SNAPSHOT_MANIFEST_VERSIONS",
    "STATIC_DISTRIBUTION_VERSION",
    "RegistryClient",
    "RegistryRecord",
    "DatasetReference",
    "RegistryEntry",
    "RegistryError",
    "fetch_dataset_file",
    "build_handoff_manifest",
    "load_registry",
]
