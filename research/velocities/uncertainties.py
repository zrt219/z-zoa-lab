"""Uncertainty propagation for cosmological velocities."""

import math
from typing import Optional
import astropy.units as u
from astropy.units import Quantity

from research.units.validation import ensure_quantity


def propagate_linear_velocity_uncertainty(
    cz_err: Optional[Quantity],
    distance: Quantity,
    distance_err: Optional[Quantity],
    H0: Quantity,
    H0_err: Optional[Quantity] = None,
) -> Quantity:
    """
    Propagate standard linear uncertainty for v_pec = cz - H0 * d:
    sigma_v^2 = sigma_cz^2 + (H0 * sigma_d)^2 + (d * sigma_H0)^2
    """
    d = ensure_quantity(distance, u.Mpc, "distance")
    h0 = ensure_quantity(H0, u.km / (u.s * u.Mpc), "H0")

    var = 0.0 * (u.km / u.s)**2

    if cz_err is not None:
        c_err = ensure_quantity(cz_err, u.km / u.s, "cz_err")
        var += c_err**2

    if distance_err is not None:
        d_err = ensure_quantity(distance_err, u.Mpc, "distance_err")
        var += (h0 * d_err)**2

    if H0_err is not None:
        h_err = ensure_quantity(H0_err, u.km / (u.s * u.Mpc), "H0_err")
        var += (d * h_err)**2

    return (math.sqrt(var.value) * var.unit**0.5).to(u.km / u.s)


def propagate_lognormal_distance_modulus_uncertainty(
    distance: Quantity,
    mu_err: float,
    H0: Quantity,
    cz_err: Optional[Quantity] = None,
    H0_err: Optional[Quantity] = None,
) -> Quantity:
    """
    Propagate peculiar velocity uncertainty when distance is derived from distance modulus mu:
    sigma_v_dist = (ln(10) / 5) * H0 * d * sigma_mu ~= 0.461517 * H0 * d * sigma_mu.
    Total sigma_v^2 = sigma_cz^2 + sigma_v_dist^2 + (d * sigma_H0)^2.
    """
    d = ensure_quantity(distance, u.Mpc, "distance")
    h0 = ensure_quantity(H0, u.km / (u.s * u.Mpc), "H0")

    var = 0.0 * (u.km / u.s)**2

    if cz_err is not None:
        c_err = ensure_quantity(cz_err, u.km / u.s, "cz_err")
        var += c_err**2

    # Distance uncertainty from mu_err
    scale_factor = math.log(10.0) / 5.0  # ~0.4615170186
    v_dist_err = scale_factor * h0 * d * mu_err
    var += v_dist_err.to(u.km / u.s)**2

    if H0_err is not None:
        h_err = ensure_quantity(H0_err, u.km / (u.s * u.Mpc), "H0_err")
        var += (d * h_err.to(u.km / (u.s * u.Mpc)))**2

    return (math.sqrt(var.value) * var.unit**0.5).to(u.km / u.s)
