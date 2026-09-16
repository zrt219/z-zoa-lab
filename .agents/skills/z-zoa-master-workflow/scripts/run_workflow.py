#!/usr/bin/env python3
"""
Z-ZOA Master Workflow Orchestrator (`run_workflow.py`)

Provides unified CLI orchestration for:
- Environment & dataset status audits
- Catalogue TAP/VizieR synchronization
- Pytest scientific verification suite
- 15-stage numerical reproduction pipeline
- Freeze manifest & leakage certificate auditing
- End-to-end all-in-one execution
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

# 15 numerical stages from reproducibility/REPRODUCE_ALL.py
REPRODUCTION_STAGES = [
    (1, "research.catalogs.inventory", "Catalog inventory & schema audit"),
    (2, "research.catalogs.normalize", "Standardize coordinate frames & units"),
    (3, "research.catalogs.decontamination_pipeline", "HIZOA 39-source decontamination"),
    (4, "research.validation.cf4_baseline", "Cosmicflows-4 baseline distance modulus"),
    (5, "research.validation.masks", "Supergalactic & galactic zone of avoidance masks"),
    (6, "research.validation.mock_universe", "Constrained mock universe generation"),
    (7, "research.reconstruction.engine", "Density & peculiar velocity reconstruction engine"),
    (8, "research.reconstruction.constrained", "Wiener-filtered constrained field synthesis"),
    (9, "research.experiments.freeze", "Freeze prediction tensors & create freeze manifest"),
    (10, "research.validation.leakage_suite", "12-test comprehensive holdout leakage suite"),
    (11, "research.holdouts.reveal_gate", "Holdout cryptographic token reveal gate"),
    (12, "research.validation.reveal_and_score", "Reveal holdout data and calculate score metrics"),
    (13, "research.reconstruction.hybrid", "Hybrid data-model reconstruction fusion"),
    (14, "research.experiments.robustness", "Cosmological parameter robustness sweep"),
    (15, "research.experiments.paper_factory", "Generate figures, tables, and manuscript assets"),
]

def find_workspace_root(start_path: Path) -> Path:
    current = start_path.resolve()
    for _ in range(5):
        if (current / "pyproject.toml").exists() and (current / "research").exists():
            return current
        if current.parent == current:
            break
        current = current.parent
    return start_path.resolve()

def resolve_python(workspace: Path) -> str:
    # Check for virtual environment in workspace
    venv_win = workspace / ".venv" / "Scripts" / "python.exe"
    venv_posix = workspace / ".venv" / "bin" / "python"
    if venv_win.exists():
        return str(venv_win)
    if venv_posix.exists():
        return str(venv_posix)
    return sys.executable

def compute_sha256(file_path: Path) -> str:
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def cmd_status(workspace: Path, args) -> dict:
    python_exec = resolve_python(workspace)
    report = {
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "workspace": str(workspace),
        "python_executable": python_exec,
        "datasets": {},
        "manifests": {},
        "leakage_status": "UNKNOWN",
    }

    # Datasets
    raw_cf4 = workspace / "datasets" / "raw" / "cf4" / "cf4_sample.parquet"
    raw_hizoa = workspace / "datasets" / "raw" / "hizoa" / "hizoa_sample.parquet"
    holdout_vela = workspace / "datasets" / "HOLDOUT" / "vela_smgps" / "vela_smgps_sample.parquet"
    holdout_ga = workspace / "datasets" / "HOLDOUT" / "ga_smgps" / "ga_smgps_477.csv"

    for label, p in [
        ("cf4_sample", raw_cf4),
        ("hizoa_sample", raw_hizoa),
        ("vela_smgps_holdout", holdout_vela),
        ("ga_smgps_holdout", holdout_ga),
    ]:
        report["datasets"][label] = {
            "path": str(p.relative_to(workspace) if p.is_relative_to(workspace) else p),
            "exists": p.exists(),
            "sha256": compute_sha256(p) if p.exists() else None,
        }

    # Manifests
    freeze_manifest = workspace / "reproducibility" / "freeze_manifest.json"
    leakage_cert = workspace / "reproducibility" / "leakage_certificate.json"

    for label, p in [
        ("freeze_manifest", freeze_manifest),
        ("leakage_certificate", leakage_cert),
    ]:
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                report["manifests"][label] = {
                    "exists": True,
                    "sha256": compute_sha256(p),
                    "summary": {k: data.get(k) for k in ("manifest_type", "certificate_type", "run_id", "final_status", "status") if k in data},
                }
            except Exception as e:
                report["manifests"][label] = {"exists": True, "error": str(e)}
        else:
            report["manifests"][label] = {"exists": False}

    if leakage_cert.exists():
        try:
            with open(leakage_cert, "r", encoding="utf-8") as f:
                cert_data = json.load(f)
            report["leakage_status"] = cert_data.get("final_status", "UNKNOWN")
        except Exception:
            pass

    return report

def cmd_sync(workspace: Path, args) -> dict:
    python_exec = resolve_python(workspace)
    sync_script = workspace / "scripts" / "sync_data.py"
    if not sync_script.exists():
        raise FileNotFoundError(f"Sync script not found at {sync_script}")

    print(f"Executing sync: {python_exec} {sync_script}")
    start = time.monotonic()
    result = subprocess.run(
        [python_exec, str(sync_script)],
        cwd=str(workspace),
        capture_output=True,
        text=True,
    )
    elapsed = time.monotonic() - start

    if result.returncode != 0:
        print(f"[FAIL] Data sync failed with returncode {result.returncode}", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)

    return {
        "status": "SUCCESS",
        "duration_seconds": round(elapsed, 2),
        "stdout_tail": result.stdout.strip().splitlines()[-5:] if result.stdout else [],
    }

def cmd_test(workspace: Path, args) -> dict:
    python_exec = resolve_python(workspace)
    tests_dir = workspace / "tests"
    if not tests_dir.exists():
        raise FileNotFoundError(f"Tests directory not found at {tests_dir}")

    cmd = [python_exec, "-m", "pytest", "-v", "--tb=short"]
    if getattr(args, "test_target", None):
        cmd.append(args.test_target)

    print(f"Executing tests: {' '.join(cmd)}")
    start = time.monotonic()
    result = subprocess.run(
        cmd,
        cwd=str(workspace),
        capture_output=True,
        text=True,
    )
    elapsed = time.monotonic() - start

    if result.returncode != 0:
        print(f"[FAIL] Test suite failed with returncode {result.returncode}", file=sys.stderr)
        print(result.stdout, file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)

    summary_lines = [l for l in result.stdout.splitlines() if "passed" in l or "failed" in l or "error" in l]
    return {
        "status": "SUCCESS",
        "duration_seconds": round(elapsed, 2),
        "test_summary": summary_lines[-1] if summary_lines else "All tests passed",
    }

def cmd_reproduce(workspace: Path, args) -> dict:
    python_exec = resolve_python(workspace)
    from_stage = getattr(args, "from_stage", 1) or 1
    selected_stages = [s for s in REPRODUCTION_STAGES if s[0] >= from_stage]

    print(f"Executing 15-stage numerical reproduction pipeline (from stage {from_stage}/15)...")
    results = []
    start_total = time.monotonic()

    for num, mod, desc in selected_stages:
        print(f"--> [Stage {num:02d}/15] {desc} ({mod})")
        stage_start = time.monotonic()
        res = subprocess.run(
            [python_exec, "-m", mod],
            cwd=str(workspace),
            capture_output=True,
            text=True,
        )
        stage_dur = time.monotonic() - stage_start

        if res.returncode != 0:
            print(f"\n[FAIL] Pipeline halted at Stage {num:02d} ({mod})!", file=sys.stderr)
            print("STDOUT:", file=sys.stderr)
            print(res.stdout, file=sys.stderr)
            print("STDERR:", file=sys.stderr)
            print(res.stderr, file=sys.stderr)
            sys.exit(res.returncode)

        results.append({
            "stage": num,
            "module": mod,
            "description": desc,
            "duration_seconds": round(stage_dur, 2),
            "status": "PASS",
        })

    total_dur = time.monotonic() - start_total
    return {
        "status": "SUCCESS",
        "total_stages_run": len(results),
        "total_duration_seconds": round(total_dur, 2),
        "stages": results,
    }

def cmd_audit(workspace: Path, args) -> dict:
    freeze_manifest_path = workspace / "reproducibility" / "freeze_manifest.json"
    leakage_cert_path = workspace / "reproducibility" / "leakage_certificate.json"
    audit_results = {
        "status": "PASS",
        "freeze_manifest_verified": False,
        "leakage_certificate_verified": False,
        "checks": [],
    }

    # 1. Audit freeze manifest
    if freeze_manifest_path.exists():
        with open(freeze_manifest_path, "r", encoding="utf-8") as f:
            freeze_data = json.load(f)
        status_val = freeze_data.get("status")
        seal = freeze_data.get("manifest_seal_sha256")
        if status_val == "PREDICTION_FROZEN" and seal:
            audit_results["freeze_manifest_verified"] = True
            audit_results["checks"].append({
                "name": "freeze_manifest",
                "status": "PASS",
                "run_id": freeze_data.get("run_id"),
                "seal": seal,
            })
        else:
            audit_results["status"] = "FAIL"
            audit_results["checks"].append({"name": "freeze_manifest", "status": "FAIL", "reason": "Manifest unsealed"})
    else:
        audit_results["status"] = "FAIL"
        audit_results["checks"].append({"name": "freeze_manifest", "status": "FAIL", "reason": "Missing freeze_manifest.json"})

    # 2. Audit leakage certificate
    if leakage_cert_path.exists():
        with open(leakage_cert_path, "r", encoding="utf-8") as f:
            cert_data = json.load(f)
        final_status = cert_data.get("final_status")
        tests_exec = cert_data.get("tests_executed")
        tests_pass = cert_data.get("tests_passed")
        cert_hash = cert_data.get("certificate_sha256")

        if final_status == "PASS" and tests_exec == tests_pass and cert_hash:
            audit_results["leakage_certificate_verified"] = True
            audit_results["checks"].append({
                "name": "leakage_certificate",
                "status": "PASS",
                "tests_passed": f"{tests_pass}/{tests_exec}",
                "certificate_sha256": cert_hash,
            })
        else:
            audit_results["status"] = "FAIL"
            audit_results["checks"].append({"name": "leakage_certificate", "status": "FAIL", "reason": "Leakage suite tests failed"})
    else:
        audit_results["status"] = "FAIL"
        audit_results["checks"].append({"name": "leakage_certificate", "status": "FAIL", "reason": "Missing leakage_certificate.json"})

    if audit_results["status"] != "PASS":
        print(f"[FAIL] Audit failed: {audit_results['checks']}", file=sys.stderr)
        sys.exit(1)

    return audit_results

def cmd_all(workspace: Path, args) -> dict:
    print("==================================================================")
    print("   Z-ZOA Master Numerical Workflow: Comprehensive End-to-End Run   ")
    print("==================================================================")
    t0 = time.monotonic()
    
    print("\n--- 1. Synchronizing External Catalogues ---")
    sync_res = cmd_sync(workspace, args)

    print("\n--- 2. Executing Pytest Scientific Verification Suite ---")
    test_res = cmd_test(workspace, args)

    print("\n--- 3. Running 15-Stage Numerical Reproduction Pipeline ---")
    reproduce_res = cmd_reproduce(workspace, args)

    print("\n--- 4. Auditing Freeze Manifest & Leakage Certificate ---")
    audit_res = cmd_audit(workspace, args)

    print("\n--- 5. Compiling Environment & Status Audit ---")
    status_res = cmd_status(workspace, args)

    total_time = round(time.monotonic() - t0, 2)
    print("==================================================================")
    print(f" SUCCESS: Full Z-ZOA Scientific Reproduction verified in {total_time}s")
    print("==================================================================")

    return {
        "status": "PASS",
        "total_duration_seconds": total_time,
        "sync": sync_res,
        "test": test_res,
        "reproduce": reproduce_res,
        "audit": audit_res,
        "status_snapshot": status_res,
    }

def main():
    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument("--workspace", type=str, default=".", help="Root directory of z-zoa-lab")
    common_parser.add_argument("--output", type=str, default=None, help="File path to write JSON results")

    parser = argparse.ArgumentParser(description="Z-ZOA Master Workflow Orchestrator", parents=[common_parser])
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # status
    subparsers.add_parser("status", help="Inspect datasets, manifests, and environment", parents=[common_parser])

    # sync
    subparsers.add_parser("sync", help="Sync catalogues and update SHA-256 manifests", parents=[common_parser])

    # test
    p_test = subparsers.add_parser("test", help="Run pytest scientific test suite", parents=[common_parser])
    p_test.add_argument("--test-target", type=str, default=None, help="Optional test file or filter")

    # reproduce
    p_reproduce = subparsers.add_parser("reproduce", help="Run 15-stage numerical reproduction pipeline", parents=[common_parser])
    p_reproduce.add_argument("--from-stage", type=int, default=1, help="Stage number to start from (1 to 15)")

    # audit
    subparsers.add_parser("audit", help="Audit freeze manifest and leakage certificate integrity", parents=[common_parser])

    # all
    subparsers.add_parser("all", help="Execute complete pipeline: sync -> test -> reproduce -> audit -> status", parents=[common_parser])

    args = parser.parse_args()
    workspace = find_workspace_root(Path(args.workspace))

    commands = {
        "status": cmd_status,
        "sync": cmd_sync,
        "test": cmd_test,
        "reproduce": cmd_reproduce,
        "audit": cmd_audit,
        "all": cmd_all,
    }

    cmd_fn = commands[args.subcommand]
    results = cmd_fn(workspace, args)

    # Handle output
    output_file = args.output
    if not output_file:
        runs_dir = workspace / "runs"
        runs_dir.mkdir(parents=True, exist_ok=True)
        output_file = str(runs_dir / f"workflow_{args.subcommand}_result.json")

    out_path = Path(output_file)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"Result artifact written to: {out_path.resolve()}")

if __name__ == "__main__":
    main()
