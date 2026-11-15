"""Unit and schema validation tests for GA-001 experiment artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from research.experiments.manifest import RunManifest


@pytest.fixture
def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


@pytest.fixture
def ga_run_dir(repo_root: Path) -> Path:
    return repo_root / "runs" / "GA-001"


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def test_ga_freeze_manifest_schema(repo_root: Path, ga_run_dir: Path):
    """Verify GA-001 freeze manifest adheres to Z-ZOA freeze schema and hashes match disk."""
    freeze_path = ga_run_dir / "freeze_manifest.json"
    assert freeze_path.exists(), "GA-001 freeze manifest must exist"

    data = json.loads(freeze_path.read_text(encoding="utf-8"))
    assert data["manifest_type"] == "Z-ZOA_PREDICTION_FREEZE_MANIFEST"
    assert data["run_id"] == "GA-001"
    assert data["status"] == "PREDICTION_FROZEN"
    assert "frozen_at_utc" in data
    assert "git_commit" in data
    assert "manifest_seal_sha256" in data
    assert len(data["manifest_seal_sha256"]) == 64

    # Verify input catalog
    clean_cat_rel = data["train_clean_catalog_path"]
    clean_cat_abs = repo_root / clean_cat_rel
    assert clean_cat_abs.exists(), f"Input catalog {clean_cat_abs} must exist"
    assert sha256_file(clean_cat_abs) == data["train_clean_catalog_sha256"]

    # Verify file hashes match disk
    file_hashes = data["file_hashes"]
    expected_files = [
        "prediction_mean.npy",
        "prediction_sigma.npy",
        "prediction_probability.npy",
        "prediction_velocity_mean.npy",
        "prediction_velocity_sigma.npy",
        "ensemble_meta.json",
        "metrics_spec.json",
        "null_spec.json",
    ]
    for fn in expected_files:
        assert fn in file_hashes, f"{fn} must be sealed in file_hashes"
        fp = ga_run_dir / fn
        assert fp.exists(), f"{fp} must exist on disk"
        assert sha256_file(fp) == file_hashes[fn], f"SHA-256 mismatch for {fn}"


def test_ga_validation_report_schema(ga_run_dir: Path):
    """Verify GA-001 validation report conforms to schema and confirms holdout recovery."""
    report_path = ga_run_dir / "validation_report.json"
    assert report_path.exists(), "validation_report.json must exist in runs/GA-001"

    rep = json.loads(report_path.read_text(encoding="utf-8"))
    assert rep["run_id"] == "GA-001"
    assert rep["holdout_count"] == 477
    assert rep["primary_metric"] == "mean_overdensity_at_holdout"
    assert rep["status"] == "VALIDATION_CONFIRMED"
    assert rep["n_null_realizations"] == 1000

    # Confirmatory significance assertions
    assert rep["effect_size_cohens_d"] > 1.5, "Effect size must exceed 1.5 sigma threshold"
    assert rep["observed_mean_delta"] > rep["null_hypothesis_mean"]
    assert 0.0 <= rep["fraction_in_overdense_voxels"] <= 1.0
    assert 0.0 <= rep["fraction_in_high_prob_voxels"] <= 1.0


def test_ga_run_manifest_schema(ga_run_dir: Path):
    """Verify GA-001 run manifest deserializes into Pydantic RunManifest model."""
    manifest_path = ga_run_dir / "manifest.json"
    assert manifest_path.exists(), "manifest.json must exist in runs/GA-001"

    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest = RunManifest.model_validate(data)
    assert manifest.run_id == "GA-001"
    assert manifest.manifest_sha256 is not None
    assert len(manifest.manifest_sha256) == 64

    # Verify datasets recorded
    ds_ids = {d["dataset_id"]: d for d in manifest.datasets}
    assert "train_clean_ga_combined" in ds_ids
    assert "ga_smgps_477" in ds_ids
    assert ds_ids["ga_smgps_477"]["row_count"] == 477


def test_ga_prediction_arrays_physical_bounds(ga_run_dir: Path):
    """Verify dimensional shapes and physical bounds of GA-001 prediction fields."""
    mean_arr = np.load(ga_run_dir / "prediction_mean.npy")
    sigma_arr = np.load(ga_run_dir / "prediction_sigma.npy")
    prob_arr = np.load(ga_run_dir / "prediction_probability.npy")
    null_arr = np.load(ga_run_dir / "null_distribution_means.npy")

    assert mean_arr.shape == (32, 32, 32)
    assert sigma_arr.shape == (32, 32, 32)
    assert prob_arr.shape == (32, 32, 32)
    assert null_arr.shape == (1000,)

    # Physical scale sanity invariants
    assert np.all(sigma_arr >= 0.0), "Uncertainty sigma must be non-negative"
    assert np.all((prob_arr >= 0.0) & (prob_arr <= 1.0)), "Probabilities must be in [0, 1]"
    assert abs(float(np.mean(mean_arr))) < 0.01, f"Spatial mean density must be ~0, got {np.mean(mean_arr)}"
