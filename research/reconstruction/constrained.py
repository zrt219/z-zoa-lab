"""Constrained realizations and uncertainty ensemble generator for Z-ZOA (Prompt 11).

Generates N constrained realizations under TRAIN_CLEAN constraints,
producing:
- per-voxel mean density <delta(x)>
- per-voxel uncertainty sigma_delta(x)
- probability of exceeding critical overdensity thresholds P(delta(x) > delta_th)
- ensemble summary metadata and random seeds.
Strictly denies any access to HOLDOUT catalogues.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple
import numpy as np

from research.reconstruction.engine import ReconstructionConfig, ReconstructionEngine


def run_constrained_ensemble(
    repo_root: Path,
    n_realizations: int = 20,
    base_seed: int = 1000,
    threshold: float = 1.0,
    run_id: str = "VELA-001",
) -> Dict[str, Any]:
    clean_catalog = repo_root / "datasets" / "processed" / "TRAIN_CLEAN" / "train_clean_combined.parquet"
    if not clean_catalog.exists():
        from research.catalogs.decontamination_pipeline import run_decontamination_pipeline
        run_decontamination_pipeline(repo_root)

    runs_dir = repo_root / "runs" / run_id
    runs_dir.mkdir(parents=True, exist_ok=True)

    cfg = ReconstructionConfig(random_seed=base_seed)
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

    # Compute ensemble statistics
    pred_mean = np.mean(delta_realizations, axis=0)
    pred_sigma = np.std(delta_realizations, axis=0)
    # Per-voxel probability of exceeding threshold
    pred_probability = np.mean(delta_realizations > threshold, axis=0)

    # Velocity stats
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

    # Save outputs
    np.save(runs_dir / "prediction_mean.npy", pred_mean)
    np.save(runs_dir / "prediction_sigma.npy", pred_sigma)
    np.save(runs_dir / "prediction_probability.npy", pred_probability)
    np.save(runs_dir / "prediction_velocity_mean.npy", v_mean)
    np.save(runs_dir / "prediction_velocity_sigma.npy", v_sigma)

    ensemble_meta = {
        "run_id": run_id,
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

    return ensemble_meta


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parent.parent.parent
    res = run_constrained_ensemble(repo_root)
    print("Constrained ensemble complete:")
    print(json.dumps(res, indent=2))
