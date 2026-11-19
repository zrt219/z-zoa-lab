# Z-ZOA Project Rules & Repository Architecture Guide

This document defines the persistent structural taxonomy, dataset provenance rules, holdout security invariants, and asset locations for the **Z-ZOA** repository (*Out-of-Sample Reconstruction and H I Validation of Large-Scale Structure Across the Galactic Zone of Avoidance*).

---

## 1. Directory Structure & File Taxonomy

```
Z-zoa-lab/
├── datasets/                             # Observational catalogues & survey products
│   ├── raw/                              # Original ingested astronomical surveys
│   │   ├── cf4/                          # Cosmicflows-4 distances & radial velocities (cf4_sample.csv / .parquet)
│   │   ├── 2mrs/                         # 2MASS Redshift Survey (2mrs_sample.csv)
│   │   └── hizoa/                        # Parkes Southern ZoA H I survey (hizoa_s_full.csv, hizoa_sample.parquet)
│   ├── HOLDOUT/                          # STRICTLY QUARANTINED holdouts (Never access during training!)
│   │   ├── vela_smgps/                   # MeerKAT Vela-SMGPS sample (vela_smgps_sample.parquet / .csv)
│   │   └── ga_smgps/                     # MeerKAT Great Attractor (ga_smgps_477.csv via VizieR J/MNRAS/529/L88)
│   ├── reference/                        # Comparison surveys & external reference grids
│   │   ├── wallaby_dr2/                  # ASKAP WALLABY Pilot DR2 (wallaby_dr2_source_catalogue.csv via CANFAR)
│   │   ├── cf4/                          # Published CF4 Cartesian grids (CF4_new_64-z008_delta/velocity.fits)
│   │   └── cf4pp/                        # CF4++ comparison grids (CF4pp_mean_std_grids.npz)
│   ├── processed/                        # Standardized coordinate tables & decontaminated data
│   │   ├── normalized/                   # ICRS (RA, Dec) + Supergalactic (SGX, SGY, SGZ) + cz km/s
│   │   └── TRAIN_CLEAN/                  # Decontaminated training inputs (train_clean_combined.parquet)
│   └── manifests/                        # Catalog registry and download verification manifests
│       ├── catalog_registry.json         # Master dataset registry with cryptographic SHA-256 hashes
│       └── missing_download_manifest.json# Automated TAP/VizieR sync verification manifest
├── paper/                                # Publication-ready figures and data tables
│   ├── figures/                          # High-resolution (300 DPI) publication figures
│   │   ├── figure1_reconstruction_slice.png      # 2D Supergalactic Z=0 slice of cosmic density field
│   │   ├── figure2_uncertainty_map.png           # Posterior standard deviation sigma_delta(x) map
│   │   ├── figure3_null_distribution_scoring.png # 1,000 empirical null realizations vs holdout score
│   │   └── figure4_hybrid_differential.png       # Post-unblinding differential delta & sigma reduction
│   └── tables/                           # CSV and LaTeX publication data tables
│       ├── table1_data_footprints.csv            # Survey footprints, sky areas, and tracer counts
│       ├── table2_leakage_decontamination.csv    # 39 HIZOA overlap isolation & audit summary
│       ├── table3_reconstruction_config.csv      # Reconstruction hyperparameters & prior settings
│       ├── table4_validation_metrics.csv         # Confirmatory holdout test statistics & p-values
│       └── table5_hybrid_information_gain.csv    # Post-unblinding information gain metrics
├── runs/                                 # Reconstruction outputs & experiment artifacts
│   └── VELA-001/                         # Primary Vela confirmatory experiment
│       ├── prediction_mean.npy           # Frozen mean density field <delta(x)> (32x32x32)
│       ├── prediction_sigma.npy          # Posterior density uncertainty sigma_delta(x)
│       ├── prediction_probability.npy    # Overdensity exceedance probability P(delta > 1.0)
│       ├── prediction_velocity_mean.npy  # Mean peculiar velocity vector field
│       ├── prediction_velocity_sigma.npy # Velocity vector uncertainty
│       ├── freeze_manifest.json          # Pre-unblinding SHA-256 seal manifest
│       ├── UNBLINDING_RECEIPT.json       # Double-blind ceremony unblinding authorization receipt
│       ├── validation_report.json        # Confirmatory holdout scoring & p-value results
│       └── hybrid_report.json            # Post-unblinding hybrid reconstruction report
├── leakage/                              # 18-stage leakage audit reports & cryptographic certificates
│   ├── 01_file_role_integrity.json       # Test 01: Registry role and SHA-256 integrity
│   ├── 02_exact_id_scan.json             # Test 02: Exact ID and alias collision scan
│   ├── 03_sky_position_crossmatch.json   # Test 03: Multi-radius spherical matching (1', 3', 6')
│   ├── 04_velocity_crossmatch.json       # Test 04: Footprint velocity collision scan
│   ├── 05_hizoa_vela_overlap.parquet     # Test 05: 39 quarantined HIZOA galaxies in Vela footprint
│   ├── 05_hizoa_vela_overlap.json        # Test 05: HIZOA-S 39 overlap verification
│   ├── 06_derived_lineage_audit.json     # Test 06: Circular MeerKAT assimilation check
│   ├── 07_code_access_denial.json        # Test 07: DataGateway exception enforcement
│   ├── 08_tuning_audit.json              # Test 08: Pre-reveal hyperparameter freezing
│   ├── 09_cache_environment_audit.json   # Test 09: Cache and environment leakage check
│   ├── 10_freeze_canary_test.json        # Test 10: Freeze canary tamper detection
│   ├── 11_negative_control.json          # Test 11: Negative-control holdout byte invariance
│   ├── 12_final_leakage_report.json      # Test 12: Master audit consolidation
│   ├── 13_os_sandbox_test.json           # Test 13: Physical OS holdout sandbox & socket blocking
│   ├── 14_taint_scan.json                # Test 14: Transitive dependency taint scan on DAG
│   ├── 15_preregistration_lock.json      # Test 15: Preregistered analysis plan hash lock
│   ├── 16_side_channel_scan.json         # Test 16: Environment variables & build cache scan
│   ├── 17_reveal_gate.json               # Test 17: Double-blind unblinding reveal gate
│   ├── 18_cleanroom_reproduction.json    # Test 18: Cleanroom from-zero rebuild verification
│   ├── exclusion_list.parquet            # Master quarantined exclusion table (39 HIZOA objects)
│   ├── leakage_certificate.json          # Cryptographically signed 18/18 test pass certificate
│   └── FINAL_LEAKAGE_REPORT.md           # Master human-readable audit report
├── docs/                                 # Scientific documentation & preregistration specifications
│   ├── MANUSCRIPT_DRAFT.md               # Complete draft manuscript for journal submission
│   ├── PRE_SUBMISSION_AUDIT.md           # 12-pillar pre-submission compliance audit
│   ├── LEAKAGE_TESTS_10_PAGE_SUMMARY.md  # Comprehensive 10-page audit synthesis report
│   ├── preregistered_analysis_plan.json  # Sealed preregistration parameter contract
│   └── PREREGISTRATION.md                # Formal preregistration document
├── reproducibility/                      # End-to-end master reproduction scripts
│   └── REPRODUCE_ALL.py                  # Single-command reproduction of all 15 numerical stages
├── Z-ZOA_prompt_pack/                    # Research prompt pack (23 pipeline prompts + 19 leakage prompts)
├── Z-ZOA_all_prompts_and_leakage_tests_v2.zip # Master archive of the complete v2 prompt pack
├── Z-ZOA_missing_data_bundle/            # Self-contained bundle of external download datasets
├── Z-ZOA_missing_data_bundle.zip         # Master archive of the external dataset bundle
├── research/                             # Core research library (catalogs, holdouts, reconstruction)
├── tests/                                # Full pytest test suite (59 unit & integration tests)
└── pyproject.toml                        # Project metadata and dependencies
```

