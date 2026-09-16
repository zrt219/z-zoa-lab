"""Survey footprints, masks, and first-order selection functions for Z-ZOA (Prompt 08).

Defines survey geometries, velocity boundaries, relative selection weights,
and 3D Zone of Avoidance (ZoA) obscuration masks for:
- HIZOA-S (Parkes Southern ZoA H I survey)
- Vela-SMGPS (MeerKAT Vela holdout survey)
- Vela-HI (MeerKAT Vela extended footprint)
- 2MRS (2MASS Redshift Survey with ZoA cut)
- CF4 (Cosmicflows-4 peculiar velocities and distance catalogue)
- GA-SMGPS (MeerKAT Great Attractor holdout survey)
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union
import numpy as np
import astropy.units as u
from astropy.coordinates import CartesianRepresentation, SkyCoord


@dataclass(frozen=True)
class SurveyFootprint:
    """Survey sky footprint and velocity completeness boundaries."""

    name: str
    l_min_deg: float
    l_max_deg: float
    b_min_deg: float
    b_max_deg: float
    cz_min_kms: float
    cz_max_kms: float
    flux_limit_jy_or_mag: float = 0.0
    is_all_sky: bool = False
    zoa_avoidance_deg: float = 0.0
    notes: str = ""

    def is_inside_footprint(self, l_deg: float, b_deg: float) -> bool:
        """Check if Galactic coordinates (l, b) fall inside survey footprint."""
        if l_deg is None or b_deg is None or np.isnan(l_deg) or np.isnan(b_deg):
            return False

        # Normalize longitude to [0, 360)
        l_norm = float(l_deg) % 360.0
        b_val = float(b_deg)

        if self.is_all_sky:
            if self.zoa_avoidance_deg > 0.0:
                return abs(b_val) > self.zoa_avoidance_deg
            return True

        # Latitude check
        if not (self.b_min_deg <= b_val <= self.b_max_deg):
            return False

        # Longitude check (handle wraparound across 360 / 0)
        if self.l_min_deg <= self.l_max_deg:
            return self.l_min_deg <= l_norm <= self.l_max_deg
        else:
            return (l_norm >= self.l_min_deg) or (l_norm <= self.l_max_deg)

    def valid_velocity_range(self, cz_kms: float) -> bool:
        """Check if radial velocity cz falls inside survey sensitivity range."""
        if cz_kms is None or np.isnan(cz_kms):
            return False
        return self.cz_min_kms <= float(cz_kms) <= self.cz_max_kms

    def relative_detection_weight(
        self,
        cz_kms: float,
        b_deg: float,
        l_deg: Optional[float] = None,
    ) -> float:
        """
        Compute relative selection weight in [0.0, 1.0].
        Incorporates radial distance falloff and Galactic extinction obscuration.
        """
        if not self.valid_velocity_range(cz_kms):
            return 0.0

        if l_deg is not None and not self.is_inside_footprint(l_deg, b_deg):
            return 0.0

        # Latitude factor
        if self.is_all_sky and self.zoa_avoidance_deg > 0.0:
            if abs(b_deg) <= self.zoa_avoidance_deg:
                return 0.0
            # Extinction decreases with distance from galactic plane |b|
            lat_factor = min(1.0, (abs(b_deg) - self.zoa_avoidance_deg) / 10.0 + 0.3)
        else:
            if not (self.b_min_deg <= b_deg <= self.b_max_deg):
                return 0.0
            lat_factor = 1.0

        # Velocity completeness falloff
        span = max(self.cz_max_kms - self.cz_min_kms, 1.0)
        norm_v = np.clip((self.cz_max_kms - float(cz_kms)) / span, 0.05, 1.0)

        return float(np.clip(lat_factor * norm_v, 0.0, 1.0))


# Standard Survey Footprints & Selection Models
SURVEY_FOOTPRINTS: Dict[str, SurveyFootprint] = {
    "HIZOA": SurveyFootprint(
        name="HIZOA (Parkes Southern ZoA)",
        l_min_deg=210.0,
        l_max_deg=30.0,  # wraps across 360/0: 210 <= l <= 360 and 0 <= l <= 30
        b_min_deg=-5.0,
        b_max_deg=5.0,
        cz_min_kms=0.0,
        cz_max_kms=12000.0,
        flux_limit_jy_or_mag=0.018,
        notes="Staveley-Smith et al. 2016, AJ 151, 52. |b| <= 5 deg, 210 deg <= l <= 30 deg, cz <= 12,000 km/s.",
    ),
    "HIZOA_S": SurveyFootprint(
        name="HIZOA-S (Parkes Southern ZoA Extended)",
        l_min_deg=210.0,
        l_max_deg=36.0,
        b_min_deg=-5.0,
        b_max_deg=5.0,
        cz_min_kms=0.0,
        cz_max_kms=12700.0,
        flux_limit_jy_or_mag=0.018,
        notes="Full HIZOA southern sample catalog specification.",
    ),
    "VELA_SMGPS": SurveyFootprint(
        name="MeerKAT Vela-SMGPS",
        l_min_deg=260.0,
        l_max_deg=290.0,
        b_min_deg=-2.0,
        b_max_deg=1.0,
        cz_min_kms=0.0,
        cz_max_kms=25000.0,
        flux_limit_jy_or_mag=0.003,
        notes="Kraan-Korteweg et al. 2024, MNRAS 531, 3486. High-sensitivity MeerKAT H I survey of the Vela overdensity.",
    ),
    "VELA_HI": SurveyFootprint(
        name="MeerKAT Vela-HI Extended",
        l_min_deg=263.0,
        l_max_deg=284.0,
        b_min_deg=-3.0,
        b_max_deg=2.0,
        cz_min_kms=0.0,
        cz_max_kms=25000.0,
        flux_limit_jy_or_mag=0.003,
        notes="Vela-HI extended footprint: 263 deg <= l <= 284 deg, extended latitude, cz <= 25,000 km/s.",
    ),
    "2MRS": SurveyFootprint(
        name="2MASS Redshift Survey (2MRS)",
        l_min_deg=0.0,
        l_max_deg=360.0,
        b_min_deg=-90.0,
        b_max_deg=90.0,
        cz_min_kms=0.0,
        cz_max_kms=15000.0,
        is_all_sky=True,
        zoa_avoidance_deg=5.0,
        flux_limit_jy_or_mag=11.75,
        notes="Huchra et al. 2012, ApJS 199, 26. Near-infrared all-sky mask, |b| > 5 deg, cz <= 15,000 km/s.",
    ),
    "CF4": SurveyFootprint(
        name="Cosmicflows-4 (CF4)",
        l_min_deg=0.0,
        l_max_deg=360.0,
        b_min_deg=-90.0,
        b_max_deg=90.0,
        cz_min_kms=0.0,
        cz_max_kms=30000.0,
        is_all_sky=True,
        zoa_avoidance_deg=5.0,
        flux_limit_jy_or_mag=0.0,
        notes="Tully et al. 2023, ApJ 944, 94. CF4 peculiar velocity and distance catalogue completeness.",
    ),
    "GA_SMGPS": SurveyFootprint(
        name="MeerKAT GA-SMGPS (Great Attractor)",
        l_min_deg=300.0,
        l_max_deg=335.0,
        b_min_deg=-2.0,
        b_max_deg=2.0,
        cz_min_kms=0.0,
        cz_max_kms=20000.0,
        flux_limit_jy_or_mag=0.003,
        notes="Steyn et al. 2024, MNRAS Letters 529, L88. MeerKAT survey across the Great Attractor ZoA core.",
    ),
}


def get_survey_footprint(survey_name: str) -> SurveyFootprint:
    """Resolve survey footprint by name or common alias."""
    key = survey_name.strip().upper().replace("-", "_").replace(" ", "_")
    if key in SURVEY_FOOTPRINTS:
        return SURVEY_FOOTPRINTS[key]

    alias_map = {
        "HIZOA_SOUTH": "HIZOA",
        "HIZOA_S_FULL": "HIZOA",
        "VELA": "VELA_SMGPS",
        "VELA_SMGPS_SAMPLE": "VELA_SMGPS",
        "VELA_EXTENDED": "VELA_HI",
        "2MASS": "2MRS",
        "2MRS_MAIN": "2MRS",
        "2MRS_SAMPLE": "2MRS",
        "COSMICFLOWS4": "CF4",
        "CF4_SAMPLE": "CF4",
        "GREAT_ATTRACTOR": "GA_SMGPS",
    }
    if key in alias_map:
        return SURVEY_FOOTPRINTS[alias_map[key]]

    raise KeyError(f"Unknown survey footprint: '{survey_name}'. Available: {list(SURVEY_FOOTPRINTS.keys())}")


def is_inside_footprint(survey_name: str, l_deg: float, b_deg: float) -> bool:
    """Check if Galactic (l, b) coordinates fall within the given survey's sky footprint."""
    fp = get_survey_footprint(survey_name)
    return fp.is_inside_footprint(l_deg, b_deg)


