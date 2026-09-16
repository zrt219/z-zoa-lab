from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_missing_download_manifest_exists():
    manifest_path = REPO_ROOT / "datasets" / "manifests" / "missing_download_manifest.json"
    assert manifest_path.is_file(), f"Missing manifest: {manifest_path}"
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    assert "datasets" in manifest
    assert len(manifest["datasets"]) == 2


def test_ga_smgps_dataset_integrity():
    csv_path = REPO_ROOT / "datasets" / "HOLDOUT" / "GA_SMGPS" / "ga_smgps_477.csv"
    json_path = REPO_ROOT / "datasets" / "HOLDOUT" / "GA_SMGPS" / "ga_smgps_source.json"

    assert csv_path.is_file(), f"GA-SMGPS CSV missing: {csv_path}"
    assert json_path.is_file(), f"GA-SMGPS JSON metadata missing: {json_path}"

    with open(json_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    assert meta["dataset_id"] == "GA_SMGPS_2024"
    assert meta["role"] == "HOLDOUT"
    assert meta["rows"] == 477

    # Verify SHA256
    file_bytes = csv_path.read_bytes()
    computed_hash = hashlib.sha256(file_bytes).hexdigest()
    assert computed_hash == meta["sha256"], f"GA-SMGPS SHA256 mismatch: {computed_hash} vs {meta['sha256']}"
    assert len(file_bytes) == meta["bytes"]

    # Verify CSV parsing and rows
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)

    assert len(rows) == 477, f"Expected 477 rows, got {len(rows)}"
    # Verify expected columns present in VizieR table
    expected_cols = {"Name", "GLON", "GLAT", "HRV", "W50", "log(MHI)", "Fint", "_RA.icrs", "_DE.icrs"}
    assert expected_cols.issubset(set(header)), f"Missing expected columns in GA-SMGPS: {expected_cols - set(header)}"


def test_wallaby_dr2_dataset_integrity():
    csv_path = REPO_ROOT / "datasets" / "reference" / "WALLABY_DR2" / "wallaby_dr2_source_catalogue.csv"
    json_path = REPO_ROOT / "datasets" / "reference" / "WALLABY_DR2" / "wallaby_dr2_source.json"

    assert csv_path.is_file(), f"WALLABY DR2 CSV missing: {csv_path}"
    assert json_path.is_file(), f"WALLABY DR2 JSON metadata missing: {json_path}"

    with open(json_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    assert meta["dataset_id"] == "WALLABY_PILOT_DR2_30ARCSEC"
    assert meta["role"] == "COMPARISON_ONLY"
    assert meta["rows"] == 3454

    # Verify SHA256
    file_bytes = csv_path.read_bytes()
    computed_hash = hashlib.sha256(file_bytes).hexdigest()
    assert computed_hash == meta["sha256"], f"WALLABY DR2 SHA256 mismatch: {computed_hash} vs {meta['sha256']}"
    assert len(file_bytes) == meta["bytes"]

    # Verify CSV parsing and rows
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)

    assert len(rows) == 3454, f"Expected 3454 rows, got {len(rows)}"
    # Verify expected key columns
    header_lower = {col.lower() for col in header}
    expected_cols = {"name", "ra", "dec", "freq", "w50", "log_m_hi"}
    assert expected_cols.issubset(header_lower), f"Missing expected columns in WALLABY DR2: {expected_cols - header_lower}"