---

## 2. Core Operational Invariants

1. **Holdout Protection Invariant**:
   - `datasets/HOLDOUT/` contains evaluation data only (`vela_smgps_sample` and `ga_smgps_477`).
   - Under `ExecutionMode.TRAINING`, `DataGateway` raises `HoldoutLeakageViolationError` if code attempts to read holdout files.
   - Holdouts must never be imported, copied, or merged into training sets.

2. **The 39 HIZOA Footprint Quarantine**:
   - Exactly 39 HIZOA galaxies fall within the Vela-SMGPS footprint ($260^\circ \le \ell \le 290^\circ, -2^\circ \le b \le +1^\circ$).
   - They are quarantined in `leakage/exclusion_list.parquet` and stripped from `TRAIN_CLEAN` ($N = 902$).

3. **Cryptographic Freeze & Unblinding Gate**:
   - Training predictions must be hashed and sealed in `runs/VELA-001/freeze_manifest.json` before holdout scoring.
   - Unblinding requires executing `python -m research.holdouts.reveal_gate` with a valid freeze seal, passing leakage certificate, and preregistration hash lock.

4. **Master Numerical Reproduction**:
   - The entire pipeline can be verified from scratch via:
     ```powershell
     python reproducibility/REPRODUCE_ALL.py
     python -m pytest
     ```

