"""Experiment run and manifest management routes."""

import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from research.cosmology.models import COSMOLOGY_PRESETS
from research.catalogs.registry import CatalogRegistry
from research.experiments.runner import ExperimentRunner
from research.holdouts.guard import ExecutionMode
from backend.config import REGISTRY_PATH, RUNS_DIR, BASE_DIR
from backend.schemas.api_models import RunExperimentRequest

router = APIRouter(prefix="/experiments", tags=["experiments"])


@router.get("/runs")
def list_runs():
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    runs = []
    for run_folder in RUNS_DIR.iterdir():
        if run_folder.is_dir():
            manifest_file = run_folder / "manifest.json"
            if not manifest_file.exists():
                manifest_file = run_folder / "freeze_manifest.json"
            if manifest_file.exists():
                try:
                    with open(manifest_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        runs.append({
                            "run_id": data.get("run_id", run_folder.name),
                            "experiment_name": data.get("experiment_name") or data.get("manifest_type") or run_folder.name,
                            "created_at": data.get("created_at") or data.get("frozen_at_utc", ""),
                            "git_commit": data.get("git_commit", ""),
                            "manifest_sha256": data.get("manifest_sha256") or data.get("manifest_seal_sha256", ""),
                            "calculation_count": len(data.get("calculations", [])) or len(data.get("file_hashes", {})),
                        })
                except Exception:
                    pass
    return sorted(runs, key=lambda r: r.get("created_at", ""), reverse=True)


@router.get("/runs/{run_id}")
def get_run_details(run_id: str):
    run_dir = RUNS_DIR / run_id
    manifest_file = run_dir / "manifest.json"
    if not manifest_file.exists():
        manifest_file = run_dir / "freeze_manifest.json"
    if not manifest_file.exists():
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found.")
    with open(manifest_file, "r", encoding="utf-8") as f:
        return json.load(f)


@router.post("/execute")
def execute_experiment(req: RunExperimentRequest):
    reg = CatalogRegistry(registry_file=REGISTRY_PATH)
    if req.cosmology_name not in COSMOLOGY_PRESETS:
        raise HTTPException(status_code=400, detail=f"Unknown cosmology '{req.cosmology_name}'")

    cosmo = COSMOLOGY_PRESETS[req.cosmology_name]
    mode = ExecutionMode(req.execution_mode.upper())

    runner = ExperimentRunner(
        run_id=req.run_id,
        experiment_name=req.experiment_name,
        cosmology=cosmo,
        mode=mode,
        registry=reg,
        base_dir=str(BASE_DIR),
        freeze_token=req.freeze_token,
    )

    try:
        # Load datasets requested
        all_results = []
        for ds_id in req.dataset_ids:
            df = runner.load_dataset(ds_id)
            if "cz_obs" in df.columns and "distance_mpc" in df.columns:
                for row in df.iter_rows(named=True):
                    res = runner.compute_peculiar_velocity(
                        cz_kms=row["cz_obs"],
                        distance_mpc=row["distance_mpc"],
                        cz_err_kms=row.get("cz_err"),
                        mu_err=row.get("mu_err"),
                        source=f"{ds_id} (row {row.get('pgc', row.get('source_id', 'unknown'))})",
                    )
                    all_results.append(res)

        runner.outputs = {"velocities": all_results}
        run_dir = runner.save_run(runs_root=RUNS_DIR)
        manifest = runner.generate_manifest()
        return {
            "status": "COMPLETED",
            "run_id": runner.run_id,
            "manifest_sha256": manifest.manifest_sha256,
            "saved_to": str(run_dir),
            "manifest": manifest.model_dump(),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
