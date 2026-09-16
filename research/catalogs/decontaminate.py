"""Cross-matching and holdout decontamination for Zone of Avoidance catalogues."""

from typing import Tuple, List, Dict, Any
import numpy as np
import polars as pl
import astropy.units as u
from astropy.coordinates import SkyCoord


def cross_match_and_decontaminate(
    candidate_df: pl.DataFrame,
    holdout_df: pl.DataFrame,
    ra_col: str = "ra",
    dec_col: str = "dec",
    cz_col: str = "cz",
    angular_sep_arcmin: float = 3.0,
    velocity_sep_kms: float = 150.0,
) -> Tuple[pl.DataFrame, pl.DataFrame, List[Dict[str, Any]]]:
    """
    Cross-match candidate survey galaxies (e.g. HIZOA-S) against a protected holdout
    catalogue (e.g. Vela-SMGPS) by sky position and radial velocity.
    Removes overlapping detections to prevent leakage into reconstruction.

    Returns:
      (clean_df, contaminated_df, match_audit_records)
    """
    if candidate_df.height == 0 or holdout_df.height == 0:
        return candidate_df, candidate_df.clear(), []

    # Build SkyCoords
    cand_ra = candidate_df[ra_col].to_numpy()
    cand_dec = candidate_df[dec_col].to_numpy()
    cand_coords = SkyCoord(ra=cand_ra * u.deg, dec=cand_dec * u.deg, frame="icrs")

    hold_ra = holdout_df[ra_col].to_numpy()
    hold_dec = holdout_df[dec_col].to_numpy()
    hold_coords = SkyCoord(ra=hold_ra * u.deg, dec=hold_dec * u.deg, frame="icrs")

    cand_cz = candidate_df[cz_col].to_numpy() if cz_col in candidate_df.columns else None
    hold_cz = holdout_df[cz_col].to_numpy() if cz_col in holdout_df.columns else None

    # Perform nearest neighbor match
    idx, sep2d, _ = cand_coords.match_to_catalog_sky(hold_coords)
    sep_arcmin = sep2d.arcminute

    is_match = sep_arcmin <= angular_sep_arcmin

    if cand_cz is not None and hold_cz is not None:
        v_diff = np.abs(cand_cz - hold_cz[idx])
        is_match = is_match & (v_diff <= velocity_sep_kms)

    contaminated_indices = np.where(is_match)[0].tolist()
    clean_indices = np.where(~is_match)[0].tolist()

    audit_records = []
    for i in contaminated_indices:
        match_idx = idx[i]
        audit_records.append({
            "candidate_index": int(i),
            "holdout_index": int(match_idx),
            "angular_separation_arcmin": float(sep_arcmin[i]),
            "velocity_diff_kms": float(abs(cand_cz[i] - hold_cz[match_idx])) if cand_cz is not None else None,
        })

    clean_df = candidate_df[clean_indices]
    contaminated_df = candidate_df[contaminated_indices]

    return clean_df, contaminated_df, audit_records
