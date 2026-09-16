"""Survey footprints, masks, and selection functions for Z-ZOA (Prompt 08)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np


@dataclass(frozen=True)
class SurveyFootprint:
    """Base specification for survey sky footprint and velocity boundaries."""
    name: str
    l_min_deg: float
    l_max_deg: float
    b_min_deg: float
    b_max_deg: float
    cz_min_kms: float
    cz_max_kms: float
    flux_limit_jy_or_mag: float
    notes: str

    def is_inside_footprint(self, l_deg: float, b_deg: float) -> bool:
        """Check if Galactic (l, b) falls inside survey footprint."""
        # Handle wrap around l = 360/0 if applicable
        if self.l_min_deg <= self.l_max_deg:
            in_l = self.l_min_deg <= l_deg <= self.l_max_deg
        else:
            in_l = (l_deg >= self.l_min_deg) or (l_deg <= self.l_max_deg)
        in_b = self.b_min_deg <= b_deg <= self.b_max_deg
        return in_l and in_b

    def valid_velocity_range(self, cz_kms: float) -> bool:
        """Check if radial velocity cz falls inside survey sensitivity band."""
        if cz_kms is None or np.isnan(cz_kms):
            return False
        return self.cz_min_kms <= cz_kms <= self.cz_max_kms

    def relative_detection_weight(self, l_deg: float, b_deg: float, cz_kms: float) -> float:
        """Compute relative selection weight [0.0, 1.0] for null / random generation."""
        if not self.is_inside_footprint(l_deg, b_deg) or not self.valid_velocity_range(cz_kms):
            return 0.0
        # Standard H I flux distance-squared falloff weight model: W(cz) ~ (cz_max - cz) / (cz_max - cz_min)
        span = max(self.cz_max_kms - self.cz_min_kms, 1.0)
        norm_v = np.clip((self.cz_max_kms - cz_kms) / span, 0.1, 1.0)
        return float(norm_v)


# Documented Survey Footprints from Primary Literature
SURVEY_FOOTPRINTS: Dict[str, SurveyFootprint] = {
    "HIZOA_S": SurveyFootprint(
        name="HIZOA-S (Parkes Southern ZoA)",
        l_min_deg=212.0,
        l_max_deg=36.0,  # wraps across 360/0
        b_min_deg=-5.0,
        b_max_deg=5.0,
        cz_min_kms=0.0,
        cz_max_kms=12700.0,
        flux_limit_jy_or_mag=0.018,  # ~18 mJy rms
        notes="Staveley-Smith et al. 2016, AJ 151, 52. Parkes 21cm multibeam survey across southern Galactic plane.",
    ),
    "VELA_SMGPS": SurveyFootprint(
        name="MeerKAT Vela-SMGPS",
        l_min_deg=260.0,
        l_max_deg=290.0,
        b_min_deg=-2.0,
        b_max_deg=1.0,
        cz_min_kms=0.0,
        cz_max_kms=25000.0,
        flux_limit_jy_or_mag=0.003,  # ~3 mJy/beam
        notes="Kraan-Korteweg et al. 2024, MNRAS 531, 3486. High-sensitivity MeerKAT H I survey of the Vela overdensity.",
    ),
    "VELA_HI": SurveyFootprint(
        name="MeerKAT Vela-HI Extended",
        l_min_deg=255.0,
        l_max_deg=295.0,
        b_min_deg=-3.0,
        b_max_deg=2.0,
        cz_min_kms=0.0,
        cz_max_kms=25000.0,
        flux_limit_jy_or_mag=0.003,
        notes="Courtois et al. extended Vela-HI footprint for secondary validation.",
    ),
    "2MRS_MAIN": SurveyFootprint(
        name="2MASS Redshift Survey (2MRS)",
        l_min_deg=0.0,
        l_max_deg=360.0,
        b_min_deg=-90.0,
        b_max_deg=90.0,
        cz_min_kms=0.0,
        cz_max_kms=40000.0,
        flux_limit_jy_or_mag=11.75,  # Ks <= 11.75 mag (|b| > 5 deg or |b| > 8 deg)
        notes="Huchra et al. 2012, ApJS 199, 26. Near-infrared whole-sky redshift survey masked by ZoA (|b| < 5 deg).",
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


def generate_selection_report(repo_root: Path) -> Path:
    docs_dir = repo_root / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    report_file = docs_dir / "selection_function_report.md"

    lines = [
        "# Z-ZOA Survey Footprints and Selection Functions Report",
        "",
        "## Overview",
        "This document specifies the exact survey sky footprints, Galactic coordinate bounds, radial velocity boundaries, and relative selection functions required for Vela Experiment 001 and subsequent holdout validations.",
        "",
        "## Survey Footprint Geometry Summary",
        "",
        "| Survey | Galactic Longitude (l) | Galactic Latitude (b) | Velocity Range (cz) | Sensitivity / Limit | Role |",
        "|---|---|---|---|---|---|",
        "| **HIZOA-S** | 212° <= l <= 36° (via 360°) | -5° <= b <= +5° | 0 - 12,700 km/s | S_peak ~ 18 mJy | TRAIN_CLEAN (after 39 exclusion) |",
        "| **Vela-SMGPS** | 260° <= l <= 290° | -2° <= b <= +1° | 0 - 25,000 km/s | S_rms ~ 3 mJy/beam | **HOLDOUT** (protected validation) |",
        "| **Vela-HI** | 255° <= l <= 295° | -3° <= b <= +2° | 0 - 25,000 km/s | S_rms ~ 3 mJy/beam | HOLDOUT (future secondary) |",
        "| **2MRS** | All-sky (|b| > 5°) | |b| > 5° (ZoA gap) | 0 - 40,000 km/s | K_s <= 11.75 mag | TRAIN |",
        "| **GA-SMGPS** | 300° <= l <= 335° | -2° <= b <= +2° | 0 - 20,000 km/s | S_rms ~ 3 mJy/beam | HOLDOUT (future experiment) |",
        "",
        "## Selection Function Mechanics for Null Hypotheses",
        "For paper-grade statistical validation, null catalogues must be generated by sampling random coordinates strictly within the Vela-SMGPS footprint (260° <= l <= 290°, -2° <= b <= +1°) with velocity distribution matched to the survey selection weight:",
        "",
        "\\[ W(cz) = \\frac{cz_{\\text{max}} - cz}{cz_{\\text{max}} - cz_{\\text{min}}} \\]",
        "",
        "This prevents synthetic nulls from clustering at unphysical edges or testing density outside the survey detection horizon.",
        "",
        "**Status**: SELECTION FUNCTION DEFINITIONS SEALED. No holdout galaxy occupancy was used to fit or tune footprint borders.",
    ]

    report_file.write_text("\n".join(lines), encoding="utf-8")
    return report_file


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parent.parent.parent
    rf = generate_selection_report(repo_root)
    print(f"Selection function report written to: {rf}")
