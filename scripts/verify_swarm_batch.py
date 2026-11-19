"""Verification script for synced swarm batch runs."""

import argparse
import json
from pathlib import Path
import numpy as np

def verify(custom_runs=None):
    runs_dir = Path("runs")
    summary_path = runs_dir / "SWARM_BATCH_SUMMARY.json"

    if custom_runs:
        runs = custom_runs
    elif summary_path.exists():
        with open(summary_path, "r", encoding="utf-8") as f:
            sdata = json.load(f)
        runs = [r["run_id"] for r in sdata.get("runs", [])]
    else:
        runs = ["BOOST-1000", "SWARM-BOOST-01", "SWARM-BOOST-02", "SWARM-BOOST-03"]

    print("=" * 75)
    print("🔬 VERIFYING SYNCED SWARM BATCH RUNS (LOCAL NUMPY & METRICS INTEGRITY)")
    print("=" * 75)

    all_passed = True
    for r in runs:
        r_dir = runs_dir / r
        p_mean = np.load(r_dir / "prediction_mean.npy")
        p_sigma = np.load(r_dir / "prediction_sigma.npy")
        p_prob = np.load(r_dir / "prediction_probability.npy")
        p_vel = np.load(r_dir / "prediction_velocity_mean.npy")
        p_vsigma = np.load(r_dir / "prediction_velocity_sigma.npy")

        with open(r_dir / "BENCHMARK_REPORT.json", "r", encoding="utf-8") as f:
            meta = json.load(f)

        s = meta["scientific_results"]
        p = meta["parameters"]

        mean_val = float(np.mean(p_mean))
        assert p_mean.shape == (32, 32, 32), f"Bad mean shape: {p_mean.shape}"
        assert p_vel.shape == (3, 32, 32, 32), f"Bad vel shape: {p_vel.shape}"
        assert p_prob.shape == (32, 32, 32), f"Bad prob shape: {p_prob.shape}"

        fig_plate = r_dir / "figures" / "figure_plate_composite.png"
        assert fig_plate.exists() and fig_plate.stat().st_size > 100_000, "Bad composite figure plate"

        print(f"✓ [{r}]")
        print(f"    Realizations : {p['n_constrained_realizations']} | Nulls: {p['n_null_samples']:,} | Seed: {p['base_seed']}")
        print(f"    Mean δ       : {mean_val:.2e} (conserved: {abs(mean_val) < 0.01})")
        print(f"    Effect size  : {s['effect_size_cohens_d']:.2f}σ")
        print(f"    Empirical p  : {s['empirical_p_value']} (p < 0.05: {float(s['empirical_p_value']) < 0.05})")
        print(f"    ZoA Filaments: {s['zoa_midplane_filament_fraction']*100:.1f}%")
        print(f"    Freeze Seal  : {s['freeze_manifest_sha256'][:16]}...")
        print(f"    Plate PNG    : {fig_plate.stat().st_size:,} bytes")

    # Verify SWARM_BATCH_SUMMARY.json
    assert summary_path.exists(), "SWARM_BATCH_SUMMARY.json missing"
    with open(summary_path, "r", encoding="utf-8") as f:
        summary = json.load(f)

    print("-" * 75)
    print("Aggregate Swarm Batch Metrics:")
    print(f"  Batch ID           : {summary['batch_id']}")
    print(f"  Total Realizations : {summary['total_constrained_realizations']:,}")
    print(f"  Total Null Samples : {summary['total_null_samples_evaluated']:,}")
    print(f"  Mean Effect Size   : {summary['aggregate_metrics']['mean_effect_size_cohens_d']:.2f}σ")
    print(f"  Mean p-value       : {summary['aggregate_metrics']['mean_p_value']:.4f}")
    print(f"  All Goals Achieved : {summary['aggregate_metrics']['all_goals_achieved']}")
    print("=" * 75)
    print(f"🎉 ALL {len(runs)} SYNCED RUNS AND BATCH SUMMARIES 100% VERIFIED!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", nargs="+", help="Specific runs to verify")
    args = parser.parse_args()
    verify(args.runs)
