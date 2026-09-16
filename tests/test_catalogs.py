"""Test catalog loading, integrity verification, and ZoA decontamination."""

from pathlib import Path
import pytest
import polars as pl
from research.catalogs.schema import DatasetMetadata, DatasetRole
from research.catalogs.registry import CatalogRegistry
from research.catalogs.loader import (
    ChecksumMismatchError,
    load_dataset_table,
    compute_file_sha256,
)
from research.catalogs.decontaminate import cross_match_and_decontaminate


def test_load_real_cf4_sample_with_sha():
    reg = CatalogRegistry("datasets/manifests/catalog_registry.json")
    cf4_meta = reg.get("cf4_sample")
    df = load_dataset_table(cf4_meta)
    assert df.height == 8
    assert "pgc" in df.columns
    assert "cz_obs" in df.columns
    assert "distance_mpc" in df.columns


def test_checksum_mismatch_fails():
    bad_meta = DatasetMetadata(
        dataset_id="tampered_test",
        survey="Test",
        release="1.0",
        role=DatasetRole.TRAIN,
        file_path="datasets/raw/cf4/cf4_sample.parquet",
        sha256="0000000000000000000000000000000000000000000000000000000000000000",
        row_count=8,
        imported_at="2026-09-15T00:00:00Z",
        citation="None",
        is_synthetic=True,
    )
    with pytest.raises(ChecksumMismatchError, match="Integrity check failed"):
        load_dataset_table(bad_meta)


def test_hizoa_cross_match_and_decontaminate():
    reg = CatalogRegistry("datasets/manifests/catalog_registry.json")
    hizoa_df = load_dataset_table(reg.get("hizoa_s_sample"))
    vela_df = load_dataset_table(reg.get("vela_smgps_sample"))

    clean_df, contaminated_df, audit_records = cross_match_and_decontaminate(
        candidate_df=hizoa_df,
        holdout_df=vela_df,
        ra_col="ra",
        dec_col="dec",
        cz_col="cz",
        angular_sep_arcmin=5.0,
        velocity_sep_kms=100.0,
    )

    # In our sample data, HIZSS 001 and HIZSS 014 match Vela holdout; HIZSS 105 and 210 are outside
    assert contaminated_df.height == 2
    assert clean_df.height == 2
    assert len(audit_records) == 2
    clean_ids = clean_df["source_id"].to_list()
    assert "HIZSS 105" in clean_ids
    assert "HIZSS 210" in clean_ids
