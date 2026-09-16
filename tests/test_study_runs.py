"""Automated tests for dedicated study runs, per-run figures suite archival, and backend endpoints."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from backend.main import app

REPO_ROOT = Path(__file__).resolve().parent.parent
client = TestClient(app)
PNG_MAGIC_BYTES = b"\x89PNG\r\n\x1a\n"


def compute_sha256(path: Path) -> str:
    """Compute standard SHA-256 digest of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def test_api_list_reconstruction_runs():
    """Verify GET /reconstruction/runs returns all runs with their figure suite metadata."""
    res = client.get("/reconstruction/runs")
    assert res.status_code == 200
    data = res.json()
    assert "runs" in data
    assert "total" in data
    assert data["total"] >= 2

    # Check VELA-001 is present and prioritized
    runs = data["runs"]
    assert runs[0]["run_id"] == "VELA-001"
    assert runs[0]["has_figures"] is True
    assert runs[0]["figures_count"] >= 10
    assert runs[0]["has_figures_manifest"] is True
    assert runs[0]["has_validation"] is True
    assert "z_score" in runs[0]["validation_summary"]

    # Check STUDY-001 is present
    study_run = next((r for r in runs if r["run_id"] == "STUDY-001"), None)
    assert study_run is not None
    assert study_run["has_figures"] is True
    assert study_run["figures_count"] >= 10


def test_api_get_run_figures_metadata():
    """Verify GET /reconstruction/runs/{run_id}/figures returns valid manifest and figure items."""
    res = client.get("/reconstruction/runs/VELA-001/figures")
    assert res.status_code == 200
    data = res.json()

    assert data["run_id"] == "VELA-001"
    assert data["figures_count"] >= 10
    assert "figures" in data
    assert "manifest" in data
    assert "numerical_bounds" in data

    # Check presence of key figure files
    filenames = [f["filename"] for f in data["figures"]]
    assert "figure1_reconstruction_slice.png" in filenames
    assert "figure1_reconstruction_slice.svg" in filenames
    assert "figure2_uncertainty_map.png" in filenames
    assert "figure3_null_distribution_scoring.png" in filenames
    assert "figure4_hybrid_differential.png" in filenames
    assert "figure_plate_composite.png" in filenames

    # Verify each figure has valid URL and sha256
    for fig in data["figures"]:
        assert fig["url"].startswith("/reconstruction/runs/VELA-001/figures/")
        assert len(fig["sha256"]) == 64


def test_api_download_run_figure():
    """Verify GET /reconstruction/runs/{run_id}/figures/{filename} serves valid PNG/SVG bytes."""
    # Test PNG download
    res_png = client.get("/reconstruction/runs/VELA-001/figures/figure1_reconstruction_slice.png")
    assert res_png.status_code == 200
    assert res_png.headers["content-type"] == "image/png"
    assert res_png.content.startswith(PNG_MAGIC_BYTES)
    assert len(res_png.content) > 10000

    # Test SVG download
    res_svg = client.get("/reconstruction/runs/VELA-001/figures/figure1_reconstruction_slice.svg")
    assert res_svg.status_code == 200
    assert res_svg.headers["content-type"] == "image/svg+xml"
    assert b"<svg" in res_svg.content


def test_api_security_traversal_guards():
    """Verify path traversal attacks and non-existent files return 400 or 404."""
    # Directory traversal in run_id
    res_bad_run = client.get("/reconstruction/runs/..%2F..%2Fetc/figures")
    assert res_bad_run.status_code in [400, 404]

    # Directory traversal in filename
    res_bad_file = client.get("/reconstruction/runs/VELA-001/figures/..%2F..%2Fpyproject.toml")
    assert res_bad_file.status_code in [400, 404]

    # Non-existent figure
    res_not_found = client.get("/reconstruction/runs/VELA-001/figures/non_existent_plot.png")
    assert res_not_found.status_code == 404


def test_figures_manifest_cryptographic_integrity():
    """Verify that sha256 digests in figures_manifest.json match actual bytes on disk."""
    for run_id in ["VELA-001", "STUDY-001"]:
        manifest_path = REPO_ROOT / "runs" / run_id / "figures_manifest.json"
        if not manifest_path.exists():
            continue

        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        assert manifest["run_id"] == run_id
        figures_meta = manifest.get("figures", {})
        assert len(figures_meta) >= 10

        for filename, meta in figures_meta.items():
            fig_path = REPO_ROOT / meta["relative_path"]
            assert fig_path.exists(), f"Figure file '{fig_path}' missing"
            actual_sha = compute_sha256(fig_path)
            assert actual_sha == meta["sha256"], f"SHA-256 mismatch for {filename} in run {run_id}"
            assert fig_path.stat().st_size == meta["bytes"]


def test_cli_run_study():
    """Verify scripts/run_study.py executes cleanly and archives figures for a new study run."""
    cmd = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "run_study.py"),
        "--run-id",
        "TEST-STUDY-99",
        "--name",
        "Integration Test Study Run",
        "--grid-size",
        "16",
        "--dpi",
        "80",
    ]
    study_dir = REPO_ROOT / "runs" / "TEST-STUDY-99"
    try:
        proc = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
        assert proc.returncode == 0, f"run_study failed:\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"

        # Verify artifacts were created in dedicated directory
        assert study_dir.is_dir()

        figures_dir = study_dir / "figures"
        assert figures_dir.is_dir()
        assert (figures_dir / "figure1_reconstruction_slice.png").exists()
        assert (figures_dir / "figure_plate_composite.png").exists()

        manifest_file = study_dir / "figures_manifest.json"
        assert manifest_file.exists()

        with open(manifest_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["run_id"] == "TEST-STUDY-99"
        assert data["has_composite"] is True
        assert data["figures_count"] >= 10
    finally:
        if study_dir.exists():
            import shutil
            shutil.rmtree(study_dir, ignore_errors=True)
