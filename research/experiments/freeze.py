"""Formal freeze protocol and manifest generator for Z-ZOA (Prompt 12).

Locks down the prediction ensemble, input hashes, code commits, config,
metrics spec, and null-hypothesis specifications before out-of-sample validation.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def get_git_commit(repo_root: Path) -> str:
    try:
        res = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        )
        return res.stdout.strip()
    except Exception:
        return "UNKNOWN_GIT_COMMIT"


def freeze_prediction(repo_root: Path, run_id: str = "VELA-001") -> Dict[str, Any]:
    runs_dir = repo_root / "runs" / run_id
    if not runs_dir.exists():
        raise FileNotFoundError(f"Run directory not found: {runs_dir}")

    # 1. Define Metrics Spec
    metrics_spec = {
        "spec_version": "1.0",
        "primary_metric": "mean_overdensity_at_holdout",
        "description": "Mean reconstructed density contrast delta evaluated at verified out-of-sample galaxy locations",
        "secondary_metrics": [
            "fraction_in_overdense_voxels_delta_gt_0",
            "fraction_in_high_prob_voxels_p_gt_0_5",
            "spatial_cross_correlation_r",
            "null_hypothesis_empirical_p_value",
            "effect_size_cohens_d",
        ],
        "null_samples_count": 1000,
        "significance_threshold_alpha": 0.001,
    }
    with (runs_dir / "metrics_spec.json").open("w", encoding="utf-8") as f:
        json.dump(metrics_spec, f, indent=2)

    # 2. Define Null Generation Spec
    null_spec = {
        "spec_version": "1.0",
        "survey_footprint": "VELA_SMGPS",
        "bounds": {
            "l_min_deg": 260.0,
            "l_max_deg": 290.0,
            "b_min_deg": -2.0,
            "b_max_deg": 1.0,
            "cz_min_kms": 0.0,
            "cz_max_kms": 25000.0,
        },
        "selection_weight_model": "linear_distance_falloff",
        "null_realizations": 1000,
        "seed": 20240915,
        "condition": "Holdout coordinates and counts matched; drawn strictly from footprint under sensitivity weight.",
    }
    with (runs_dir / "null_spec.json").open("w", encoding="utf-8") as f:
        json.dump(null_spec, f, indent=2)

    # 3. Compute Checksums of All Run Artifacts
    target_files = [
        "prediction_mean.npy",
        "prediction_sigma.npy",
        "prediction_probability.npy",
        "prediction_velocity_mean.npy",
        "prediction_velocity_sigma.npy",
        "ensemble_meta.json",
        "metrics_spec.json",
        "null_spec.json",
    ]

    file_hashes: Dict[str, str] = {}
    checksum_lines = []
    for fn in target_files:
        fp = runs_dir / fn
        if fp.exists():
            h = sha256_file(fp)
            file_hashes[fn] = h
            checksum_lines.append(f"{h}  {fn}")

    with (runs_dir / "checksums.sha256").open("w", encoding="utf-8") as f:
        f.write("\n".join(checksum_lines) + "\n")

    # 4. Input clean dataset hash
    clean_catalog_path = repo_root / "datasets" / "processed" / "TRAIN_CLEAN" / "train_clean_combined.parquet"
    train_clean_hash = sha256_file(clean_catalog_path) if clean_catalog_path.exists() else "NONE"

    # 5. Build Freeze Manifest
    freeze_manifest = {
        "manifest_type": "Z-ZOA_PREDICTION_FREEZE_MANIFEST",
        "run_id": run_id,
        "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": get_git_commit(repo_root),
        "python_version": sys.version,
        "train_clean_catalog_path": str(clean_catalog_path.relative_to(repo_root)).replace("\\", "/"),
        "train_clean_catalog_sha256": train_clean_hash,
        "file_hashes": file_hashes,
        "metrics_spec_sha256": file_hashes.get("metrics_spec.json"),
        "null_spec_sha256": file_hashes.get("null_spec.json"),
        "status": "PREDICTION_FROZEN",
    }

    manifest_json = runs_dir / "freeze_manifest.json"
    with manifest_json.open("w", encoding="utf-8") as f:
        json.dump(freeze_manifest, f, indent=2)

    # Compute sealing hash of the manifest itself
    seal_hash = sha256_file(manifest_json)
    freeze_manifest["manifest_seal_sha256"] = seal_hash
    with manifest_json.open("w", encoding="utf-8") as f:
        json.dump(freeze_manifest, f, indent=2)

    print("=" * 60)
    print("PREDICTION FROZEN — VALIDATION MAY BEGIN")
    print(f"Run ID:        {run_id}")
    print(f"Manifest:      {manifest_json}")
    print(f"Seal SHA-256:  {seal_hash}")
    print("=" * 60)

    return freeze_manifest


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parent.parent.parent
    freeze_prediction(repo_root)
