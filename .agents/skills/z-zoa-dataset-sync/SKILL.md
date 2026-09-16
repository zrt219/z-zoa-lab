---
name: z-zoa-dataset-sync
description: >-
  Automates data catalog updates, TAP/VizieR fetching, SHA-256 manifest integrity,
  holdout dataset isolation, figure/table generation mapping, and test suite verification for Z-ZOA.
---

# Z-ZOA Dataset Synchronization, Provenance, & Asset Directory Skill

## Overview

This skill provides a standardized workflow and reference registry for acquiring, refreshing, checksumming, and auditing astronomical catalogues, as well as locating publication figures and tables in Z-ZOA:
- **GA-SMGPS**: VizieR catalogue `J/MNRAS/529/L88/ga-smgps` (Holdout).
- **WALLABY Pilot DR2**: CANFAR TAP catalogue `cirada.Wallaby_dr2_source_catalogue` (Comparison reference).
- **CF4 & 2MRS**: Ingested survey benchmarks for cosmic reconstruction (`datasets/raw/`).
- **Parkes HIZOA-S**: Southern ZoA survey with 39 known Vela footprint overlaps quarantined.

---

## 1. Master Dataset Provenance & Locations

| Dataset ID | Ingestion / Remote Source | Local Repository Path | Role | Tracers |
|---|---|---|---|---|
| `cf4_sample` | Cosmicflows-4 Tully-Fisher & distances | `datasets/raw/cf4/cf4_sample.csv` | `TRAIN` | 465 |
| `2mrs_sample` | 2MASS Redshift Survey ($K_s \le 11.75$) | `datasets/raw/2mrs/2mrs_sample.csv` | `TRAIN` | 137 |
| `hizoa_s_full` | Parkes H I Southern ZoA (Staveley-Smith 2016) | `datasets/raw/hizoa/hizoa_s_full.csv` | `TRAIN_AFTER_DECONTAMINATION` | 883 (39 quarantined) |
| `vela_smgps_sample` | MeerKAT Vela-SMGPS (Kraan-Korteweg et al. 2024) | `datasets/HOLDOUT/vela_smgps/vela_smgps_sample.parquet` | `HOLDOUT` | 4 |
| `ga_smgps_477` | MeerKAT Great Attractor (VizieR `J/MNRAS/529/L88`) | `datasets/HOLDOUT/ga_smgps/ga_smgps_477.csv` | `HOLDOUT` | 477 |
| `wallaby_dr2` | ASKAP WALLABY DR2 (CANFAR TAP `cirada`) | `datasets/reference/wallaby_dr2/wallaby_dr2_source_catalogue.csv` | `COMPARISON_ONLY` | 1,844 |
| `cf4_grids` | CF4 Cartesian density & velocity FITS | `datasets/reference/cf4/CF4_new_64-z008_*.fits` | `REFERENCE` | Gridded field |
| `cf4pp_grids` | CF4++ Wiener Filter reconstruction mean & std | `datasets/reference/cf4pp/CF4pp_mean_std_grids.npz` | `COMPARISON_ONLY` | Gridded field |

---

## 2. Generated Figures and Tables Registry

### Publication Figures (`paper/figures/`)
1. **`figure1_reconstruction_slice.png`**:
   - 2D Supergalactic plane slice ($SGZ = 0$) through reconstructed cosmic density field $\langle \delta(x) \rangle$.
2. **`figure2_uncertainty_map.png`**:
   - Posterior standard deviation $\sigma_\delta(x)$ map illustrating ZoA mask broadening.
3. **`figure3_null_distribution_scoring.png`**:
   - 1,000 survey-matched empirical null realizations compared against observed Vela holdout score ($1.96\,\sigma$, $p = 0.0270$).
4. **`figure4_hybrid_differential.png`**:
   - Post-unblinding differential overdensity gain ($\Delta \delta$) and regional uncertainty reduction ($\Delta \sigma$).

### Publication Tables (`paper/tables/`)
- **`table1_data_footprints.csv`**: Footprint geometries, sky coverage ($\text{deg}^2$), coordinate ranges, and tracer counts.
- **`table2_leakage_decontamination.csv`**: 39 HIZOA overlap isolation and exclusion list audit.
- **`table3_reconstruction_config.csv`**: Cosmological prior parameters ($\Omega_m = 0.30$, $H_0 = 74.6$, $R_s = 10\text{ Mpc}$).
- **`table4_validation_metrics.csv`**: Primary and secondary holdout validation statistics and empirical p-values.
- **`table5_hybrid_information_gain.csv`**: Quantitative information gain following MeerKAT integration.

---

## 3. Usage & Sync Commands

To refresh TAP/VizieR catalogues and audit SHA-256 manifests:
```powershell
python scripts/sync_data.py
```

To run end-to-end numerical reproduction across all 15 pipeline stages:
```powershell
python reproducibility/REPRODUCE_ALL.py
```

To run the full unit and integration test suite:
```powershell
python -m pytest
```

---

## 4. Operational Invariants & Safeguards

1. **Holdout Protection**: Code executing in training or model tuning contexts must NEVER open files in `datasets/HOLDOUT/`. Any attempt raises machine-enforced `HoldoutLeakageViolationError`.
2. **Checksum Audit**: All downloaded and synchronized files must match their SHA-256 digest in `datasets/manifests/catalog_registry.json`.
3. **Decontamination Protocol**: All 39 HIZOA galaxies within $260^\circ \le \ell \le 290^\circ, -2^\circ \le b \le +1^\circ$ must remain strictly quarantined in `leakage/exclusion_list.parquet`.
