"""Unit tests for mock-universe validation suite (Prompt 09)."""

from pathlib import Path
import numpy as np
import pytest

from research.mock_universe.mock_engine import (
    MockUniverseConfig,
    MockUniverseEngine,
    generate_mock_cosmological_field,
    run_mock_validation_pipeline,
)


@pytest.fixture
def repo_root():
    return Path(__file__).resolve().parent.parent


class TestMockUniverseGeneration:
    def test_generate_mock_field_properties(self):
        grid_size = 16
        box_size_mpc = 100.0
        delta_true, v_true, meta = generate_mock_cosmological_field(
            grid_size=grid_size,
            box_size_mpc=box_size_mpc,
            seed=42,
        )

        assert delta_true.shape == (grid_size, grid_size, grid_size)
        assert v_true.shape == (3, grid_size, grid_size, grid_size)
        assert meta["tag"] == "SYNTHETIC_TEST_ONLY"
        assert abs(np.mean(delta_true)) < 0.05
        assert 0.40 < np.std(delta_true) < 0.60
        assert meta["v_max_kms"] > 0.0

    def test_sample_mock_tracers(self):
        cfg = MockUniverseConfig(grid_size=16, box_size_mpc=100.0, random_seed=42)
        engine = MockUniverseEngine(cfg)
        delta_true, _, _ = engine.generate_true_fields()
        zoa_mask = engine.generate_obscuration_mask()

        tracers = engine.sample_mock_tracers(delta_true, zoa_mask, n_tracers=500, seed=123)
        assert tracers["tag"] == "SYNTHETIC_TEST_ONLY"
        assert tracers["n_sampled"] == 500
        assert len(tracers["x_mpc"]) == 500
        assert len(tracers["cz_kms"]) == 500

        # Coordinates should lie within cosmological box bounds [-box/2, box/2]
        half_box = cfg.box_size_mpc / 2.0
        assert np.all(tracers["x_mpc"] >= -half_box)
        assert np.all(tracers["x_mpc"] <= half_box)


class TestMockReconstructionAndMetrics:
    def test_wiener_reconstruction_and_benchmarks(self):
        cfg = MockUniverseConfig(grid_size=32, box_size_mpc=200.0, random_seed=42)
        engine = MockUniverseEngine(cfg)
        delta_true, _, _ = engine.generate_true_fields()
        zoa_mask = engine.generate_obscuration_mask()

        delta_recon, posterior_sigma = engine.reconstruct_field(delta_true, zoa_mask)
        metrics = engine.compute_validation_metrics(
            delta_true, delta_recon, posterior_sigma, zoa_mask
        )

        # Invariant requirements from Prompt 09
        assert metrics["tag"] == "SYNTHETIC_TEST_ONLY"
        assert metrics["status"] == "PASS"

        # Pearson r must strictly exceed 0.65
        assert metrics["field_correlation_r"] >= 0.65, f"r was {metrics['field_correlation_r']}"
        assert metrics["rmse"] < 0.45
        assert metrics["peak_recovery_rate"] >= 0.60
        assert metrics["false_positive_rate"] <= 0.12

        # Posterior variance calibration
        calib = metrics["posterior_calibration"]
        assert 0.40 <= calib["chi2_reduced"] <= 2.20
        assert calib["status"] == "CALIBRATED"

    def test_pipeline_execution_and_report(self, repo_root):
        metrics = run_mock_validation_pipeline(repo_root=repo_root)
        assert metrics["tag"] == "SYNTHETIC_TEST_ONLY"
        assert metrics["status"] == "PASS"

        report_file = repo_root / "docs" / "mock_universe_validation.md"
        assert report_file.exists()
        text = report_file.read_text(encoding="utf-8")
        assert "SYNTHETIC_TEST_ONLY" in text
        assert "Field Correlation (Pearson r)" in text
        assert "PASS" in text
