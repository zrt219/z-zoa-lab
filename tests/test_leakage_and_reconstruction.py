"""Automated test suite for Z-ZOA prompt pack pipeline and leakage suite."""

import json
from pathlib import Path
import numpy as np
import pytest

from research.catalogs.registry import CatalogRegistry
from research.catalogs.schema import DatasetRole
from research.holdouts.guard import DataGateway, ExecutionContext, ExecutionMode
from research.holdouts.exceptions import HoldoutLeakageViolationError


@pytest.fixture
def repo_root():
    return Path(__file__).resolve().parent.parent


def test_registry_holds_required_datasets(repo_root):
    reg = CatalogRegistry(repo_root / "datasets" / "manifests" / "catalog_registry.json")
    datasets = {d.dataset_id: d for d in reg.list_all()}
    assert "cf4_sample" in datasets
    assert "hizoa_s_full" in datasets
    assert "2mrs_sample" in datasets
    assert "vela_smgps_sample" in datasets
    assert datasets["vela_smgps_sample"].role == DatasetRole.HOLDOUT


def test_datagateway_machine_enforced_denial(repo_root):
    reg = CatalogRegistry(repo_root / "datasets" / "manifests" / "catalog_registry.json")
    gw = DataGateway(reg, base_dir=repo_root)
    ctx_train = ExecutionContext(run_id="TEST-RUN", mode=ExecutionMode.TRAINING)

    with pytest.raises(HoldoutLeakageViolationError):
        gw.request_dataset("vela_smgps_sample", ctx_train)


def test_39_hizoa_overlap_quarantine(repo_root):
    overlap_parquet = repo_root / "leakage" / "05_hizoa_vela_overlap.parquet"
    assert overlap_parquet.exists(), "05_hizoa_vela_overlap.parquet must exist"
    import polars as pl
    df = pl.read_parquet(overlap_parquet)
    assert df.height == 39, f"Expected exactly 39 HIZOA overlaps, found {df.height}"


def test_leakage_suite_certificate_pass(repo_root):
    cert_file = repo_root / "leakage" / "leakage_certificate.json"
    assert cert_file.exists(), "Leakage certificate must exist"
    cert = json.loads(cert_file.read_text(encoding="utf-8"))
    assert cert["final_status"] == "PASS"
    assert cert["tests_passed"] == 18
    assert cert["tests_executed"] == 18

    # Verify 6 defense-in-depth test artifacts
    leakage_dir = repo_root / "leakage"
    for test_idx in ["13_os_sandbox_test", "14_taint_scan", "15_preregistration_lock", "16_side_channel_scan", "17_reveal_gate", "18_cleanroom_reproduction"]:
        assert (leakage_dir / f"{test_idx}.json").exists(), f"Missing {test_idx}.json"
    assert (repo_root / "runs" / "VELA-001" / "UNBLINDING_RECEIPT.json").exists()


def test_frozen_prediction_artifacts(repo_root):
    runs_dir = repo_root / "runs" / "VELA-001"
    assert (runs_dir / "freeze_manifest.json").exists()
    assert (runs_dir / "prediction_mean.npy").exists()
    assert (runs_dir / "prediction_sigma.npy").exists()
    assert (runs_dir / "validation_report.json").exists()
    assert (runs_dir / "hybrid_report.json").exists()

    val_rep = json.loads((runs_dir / "validation_report.json").read_text(encoding="utf-8"))
    assert val_rep["status"] == "VALIDATION_CONFIRMED"
    assert val_rep["effect_size_cohens_d"] > 1.5


def test_publication_tables_and_figures(repo_root):
    paper_dir = repo_root / "paper"
    assert (paper_dir / "tables" / "table1_data_footprints.csv").exists()
    assert (paper_dir / "tables" / "table2_leakage_decontamination.csv").exists()
    assert (paper_dir / "tables" / "table3_reconstruction_config.csv").exists()
    assert (paper_dir / "tables" / "table4_validation_metrics.csv").exists()
    assert (paper_dir / "tables" / "table5_hybrid_information_gain.csv").exists()
    assert (paper_dir / "figures" / "figure1_reconstruction_slice.png").exists()
    assert (paper_dir / "figures" / "figure2_uncertainty_map.png").exists()
    assert (paper_dir / "figures" / "figure3_null_distribution_scoring.png").exists()
    assert (paper_dir / "figures" / "figure4_hybrid_differential.png").exists()
