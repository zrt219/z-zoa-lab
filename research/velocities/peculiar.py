"""Peculiar velocity calculation estimators and provenance tracking."""

from abc import ABC, abstractmethod
from typing import Optional, Union, Dict, Any
import astropy.units as u
from astropy.units import Quantity
from astropy.constants import c as c_light

from research.units.validation import ensure_quantity, quantity_to_dict
from research.cosmology.models import CosmologyConfig
from research.cosmology.distances import redshift_from_comoving_distance
from research.velocities.uncertainties import (
    propagate_linear_velocity_uncertainty,
    propagate_lognormal_distance_modulus_uncertainty,
)


class PeculiarVelocityResult:
    """Encapsulates a computed peculiar velocity with units, uncertainty, and formula."""

    def __init__(
        self,
        v_pec: Quantity,
        uncertainty: Optional[Quantity],
        estimator_name: str,
        formula: str,
        inputs: Dict[str, Any],
    ):
        self.v_pec = v_pec
        self.uncertainty = uncertainty
        self.estimator_name = estimator_name
        self.formula = formula
        self.inputs = inputs

    def to_dict(self) -> Dict[str, Any]:
        return {
            "v_pec": quantity_to_dict(self.v_pec),
            "uncertainty": quantity_to_dict(self.uncertainty) if self.uncertainty is not None else None,
            "estimator": self.estimator_name,
            "formula": self.formula,
            "inputs": self.inputs,
        }

    def __repr__(self) -> str:
        unc_str = f" +/- {self.uncertainty}" if self.uncertainty is not None else ""
        return f"<PeculiarVelocity: {self.v_pec}{unc_str} [{self.estimator_name}]>"


class BasePeculiarVelocityEstimator(ABC):
    """Abstract base class for peculiar velocity estimators."""

    @abstractmethod
    def calculate(
        self,
        cz: Quantity,
        distance: Quantity,
        cosmo: CosmologyConfig,
        cz_err: Optional[Quantity] = None,
        distance_err: Optional[Quantity] = None,
        mu_err: Optional[float] = None,
        H0_err: Optional[Quantity] = None,
    ) -> PeculiarVelocityResult:
        pass


class LinearPeculiarVelocityEstimator(BasePeculiarVelocityEstimator):
    """
    Standard low-redshift linear approximation:
    v_pec = cz - H0 * d
    NOTE: Low-redshift exploratory estimator.
    """

    def calculate(
        self,
        cz: Quantity,
        distance: Quantity,
        cosmo: CosmologyConfig,
        cz_err: Optional[Quantity] = None,
        distance_err: Optional[Quantity] = None,
        mu_err: Optional[float] = None,
        H0_err: Optional[Quantity] = None,
    ) -> PeculiarVelocityResult:
        cz = ensure_quantity(cz, u.km / u.s, "cz")
        distance = ensure_quantity(distance, u.Mpc, "distance")
        H0 = cosmo.H0 * (u.km / (u.s * u.Mpc))

        # Core computation
        v_hubble = H0 * distance
        v_pec = cz - v_hubble.to(u.km / u.s)

        # Propagate uncertainty
        uncertainty = None
        if mu_err is not None:
            uncertainty = propagate_lognormal_distance_modulus_uncertainty(
                distance=distance,
                mu_err=mu_err,
                H0=H0,
                cz_err=cz_err,
                H0_err=H0_err,
            )
        elif distance_err is not None or cz_err is not None or H0_err is not None:
            uncertainty = propagate_linear_velocity_uncertainty(
                cz_err=cz_err,
                distance=distance,
                distance_err=distance_err,
                H0=H0,
                H0_err=H0_err,
            )

        inputs = {
            "cz": quantity_to_dict(cz),
            "distance": quantity_to_dict(distance),
            "H0": quantity_to_dict(H0),
            "cz_err": quantity_to_dict(cz_err) if cz_err is not None else None,
            "distance_err": quantity_to_dict(distance_err) if distance_err is not None else None,
            "mu_err": mu_err,
        }

        return PeculiarVelocityResult(
            v_pec=v_pec.to(u.km / u.s),
            uncertainty=uncertainty,
            estimator_name="Linear (v_pec = cz - H0*d)",
            formula="v_pec = cz - H0 * d",
            inputs=inputs,
        )


