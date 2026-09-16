"""Run manifest data structures and serialization."""

import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import yaml

import astropy
import numpy
import scipy
import polars
import pydantic


def get_git_commit() -> str:
    """Safely get current git commit hash."""
    try:
        res = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5,
        )
        if res.returncode == 0:
            return res.stdout.strip()
    except Exception:
        pass
    return "UNKNOWN_COMMIT"


def get_environment_versions() -> Dict[str, str]:
    """Capture current Python scientific package versions."""
    return {
        "python": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
        "astropy": astropy.__version__,
        "numpy": numpy.__version__,
        "scipy": scipy.__version__,
        "polars": polars.__version__,
        "pydantic": pydantic.__version__,
    }


class RunManifest(BaseModel):
    """
    Immutable experiment manifest for total scientific repeatability.
    """
    run_id: str = Field(..., description="Unique run identifier (e.g. 'RUN_0001')")
    experiment_name: str = Field(..., description="Descriptive experiment title")
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    git_commit: str = Field(default_factory=get_git_commit)
    random_seed: int = Field(default=382019)
    package_versions: Dict[str, str] = Field(default_factory=get_environment_versions)
    cosmology: Dict[str, Any] = Field(..., description="Cosmological model parameters")
    datasets: List[Dict[str, Any]] = Field(default_factory=list, description="Datasets accessed and their SHA-256")
    calculations: List[Dict[str, Any]] = Field(default_factory=list, description="Executed calculations with provenance")
    warnings: List[str] = Field(default_factory=list)
    outputs: Dict[str, Any] = Field(default_factory=dict)
    manifest_sha256: Optional[str] = Field(default=None)

    def compute_sha256(self) -> str:
        """Compute SHA-256 hash over the deterministic JSON representation (excluding manifest_sha256)."""
        data = self.model_dump(exclude={"manifest_sha256"})
        serialized = json.dumps(data, sort_keys=True, indent=2).encode("utf-8")
        return hashlib.sha256(serialized).hexdigest()

    def seal(self) -> str:
        """Cryptographically seal the manifest and record the hash."""
        token = self.compute_sha256()
        self.manifest_sha256 = token
        return token

    def save_run_bundle(self, run_dir: Path) -> Path:
        """
        Save complete machine-readable reproducibility bundle:
        - manifest.json
        - config.yaml
        - results.json
        """
        run_dir.mkdir(parents=True, exist_ok=True)
        self.seal()

        # 1. manifest.json
        manifest_path = run_dir / "manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(self.model_dump(), f, indent=2)

        # 2. config.yaml
        config_data = {
            "run_id": self.run_id,
            "experiment_name": self.experiment_name,
            "random_seed": self.random_seed,
            "cosmology": self.cosmology,
            "datasets": self.datasets,
        }
        with open(run_dir / "config.yaml", "w", encoding="utf-8") as f:
            yaml.safe_dump(config_data, f, sort_keys=False)

        # 3. results.json
        with open(run_dir / "results.json", "w", encoding="utf-8") as f:
            json.dump(self.outputs, f, indent=2)

        return run_dir