---

## 3. Astronomical Realism & Observational Provenance Invariant

1. **Physical Scale Sanity**:
   - Reconstructed overdensity fields $\delta(\mathbf{x}) \equiv (\rho - \bar{\rho})/\bar{\rho}$ must obey linear and mildly non-linear cosmological bounds on $10\,h^{-1}\text{ Mpc}$ smoothing scales ($\delta \in [-3.0, +5.0]$, spatial mean $\langle \delta \rangle \equiv 0.00 \pm 0.01$).
   - Peculiar velocities $v_{\text{pec}}$ must never exceed physical cosmic infall limits ($v_{\text{rms}} \in [300, 600]\text{ km s}^{-1}$, $v_{\max} \le 2,500\text{ km s}^{-1}$). Any calculation yielding $v > 0.01c$ must fail loudly with `UnphysicalCosmologyError`.

2. **Survey Scope & Holdout Identity**:
   - Never conflate foreground survey objects with background target superclusters. The 39 quarantined Parkes HIZOA galaxies ($cz \le 11,790\text{ km s}^{-1}$) must be explicitly documented as foreground decontamination, not the deep MeerKAT Vela Supercluster ($cz \sim 18,000\text{--}23,000\text{ km s}^{-1}$, $N=843$).
   - Holdout null distributions must be aperture- and redshift-matched to the evaluated sample envelope.

3. **Zero Mock Fallback Policy in Production**:
   - API routes, White Calculation Room inspectors, and publication tables must report live array values directly from verified run artifacts without hardcoded overrides or mock formula fallbacks.

4. **Astronomical Discovery vs. Cross-Match Invariant**:
   - Never claim an existing published survey detection (such as the 843 sources published in the Vela-SMGPS catalog by Kraan-Korteweg et al. 2024, *MNRAS* 531, 3486) is a "novel discovery", "original candidate", or "previously uncatalogued galaxy".
   - A non-detection when cross-matching against comparison catalogs (e.g., 2MRS, CF4, or Parkes HIZOA) only establishes *catalog-specific non-detection or multi-wavelength obscuration*, NOT that the object was unknown to astronomical literature.
   - Any script, documentation, or report that evaluates catalog overlap must explicitly title and describe the analysis as a *reproducible catalog cross-match and obscuration characterization*, attributing published detections to their originating survey with exact literature citations.

5. **Zero Discrepancy Verification Handoff Invariant**:
   - Never report a test, service, or health check as "VERIFIED", "PASSED", or "100% OPERATIONAL" if the underlying command, tool, or script exited with a non-zero code or reported failing endpoints.
   - Summaries and handoff reports must quote the exact, raw exit codes, list failing endpoints, and analyze the root cause transparently. Under no circumstances may an agent cite older passing log snippets to mask or overwrite a subsequent command failure.


