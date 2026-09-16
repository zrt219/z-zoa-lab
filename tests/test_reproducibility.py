"""Test end-to-end experiment execution, manifest serialization, and bit-for-bit replay."""

import json
from pathlib import Path
import numpy as np
from research.cosmology.models import COSMOLOGY_PRESETS
from research.catalogs.registry import CatalogRegistry
from research.experiments.runner import ExperimentRunner
from research.holdouts.guard import ExecutionMode


def test_reproducible_experiment_run(tmp_path: Path):
    reg = CatalogRegistry("datasets/manifests/catalog_registry.json")
    cosmo = COSMOLOGY_PRESETS["CF4_NOMINAL"]

    runner1 = ExperimentRunner(
        run_id="RUN_0001",
        experiment_name="Vela holdout baseline",
        cosmology=cosmo,
        mode=ExecutionMode.TRAINING,
        random_seed=382019,
        registry=reg,
    )

    # 1. Load CF4
    cf4_df = runner1.load_dataset("cf4_sample")
    assert cf4_df.height == 8

    # 2. Perform peculiar velocity calculations
    results1 = []
    for row in cf4_df.iter_rows(named=True):
        res = runner1.compute_peculiar_velocity(
            cz_kms=row["cz_obs"],
            distance_mpc=row["distance_mpc"],
            cz_err_kms=row["cz_err"],
            mu_err=row["mu_err"],
            source=f"CF4 PGC {row['pgc']}",
        )
        results1.append(res)

    runner1.outputs = {"velocities": results1}

    # 3. Save run
    run_dir = runner1.save_run(runs_root=tmp_path)
    assert (run_dir / "manifest.json").exists()
    assert (run_dir / "config.yaml").exists()
    assert (run_dir / "results.json").exists()

    with open(run_dir / "manifest.json", "r", encoding="utf-8") as f:
        manifest_dict = json.load(f)

    assert manifest_dict["manifest_sha256"] is not None
    assert len(manifest_dict["calculations"]) == 9  # 1 load + 8 calculations

    # 4. Rerun independently with identical parameters
    runner2 = ExperimentRunner(
        run_id="RUN_0001_REPLAY",
        experiment_name="Vela holdout baseline",
        cosmology=cosmo,
        mode=ExecutionMode.TRAINING,
        random_seed=382019,
        registry=reg,
    )
    cf4_df_2 = runner2.load_dataset("cf4_sample")
    results2 = []
    for row in cf4_df_2.iter_rows(named=True):
        res = runner2.compute_peculiar_velocity(
            cz_kms=row["cz_obs"],
            distance_mpc=row["distance_mpc"],
            cz_err_kms=row["cz_err"],
            mu_err=row["mu_err"],
            source=f"CF4 PGC {row['pgc']}",
        )
        results2.append(res)

    # 5. Assert bit-for-bit numerical reproducibility
    for r1, r2 in zip(results1, results2):
        assert r1["v_pec"]["value"] == r2["v_pec"]["value"]
        assert r1["uncertainty"]["value"] == r2["uncertainty"]["value"]
