"""Experiment execution and reproducibility runner."""

from pathlib import Path
from typing import Optional, Dict, Any, List
import numpy as np
import astropy.units as u

from research.cosmology.models import CosmologyConfig, COSMOLOGY_PRESETS
from research.catalogs.registry import CatalogRegistry
from research.holdouts.guard import DataGateway, ExecutionContext, ExecutionMode
from research.provenance.tracker import ProvenanceTracker
from research.experiments.manifest import RunManifest, get_git_commit
from research.velocities.peculiar import calculate_peculiar_velocity
from research.coordinates.transforms import icrs_to_galactic, spherical_to_cartesian
from research.coordinates.frames import CoordinateFrame


class ExperimentRunner:
    """Orchestrates an experiment run, logging provenance, datasets, and manifests."""

    def __init__(
        self,
        run_id: str,
        experiment_name: str,
        cosmology: CosmologyConfig,
        mode: ExecutionMode = ExecutionMode.TRAINING,
        random_seed: int = 382019,
        registry: Optional[CatalogRegistry] = None,
        base_dir: str = ".",
        freeze_token: Optional[str] = None,
    ):
        self.run_id = run_id
        self.experiment_name = experiment_name
        self.cosmology = cosmology
        self.mode = mode
        self.random_seed = random_seed
        self.base_dir = Path(base_dir)

        np.random.seed(random_seed)

        self.registry = registry or CatalogRegistry()
        self.gateway = DataGateway(self.registry, base_dir=self.base_dir)
        self.context = ExecutionContext(
            run_id=run_id,
            mode=mode,
            freeze_token=freeze_token,
        )
        self.provenance = ProvenanceTracker()
        self.accessed_datasets: List[Dict[str, Any]] = []
        self.warnings: List[str] = []
        self.outputs: Dict[str, Any] = {}

    def load_dataset(self, dataset_id: str):
        """Load dataset through the gated DataGateway and log to manifest."""
        df = self.gateway.request_dataset(dataset_id, self.context)
        meta = self.registry.get(dataset_id)
        self.accessed_datasets.append({
            "dataset_id": meta.dataset_id,
            "role": meta.role.value,
            "sha256": meta.sha256,
            "row_count": df.height,
        })
        self.provenance.add(
            action="dataset_load",
            source=meta.survey,
            inputs={"dataset_id": dataset_id, "file_path": meta.file_path},
            outputs={"rows": df.height, "columns": df.columns},
            notes=f"Role: {meta.role.value}, SHA256: {meta.sha256}",
        )
        return df

    def compute_peculiar_velocity(
        self,
        cz_kms: float,
        distance_mpc: float,
        cz_err_kms: Optional[float] = None,
        distance_err_mpc: Optional[float] = None,
        mu_err: Optional[float] = None,
        source: str = "observational_input",
        method: str = "linear",
    ) -> Dict[str, Any]:
        """Compute peculiar velocity and record step in provenance DAG."""
        cz_q = cz_kms * (u.km / u.s)
        d_q = distance_mpc * u.Mpc
        cz_err_q = (cz_err_kms * (u.km / u.s)) if cz_err_kms is not None else None
        d_err_q = (distance_err_mpc * u.Mpc) if distance_err_mpc is not None else None

        res = calculate_peculiar_velocity(
            cz=cz_q,
            distance=d_q,
            cosmo=self.cosmology,
            method=method,
            cz_err=cz_err_q,
            distance_err=d_err_q,
            mu_err=mu_err,
        )

        res_dict = res.to_dict()

        # Log provenance
        self.provenance.add(
            action="peculiar_velocity",
            source=source,
            inputs=res.inputs,
            outputs={"v_pec": res_dict["v_pec"]},
            formula=res.formula,
            uncertainty=res_dict["uncertainty"],
            reference_frame="CMB",
        )

        return res_dict

    def generate_manifest(self) -> RunManifest:
        """Construct the complete RunManifest object."""
        manifest = RunManifest(
            run_id=self.run_id,
            experiment_name=self.experiment_name,
            git_commit=get_git_commit(),
            random_seed=self.random_seed,
            cosmology=self.cosmology.to_dict(),
            datasets=self.accessed_datasets,
            calculations=self.provenance.to_list(),
            warnings=self.warnings,
            outputs=self.outputs,
        )
        manifest.seal()
        return manifest

    def save_run(self, runs_root: Optional[Path] = None) -> Path:
        """Save run outputs to disk under runs/{run_id}."""
        root = runs_root or (self.base_dir / "runs")
        run_dir = root / self.run_id
        manifest = self.generate_manifest()
        manifest.save_run_bundle(run_dir)
        return run_dir
