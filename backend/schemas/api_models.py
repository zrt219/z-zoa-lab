"""Pydantic schemas for FastAPI endpoints."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class PeculiarVelocityRequest(BaseModel):
    cz_kms: float = Field(..., description="Observed or CMB frame cz in km/s")
    distance_mpc: float = Field(..., description="Luminosity or comoving distance in Mpc")
    cz_err_kms: Optional[float] = Field(default=None, description="Redshift error in km/s")
    distance_err_mpc: Optional[float] = Field(default=None, description="Distance error in Mpc")
    mu_err: Optional[float] = Field(default=None, description="Distance modulus error")
    cosmology_name: str = Field(default="CF4_NOMINAL")
    method: str = Field(default="linear", description="'linear' or 'cosmological'")
    source: str = Field(default="interactive_console")


class CoordinateTransformRequest(BaseModel):
    source_frame: str = Field(..., description="'ICRS', 'GALACTIC', or 'SUPERGALACTIC'")
    lon_deg: float = Field(..., description="RA, Galactic l, or Supergalactic SGL in degrees")
    lat_deg: float = Field(..., description="Dec, Galactic b, or Supergalactic SGB in degrees")
    distance_mpc: Optional[float] = Field(default=None)


class RunExperimentRequest(BaseModel):
    run_id: str = Field(..., description="Unique run identifier")
    experiment_name: str = Field(..., description="Title of experiment")
    cosmology_name: str = Field(default="CF4_NOMINAL")
    dataset_ids: List[str] = Field(default_factory=lambda: ["cf4_sample"])
    execution_mode: str = Field(default="TRAINING", description="'TRAINING' or 'VALIDATION'")
    freeze_token: Optional[str] = Field(default=None)


class ReconstructionRunRequest(BaseModel):
    run_id: str = Field(default="VELA-001")
    n_realizations: int = Field(default=20, ge=1, le=200)
    base_seed: int = Field(default=1000)
    threshold: float = Field(default=1.0)
    box_size_mpc: float = Field(default=400.0)
    grid_size: int = Field(default=32)


class FreezeRevealRequest(BaseModel):
    run_id: str = Field(default="VELA-001")
    n_null_samples: int = Field(default=1000, ge=10, le=10000)
    seed: int = Field(default=20240915)


class MockUniverseRequest(BaseModel):
    n_galaxies: int = Field(default=5000, ge=100, le=50000)
    box_size_mpc: float = Field(default=400.0)
    seed: int = Field(default=42)


class ReproducibilityBundleRequest(BaseModel):
    run_id: str = Field(default="VELA-001")
    include_catalogs: bool = Field(default=True)
    include_figures: bool = Field(default=True)

