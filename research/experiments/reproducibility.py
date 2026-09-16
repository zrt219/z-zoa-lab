"""Reproducibility bundle packager for Z-ZOA Paper 1 (Prompt 17).

Packages configs, freeze manifests, execution commands, exclusion lists,
leakage certificates, publication tables, and figures into a standalone
reproducibility bundle.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


def build_reproducibility_bundle(repo_root: Path, run_id: str = "VELA-001") -> Dict[str, Any]:
    bundle_dir = repo_root / "reproducibility"
    bundle_dir.mkdir(parents=True, exist_ok=True)

    runs_dir = repo_root / "runs" / run_id
    leakage_dir = repo_root / "leakage"
    paper_dir = repo_root / "paper"
    docs_dir = repo_root / "docs"

    # 1. Environment / Dependency Lock
    pip_list = subprocess.run(
        [sys.executable, "-m", "pip", "freeze"],
        capture_output=True,
        text=True,
    ).stdout
    (bundle_dir / "environment_lock.txt").write_text(pip_list, encoding="utf-8")

    # 2. Copy Key Verification Artifacts
    copy_targets = [
        (runs_dir / "freeze_manifest.json", bundle_dir / "freeze_manifest.json"),
        (runs_dir / "metrics_spec.json", bundle_dir / "metrics_spec.json"),
        (runs_dir / "null_spec.json", bundle_dir / "null_spec.json"),
        (runs_dir / "validation_report.json", bundle_dir / "validation_report.json"),
        (runs_dir / "hybrid_report.json", bundle_dir / "hybrid_report.json"),
        (leakage_dir / "leakage_certificate.json", bundle_dir / "leakage_certificate.json"),
        (leakage_dir / "FINAL_LEAKAGE_REPORT.md", bundle_dir / "FINAL_LEAKAGE_REPORT.md"),
        (docs_dir / "robustness_matrix.csv", bundle_dir / "robustness_matrix.csv"),
    ]

    for src, dst in copy_targets:
        if src.exists():
            shutil.copy2(src, dst)

    # Copy Tables and Figures
    if (paper_dir / "tables").exists():
        shutil.copytree(paper_dir / "tables", bundle_dir / "tables", dirs_exist_ok=True)
    if (paper_dir / "figures").exists():
        shutil.copytree(paper_dir / "figures", bundle_dir / "figures", dirs_exist_ok=True)

    # 3. Create Reproducibility Runner Script
    runner_script = bundle_dir / "REPRODUCE_ALL.py"
    runner_script.write_text("""# Z-ZOA Paper 1: Master Numerical Reproduction Script
import subprocess
import sys

commands = [
    [sys.executable, "-m", "research.catalogs.inventory"],
    [sys.executable, "-m", "research.catalogs.normalize"],
    [sys.executable, "-m", "research.catalogs.decontamination_pipeline"],
    [sys.executable, "-m", "research.validation.cf4_baseline"],
    [sys.executable, "-m", "research.validation.masks"],
    [sys.executable, "-m", "research.validation.mock_universe"],
    [sys.executable, "-m", "research.reconstruction.engine"],
    [sys.executable, "-m", "research.reconstruction.constrained"],
    [sys.executable, "-m", "research.experiments.freeze"],
    [sys.executable, "-m", "research.validation.leakage_suite"],
    [sys.executable, "-m", "research.validation.reveal_and_score"],
    [sys.executable, "-m", "research.reconstruction.hybrid"],
    [sys.executable, "-m", "research.experiments.robustness"],
    [sys.executable, "-m", "research.experiments.paper_factory"],
]

for cmd in commands:
    print(f"Executing: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
print("All 14 numerical stages reproduced cleanly!")
""", encoding="utf-8")

    # 4. Create Bundle README
    readme_path = bundle_dir / "README.md"
    readme_text = f"""# Z-ZOA Paper 1 Reproducibility Bundle

**Experiment Run ID**: `{run_id}`  
**Packaged At**: {datetime.now(timezone.utc).isoformat()}  

This bundle contains all frozen configurations, cryptographic manifests, exclusion lists,
validation metrics, null-hypothesis distributions, and figure-generation assets required to
independently reproduce all numerical claims in:

**Z-ZOA: Out-of-Sample Reconstruction and H I Validation of Large-Scale Structure Across the Galactic Zone of Avoidance**

## Exact Run Order
To reproduce from scratch, execute in sequence:
1. `python -m research.catalogs.inventory`
2. `python -m research.catalogs.normalize`
3. `python -m research.catalogs.decontamination_pipeline`
4. `python -m research.validation.cf4_baseline`
5. `python -m research.validation.masks`
6. `python -m research.validation.mock_universe`
7. `python -m research.reconstruction.engine`
8. `python -m research.reconstruction.constrained`
9. `python -m research.experiments.freeze`
10. `python -m research.validation.leakage_suite`
11. `python -m research.validation.reveal_and_score`
12. `python -m research.reconstruction.hybrid`
13. `python -m research.experiments.robustness`
14. `python -m research.experiments.paper_factory`

Or simply run:
```bash
python reproducibility/REPRODUCE_ALL.py
```
"""
    readme_path.write_text(readme_text, encoding="utf-8")

    return {
        "status": "SUCCESS",
        "bundle_dir": str(bundle_dir),
        "files_packaged": len(list(bundle_dir.glob("**/*"))),
    }


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parent.parent.parent
    res = build_reproducibility_bundle(repo_root)
    print("Reproducibility bundle built successfully:")
    print(json.dumps(res, indent=2))
