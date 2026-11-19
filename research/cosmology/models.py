"""Cosmological parameter configurations and FLRW bindings for Z-ZOA."""

from typing import Optional
from pydantic import BaseModel, Field, field_validator
import astropy.units as u
from astropy.cosmology import FlatLambdaCDM, LambdaCDM, FLRW


class UnphysicalCosmologyError(ValueError):
    """
    Exception raised when cosmological or astronomical parameters violate physical bounds
    (e.g., peculiar velocities exceeding cosmic infall limits v > 0.01c).
    """
    pass


class CosmologyConfig(BaseModel):
    """
    Explicit cosmological model configuration.
    Scientific Rule #3: Cosmology must be explicit and immutable per run.
    """
    cosmology_name: str = Field(..., description="Unique name of cosmological model")
    H0: float = Field(..., gt=0.0, description="Hubble constant in km s-1 Mpc-1")
    Om0: float = Field(..., ge=0.0, le=1.0, description="Matter density parameter at z=0")
    Ode0: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Dark energy density parameter at z=0")
    reference: str = Field(..., description="Literature or survey reference defining these parameters")

    @field_validator("H0")
    @classmethod
    def validate_h0(cls, v: float) -> float:
        if v < 40.0 or v > 120.0:
            raise ValueError(f"Unphysical Hubble constant H0 = {v} km/s/Mpc.")
        return v

    def to_astropy(self) -> FLRW:
        """Instantiate an Astropy FLRW cosmology instance."""
        h0_q = self.H0 * (u.km / (u.s * u.Mpc))
        if self.Ode0 is None or abs(self.Om0 + self.Ode0 - 1.0) < 1e-6:
            return FlatLambdaCDM(H0=h0_q, Om0=self.Om0, name=self.cosmology_name)
        return LambdaCDM(H0=h0_q, Om0=self.Om0, Ode0=self.Ode0, name=self.cosmology_name)

    def to_dict(self) -> dict:
        return {
            "cosmology_name": self.cosmology_name,
            "H0": self.H0,
            "H0_unit": "km / (s Mpc)",
            "Om0": self.Om0,
            "Ode0": self.Ode0 if self.Ode0 is not None else round(1.0 - self.Om0, 6),
            "reference": self.reference,
        }


# Standard scientific presets
COSMOLOGY_PRESETS: dict[str, CosmologyConfig] = {
    "PLANCK18": CosmologyConfig(
        cosmology_name="Planck18",
        H0=67.66,
        Om0=0.30966,
        Ode0=0.69034,
        reference="Planck Collaboration 2018 (A&A 641, A6, Tab. 2)",
    ),
    "CF4_NOMINAL": CosmologyConfig(
        cosmology_name="CF4_Nominal",
        H0=74.6,
        Om0=0.30,
        Ode0=0.70,
        reference="Tully et al. 2023 (ApJ 944, 94)",
    ),
    "WMAP9": CosmologyConfig(
        cosmology_name="WMAP9",
        H0=69.32,
        Om0=0.2865,
        Ode0=0.7135,
        reference="Hinshaw et al. 2013 (ApJS 208, 19)",
    ),
}