class CosmologicalPeculiarVelocityEstimator(BasePeculiarVelocityEstimator):
    """
    Rigorous relativistic peculiar velocity estimator:
    1. Invert d_C(z_cos) = d for cosmological redshift z_cos.
    2. Decouple z_pec: (1 + z_obs) = (1 + z_cos) * (1 + z_pec) => z_pec = (1 + z_obs)/(1 + z_cos) - 1
    3. Relativistic peculiar velocity: v_pec = c * ((1+z_pec)^2 - 1) / ((1+z_pec)^2 + 1)
    """

    def calculate(
        self,
        cz: Quantity,
        distance: Quantity,
        cosmo: CosmologyConfig,
        cz_err: Optional[Quantity] = None,
        distance_err: Optional[Quantity] = None,
        mu_err: Optional[float] = None,
        H0_err: Optional[Quantity] = None,
    ) -> PeculiarVelocityResult:
        cz = ensure_quantity(cz, u.km / u.s, "cz")
        distance = ensure_quantity(distance, u.Mpc, "distance")
        c_val = c_light.to(u.km / u.s)

        z_obs = (cz / c_val).decompose().value
        z_cos = redshift_from_comoving_distance(distance, cosmo)

        one_plus_z_pec = (1.0 + z_obs) / (1.0 + z_cos)
        z_pec = one_plus_z_pec - 1.0

        # Relativistic velocity addition formula
        v_rel = c_val * ((one_plus_z_pec**2 - 1.0) / (one_plus_z_pec**2 + 1.0))

        # Propagate uncertainty using linear approximation scaled
        H0 = cosmo.H0 * (u.km / (u.s * u.Mpc))
        uncertainty = None
        if mu_err is not None:
            uncertainty = propagate_lognormal_distance_modulus_uncertainty(
                distance=distance,
                mu_err=mu_err,
                H0=H0,
                cz_err=cz_err,
                H0_err=H0_err,
            )
        elif distance_err is not None or cz_err is not None:
            uncertainty = propagate_linear_velocity_uncertainty(
                cz_err=cz_err,
                distance=distance,
                distance_err=distance_err,
                H0=H0,
                H0_err=H0_err,
            )

        inputs = {
            "cz": quantity_to_dict(cz),
            "distance": quantity_to_dict(distance),
            "z_obs": z_obs,
            "z_cos": z_cos,
            "z_pec": z_pec,
            "cosmology": cosmo.cosmology_name,
        }

        return PeculiarVelocityResult(
            v_pec=v_rel.to(u.km / u.s),
            uncertainty=uncertainty,
            estimator_name="Cosmological Relativistic",
            formula="(1 + z_obs) = (1 + z_cos)(1 + z_pec), v_pec = c * ((1+z_pec)^2 - 1) / ((1+z_pec)^2 + 1)",
            inputs=inputs,
        )


def calculate_peculiar_velocity(
    cz: Quantity,
    distance: Quantity,
    cosmo: CosmologyConfig,
    method: str = "linear",
    cz_err: Optional[Quantity] = None,
    distance_err: Optional[Quantity] = None,
    mu_err: Optional[float] = None,
    H0_err: Optional[Quantity] = None,
) -> PeculiarVelocityResult:
    """Convenience function dispatching to chosen peculiar velocity estimator."""
    if method == "linear":
        estimator = LinearPeculiarVelocityEstimator()
    elif method in ("cosmological", "relativistic"):
        estimator = CosmologicalPeculiarVelocityEstimator()
    else:
        raise ValueError(f"Unknown peculiar velocity estimator method: '{method}'")

    return estimator.calculate(
        cz=cz,
        distance=distance,
        cosmo=cosmo,
        cz_err=cz_err,
        distance_err=distance_err,
        mu_err=mu_err,
        H0_err=H0_err,
    )
