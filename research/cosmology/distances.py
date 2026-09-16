"""Cosmological distance computations adhering to FLRW metrics."""

import math
from typing import Optional, Tuple, Union
import numpy as np
import astropy.units as u
from astropy.units import Quantity
from scipy.optimize import brentq

from research.units.validation import ensure_quantity
from research.cosmology.models import CosmologyConfig


def comoving_distance(z: Union[float, np.ndarray], cosmo: CosmologyConfig) -> Quantity:
    """Calculate line-of-sight comoving distance d_C in Mpc."""
    astropy_cosmo = cosmo.to_astropy()
    return astropy_cosmo.comoving_distance(z).to(u.Mpc)


def luminosity_distance(z: Union[float, np.ndarray], cosmo: CosmologyConfig) -> Quantity:
    """Calculate luminosity distance d_L in Mpc."""
    astropy_cosmo = cosmo.to_astropy()
    return astropy_cosmo.luminosity_distance(z).to(u.Mpc)


def angular_diameter_distance(z: Union[float, np.ndarray], cosmo: CosmologyConfig) -> Quantity:
    """Calculate angular diameter distance d_A in Mpc."""
    astropy_cosmo = cosmo.to_astropy()
    return astropy_cosmo.angular_diameter_distance(z).to(u.Mpc)


def hubble_parameter(z: Union[float, np.ndarray], cosmo: CosmologyConfig) -> Quantity:
    """Calculate Hubble expansion rate H(z) in km s-1 Mpc-1."""
    astropy_cosmo = cosmo.to_astropy()
    return astropy_cosmo.H(z).to(u.km / (u.s * u.Mpc))


def distance_modulus_to_distance(
    mu: float,
    mu_err: Optional[float] = None
) -> Tuple[Quantity, Optional[Tuple[Quantity, Quantity]]]:
    """
    Convert distance modulus mu = m - M to luminosity/linear distance d in Mpc.
    d = 10^( (mu - 25) / 5 ) Mpc  (since mu = 5 log10(d_pc) - 5)
    If mu_err is provided, computes asymmetric log-normal linear distance errors:
      sigma_d_plus = d * (10^(mu_err / 5) - 1)
      sigma_d_minus = d * (1 - 10^(-mu_err / 5))
    """
    # d in pc = 10^((mu + 5)/5), in Mpc = 10^((mu - 25)/5)
    d_mpc = 10.0 ** ((mu - 25.0) / 5.0)
    d_quantity = d_mpc * u.Mpc

    if mu_err is not None:
        err_plus = d_mpc * (10.0 ** (mu_err / 5.0) - 1.0) * u.Mpc
        err_minus = d_mpc * (1.0 - 10.0 ** (-mu_err / 5.0)) * u.Mpc
        return d_quantity, (err_plus, err_minus)

    return d_quantity, None


def distance_to_distance_modulus(
    distance: Quantity,
    distance_err: Optional[Quantity] = None
) -> Tuple[float, Optional[float]]:
    """
    Convert luminosity distance d to distance modulus mu.
    mu = 5 log10(d_Mpc) + 25.
    If distance_err is provided, propagates symmetric approximation:
      sigma_mu = (5 / ln(10)) * (sigma_d / d) = 2.17147 * (sigma_d / d)
    """
    d = ensure_quantity(distance, u.Mpc, "distance").to(u.Mpc).value
    if d <= 0:
        raise ValueError("Distance must be strictly positive to compute distance modulus.")

    mu = 5.0 * math.log10(d) + 25.0

    if distance_err is not None:
        d_err = ensure_quantity(distance_err, u.Mpc, "distance_err").to(u.Mpc).value
        mu_err = (5.0 / math.log(10.0)) * (d_err / d)
        return mu, float(mu_err)

    return mu, None


def redshift_from_comoving_distance(distance: Quantity, cosmo: CosmologyConfig) -> float:
    """
    Numerically invert comoving distance d_C(z) to obtain cosmological redshift z_cos.
    Uses Brent's method.
    """
    d_target = ensure_quantity(distance, u.Mpc, "distance").to(u.Mpc).value
    if d_target <= 0:
        return 0.0

    astropy_cosmo = cosmo.to_astropy()

    def objective(z_val: float) -> float:
        return astropy_cosmo.comoving_distance(z_val).to(u.Mpc).value - d_target

    # Upper bracket search
    z_upper = 0.1
    while objective(z_upper) < 0 and z_upper < 20.0:
        z_upper *= 2.0

    z_sol = brentq(objective, 0.0, z_upper, xtol=1e-8)
    return float(z_sol)