def valid_velocity_range(survey_name: str, cz_kms: float) -> bool:
    """Check if radial velocity cz falls inside the given survey's sensitivity band."""
    fp = get_survey_footprint(survey_name)
    return fp.valid_velocity_range(cz_kms)


def relative_detection_weight(
    survey_name: str,
    cz_kms: float,
    b_deg: float,
    l_deg: Optional[float] = None,
) -> float:
    """Compute relative detection weight [0.0, 1.0] for the specified survey."""
    fp = get_survey_footprint(survey_name)
    return fp.relative_detection_weight(cz_kms=cz_kms, b_deg=b_deg, l_deg=l_deg)


def zoa_obscuration_mask(
    grid_shape: Union[int, Tuple[int, int, int]],
    box_size_mpc: Union[float, Tuple[float, float, float]],
    b_cut_deg: float = 5.0,
    frame: str = "supergalactic",
) -> np.ndarray:
    """
    Generate a 3D boolean obscuration mask for the Galactic Zone of Avoidance (|b| <= b_cut_deg).
    Returns True for voxels obscured by the Galactic plane, False for unmasked / visible volume.

    Parameters:
    -----------
    grid_shape: int or (nx, ny, nz) grid dimensions.
    box_size_mpc: float or (lx, ly, lz) cosmological box physical size in Mpc (observer at center).
    b_cut_deg: Galactic latitude cutoff angle (default 5.0 deg).
    frame: Coordinate frame of the Cartesian grid ('supergalactic' or 'galactic').
    """
    if isinstance(grid_shape, (int, np.integer)):
        nx = ny = nz = int(grid_shape)
    else:
        nx, ny, nz = int(grid_shape[0]), int(grid_shape[1]), int(grid_shape[2])

    if isinstance(box_size_mpc, (int, float, np.floating)):
        lx = ly = lz = float(box_size_mpc)
    else:
        lx, ly, lz = float(box_size_mpc[0]), float(box_size_mpc[1]), float(box_size_mpc[2])

    # Voxel centers spanning [-L/2, +L/2]
    x_coords = np.linspace(-lx / 2.0 + lx / (2.0 * nx), lx / 2.0 - lx / (2.0 * nx), nx)
    y_coords = np.linspace(-ly / 2.0 + ly / (2.0 * ny), ly / 2.0 - ly / (2.0 * ny), ny)
    z_coords = np.linspace(-lz / 2.0 + lz / (2.0 * nz), lz / 2.0 - lz / (2.0 * nz), nz)

    xx, yy, zz = np.meshgrid(x_coords, y_coords, z_coords, indexing="ij")

    frame_clean = frame.lower().strip()
    if frame_clean == "supergalactic":
        flat_x = xx.ravel()
        flat_y = yy.ravel()
        flat_z = zz.ravel()

        cart = CartesianRepresentation(flat_x * u.Mpc, flat_y * u.Mpc, flat_z * u.Mpc)
        coord = SkyCoord(cart, frame="supergalactic")
        b_deg = np.array(coord.galactic.b.deg).reshape((nx, ny, nz))
        # Voxels exactly at origin (0, 0, 0) are at the observer location
        r = np.sqrt(xx**2 + yy**2 + zz**2)
        b_deg[r < 1e-6] = 0.0
    elif frame_clean == "galactic":
        r = np.sqrt(xx**2 + yy**2 + zz**2)
        safe_r = np.maximum(r, 1e-12)
        sin_b = np.clip(zz / safe_r, -1.0, 1.0)
        b_deg = np.degrees(np.arcsin(sin_b))
        b_deg[r < 1e-6] = 0.0
    else:
        raise ValueError(f"Unsupported frame for zoa_obscuration_mask: '{frame}'. Use 'supergalactic' or 'galactic'.")

    return np.abs(b_deg) <= b_cut_deg
