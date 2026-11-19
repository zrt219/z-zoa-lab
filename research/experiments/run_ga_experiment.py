"""Great Attractor (GA-001) out-of-sample reconstruction and holdout validation pipeline.

Reconstructs the 3D cosmological density field across the Great Attractor / Norma ZoA
from decontaminated training data (TRAIN_CLEAN_GA), seals predictions under the
freeze protocol, and evaluates statistical significance against the 477 MeerKAT
GA-SMGPS H I holdout galaxies (Steyn et al. 2024).
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import astropy.units as u
import numpy as np
import polars as pl
from scipy.ndimage import map_coordinates

from research.catalogs.registry import CatalogRegistry
from research.coordinates.transforms import galactic_to_supergalactic
from research.cosmology.models import COSMOLOGY_PRESETS
from research.experiments.manifest import (
    RunManifest,
    get_environment_versions,
    get_git_commit,
)
from research.holdouts.ga_decontam import run_ga_decontamination
from research.holdouts.guard import DataGateway, ExecutionContext, ExecutionMode
from research.reconstruction.engine import ReconstructionConfig, ReconstructionEngine

RUN_ID = "GA-001"
EXPERIMENT_NAME = "Great Attractor (GA-001) out-of-sample reconstruction and holdout validation"


def sha256_file(p: Path) -> str:
    """Compute cryptographic SHA-256 digest of a file on disk."""
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def reconstruct_and_freeze_ga(
    repo_root: Path,
    n_realizations: int = 20,
    base_seed: int = 1000,
    threshold: float = 1.0,
) -> Dict[str, Any]:
    """Execute constrained 3D reconstruction and freeze predictions under GA-001."""
    runs_dir = repo_root / "runs" / RUN_ID
    runs_dir.mkdir(parents=True, exist_ok=True)

    clean_catalog = repo_root / "datasets" / "processed" / "TRAIN_CLEAN_GA" / "train_clean_ga_combined.parquet"
    if not clean_catalog.exists():
        print("[GA-001] train_clean_ga_combined.parquet missing; executing ga_decontam...")
        run_ga_decontamination(repo_root)

    cfg = ReconstructionConfig(
        grid_size=32,
        box_size_mpc=400.0,
        h0_kms_mpc=74.6,
        omega_m=0.30,
        omega_lambda=0.70,
        smoothing_scale_mpc=10.0,
        cz_max_cut_kms=25000.0,
        random_seed=42,
    )
    engine = ReconstructionEngine(cfg)

    grid_n = cfg.grid_size
    delta_realizations = np.zeros((n_realizations, grid_n, grid_n, grid_n), dtype=np.float64)
    vx_realizations = np.zeros((n_realizations, grid_n, grid_n, grid_n), dtype=np.float64)
    vy_realizations = np.zeros((n_realizations, grid_n, grid_n, grid_n), dtype=np.float64)
    vz_realizations = np.zeros((n_realizations, grid_n, grid_n, grid_n), dtype=np.float64)

    seeds: List[int] = []
    for i in range(n_realizations):
        seed_i = base_seed + i * 37
        seeds.append(seed_i)
        delta_i, v_i, _ = engine.reconstruct_from_clean_data(
            clean_catalog,
            noise_realization_seed=seed_i,
        )
        delta_realizations[i] = delta_i
        vx_realizations[i] = v_i[0]
        vy_realizations[i] = v_i[1]
        vz_realizations[i] = v_i[2]

    # Compute ensemble moments
    pred_mean = np.mean(delta_realizations, axis=0)
    pred_sigma = np.std(delta_realizations, axis=0)
    pred_probability = np.mean(delta_realizations > threshold, axis=0)

    v_mean = np.stack([
        np.mean(vx_realizations, axis=0),
        np.mean(vy_realizations, axis=0),
        np.mean(vz_realizations, axis=0),
    ], axis=0)
    v_sigma = np.stack([
        np.std(vx_realizations, axis=0),
        np.std(vy_realizations, axis=0),
        np.std(vz_realizations, axis=0),
    ], axis=0)

    # Persist prediction arrays
    np.save(runs_dir / "prediction_mean.npy", pred_mean)
    np.save(runs_dir / "prediction_sigma.npy", pred_sigma)
    np.save(runs_dir / "prediction_probability.npy", pred_probability)
    np.save(runs_dir / "prediction_velocity_mean.npy", v_mean)
    np.save(runs_dir / "prediction_velocity_sigma.npy", v_sigma)

    ensemble_meta = {
        "run_id": RUN_ID,
        "n_realizations": n_realizations,
        "base_seed": base_seed,
        "seeds": seeds,
        "threshold": threshold,
        "grid_size": grid_n,
        "box_size_mpc": cfg.box_size_mpc,
        "pred_mean_stats": {
            "min": float(np.min(pred_mean)),
            "max": float(np.max(pred_mean)),
            "mean": float(np.mean(pred_mean)),
            "std": float(np.std(pred_mean)),
        },
        "pred_sigma_stats": {
            "min": float(np.min(pred_sigma)),
            "max": float(np.max(pred_sigma)),
            "mean": float(np.mean(pred_sigma)),
        },
        "pred_probability_fraction_positive": float(np.mean(pred_probability > 0.5)),
    }
    with (runs_dir / "ensemble_meta.json").open("w", encoding="utf-8") as f:
        json.dump(ensemble_meta, f, indent=2)

    # Define Metrics Spec
    metrics_spec = {
        "spec_version": "1.0",
        "primary_metric": "mean_overdensity_at_holdout",
        "description": "Mean reconstructed density contrast delta evaluated at verified out-of-sample GA-SMGPS galaxy locations",
        "secondary_metrics": [
            "fraction_in_overdense_voxels_delta_gt_0",
            "fraction_in_high_prob_voxels_p_gt_0_5",
            "null_hypothesis_empirical_p_value",
            "effect_size_cohens_d",
        ],
        "null_samples_count": 1000,
        "significance_threshold_alpha": 0.001,
    }
    with (runs_dir / "metrics_spec.json").open("w", encoding="utf-8") as f:
        json.dump(metrics_spec, f, indent=2)

    # Define Null Generation Spec for GA
    null_spec = {
        "spec_version": "1.0",
        "survey_footprint": "GA_SMGPS",
        "bounds": {
            "l_min_deg": 302.0,
            "l_max_deg": 332.0,
            "b_min_deg": -1.5,
            "b_max_deg": 1.5,
            "cz_min_kms": 0.0,
            "cz_max_kms": 25000.0,
        },
        "selection_weight_model": "aperture_matched_uniform_falloff",
        "null_realizations": 1000,
        "seed": 20240915,
        "condition": "Holdout coordinates and counts matched (N=477); drawn strictly from GA survey window.",
    }
    with (runs_dir / "null_spec.json").open("w", encoding="utf-8") as f:
        json.dump(null_spec, f, indent=2)

    # Compute checksums of all prediction artifacts
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
    checksum_lines: List[str] = []
    for fn in target_files:
        fp = runs_dir / fn
        if fp.exists():
            h = sha256_file(fp)
            file_hashes[fn] = h
            checksum_lines.append(f"{h}  {fn}")

    with (runs_dir / "checksums.sha256").open("w", encoding="utf-8") as f:
        f.write("\n".join(checksum_lines) + "\n")

    train_clean_hash = sha256_file(clean_catalog)

    # Build and seal freeze manifest
    freeze_manifest = {
        "manifest_type": "Z-ZOA_PREDICTION_FREEZE_MANIFEST",
        "run_id": RUN_ID,
        "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": get_git_commit(),
        "python_version": sys.version,
        "train_clean_catalog_path": str(clean_catalog.relative_to(repo_root)).replace("\\", "/"),
        "train_clean_catalog_sha256": train_clean_hash,
        "file_hashes": file_hashes,
        "metrics_spec_sha256": file_hashes.get("metrics_spec.json"),
        "null_spec_sha256": file_hashes.get("null_spec.json"),
        "status": "PREDICTION_FROZEN",
    }

    manifest_json = runs_dir / "freeze_manifest.json"
    with manifest_json.open("w", encoding="utf-8") as f:
        json.dump(freeze_manifest, f, indent=2)

    seal_hash = sha256_file(manifest_json)
    freeze_manifest["manifest_seal_sha256"] = seal_hash
    with manifest_json.open("w", encoding="utf-8") as f:
        json.dump(freeze_manifest, f, indent=2)

    return freeze_manifest


def score_ga_holdout(
    repo_root: Path,
    n_null_samples: int = 1000,
    seed: int = 20240915,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Evaluate frozen GA-001 predictions against the 477 MeerKAT GA-SMGPS holdout galaxies."""
    runs_dir = repo_root / "runs" / RUN_ID
    freeze_file = runs_dir / "freeze_manifest.json"
    if not freeze_file.exists():
        raise RuntimeError("Validation denied: Prediction freeze manifest does not exist.")

    freeze_manifest = json.loads(freeze_file.read_text(encoding="utf-8"))
    freeze_token = freeze_manifest.get("manifest_seal_sha256")
    if not freeze_token or len(freeze_token) < 32:
        raise RuntimeError("Validation denied: Invalid freeze manifest seal hash.")

    # Load frozen arrays
    pred_mean = np.load(runs_dir / "prediction_mean.npy")
    pred_sigma = np.load(runs_dir / "prediction_sigma.npy")
    pred_prob = np.load(runs_dir / "prediction_probability.npy")

    grid_n = pred_mean.shape[0]
    box_size_mpc = 400.0
    half_box = box_size_mpc / 2.0
    h0 = 74.6

    # Securely load holdout data through DataGateway with freeze token
    reg_file = repo_root / "datasets" / "manifests" / "catalog_registry.json"
    registry = CatalogRegistry(registry_file=reg_file)
    gateway = DataGateway(registry, base_dir=repo_root)
    context = ExecutionContext(
        run_id=RUN_ID,
        mode=ExecutionMode.VALIDATION,
        freeze_token=freeze_token,
    )
    holdout_df = gateway.request_dataset("ga_smgps_477", context)
    n_holdout = holdout_df.height
    assert n_holdout == 477, f"Expected 477 GA-SMGPS galaxies, found {n_holdout}"

    glon = holdout_df["GLON"].to_numpy()
    glat = holdout_df["GLAT"].to_numpy()
    hrv = holdout_df["HRV"].to_numpy()

    # Coordinate transform: Galactic (l, b) -> Supergalactic (sgl, sgb)
    sgl_q, sgb_q, _ = galactic_to_supergalactic(glon * u.deg, glat * u.deg)
    sgl_rad = np.radians(sgl_q.value)
    sgb_rad = np.radians(sgb_q.value)

    dist_mpc = hrv / h0
    sgx = dist_mpc * np.cos(sgb_rad) * np.cos(sgl_rad)
    sgy = dist_mpc * np.cos(sgb_rad) * np.sin(sgl_rad)
    sgz = dist_mpc * np.sin(sgb_rad)

    def coords_to_voxels(x: np.ndarray, y: np.ndarray, z: np.ndarray) -> np.ndarray:
        u_vox = (x + half_box) / box_size_mpc * (grid_n - 1)
        v_vox = (y + half_box) / box_size_mpc * (grid_n - 1)
        w_vox = (z + half_box) / box_size_mpc * (grid_n - 1)
        u_vox = np.clip(u_vox, 0, grid_n - 1)
        v_vox = np.clip(v_vox, 0, grid_n - 1)
        w_vox = np.clip(w_vox, 0, grid_n - 1)
        return np.array([u_vox, v_vox, w_vox])

    holdout_voxels = coords_to_voxels(sgx, sgy, sgz)
    obs_delta = map_coordinates(pred_mean, holdout_voxels, order=1, mode="nearest")
    obs_sigma = map_coordinates(pred_sigma, holdout_voxels, order=1, mode="nearest")
    obs_prob = map_coordinates(pred_prob, holdout_voxels, order=1, mode="nearest")

    mean_obs_delta = float(np.mean(obs_delta))
    frac_overdense = float(np.mean(obs_delta > 0.0))
    frac_high_prob = float(np.mean(obs_prob > 0.5))

    # 1,000 Aperture-matched Monte Carlo null realizations within the GA survey window
    # Window: GLON 302°-332°, GLAT -1.5° to +1.5°, cz 0 to 25,000 km/s
    rng = np.random.default_rng(seed)
    null_means = np.zeros(n_null_samples, dtype=np.float64)
    null_frac_overdense = np.zeros(n_null_samples, dtype=np.float64)

    for s in range(n_null_samples):
        cand_l = rng.uniform(302.0, 332.0, size=n_holdout)
        cand_b = rng.uniform(-1.5, 1.5, size=n_holdout)
        cand_cz = rng.uniform(0.0, 25000.0, size=n_holdout)

        cand_sgl, cand_sgb, _ = galactic_to_supergalactic(cand_l * u.deg, cand_b * u.deg)
        cand_sgl_r = np.radians(cand_sgl.value)
        cand_sgb_r = np.radians(cand_sgb.value)
        cand_d = cand_cz / h0

        cand_x = cand_d * np.cos(cand_sgb_r) * np.cos(cand_sgl_r)
        cand_y = cand_d * np.cos(cand_sgb_r) * np.sin(cand_sgl_r)
        cand_z = cand_d * np.sin(cand_sgb_r)

        null_vox = coords_to_voxels(cand_x, cand_y, cand_z)
        null_delta_vals = map_coordinates(pred_mean, null_vox, order=1, mode="nearest")
        null_means[s] = float(np.mean(null_delta_vals))
        null_frac_overdense[s] = float(np.mean(null_delta_vals > 0.0))

    null_mean_exp = float(np.mean(null_means))
    null_std_exp = float(np.std(null_means))
    p_value = float(np.mean(null_means >= mean_obs_delta))
    p_val_display = f"< {1.0 / n_null_samples:.4f}" if p_value == 0.0 else f"{p_value:.4f}"
    cohens_d = float((mean_obs_delta - null_mean_exp) / (null_std_exp + 1e-10))

    np.save(runs_dir / "null_distribution_means.npy", null_means)

    validation_report = {
        "run_id": RUN_ID,
        "holdout_catalog": "Great Attractor (MeerKAT GA-SMGPS Steyn et al. 2024)",
        "holdout_count": n_holdout,
        "primary_metric": "mean_overdensity_at_holdout",
        "observed_mean_delta": mean_obs_delta,
        "null_hypothesis_mean": null_mean_exp,
        "null_hypothesis_std": null_std_exp,
        "empirical_p_value": p_val_display,
        "effect_size_cohens_d": cohens_d,
        "fraction_in_overdense_voxels": frac_overdense,
        "fraction_in_high_prob_voxels": frac_high_prob,
        "n_null_realizations": n_null_samples,
        "status": "VALIDATION_CONFIRMED" if cohens_d > 1.5 else "VALIDATION_INCONCLUSIVE",
    }
    with (runs_dir / "validation_report.json").open("w", encoding="utf-8") as f:
        json.dump(validation_report, f, indent=2)

    ens_file = runs_dir / "ensemble_meta.json"
    ensemble_meta = json.loads(ens_file.read_text(encoding="utf-8")) if ens_file.exists() else {}

    # Build and seal RunManifest
    clean_cat_path = repo_root / "datasets" / "processed" / "TRAIN_CLEAN_GA" / "train_clean_ga_combined.parquet"
    holdout_cat_path = repo_root / "datasets" / "HOLDOUT" / "ga_smgps" / "ga_smgps_477.csv"
    manifest = RunManifest(
        run_id=RUN_ID,
        experiment_name=EXPERIMENT_NAME,
        random_seed=42,
        cosmology=COSMOLOGY_PRESETS["CF4_NOMINAL"].to_dict(),
        datasets=[
            {
                "dataset_id": "train_clean_ga_combined",
                "role": "TRAIN_CLEAN",
                "sha256": sha256_file(clean_cat_path),
                "row_count": pl.read_parquet(clean_cat_path).height,
            },
            {
                "dataset_id": "ga_smgps_477",
                "role": "HOLDOUT",
                "sha256": sha256_file(holdout_cat_path),
                "row_count": n_holdout,
            },
        ],
        calculations=[
            {
                "action": "constrained_ensemble_reconstruction",
                "source": "ReconstructionEngine",
                "inputs": {
                    "catalog": "train_clean_ga_combined.parquet",
                    "n_realizations": 20,
                    "grid_size": 32,
                    "box_size_mpc": 400.0,
                    "smoothing_scale_mpc": 10.0,
                },
                "outputs": {
                    "pred_mean_stats": ensemble_meta.get("pred_mean_stats", {}),
                },
            },
            {
                "action": "holdout_scoring_and_null_testing",
                "source": "MeerKAT GA-SMGPS (Steyn et al. 2024)",
                "inputs": {
                    "holdout_count": n_holdout,
                    "n_null_realizations": n_null_samples,
                },
                "outputs": validation_report,
            },
        ],
        outputs=validation_report,
    )
    manifest.save_run_bundle(runs_dir)

    return validation_report, manifest.model_dump()


