"""Test cosmological distance measures and parameters."""

import numpy as np
import pytest
import astropy.units as u
from astropy.cosmology import Planck18, FlatLambdaCDM
from research.cosmology.models import CosmologyConfig, COSMOLOGY_PRESETS, UnphysicalCosmologyError
from research.cosmology.distances import (
    comoving_distance,
    luminosity_distance,
    angular_diameter_distance,
    hubble_parameter,
    distance_modulus_to_distance,
    distance_to_distance_modulus,
    redshift_from_comoving_distance,
)


def test_cosmology_config_validation():
    # Valid
    cfg = CosmologyConfig(cosmology_name="Test", H0=70.0, Om0=0.3, reference="Test Ref")
    assert cfg.H0 == 70.0

    # Invalid H0
    with pytest.raises(ValueError, match="Unphysical Hubble constant"):
        CosmologyConfig(cosmology_name="BadH0", H0=200.0, Om0=0.3, reference="Test")


def test_distances_against_astropy_planck18():
    cfg = COSMOLOGY_PRESETS["PLANCK18"]
    test_z = [0.01, 0.05, 0.1, 0.5]

    astropy_flat = FlatLambdaCDM(H0=67.66 * (u.km / (u.s * u.Mpc)), Om0=0.30966)
    for z in test_z:
        # Comoving distance
        dc = comoving_distance(z, cfg)
        expected_dc = astropy_flat.comoving_distance(z).to(u.Mpc)
        assert np.isclose(dc.value, expected_dc.value, rtol=1e-6)

        # Luminosity distance: d_L = (1 + z) * d_C
        dl = luminosity_distance(z, cfg)
        expected_dl = (1.0 + z) * expected_dc
        assert np.isclose(dl.value, expected_dl.value, rtol=1e-6)

        # Angular diameter distance: d_A = d_C / (1 + z)
        da = angular_diameter_distance(z, cfg)
        expected_da = expected_dc / (1.0 + z)
        assert np.isclose(da.value, expected_da.value, rtol=1e-6)


def test_distance_modulus_inversion():
    # d = 10 pc -> mu = 0
    d_10pc = 0.00001 * u.Mpc
    mu, _ = distance_to_distance_modulus(d_10pc)
    assert np.isclose(mu, 0.0, atol=1e-4)

    # d = 100 Mpc -> mu = 35.0
    d_100mpc = 100.0 * u.Mpc
    mu_100, _ = distance_to_distance_modulus(d_100mpc)
    assert np.isclose(mu_100, 35.0, atol=1e-4)

    # Invert mu=35.0
    d_rec, errs = distance_modulus_to_distance(35.0, mu_err=0.2)
    assert np.isclose(d_rec.value, 100.0, atol=1e-4)
    assert errs is not None
    err_plus, err_minus = errs
    assert err_plus.value > 0
    assert err_minus.value > 0
    # Asymmetric: err_plus > err_minus for log-normal
    assert err_plus.value > err_minus.value


def test_redshift_inversion():
    cfg = COSMOLOGY_PRESETS["CF4_NOMINAL"]
    target_dist = 100.0 * u.Mpc
    z_sol = redshift_from_comoving_distance(target_dist, cfg)
    dc_check = comoving_distance(z_sol, cfg)
    assert np.isclose(dc_check.value, 100.0, atol=1e-4)


def test_unphysical_cosmology_error_definition():
    """Verify UnphysicalCosmologyError inherits from ValueError and can be raised."""
    with pytest.raises(UnphysicalCosmologyError, match="exceeds cosmic infall limits"):
        raise UnphysicalCosmologyError("Velocity v = 95000 km/s exceeds cosmic infall limits (v_max <= 2500 km/s).")

