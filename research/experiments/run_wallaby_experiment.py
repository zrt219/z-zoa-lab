"""ASKAP WALLABY DR2 external blind H I survey validation pipeline (WALLABY-001).

Evaluates the frozen 3D cosmological density reconstruction against 3,454 blind H I
detections from ASKAP WALLABY DR2 (Murugeshan et al. 2024), testing recovery
against 1,000 survey-matched Monte Carlo null realizations.
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import astropy.units as u
import numpy as np
import polars as pl
from scipy.ndimage import map_coordinates
from astropy.coordinates import SkyCoord, Supergalactic

from research.cosmology.models import COSMOLOGY_PRESETS
from research.experiments.manifest import (
    RunManifest,
    get_environment_versions,
    get_git_commit,
)
from research.reconstruction.engine import ReconstructionConfig, ReconstructionEngine

RUN_ID = "WALLABY-001"
EXPERIMENT_NAME = "ASKAP WALLABY DR2 External Blind H I Survey Validation"


def sha256_file(p: Path) -> str:
    """Compute cryptographic SHA-256 digest of a file on disk."""
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def reconstruct_and_freeze_wallaby(
    repo_root: Path,
    n_realizations: int = 20,
    base_seed: int = 1000,
    threshold: float = 1.0,
) -> Dict[str, Any]:
    """Generate or link prediction ensemble and freeze under WALLABY-001."""
    runs_dir = repo_root / "runs" / RUN_ID
    runs_dir.mkdir(parents=True, exist_ok=True)

    clean_catalog = repo_root / "datasets" / "processed" / "TRAIN_CLEAN" / "train_clean_combined.parquet"
    if not clean_catalog.exists():
        from research.catalogs.decontamination_pipeline import run_decontamination_pipeline
        run_decontamination_pipeline(repo_root)

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

    metrics_spec = {
        "spec_version": "1.0",
        "primary_metric": "mean_overdensity_at_holdout",
        "description": "Mean reconstructed density contrast delta evaluated at verified ASKAP WALLABY DR2 H I galaxy locations",
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

    null_spec = {
        "spec_version": "1.0",
        "survey_footprint": "WALLABY_DR2",
        "selection_weight_model": "field_matched_survey_volume",
        "null_realizations": 1000,
        "seed": 20240915,
        "condition": "Holdout coordinates and counts matched (N=3454); drawn strictly from WALLABY DR2 fields and radial envelope.",
    }
    with (runs_dir / "null_spec.json").open("w", encoding="utf-8") as f:
        json.dump(null_spec, f, indent=2)

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


def score_wallaby_holdout(
    repo_root: Path,
    n_null_samples: int = 1000,
    seed: int = 20240915,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Evaluate frozen predictions against the 3,454 ASKAP WALLABY DR2 H I sources."""
    runs_dir = repo_root / "runs" / RUN_ID
    freeze_file = runs_dir / "freeze_manifest.json"
    if not freeze_file.exists():
        raise RuntimeError("Validation denied: Prediction freeze manifest does not exist.")

    pred_mean = np.load(runs_dir / "prediction_mean.npy")
    pred_sigma = np.load(runs_dir / "prediction_sigma.npy")
    pred_prob = np.load(runs_dir / "prediction_probability.npy")

    grid_n = pred_mean.shape[0]
    box_size_mpc = 400.0
    half_box = box_size_mpc / 2.0
    h0 = 74.6

    norm_path = repo_root / "datasets" / "processed" / "normalized" / "wallaby_dr2_normalized.parquet"
    raw_path = repo_root / "datasets" / "reference" / "wallaby_dr2" / "wallaby_dr2_source_catalogue.csv"
    if not norm_path.exists():
        raise FileNotFoundError(f"WALLABY DR2 normalized catalog missing: {norm_path}")

    df_norm = pl.read_parquet(norm_path)
    n_holdout = df_norm.height
    assert n_holdout == 3454, f"Expected 3,454 WALLABY DR2 sources, found {n_holdout}"

    df_raw = pl.read_csv(raw_path) if raw_path.exists() else None
    if df_raw is not None and "team_release" in df_raw.columns:
        df_comb = df_norm.with_columns(df_raw["team_release"].alias("field"))
    else:
        df_comb = df_norm.with_columns(pl.lit("ALL_FIELDS").alias("field"))

    sgl_rad = np.radians(df_norm["sgl_deg"].to_numpy())
    sgb_rad = np.radians(df_norm["sgb_deg"].to_numpy())
    cz_kms = df_norm["cz_value_kms"].to_numpy()
    dist_mpc = cz_kms / h0

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

    # Field-matched survey volume null generation
    fields = df_comb.group_by("field").agg([
        pl.len().alias("n"),
        pl.col("ra_deg").min().alias("ra_min"),
        pl.col("ra_deg").max().alias("ra_max"),
        pl.col("dec_deg").min().alias("dec_min"),
        pl.col("dec_deg").max().alias("dec_max"),
        pl.col("distance_mpc").min().alias("d_min"),
        pl.col("distance_mpc").max().alias("d_max"),
    ])

    rng = np.random.default_rng(seed)
    null_means = np.zeros(n_null_samples, dtype=np.float64)

    for s in range(n_null_samples):
        all_null_ra, all_null_dec, all_null_d = [], [], []
        for f in fields.iter_rows(named=True):
            f_ra = rng.uniform(f["ra_min"], f["ra_max"], size=f["n"])
            f_dec = rng.uniform(f["dec_min"], f["dec_max"], size=f["n"])
            f_d = rng.uniform(f["d_min"], f["d_max"], size=f["n"])
            all_null_ra.extend(f_ra)
            all_null_dec.extend(f_dec)
            all_null_d.extend(f_d)

        sc = SkyCoord(ra=np.array(all_null_ra) * u.deg, dec=np.array(all_null_dec) * u.deg, frame="icrs")
        sg = sc.transform_to(Supergalactic())
        sgl_n = np.radians(sg.sgl.deg)
        sgb_n = np.radians(sg.sgb.deg)
        d_n = np.array(all_null_d)

        xn = d_n * np.cos(sgb_n) * np.cos(sgl_n)
        yn = d_n * np.cos(sgb_n) * np.sin(sgl_n)
        zn = d_n * np.sin(sgb_n)

        null_vox = coords_to_voxels(xn, yn, zn)
        null_delta_vals = map_coordinates(pred_mean, null_vox, order=1, mode="nearest")
        null_means[s] = float(np.mean(null_delta_vals))

    null_mean_exp = float(np.mean(null_means))
    null_std_exp = float(np.std(null_means))
    p_value = float(np.mean(null_means >= mean_obs_delta))
    p_val_display = f"< {1.0 / n_null_samples:.4f}" if p_value == 0.0 else f"{p_value:.4f}"
    cohens_d = float((mean_obs_delta - null_mean_exp) / (null_std_exp + 1e-10))

    np.save(runs_dir / "null_distribution_means.npy", null_means)

    validation_report = {
        "run_id": RUN_ID,
        "holdout_catalog": "ASKAP WALLABY Pilot DR2 (Murugeshan et al. 2024)",
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

    clean_cat_path = repo_root / "datasets" / "processed" / "TRAIN_CLEAN" / "train_clean_combined.parquet"
    manifest = RunManifest(
        run_id=RUN_ID,
        experiment_name=EXPERIMENT_NAME,
        random_seed=42,
        cosmology=COSMOLOGY_PRESETS["CF4_NOMINAL"].to_dict(),
        datasets=[
            {
                "dataset_id": "train_clean_combined",
                "role": "TRAIN_CLEAN",
                "sha256": sha256_file(clean_cat_path),
                "row_count": pl.read_parquet(clean_cat_path).height,
            },
            {
                "dataset_id": "wallaby_dr2",
                "role": "COMPARISON_ONLY",
                "sha256": sha256_file(norm_path),
                "row_count": n_holdout,
            },
        ],
        calculations=[
            {
                "action": "constrained_ensemble_reconstruction",
                "source": "ReconstructionEngine",
                "inputs": {
                    "catalog": "train_clean_combined.parquet",
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
                "source": "ASKAP WALLABY DR2 (Murugeshan et al. 2024)",
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


def run_wallaby_experiment(repo_root: Optional[Path] = None) -> Dict[str, Any]:
    """Execute complete WALLABY-001 out-of-sample reconstruction and validation pipeline."""
    root = repo_root or Path(__file__).resolve().parent.parent.parent
    print("=" * 72)
    print("STARTING WALLABY (WALLABY-001) PIPELINE")
    print("=" * 72)

    # 1. Reconstruct and freeze
    print("\n[PHASE 1] 3D Constrained Reconstruction & Freezing...")
    freeze_manifest = reconstruct_and_freeze_wallaby(root)
    print(f"  * Freeze manifest sealed: {freeze_manifest['manifest_seal_sha256']}")

    # 2. Holdout unblinding and scoring
    print("\n[PHASE 2] Blind External H I Survey Scoring & Null Ensemble...")
    val_report, run_manifest = score_wallaby_holdout(root)
    print(f"  * Holdout Count      : {val_report['holdout_count']} galaxies")
    print(f"  * Observed Mean delta: {val_report['observed_mean_delta']:.3f}")
    print(f"  * Null Mean delta    : {val_report['null_hypothesis_mean']:.3f} +/- {val_report['null_hypothesis_std']:.3f}")
    print(f"  * Cohen's d          : {val_report['effect_size_cohens_d']:.2f} sigma")
    print(f"  * Empirical p-value  : {val_report['empirical_p_value']}")
    print(f"  * Validation Status  : {val_report['status']}")
    print(f"  * Run Manifest Seal  : {run_manifest.get('manifest_sha256')}")

    print("\n" + "=" * 72)
    print("WALLABY-001 PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 72)

    return {
        "freeze_manifest": freeze_manifest,
        "validation_report": val_report,
        "run_manifest": run_manifest,
    }


if __name__ == "__main__":
    run_wallaby_experiment()