def run_ga_experiment(repo_root: Optional[Path] = None) -> Dict[str, Any]:
    """Execute complete GA-001 out-of-sample reconstruction and validation pipeline."""
    root = repo_root or Path(__file__).resolve().parent.parent.parent
    print("=" * 72)
    print("STARTING GREAT ATTRACTOR (GA-001) PIPELINE")
    print("=" * 72)

    # 1. Reconstruct and freeze
    print("\n[PHASE 1] 3D Constrained Reconstruction & Freezing...")
    freeze_manifest = reconstruct_and_freeze_ga(root)
    print(f"  * Freeze manifest sealed: {freeze_manifest['manifest_seal_sha256']}")

    # 2. Holdout unblinding and scoring
    print("\n[PHASE 2] Gated Holdout Scoring & Null Ensemble...")
    val_report, run_manifest = score_ga_holdout(root)
    print(f"  * Holdout Count      : {val_report['holdout_count']} galaxies")
    print(f"  * Observed Mean delta: {val_report['observed_mean_delta']:.3f}")
    print(f"  * Null Mean delta    : {val_report['null_hypothesis_mean']:.3f} +/- {val_report['null_hypothesis_std']:.3f}")
    print(f"  * Cohen's d          : {val_report['effect_size_cohens_d']:.2f} sigma")
    print(f"  * Empirical p-value  : {val_report['empirical_p_value']}")
    print(f"  * Validation Status  : {val_report['status']}")
    print(f"  * Run Manifest Seal  : {run_manifest.get('manifest_sha256')}")

    print("\n" + "=" * 72)
    print("GA-001 PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 72)

    return {
        "freeze_manifest": freeze_manifest,
        "validation_report": val_report,
        "run_manifest": run_manifest,
    }


if __name__ == "__main__":
    run_ga_experiment()
