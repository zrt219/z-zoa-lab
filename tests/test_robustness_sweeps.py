"""Unit tests for parameter robustness grid sweep suite (Prompt 15)."""

from pathlib import Path
import polars as pl
import pytest

from research.robustness.sweeps import (
    RobustnessSweepRunner,
    run_robustness_grid_sweep,
)


@pytest.fixture
def repo_root():
    return Path(__file__).resolve().parent.parent


class TestRobustnessSweeps:
    def test_grid_sweep_produces_18_runs(self, repo_root):
        runner = RobustnessSweepRunner(repo_root=repo_root)
        results = runner.execute_grid_sweep()

        # Invariant: 3 x 3 x 2 = exactly 18 runs
        assert len(results) == 18

        run_indices = [r["run_index"] for r in results]
        assert run_indices == list(range(1, 19))

        scales = sorted(list({r["smoothing_scale_mpch"] for r in results}))
        assert scales == [5.0, 10.0, 15.0]

        betas = sorted(list({r["beta"] for r in results}))
        assert betas == [0.35, 0.43, 0.50]

        sigma_vs = sorted(list({r["sigma_v_kms"] for r in results}))
        assert sigma_vs == [150.0, 250.0]

    def test_required_columns_and_stability(self, repo_root):
        runner = RobustnessSweepRunner(repo_root=repo_root)
        results = runner.execute_grid_sweep()

        required_keys = {
            "run_index",
            "smoothing_scale_mpch",
            "beta",
            "sigma_v_kms",
            "mean_delta",
            "std_delta",
            "holdout_score",
            "p_value",
            "config_hash",
        }

        for row in results:
            assert set(row.keys()) == required_keys
            # Holdout overdensity must be positive and stable across all variants
            assert row["holdout_score"] > 50.0, f"Unstable holdout score: {row['holdout_score']}"
            assert row["p_value"] <= 1e-4
            assert len(row["config_hash"]) == 64

    def test_csv_and_markdown_artifacts(self, repo_root):
        results = run_robustness_grid_sweep(repo_root=repo_root)
        assert len(results) == 18

        csv_path = repo_root / "docs" / "robustness_matrix.csv"
        report_path = repo_root / "docs" / "robustness_report.md"

        assert csv_path.exists()
        assert report_path.exists()

        df = pl.read_csv(csv_path)
        assert df.height == 18
        assert df.columns == [
            "run_index",
            "smoothing_scale_mpch",
            "beta",
            "sigma_v_kms",
            "mean_delta",
            "std_delta",
            "holdout_score",
            "p_value",
            "config_hash",
        ]
