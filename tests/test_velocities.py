"""Test peculiar velocity calculations, frame transformations, and errors."""

import numpy as np
import pytest
import astropy.units as u
from research.cosmology.models import COSMOLOGY_PRESETS
from research.velocities.peculiar import (
    calculate_peculiar_velocity,
    LinearPeculiarVelocityEstimator,
    CosmologicalPeculiarVelocityEstimator,
)
from research.velocities.frames import (
    heliocentric_to_cmb,
    cmb_to_heliocentric,
    CMB_DIPOLE_V_APEX,
    CMB_DIPOLE_L,
    CMB_DIPOLE_B,
)
from research.velocities.uncertainties import (
    propagate_linear_velocity_uncertainty,
    propagate_lognormal_distance_modulus_uncertainty,
)


def test_linear_peculiar_velocity():
    cosmo = COSMOLOGY_PRESETS["CF4_NOMINAL"]  # H0 = 74.6
    cz = 5801.0 * (u.km / u.s)
    distance = 71.42 * u.Mpc

    # Expected: 5801 - 74.6 * 71.42 = 5801 - 5327.932 = 473.068 km/s
    res = calculate_peculiar_velocity(
        cz=cz,
        distance=distance,
        cosmo=cosmo,
        method="linear",
    )
    assert np.isclose(res.v_pec.value, 473.068, atol=0.1)
    assert res.v_pec.unit == u.km / u.s


def test_cosmological_peculiar_velocity():
    cosmo = COSMOLOGY_PRESETS["CF4_NOMINAL"]
    cz = 5801.0 * (u.km / u.s)
    distance = 71.42 * u.Mpc

    res_rel = calculate_peculiar_velocity(
        cz=cz,
        distance=distance,
        cosmo=cosmo,
        method="cosmological",
    )
    # At modest redshift, cosmological and linear should be within ~20 km/s
    assert abs(res_rel.v_pec.value - 473.0) < 30.0


def test_uncertainty_propagation():
    # Linear uncertainty: sigma_cz = 20 km/s, sigma_d = 2 Mpc, H0 = 74.6
    # sigma_v = sqrt(20^2 + (74.6 * 2)^2) = sqrt(400 + 22260.64) = 150.53 km/s
    err = propagate_linear_velocity_uncertainty(
        cz_err=20.0 * (u.km / u.s),
        distance=50.0 * u.Mpc,
        distance_err=2.0 * u.Mpc,
        H0=74.6 * (u.km / (u.s * u.Mpc)),
    )
    assert np.isclose(err.value, 150.53, atol=0.1)

    # Log-normal distance modulus error:
    # sigma_v ~= 0.461517 * H0 * d * sigma_mu
    # For d=50 Mpc, H0=74.6, sigma_mu=0.15:
    # 0.461517 * 74.6 * 50 * 0.15 ~= 258.2 km/s
    err_mu = propagate_lognormal_distance_modulus_uncertainty(
        distance=50.0 * u.Mpc,
        mu_err=0.15,
        H0=74.6 * (u.km / (u.s * u.Mpc)),
    )
    expected_err_mu = (np.log(10.0) / 5.0) * 74.6 * 50.0 * 0.15
    assert np.isclose(err_mu.value, expected_err_mu, atol=1e-5)


def test_cmb_dipole_frame_correction():
    # Exactly along apex:
    v_helio = 1000.0 * (u.km / u.s)
    v_cmb = heliocentric_to_cmb(v_helio, CMB_DIPOLE_L, CMB_DIPOLE_B)
    expected = v_helio + CMB_DIPOLE_V_APEX
    assert np.isclose(v_cmb.value, expected.value, atol=1e-3)

    # Invert
    v_helio_back = cmb_to_heliocentric(v_cmb, CMB_DIPOLE_L, CMB_DIPOLE_B)
    assert np.isclose(v_helio_back.value, v_helio.value, atol=1e-3)
