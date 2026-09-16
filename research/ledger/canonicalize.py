"""Deterministic canonicalization and hashing for Z-ZOA research runs."""

import hashlib
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union


CANONICALIZATION_VERSION = 1


def canonical_serialize(data: Dict[str, Any]) -> bytes:
    """
    Deterministically serialize a dictionary into UTF-8 JSON bytes.
    Uses sorted keys, fixed separators without whitespace, and strict UTF-8.
    """
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False
    ).encode("utf-8")


def compute_sha256(content: Union[bytes, str]) -> str:
    """Compute standard SHA-256 hexadecimal digest for bytes or string."""
    if isinstance(content, str):
        content = content.encode("utf-8")
    return hashlib.sha256(content).hexdigest()


def compute_file_sha256(file_path: Union[str, Path]) -> str:
    """Compute SHA-256 digest of a local file."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Cannot compute hash: file does not exist: {path}")
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def build_canonical_anchor_manifest(
    run_dir: Union[str, Path],
    stage: str,
    previous_tx_hash: Optional[str] = None,
    schema_version: int = CANONICALIZATION_VERSION,
) -> Dict[str, Any]:
    """
    Construct a deterministic canonical anchor manifest dictionary from a frozen run directory.
    Validates presence of manifest.json, config.yaml, and results.json if present.
    """
    run_path = Path(run_dir)
    manifest_file = run_path / "manifest.json"
    if not manifest_file.exists():
        raise FileNotFoundError(f"Run directory {run_path} missing required 'manifest.json'")

    with open(manifest_file, "r", encoding="utf-8") as f:
        manifest_data = json.load(f)

    run_id = manifest_data.get("run_id", run_path.name)
    git_commit = manifest_data.get("git_commit", "UNKNOWN")
    manifest_sha256 = manifest_data.get("manifest_sha256") or compute_file_sha256(manifest_file)

    # Config hash
    config_file = run_path / "config.yaml"
    if config_file.exists():
        config_sha256 = compute_file_sha256(config_file)
    else:
        # Compute from cosmology and run config in manifest
        config_payload = {
            "cosmology": manifest_data.get("cosmology", {}),
            "random_seed": manifest_data.get("random_seed", 0),
        }
        config_sha256 = compute_sha256(canonical_serialize(config_payload))

    # Dataset manifest hash
    datasets = manifest_data.get("datasets", [])
    datasets_serialized = canonical_serialize({"datasets": datasets})
    dataset_manifest_sha256 = compute_sha256(datasets_serialized)

    # Results manifest hash
    results_file = run_path / "results.json"
    if results_file.exists():
        results_manifest_sha256 = compute_file_sha256(results_file)
    else:
        outputs = manifest_data.get("outputs", {})
        results_manifest_sha256 = compute_sha256(canonical_serialize({"outputs": outputs}))

    canonical_payload: Dict[str, Any] = {
        "schema_version": schema_version,
        "project": "Z-ZOA",
        "run_id": str(run_id),
        "stage": str(stage),
        "git_commit": str(git_commit),
        "manifest_sha256": str(manifest_sha256),
        "config_sha256": str(config_sha256),
        "dataset_manifest_sha256": str(dataset_manifest_sha256),
        "results_manifest_sha256": str(results_manifest_sha256),
        "previous_tx_hash": str(previous_tx_hash) if previous_tx_hash else None,
    }

    return canonical_payload


def compute_anchor_payload_hash(canonical_payload: Dict[str, Any]) -> str:
    """Compute the cryptographic SHA-256 fingerprint from a canonical payload dict."""
    serialized = canonical_serialize(canonical_payload)
    return compute_sha256(serialized)
