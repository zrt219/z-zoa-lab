"""Velocity reference frames and kinematic conversions."""

import math
from enum import Enum
from typing import Tuple
import astropy.units as u
from astropy.units import Quantity

from research.units.validation import ensure_quantity


class VelocityFrame(str, Enum):
    HELIOCENTRIC = "HELIOCENTRIC"
    LOCAL_GROUP = "LOCAL_GROUP"
    CMB = "CMB"


# Standard Planck 2018 / Fixsen et al. (1996) CMB dipole apex parameters
CMB_DIPOLE_V_APEX = 369.82 * (u.km / u.s)
CMB_DIPOLE_L = 264.021 * u.deg
CMB_DIPOLE_B = 48.253 * u.deg

# Standard Local Group apex (Yahil, Tammann & Sandage 1977 / Courteau & van den Bergh 1999)
LG_V_APEX = 316.0 * (u.km / u.s)
LG_L = 93.0 * u.deg
LG_B = -4.0 * u.deg


def heliocentric_to_cmb(
    v_helio: Quantity,
    l: Quantity,
    b: Quantity,
) -> Quantity:
    """
    Convert heliocentric radial velocity to CMB rest frame.
    v_CMB = v_hel + v_apex * [ sin(b) sin(b_apex) + cos(b) cos(b_apex) cos(l - l_apex) ]
    """
    v = ensure_quantity(v_helio, u.km / u.s, "v_helio")
    gal_l = ensure_quantity(l, u.deg, "l").to(u.rad).value
    gal_b = ensure_quantity(b, u.deg, "b").to(u.rad).value

    apex_l = CMB_DIPOLE_L.to(u.rad).value
    apex_b = CMB_DIPOLE_B.to(u.rad).value
    v_apex = CMB_DIPOLE_V_APEX.to(u.km / u.s).value

    # Dot product in Galactic spherical coordinates
    cos_theta = (
        math.sin(gal_b) * math.sin(apex_b)
        + math.cos(gal_b) * math.cos(apex_b) * math.cos(gal_l - apex_l)
    )
    v_correction = v_apex * cos_theta * (u.km / u.s)
    return (v + v_correction).to(u.km / u.s)


def cmb_to_heliocentric(
    v_cmb: Quantity,
    l: Quantity,
    b: Quantity,
) -> Quantity:
    """Convert CMB rest frame velocity back to heliocentric radial velocity."""
    v = ensure_quantity(v_cmb, u.km / u.s, "v_cmb")
    gal_l = ensure_quantity(l, u.deg, "l").to(u.rad).value
    gal_b = ensure_quantity(b, u.deg, "b").to(u.rad).value

    apex_l = CMB_DIPOLE_L.to(u.rad).value
    apex_b = CMB_DIPOLE_B.to(u.rad).value
    v_apex = CMB_DIPOLE_V_APEX.to(u.km / u.s).value

    cos_theta = (
        math.sin(gal_b) * math.sin(apex_b)
        + math.cos(gal_b) * math.cos(apex_b) * math.cos(gal_l - apex_l)
    )
    v_correction = v_apex * cos_theta * (u.km / u.s)
    return (v - v_correction).to(u.km / u.s)
