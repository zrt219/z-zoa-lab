"""Dataset loader with cryptographic checksum verification."""

import hashlib
import os
from pathlib import Path
from typing import Union
import polars as pl

from research.catalogs.schema import DatasetMetadata


class ChecksumMismatchError(ValueError):
    """Raised when file on disk does not match registered SHA-256."""
    pass


def compute_file_sha256(file_path: Union[str, Path]) -> str:
    """Compute cryptographic SHA-256 hash of a file on disk."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def load_dataset_table(
    metadata: DatasetMetadata,
    base_dir: Union[str, Path] = "."
) -> pl.DataFrame:
    """
    Load dataset table into Polars DataFrame after verifying SHA-256 integrity.
    Never silently modifies raw data.
    """
    path = Path(base_dir) / metadata.file_path
    if not path.exists():
        raise FileNotFoundError(f"Dataset file not found at path: '{path}'")

    actual_sha = compute_file_sha256(path)
    if actual_sha.lower() != metadata.sha256.lower():
        raise ChecksumMismatchError(
            f"Integrity check failed for dataset '{metadata.dataset_id}'. "
            f"Expected SHA-256 '{metadata.sha256}', but computed '{actual_sha}'."
        )

    # Read based on suffix
    suffix = path.suffix.lower()
    if suffix == ".parquet":
        df = pl.read_parquet(path)
    elif suffix in (".csv", ".txt"):
        df = pl.read_csv(path)
    elif suffix == ".json":
        df = pl.read_json(path)
    else:
        raise ValueError(f"Unsupported file format '{suffix}' for dataset '{metadata.dataset_id}'.")

    return df
