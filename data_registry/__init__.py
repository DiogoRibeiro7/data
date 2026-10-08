"""Reusable core for the DiogoRibeiro7 data registry.

This package is intentionally not yet distributed as an installable project.
Phase 9 first establishes shared importable modules; packaging and public API
versioning are handled by later roadmap issues.
"""

from .core import RegistryEntry, RegistryError, load_registry
from .fetch import DatasetReference, fetch_dataset_file
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
    "CanonicalDataset",
    "ConsumerRelationship",
    "ExternalRecord",
    "LegacyRecord",
    "LifecycleDataset",
    "ProvenanceDebtItem",
    "RegistryModelError",
    "DatasetReference",
    "RegistryEntry",
    "RegistryError",
    "fetch_dataset_file",
    "load_registry",
]
