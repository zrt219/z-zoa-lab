"""Deterministic normalization pipeline for astronomical catalogues."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np
import polars as pl
import astropy.units as u
from astropy.coordinates import SkyCoord, Supergalactic

from research.coordinates.transforms import icrs_to_galactic, galactic_to_supergalactic
from research.catalogs.registry import CatalogRegistry
from research.catalogs.schema import DatasetMetadata


C_KMS = 299792.458  # speed of light in km/s


def normalize_dataset(
    metadata: DatasetMetadata,
    base_dir: Path,
    output_dir: Optional[Path] = None,
) -> Path:
    """
    Normalize raw catalogue to standard schema:
    source_row_id, canonical_object_id, ra_deg, dec_deg,
    gal_l_deg, gal_b_deg, sgl_deg, sgb_deg,
    cz_value_kms, cz_frame, redshift,
    distance_mpc, distance_err_mpc,
    distance_modulus, distance_modulus_err,
    hi_flux, w50_kms, survey, release, quality_flags.
    """
    if output_dir is None:
        output_dir = base_dir / "datasets" / "processed" / "normalized"
    output_dir.mkdir(parents=True, exist_ok=True)

    input_path = base_dir / metadata.file_path

    # Read input file
    if input_path.suffix == ".parquet":
        raw_df = pl.read_parquet(input_path)
    elif input_path.suffix == ".csv":
        # Handle comment lines
        raw_df = pl.read_csv(input_path, comment_prefix="#")
    else:
        raise ValueError(f"Unsupported format: {input_path.suffix}")

    d_id = metadata.dataset_id
    n_rows = raw_df.height

    # Parse columns based on known dataset schemas
    if d_id == "cf4_sample":
        source_row_ids = [f"CF4_{i:06d}" for i in range(n_rows)]
        canonical_ids = [str(p) for p in raw_df["pgc"].to_list()]
        ra = raw_df["ra"].to_numpy()
        dec = raw_df["dec"].to_numpy()
        cz = raw_df["cz_obs"].to_numpy()
        cz_frame = ["HELIOCENTRIC"] * n_rows
        dist_mpc = raw_df["distance_mpc"].to_numpy()
        dist_err_mpc = [None] * n_rows
        mu = raw_df["dist_modulus_mu"].to_numpy()
        mu_err = raw_df["mu_err"].to_numpy()
        hi_flux = [None] * n_rows
        w50 = [None] * n_rows
        quality_flags = ["OK"] * n_rows

    elif d_id == "hizoa_s_sample":
        source_row_ids = [f"HIZOA_{i:06d}" for i in range(n_rows)]
        canonical_ids = raw_df["source_id"].to_list()
        ra = raw_df["ra"].to_numpy()
        dec = raw_df["dec"].to_numpy()
        cz = raw_df["cz"].to_numpy()
        cz_frame = ["HELIOCENTRIC"] * n_rows
        dist_mpc = [None] * n_rows
        dist_err_mpc = [None] * n_rows
        mu = [None] * n_rows
        mu_err = [None] * n_rows
        hi_flux = [None] * n_rows
        w50 = raw_df["w50"].to_numpy()
        quality_flags = ["OK"] * n_rows

    elif d_id == "hizoa_s_full":
        source_row_ids = [f"HIZOA_{i:06d}" for i in range(n_rows)]
        canonical_ids = [str(r).strip() for r in raw_df["HIZOA"].to_list()]
        ra_raw = [str(r).strip() for r in raw_df["RAJ2000"].to_list()]
        dec_raw = [str(r).strip() for r in raw_df["DEJ2000"].to_list()]
        h_coords = SkyCoord(ra_raw, dec_raw, unit=(u.hourangle, u.deg), frame="icrs")
        ra = h_coords.ra.deg
        dec = h_coords.dec.deg
        cz = raw_df["HRV"].cast(pl.Float64, strict=False).to_numpy()
        cz_frame = ["HELIOCENTRIC"] * n_rows
        dist_mpc = raw_df["Dist"].cast(pl.Float64, strict=False).to_numpy() if "Dist" in raw_df.columns else [None] * n_rows
        dist_err_mpc = [None] * n_rows
        mu = [None] * n_rows
        mu_err = [None] * n_rows
        hi_flux = raw_df["FHI"].cast(pl.Float64, strict=False).to_numpy() if "FHI" in raw_df.columns else [None] * n_rows
        w50 = raw_df["W50"].cast(pl.Float64, strict=False).to_numpy()
        quality_flags = ["OK"] * n_rows

    elif d_id == "2mrs_sample":
        source_row_ids = [f"2MRS_{i:06d}" for i in range(n_rows)]
        canonical_ids = [str(r).strip() for r in raw_df["ID"].to_list()]
        ra = raw_df["RAJ2000"].cast(pl.Float64, strict=False).to_numpy()
        dec = raw_df["DEJ2000"].cast(pl.Float64, strict=False).to_numpy()
        cz = raw_df["cz"].cast(pl.Float64, strict=False).to_numpy()
        cz_frame = ["HELIOCENTRIC"] * n_rows
        dist_mpc = [None] * n_rows
        dist_err_mpc = [None] * n_rows
        mu = [None] * n_rows
        mu_err = [None] * n_rows
        hi_flux = [None] * n_rows
        w50 = [None] * n_rows
        quality_flags = ["OK"] * n_rows

    elif d_id == "vela_smgps_sample":
        source_row_ids = [f"VELA_{i:06d}" for i in range(n_rows)]
        canonical_ids = raw_df["source_id"].to_list()
        ra = raw_df["ra"].to_numpy()
        dec = raw_df["dec"].to_numpy()
        cz = raw_df["cz"].to_numpy()
        cz_frame = ["HELIOCENTRIC"] * n_rows
        dist_mpc = [None] * n_rows
        dist_err_mpc = [None] * n_rows
        mu = [None] * n_rows
        mu_err = [None] * n_rows
        hi_flux = [None] * n_rows
        w50 = [None] * n_rows
        quality_flags = [f"SNR={snr:.1f}" for snr in raw_df["snr"].to_list()]

    elif d_id == "ga_smgps_477":
        source_row_ids = [f"GA_{i:06d}" for i in range(n_rows)]
        canonical_ids = [str(x).strip() for x in raw_df["Name"].to_list()]
        ra = raw_df["_RA.icrs"].cast(pl.Float64, strict=False).to_numpy()
        dec = raw_df["_DE.icrs"].cast(pl.Float64, strict=False).to_numpy()
        cz = raw_df["HRV"].cast(pl.Float64, strict=False).to_numpy()
        cz_frame = ["HELIOCENTRIC"] * n_rows
        dist_mpc = [None] * n_rows
        dist_err_mpc = [None] * n_rows
        mu = [None] * n_rows
        mu_err = [None] * n_rows
        hi_flux = raw_df["Fint"].cast(pl.Float64, strict=False).to_numpy()
        w50 = raw_df["W50"].cast(pl.Float64, strict=False).to_numpy()
        quality_flags = ["OK"] * n_rows

    elif d_id == "wallaby_dr2":
        source_row_ids = [f"WALLABY_{i:06d}" for i in range(n_rows)]
        canonical_ids = [str(x).strip() for x in raw_df["name"].to_list()]
        ra = raw_df["ra"].cast(pl.Float64, strict=False).to_numpy()
        dec = raw_df["dec"].cast(pl.Float64, strict=False).to_numpy()
        # wallaby freq to cz: cz = c * (1420.40575 - freq) / freq
        freq = raw_df["freq"].cast(pl.Float64, strict=False).to_numpy()
        cz = C_KMS * (1420.40575 - freq) / freq
        cz_frame = ["BARYCENTRIC"] * n_rows
        dist_mpc = [None] * n_rows
        dist_err_mpc = [None] * n_rows
        mu = [None] * n_rows
        mu_err = [None] * n_rows
        hi_flux = [None] * n_rows
        w50 = raw_df["w50"].cast(pl.Float64, strict=False).to_numpy()
        quality_flags = ["OK"] * n_rows
    else:
        # Generic fallback
        source_row_ids = [f"{d_id}_{i:06d}" for i in range(n_rows)]
        canonical_ids = [str(i) for i in range(n_rows)]
        ra = np.zeros(n_rows)
        dec = np.zeros(n_rows)
        cz = np.zeros(n_rows)
        cz_frame = ["UNKNOWN"] * n_rows
        dist_mpc = [None] * n_rows
        dist_err_mpc = [None] * n_rows
        mu = [None] * n_rows
        mu_err = [None] * n_rows
        hi_flux = [None] * n_rows
        w50 = [None] * n_rows
        quality_flags = ["UNKNOWN"] * n_rows

    # Coordinate transformation using Astropy
    coords = SkyCoord(ra=ra * u.deg, dec=dec * u.deg, frame="icrs")
    gal = coords.galactic
    sgal = coords.transform_to(Supergalactic())

    gal_l = gal.l.deg
    gal_b = gal.b.deg
    sgl = sgal.sgl.deg
    sgb = sgal.sgb.deg

    # Redshift
    redshift = [float(v / C_KMS) if v is not None and not np.isnan(v) else None for v in cz]

    norm_df = pl.DataFrame({
        "source_row_id": source_row_ids,
        "canonical_object_id": canonical_ids,
        "ra_deg": [float(x) for x in ra],
        "dec_deg": [float(x) for x in dec],
        "gal_l_deg": [float(x) for x in gal_l],
        "gal_b_deg": [float(x) for x in gal_b],
        "sgl_deg": [float(x) for x in sgl],
        "sgb_deg": [float(x) for x in sgb],
        "cz_value_kms": [float(x) if x is not None and not np.isnan(x) else None for x in cz],
        "cz_frame": cz_frame,
        "redshift": redshift,
        "distance_mpc": [float(x) if x is not None and not np.isnan(x) else None for x in dist_mpc],
        "distance_err_mpc": dist_err_mpc,
        "distance_modulus": [float(x) if x is not None and not np.isnan(x) else None for x in mu],
        "distance_modulus_err": [float(x) if x is not None and not np.isnan(x) else None for x in mu_err],
        "hi_flux": [float(x) if x is not None and not np.isnan(x) else None for x in hi_flux],
        "w50_kms": [float(x) if x is not None and not np.isnan(x) else None for x in w50],
        "survey": [metadata.survey] * n_rows,
        "release": [metadata.release] * n_rows,
        "quality_flags": quality_flags,
    })

    out_file = output_dir / f"{d_id}_normalized.parquet"
    norm_df.write_parquet(out_file)

    # Write per-dataset normalization report
    rep_file = output_dir / f"{d_id}_normalization_report.md"
    with rep_file.open("w", encoding="utf-8") as f:
        f.write(f"# Normalization Report: {metadata.dataset_id}\n\n")
        f.write(f"- Survey: {metadata.survey}\n")
        f.write(f"- Release: {metadata.release}\n")
        f.write(f"- Input rows: {n_rows}\n")
        f.write(f"- Output rows: {norm_df.height}\n")
        f.write(f"- Normalized output: `{out_file.name}`\n")
        f.write(f"- Output columns: {', '.join(norm_df.columns)}\n")
        f.write(f"- RA range: [{norm_df['ra_deg'].min():.4f}, {norm_df['ra_deg'].max():.4f}] deg\n")
        f.write(f"- Dec range: [{norm_df['dec_deg'].min():.4f}, {norm_df['dec_deg'].max():.4f}] deg\n")
        f.write(f"- Galactic l range: [{norm_df['gal_l_deg'].min():.4f}, {norm_df['gal_l_deg'].max():.4f}] deg\n")
        f.write(f"- Galactic b range: [{norm_df['gal_b_deg'].min():.4f}, {norm_df['gal_b_deg'].max():.4f}] deg\n")
        if norm_df["cz_value_kms"].drop_nulls().len() > 0:
            f.write(f"- Velocity range (cz): [{norm_df['cz_value_kms'].min():.1f}, {norm_df['cz_value_kms'].max():.1f}] km/s\n")
        f.write(f"- Coordinate system: Astropy ICRS -> Galactic (l,b) -> Supergalactic (SGL, SGB)\n")
        f.write(f"- Frame tags preserved: {set(cz_frame)}\n")

    return out_file


def normalize_all(base_dir: Path) -> List[Path]:
    reg = CatalogRegistry(base_dir / "datasets" / "manifests" / "catalog_registry.json")
    out_files = []
    for meta in reg.list_all():
        p = normalize_dataset(meta, base_dir)
        out_files.append(p)
    return out_files


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parent.parent.parent
    results = normalize_all(repo_root)
    print(f"Normalized {len(results)} datasets.")
