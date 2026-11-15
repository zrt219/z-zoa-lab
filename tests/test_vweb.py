"""Unit tests for V-Web cosmic web classifier."""

import numpy as np
import pytest
from pathlib import Path

from research.reconstruction.vweb import compute_vweb_tensor, analyze_vweb_for_run


def test_vweb_synthetic_fields():
    """Test V-Web eigenvalue classification on known synthetic velocity fields."""
    grid_n = 16
    dx = 10.0
    h0 = 74.6

    # 1. Pure isotropic expansion (Hubble flow v = H * x) -> all eigenvalues negative -> Void
    x = (np.arange(grid_n) - grid_n // 2) * dx
    X, Y, Z = np.meshgrid(x, x, x, indexing="ij")
    # v = 0.5 * h0 * r -> dv/dr = 0.5 * h0 -> s = -0.5 < 0
    v_void = np.stack([0.5 * h0 * X, 0.5 * h0 * Y, 0.5 * h0 * Z], axis=0)

    classification, eigvals, fractions = compute_vweb_tensor(v_void, dx_mpc=dx, h0=h0, threshold=0.1)
    assert fractions["void_fraction"] == 1.0, "Pure expansion must be classified 100% as Void"
    assert classification.shape == (grid_n, grid_n, grid_n)
    assert eigvals.shape == (3, grid_n, grid_n, grid_n)

    # 2. Pure isotropic infall / collapse (v = -0.5 * h0 * r) -> dv/dr = -0.5 * h0 -> s = +0.5 > 0.1 -> Cluster
    v_cluster = np.stack([-0.5 * h0 * X, -0.5 * h0 * Y, -0.5 * h0 * Z], axis=0)
    classification_c, _, fractions_c = compute_vweb_tensor(v_cluster, dx_mpc=dx, h0=h0, threshold=0.1)
    assert fractions_c["cluster_fraction"] == 1.0, "Pure 3D infall must be classified 100% as Cluster"


def test_vweb_run_analysis():
    """Test V-Web analysis on existing VELA-001 run directory."""
    repo_root = Path(__file__).resolve().parent.parent
    runs_dir = repo_root / "runs" / "VELA-001"
    if not runs_dir.exists():
        pytest.skip("VELA-001 run directory not found")

    res = analyze_vweb_for_run(repo_root, run_id="VELA-001")
    assert res["run_id"] == "VELA-001"
    assert "volume_fractions" in res
    assert res["volume_fractions"]["filament_fraction"] > 0.3
    assert (runs_dir / "vweb_classification.npy").exists()
    assert (runs_dir / "vweb_report.json").exists()
    assert (runs_dir / "vweb_report.md").exists()
