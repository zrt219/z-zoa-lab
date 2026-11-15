"""Sync run artifacts from Instabox cloud VM to local workspace with chunked streaming."""

import argparse
import base64
import os
from pathlib import Path
import subprocess
from typing import List

INSTABOX_EXE = os.environ.get("INSTABOX_EXE", "instabox")
REMOTE_BOX = os.environ.get("INSTABOX_BOX_ID", "sandbox")
REMOTE_RUNS_ROOT = "/data/home/workspace/Z-zoa-lab/runs"
LOCAL_RUNS_ROOT = Path(__file__).resolve().parent.parent / "runs"


def run_remote_cmd(remote_cmd: str) -> subprocess.CompletedProcess:
    cmd = [
        INSTABOX_EXE,
        "exec",
        REMOTE_BOX,
        "--",
        remote_cmd,
    ]
    return subprocess.run(cmd, capture_output=True)


def fetch_file(remote_full_path: str, local_path: Path) -> bool:
    local_path.parent.mkdir(parents=True, exist_ok=True)

    # 1. Check remote size
    size_res = run_remote_cmd(f"stat -c %s {remote_full_path}")
    if size_res.returncode != 0:
        err = size_res.stderr.decode("utf-8", errors="ignore").strip()
        print(f"  ❌ File missing or inaccessible on remote: {local_path.name} ({err})")
        return False

    size_lines = [l for l in size_res.stdout.decode("utf-8", errors="ignore").splitlines() if not l.startswith("instabox:")]
    if not size_lines:
        return False
    try:
        remote_size = int(size_lines[-1].strip())
    except ValueError:
        return False

    # 2. If <= 500 KB, fetch directly
    if remote_size <= 500_000:
        res = run_remote_cmd(f"base64 -w 0 {remote_full_path}")
        if res.returncode != 0:
            print(f"  ❌ Error fetching {local_path.name}")
            return False
        raw_b64 = res.stdout.strip()
        if b"\n" in raw_b64:
            lines = [l for l in raw_b64.split(b"\n") if not l.startswith(b"instabox:")]
            raw_b64 = b"".join(lines)
        data = base64.b64decode(raw_b64)
        local_path.write_bytes(data)
        print(f"  ✓ Fetched {local_path.name} ({len(data):,} bytes)")
        return True

    # 3. If > 500 KB, split into 400 KB chunks to avoid 1 MB buffer truncation
    tmp_prefix = f"/tmp/_ib_chk_{abs(hash(remote_full_path)) % 1000000}_"
    setup_cmd = f"rm -f {tmp_prefix}* && split -b 400k {remote_full_path} {tmp_prefix} && ls {tmp_prefix}*"
    split_res = run_remote_cmd(setup_cmd)
    if split_res.returncode != 0:
        print(f"  ❌ Failed to split {remote_full_path} on remote")
        return False

    chunk_files = [l.strip() for l in split_res.stdout.decode("utf-8", errors="ignore").splitlines() if not l.startswith("instabox:") and l.strip()]
    full_data = bytearray()

    for chk in chunk_files:
        res = run_remote_cmd(f"base64 -w 0 {chk}")
        if res.returncode != 0:
            print(f"  ❌ Failed to fetch chunk {chk}")
            run_remote_cmd(f"rm -f {tmp_prefix}*")
            return False
        raw_b64 = res.stdout.strip()
        if b"\n" in raw_b64:
            lines = [l for l in raw_b64.split(b"\n") if not l.startswith(b"instabox:")]
            raw_b64 = b"".join(lines)
        chunk_bytes = base64.b64decode(raw_b64)
        full_data.extend(chunk_bytes)

    # Clean up remote temp chunks
    run_remote_cmd(f"rm -f {tmp_prefix}*")

    if len(full_data) != remote_size:
        print(f"  ❌ Size mismatch for {local_path.name}: expected {remote_size:,}, got {len(full_data):,}")
        return False

    local_path.write_bytes(full_data)
    print(f"  ✓ Fetched {local_path.name} (chunked {len(chunk_files)} parts, {len(full_data):,} bytes, verified!)")
    return True


def sync_run(run_id: str) -> None:
    print(f"\n[*] Syncing run artifacts for [{run_id}] from {REMOTE_BOX}...")
    remote_run_dir = f"{REMOTE_RUNS_ROOT}/{run_id}"
    local_run_dir = LOCAL_RUNS_ROOT / run_id
    local_run_dir.mkdir(parents=True, exist_ok=True)

    files_to_sync = [
        "BENCHMARK_REPORT.md",
        "BENCHMARK_REPORT.json",
        "validation_report.json",
        "hybrid_report.json",
        "vweb_report.md",
        "vweb_report.json",
        "freeze_manifest.json",
        "figures_manifest.json",
        "checksums.sha256",
        "UNBLINDING_RECEIPT.json",
        "metrics_spec.json",
        "null_spec.json",
        "null_distribution_means.npy",
        "prediction_mean.npy",
        "prediction_sigma.npy",
        "prediction_probability.npy",
        "prediction_velocity_mean.npy",
        "prediction_velocity_sigma.npy",
        "figures/figure1_reconstruction_slice.png",
        "figures/figure1_reconstruction_slice.svg",
        "figures/figure2_uncertainty_map.png",
        "figures/figure2_uncertainty_map.svg",
        "figures/figure3_null_distribution_scoring.png",
        "figures/figure3_null_distribution_scoring.svg",
        "figures/figure4_hybrid_differential.png",
        "figures/figure4_hybrid_differential.svg",
        "figures/figure_plate_composite.png",
        "figures/figure_plate_composite.svg",
    ]

    for rel_path in files_to_sync:
        remote_path = f"{remote_run_dir}/{rel_path}"
        local_path = local_run_dir / rel_path
        fetch_file(remote_path, local_path)


def sync_top_level_summaries() -> None:
    print(f"\n[*] Syncing top-level batch summaries...")
    summaries = [
        "SWARM_BATCH_SUMMARY.json",
        "SWARM_BATCH_SUMMARY.md",
    ]
    for s in summaries:
        remote_path = f"{REMOTE_RUNS_ROOT}/{s}"
        local_path = LOCAL_RUNS_ROOT / s
        fetch_file(remote_path, local_path)


def main():
    parser = argparse.ArgumentParser(description="Sync run artifacts from Instabox")
    parser.add_argument("--run-id", type=str, default="BOOST-1000", help="Run identifier to sync")
    parser.add_argument("--batch", action="store_true", help="Sync all runs from the swarm batch")
    parser.add_argument("--runs", nargs="+", help="Specific run IDs to sync")
    args = parser.parse_args()

    LOCAL_RUNS_ROOT.mkdir(parents=True, exist_ok=True)

    if args.runs:
        for r in args.runs:
            sync_run(r)
        sync_top_level_summaries()
    elif args.batch:
        sync_top_level_summaries()
        summary_file = LOCAL_RUNS_ROOT / "SWARM_BATCH_SUMMARY.json"
        batch_runs = ["BOOST-1000", "SWARM-BOOST-01", "SWARM-BOOST-02", "SWARM-BOOST-03"]
        if summary_file.exists():
            try:
                import json
                sdata = json.loads(summary_file.read_text(encoding="utf-8"))
                discovered = [r["run_id"] for r in sdata.get("runs", []) if "run_id" in r]
                if discovered:
                    batch_runs = discovered
            except Exception:
                pass
        for r in batch_runs:
            sync_run(r)
    else:
        sync_run(args.run_id)
        sync_top_level_summaries()

    print("\n[*] Sync complete!")


if __name__ == "__main__":
    main()
