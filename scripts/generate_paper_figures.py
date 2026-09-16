#!/usr/bin/env python3
"""Standalone CLI runner for reproducible publication figures generation in Z-ZOA.

Usage:
    python scripts/generate_paper_figures.py
    python scripts/generate_paper_figures.py --run-id VELA-001 --dpi 300 --inspect
    python scripts/generate_paper_figures.py --format png --no-composite
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# Add repository root to path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from research.paper_factory.make_figures import generate_figures, get_figure_inspection_summary


def main():
    parser = argparse.ArgumentParser(
        description="Z-ZOA Publication Figures Generator & Scientific Inspector",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default="VELA-001",
        help="Experiment run ID to extract density fields and validation scores from",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=300,
        help="Resolution in dots per inch for raster image outputs",
    )
    parser.add_argument(
        "--format",
        type=str,
        default="png,svg",
        help="Comma-separated output formats ('png', 'svg', or 'png,svg')",
    )
    parser.add_argument(
        "--no-composite",
        action="store_true",
        help="Skip generation of the 4-panel composite publication plate",
    )
    parser.add_argument(
        "--inspect",
        action="store_true",
        help="Print scientific inspection table of plotted numerical ranges before and after generation",
    )

    args = parser.parse_args()
    formats = tuple(fmt.strip().lower() for fmt in args.format.split(",") if fmt.strip())
    include_composite = not args.no_composite

    print("=" * 72)
    print(" Z-ZOA PUBLICATION FIGURES GENERATOR ")
    print("=" * 72)
    print(f" Run Identifier : {args.run_id}")
    print(f" Resolution     : {args.dpi} DPI")
    print(f" Formats        : {', '.join(formats).upper()}")
    print(f" Composite Plate: {'ENABLED' if include_composite else 'DISABLED'}")
    print(f" Output Target  : {REPO_ROOT / 'paper' / 'figures'}")
    print("-" * 72)

    # 1. Scientific Inspection Table
    if args.inspect:
        try:
            summary = get_figure_inspection_summary(REPO_ROOT, run_id=args.run_id)
            print("\n[SCIENTIFIC NUMERICAL SUMMARY]")
            print(f" * Grid Dimension       : {summary['grid_shape']}")
            print(f" * Reconstructed Delta  : min = {summary['mean_delta_min']:+.3f}, max = {summary['mean_delta_max']:+.3f}, mean = {summary['mean_delta_mean']:+.4f}")
            print(f" * Posterior Sigma      : min = {summary['sigma_delta_min']:.3f}, max = {summary['sigma_delta_max']:.3f}, mean = {summary['sigma_delta_mean']:.3f}")
            print(f" * Differential Delta   : min = {summary['delta_diff_min']:+.3f}, max = {summary['delta_diff_max']:+.3f}")
            print(f" * Mean Sigma Reduction : {summary['sigma_diff_mean']:.4f}")
            print(f" * Observed Holdout Val : {summary['observed_score']:.2f}")
            print(f" * Holdout Z-Score      : {summary['z_score']:+.2f} sigma")
            print(f" * Empirical p-value    : {summary['p_value']:.4f}")
            print(f" * Validation Status    : {summary['test_status']}")
            print("-" * 72)
        except Exception as e:
            print(f"[WARNING] Could not read run inspection data: {e}")

    # 2. Figure Generation
    print("\nGenerating publication figures...")
    start_time = time.time()
    try:
        results = generate_figures(
            repo_root=REPO_ROOT,
            run_id=args.run_id,
            dpi=args.dpi,
            formats=formats,
            include_composite=include_composite,
        )
        elapsed = time.time() - start_time
        print(f"[OK] Generated {len(results)} figure artifacts in {elapsed:.2f} seconds:\n")

        for key, path in sorted(results.items()):
            p = Path(path)
            size_kb = p.stat().st_size / 1024 if p.exists() else 0
            rel_path = p.relative_to(REPO_ROOT) if p.is_relative_to(REPO_ROOT) else p
            print(f"  [{key:28s}] {str(rel_path):45s} ({size_kb:6.1f} KB)")

        print("\n" + "=" * 72)
        print(" SUCCESS: All publication figures generated reproducibly.")
        print("=" * 72)
    except Exception as e:
        print(f"\n[ERROR] Figure generation failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
