"""Catalogs module for Z-ZOA."""

from research.catalogs.schema import DatasetMetadata, DatasetRole
from research.catalogs.loader import (
    ChecksumMismatchError,
    compute_file_sha256,
    load_dataset_table,
)
from research.catalogs.registry import CatalogRegistry
from research.catalogs.decontaminate import cross_match_and_decontaminate

__all__ = [
    "DatasetMetadata",
    "DatasetRole",
    "ChecksumMismatchError",
    "compute_file_sha256",
    "load_dataset_table",
    "CatalogRegistry",
    "cross_match_and_decontaminate",
]
