---
name: z-zoa-master-workflow
description: >-
  Orchestrates end-to-end scientific workflows for Z-ZOA: catalogue synchronization,
  SHA-256 integrity audits, pytest validation, 15-stage numerical reproduction pipeline,
  holdout leakage defense, and paper artifact generation.
---

# Z-ZOA Master Research Workflow

## Overview

The `z-zoa-master-workflow` skill coordinates the complete verification, synchronization, numerical reproduction, and artifact generation lifecycle for the **Z-ZOA Calculation Room** (`z-zoa-lab`). It automates the strict 4-rule scientific guarantees:
1. **Never Lose Provenance**: Tracks raw immutable checksums (SHA-256) and transformation lineage DAGs across all datasets.
2. **Units Are Not Optional**: Validates that interfaces operate on typed quantities (`astropy.units.Quantity`).
3. **Explicit Cosmology**: Asserts permanent recording of cosmological constants ($H_0 = 74.6\text{ km s}^{-1}\text{Mpc}^{-1}$, $\Omega_m = 0.3$, $\Omega_\Lambda = 0.7$).
4. **Holdout Boundary Defense**: Cryptographically seals validation catalogues (`datasets/HOLDOUT/`) with fail-fast enforcement (`HoldoutLeakageViolationError`).

## Dependencies

- `z-zoa-dataset-sync`: Used for TAP/VizieR external catalogue acquisition and integrity manifests.
- Python 3.12+ virtual environment (`.venv`) or `uv`.

## Quick Start

Inspect the current laboratory workspace status:

```powershell
python .agents/skills/z-zoa-master-workflow/scripts/run_workflow.py status
```

Run full end-to-end scientific verification and reproduction:

```powershell
python .agents/skills/z-zoa-master-workflow/scripts/run_workflow.py all
```

## Utility Scripts

The CLI runner is located at `scripts/run_workflow.py`. It accepts `--workspace <path>` (defaults to current repository) and `--output <path>` (defaults to writing structured JSON in `runs/`).

### Subcommands

#### 1. `status`
Audits the environment, active Python interpreter, catalogue presence (CF4, HIZOA, MeerKAT Vela/GA holdouts), SHA-256 checksums, and holdout gate state.
```powershell
python .agents/skills/z-zoa-master-workflow/scripts/run_workflow.py status --output runs/status.json
```

#### 2. `sync`
Executes `scripts/sync_data.py` to synchronize external VizieR/TAP catalogues (GA-SMGPS and WALLABY DR2), refreshes SHA-256 manifests, and audits registry records.
```powershell
python .agents/skills/z-zoa-master-workflow/scripts/run_workflow.py sync
```

#### 3. `test`
Executes the scientific `pytest` test suite across all units, coordinates, cosmology, velocities, catalogs, and holdout leakage boundary gates.
```powershell
python .agents/skills/z-zoa-master-workflow/scripts/run_workflow.py test
```

#### 4. `reproduce`
Runs the 15-stage numerical reproduction pipeline sequentially with strict fail-fast error handling:
1. `research.catalogs.inventory`
2. `research.catalogs.normalize`
3. `research.catalogs.decontamination_pipeline`
4. `research.validation.cf4_baseline`
5. `research.validation.masks`
6. `research.validation.mock_universe`
7. `research.reconstruction.engine`
8. `research.reconstruction.constrained`
9. `research.experiments.freeze`
10. `research.validation.leakage_suite`
11. `research.holdouts.reveal_gate`
12. `research.validation.reveal_and_score`
13. `research.reconstruction.hybrid`
14. `research.experiments.robustness`
15. `research.experiments.paper_factory`

Optionally resume from an intermediate stage:
```powershell
python .agents/skills/z-zoa-master-workflow/scripts/run_workflow.py reproduce --from-stage 10
```

#### 5. `audit`
Verifies cryptographic seals in `reproducibility/freeze_manifest.json` (`manifest_seal_sha256`) and audits that `leakage_certificate.json` has passed 100% of the 12 leakage suite tests.
```powershell
python .agents/skills/z-zoa-master-workflow/scripts/run_workflow.py audit
```

#### 6. `all`
Runs the full pipeline in order (`sync` -> `test` -> `reproduce` -> `audit` -> `status`) and writes a unified reproduction certificate to `runs/workflow_all_result.json`.
```powershell
python .agents/skills/z-zoa-master-workflow/scripts/run_workflow.py all
```

## Scientific Safeguards & Error Handling

- **Fail-Fast Policy**: If any stage or leakage test fails, execution halts immediately with a non-zero exit code. Non-reproducible states are never masked.
- **Holdout Protection**: Any attempt by reconstruction or training code to access files in `datasets/HOLDOUT/` triggers a fatal `HoldoutLeakageViolationError`.
- **Structured File Output**: Script results are written to JSON files rather than polluting stdout, ensuring provenance tracking and token efficiency.

## Common Mistakes

- **Accessing Holdouts Directly**: Never copy holdout files into `datasets/raw/` or training paths. All holdout comparisons must route through `research.holdouts.reveal_gate`.
- **Untyped Floats**: Scientific functions must wrap physical quantities in `astropy.units.Quantity` (e.g., `km / s`, `Mpc`).
- **Ignoring Manifest Seals**: Any manual modification to `freeze_manifest.json` or `leakage_certificate.json` invalidates the SHA-256 seal and will fail the `audit` command.
