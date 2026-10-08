"""Reusable core for the DiogoRibeiro7 data registry.

Installable client core for the DiogoRibeiro7 data registry.

The Git repository remains the source of truth; package reads are deterministic
and offline unless an explicit immutable fetch is requested.
"""

from .api import RegistryClient, RegistryRecord
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
    "RegistryClient",
    "RegistryRecord",
    "DatasetReference",
    "RegistryEntry",
    "RegistryError",
    "fetch_dataset_file",
    "load_registry",
]
