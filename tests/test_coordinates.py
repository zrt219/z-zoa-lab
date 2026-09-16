"""Test coordinate transformations against IAU and astronomical references."""

import numpy as np
import pytest
import astropy.units as u
from research.coordinates.frames import CoordinateFrame
from research.coordinates.transforms import (
    icrs_to_galactic,
    galactic_to_icrs,
    galactic_to_supergalactic,
    supergalactic_to_galactic,
    spherical_to_cartesian,
    cartesian_to_spherical,
)


def test_galactic_center_iau_reference():
    """
    IAU definition of Galactic Center (l=0, b=0):
    J2000 RA ~ 17h45m37.224s (~266.405 deg), Dec ~ -28d56m10.23s (~ -28.936 deg).
    """
    l = 0.0 * u.deg
    b = 0.0 * u.deg
    ra, dec, _ = galactic_to_icrs(l, b)
    assert np.isclose(ra.value, 266.405, atol=0.01)
    assert np.isclose(dec.value, -28.936, atol=0.01)

    # Invert
    l_back, b_back, _ = icrs_to_galactic(ra, dec)
    l_deg = (l_back.value + 180.0) % 360.0 - 180.0
    assert np.isclose(l_deg, 0.0, atol=1e-6)
    assert np.isclose(b_back.value, 0.0, atol=1e-6)


def test_supergalactic_plane():
    """Points on the Supergalactic equator should transform to SGB = 0."""
    sgl = 120.0 * u.deg
    sgb = 0.0 * u.deg
    l, b, _ = supergalactic_to_galactic(sgl, sgb)
    sgl_back, sgb_back, _ = galactic_to_supergalactic(l, b)
    assert np.isclose(sgl_back.value, 120.0, atol=1e-6)
    assert np.isclose(sgb_back.value, 0.0, atol=1e-6)


def test_cartesian_spherical_invertibility():
    """Test 3D spherical <-> Cartesian roundtrip across diverse points."""
    np.random.seed(42)
    ras = np.random.uniform(0.0, 360.0, 20) * u.deg
    decs = np.random.uniform(-80.0, 80.0, 20) * u.deg
    dists = np.random.uniform(10.0, 200.0, 20) * u.Mpc

    for ra, dec, dist in zip(ras, decs, dists):
        x, y, z = spherical_to_cartesian(ra, dec, dist, frame=CoordinateFrame.ICRS)
        ra_rec, dec_rec, dist_rec = cartesian_to_spherical(x, y, z, frame=CoordinateFrame.ICRS)

        assert np.isclose(ra_rec.value, ra.value, atol=1e-9)
        assert np.isclose(dec_rec.value, dec.value, atol=1e-9)
        assert np.isclose(dist_rec.value, dist.value, atol=1e-9)
