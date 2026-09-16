---
name: z-zoa-leakage-audit
description: >-
  Executes and verifies the 18-stage cryptographic leakage audit suite, DataGateway RBAC access boundaries, 39 HIZOA overlap quarantines, freeze canary tamper tests, and physical defense-in-depth security gates for Z-ZOA.
---

# Z-ZOA Leakage Audit & Holdout Defense Suite

## Overview

`z-zoa-leakage-audit` is a specialized quality and security verification skill for the **Z-ZOA Calculation Room (`z-zoa-lab`)**. It provides automated instruments to audit, test, attack, and certify that no observational holdout data (`datasets/HOLDOUT/`) leaks into training sets (`TRAIN_CLEAN`), reconstruction engines, or public endpoints before authorized, double-blind unblinding.

## Core Architectural Invariants Tested

1. **Rule #1 — Never Lose Provenance**:
   - Every raw dataset, derived product, exclusion list, and prediction field is hashed with SHA-256 and anchored in verifiable manifests.
2. **Rule #4 — Strict Holdout Boundary Isolation**:
   - Datasets with role `HOLDOUT` (e.g. `datasets/HOLDOUT/vela_smgps/` and `datasets/HOLDOUT/ga_smgps/`) are quarantined.
   - Any attempt to load holdouts under `ExecutionMode.TRAINING` raises a fatal `HoldoutLeakageViolationError`.
3. **The 39 HIZOA Overlap Quarantine**:
   - Exactly 39 HIZOA galaxies fall within the Vela-SMGPS footprint ($260^\circ \le \ell \le 290^\circ, -2^\circ \le b \le +1^\circ$).
   - They are isolated in `leakage/exclusion_list.parquet` and stripped from `TRAIN_CLEAN` ($N = 902$).
4. **Double-Blind Unblinding Gate**:
   - Predictions must be sealed in `runs/VELA-001/freeze_manifest.json` before holdouts are touched.
   - Unblinding requires a passing 18-stage leakage certificate and an unaltered preregistration plan hash.

---

## Quick Start Commands

Run directly using the bundled CLI script:

### 1. Run the Full 18-Stage Leakage Audit Suite
Executes all 12 core tests + 6 defense-in-depth tests, generating `leakage/leakage_certificate.json`:
```powershell
.venv\Scripts\python .agents/skills/z-zoa-leakage-audit/scripts/z_zoa_leakage_audit_cli.py full-suite --output runs/leakage_audit_summary.json
```

### 2. Run Adversarial Leakage Attack Simulations
Simulates 4 active penetration attacks (direct holdout read under `TRAINING`, future holdout read, unauthorized reveal gate call, and freeze canary tampering) to verify all defenses fail closed:
```powershell
.venv\Scripts\python .agents/skills/z-zoa-leakage-audit/scripts/z_zoa_leakage_audit_cli.py attack-sim --output runs/leakage_attack_results.json
```

### 3. Audit the 39 HIZOA Overlap Quarantine
Verifies that `leakage/exclusion_list.parquet` contains exactly 39 galaxies, with zero ID collisions and zero footprint intruders inside `datasets/processed/TRAIN_CLEAN/train_clean_combined.parquet`:
```powershell
.venv\Scripts\python .agents/skills/z-zoa-leakage-audit/scripts/z_zoa_leakage_audit_cli.py quarantine-check
```

### 4. Verify Cryptographic Leakage Certificate
Audits the SHA-256 integrity and completion status of `leakage/leakage_certificate.json`:
```powershell
.venv\Scripts\python .agents/skills/z-zoa-leakage-audit/scripts/z_zoa_leakage_audit_cli.py verify-cert
```

---

## 18-Stage Audit Test Inventory

| Stage | Test Name | Target / Defense Mechanism |
|---|---|---|
| **01** | File Role Integrity | SHA-256 digests of all 7 registered surveys in `catalog_registry.json` |
| **02** | Exact ID Collision Scan | Verifies zero ID collisions between `TRAIN_CLEAN` and `HOLDOUT` |
| **03** | Sky Position Cross-Match | Multi-radius spherical cone search ($1', 3', 6'$) |
| **04** | Velocity Collision Scan | Footprint velocity collision check across $|cz| \le 25,000\text{ km/s}$ |
| **05** | HIZOA Overlap Isolation | Verifies exactly 39 HIZOA galaxies quarantined in Vela footprint |
| **06** | Derived Lineage Audit | Circular assimilation and derived product dependency audit |
| **07** | Code Access Denial | Physical DataGateway RBAC exception enforcement |
| **08** | Tuning Audit | Pre-reveal hyperparameter and random seed lock |
| **09** | Cache Environment Audit | Check for holdout artifacts in `.cache`, `__pycache__`, or tempdirs |
| **10** | Freeze Canary Tamper Test | Verifies detection of altered prediction array bytes |
| **11** | Negative Control | Proves negative-control holdout byte invariance |
| **12** | Final Leakage Report | Consolidates all results into `leakage/leakage_certificate.json` |
| **13** | OS Sandbox & Socket Test | Physical holdout directory permission and socket isolation |
| **14** | Taint DAG Analysis | Transitive dependency taint analysis on calculation graph |
| **15** | Preregistration Lock | SHA-256 hash lock on `docs/preregistered_analysis_plan.json` |
| **16** | Side-Channel Scan | Environment variables, build caches, and compiler side-channels |
| **17** | Reveal Gate Validation | Double-blind unblinding ceremony and `UNBLINDING_RECEIPT.json` |
| **18** | Cleanroom Reproduction | Deterministic cleanroom rebuild verification |

---

## Error Handling & Verification Verdicts

- **`ALL_ATTACKS_BLOCKED`**: System defense-in-depth is intact; all adversarial attacks are rejected.
- **`VULNERABILITY_DETECTED`**: An attack succeeded in loading holdout data or bypassing a gate. Halts the research pipeline immediately.
- **`HoldoutLeakageViolationError`**: The expected exception when code attempts to access `datasets/HOLDOUT/` while running in `TRAINING` mode.
