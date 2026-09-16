"""Automated tests for Z-ZOA publication figures generator and scientific inspector."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import pytest

from research.paper_factory.make_figures import (
    generate_figures,
    get_figure_inspection_summary,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
PNG_MAGIC_BYTES = b"\x89PNG\r\n\x1a\n"


def test_figure_inspection_summary():
    """Verify that get_figure_inspection_summary returns complete and physically consistent metrics."""
    summary = get_figure_inspection_summary(REPO_ROOT, run_id="VELA-001")

    expected_keys = [
        "run_id",
        "grid_shape",
        "mean_delta_min",
        "mean_delta_max",
        "mean_delta_mean",
        "sigma_delta_min",
        "sigma_delta_max",
        "sigma_delta_mean",
        "delta_diff_min",
        "delta_diff_max",
        "sigma_diff_mean",
        "observed_score",
        "z_score",
        "p_value",
        "test_status",
    ]
    for key in expected_keys:
        assert key in summary, f"Missing key '{key}' in figure inspection summary"

    assert summary["run_id"] == "VELA-001"
    assert summary["grid_shape"] == [32, 32, 32]
    assert isinstance(summary["mean_delta_min"], float)
    assert isinstance(summary["mean_delta_max"], float)
    assert summary["mean_delta_max"] > summary["mean_delta_min"]
    assert summary["sigma_delta_min"] > 0
    assert summary["observed_score"] > 0
    assert summary["z_score"] > 0
    assert 0.0 <= summary["p_value"] <= 1.0
    assert summary["test_status"] == "VALIDATION_CONFIRMED"


def test_generate_figures_full_suite(tmp_path: Path):
    """Test full figure generation with PNG, SVG, and 4-panel composite plate."""
    results = generate_figures(
        repo_root=REPO_ROOT,
        run_id="VELA-001",
        dpi=100,  # Fast DPI for test
        formats=("png", "svg"),
        include_composite=True,
        output_dir=tmp_path,
    )

    expected_artifacts = [
        "figure1_png",
        "figure1_svg",
        "figure2_png",
        "figure2_svg",
        "figure3_png",
        "figure3_svg",
        "figure4_png",
        "figure4_svg",
        "figure_plate_composite_png",
        "figure_plate_composite_svg",
    ]
    assert len(results) == len(expected_artifacts)

    for key in expected_artifacts:
        assert key in results, f"Missing figure result for {key}"
        fig_path = Path(results[key])
        assert fig_path.exists(), f"Figure file does not exist: {fig_path}"
        assert fig_path.stat().st_size > 5000, f"Figure file suspiciously small: {fig_path.stat().st_size} bytes"

        # Verify magic bytes / file signatures
        content = fig_path.read_bytes()
        if key.endswith("_png"):
            assert content.startswith(PNG_MAGIC_BYTES), f"Invalid PNG magic bytes in {fig_path}"
        elif key.endswith("_svg"):
            assert b"<svg" in content, f"Missing <svg tag in {fig_path}"


def test_generate_figures_no_composite(tmp_path: Path):
    """Test generation without composite plate and single format."""
    results = generate_figures(
        repo_root=REPO_ROOT,
        run_id="VELA-001",
        dpi=72,
        formats=("png",),
        include_composite=False,
        output_dir=tmp_path,
    )

    assert len(results) == 4
    assert "figure1_png" in results
    assert "figure2_png" in results
    assert "figure3_png" in results
    assert "figure4_png" in results
    assert "figure_plate_composite_png" not in results
    assert "figure1_svg" not in results


def test_cli_standalone_script():
    """Test invoking the standalone CLI script directly via subprocess."""
    cli_script = REPO_ROOT / "scripts" / "generate_paper_figures.py"
    assert cli_script.exists(), "CLI script scripts/generate_paper_figures.py does not exist"

    cmd = [
        sys.executable,
        str(cli_script),
        "--run-id",
        "VELA-001",
        "--dpi",
        "72",
        "--format",
        "png",
        "--no-composite",
        "--inspect",
    ]
    res = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
    assert res.returncode == 0, f"CLI invocation failed with error:\nSTDOUT: {res.stdout}\nSTDERR: {res.stderr}"
    assert "SCIENTIFIC NUMERICAL SUMMARY" in res.stdout
    assert "SUCCESS: All publication figures generated reproducibly." in res.stdout
