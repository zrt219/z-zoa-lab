# Z-ZOA Master Leakage Audit & Certification Report (Final)

**Experiment / Run Candidate ID**: `VELA-001`  
**Audit Status**: **PASS**  
**Certificate SHA-256**: `df6131fc21abf99145121a45fbb9aa77a42337eb776caf3c7fd0fe678625e45e`  

---

## 1. Executive Summary & Verification Scope
This report synthesizes the complete 12-stage pre-freeze leakage audit battery mandated by the Z-ZOA research prompt pack. The overarching objective is to rigorously certify that the training snapshot (`TRAIN_CLEAN`) is free of any contaminated, duplicated, positional, or redshift constraints originating from or overlapping with the protected MeerKAT Vela-SMGPS holdout catalogue (Kraan-Korteweg et al. 2024).

---

## 2. Leakage Test Battery Summary Table

| Test Index | Name | Focus & Audit Scope | Status |
|---|---|---|---|
| **01** | File/Hash/Role Integrity | Registry validation, role boundaries, SHA-256 consistency | **PASS** |
| **02** | Exact ID & Alias Scan | Search for identical PGC, NED, 2MASX, or HIZOA names | **PASS** |
| **03** | Sky-Position Crossmatch | Spherical matching across 1.0', 3.0', 6.0' radii | **PASS** |
| **04** | Redshift/Velocity Consistency | Velocity window delta-cz < 150 km/s in footprint | **PASS** |
| **05** | HIZOA-S ↔ Vela 39 Overlap | Verification of the published 39 HIZOA overlap detections | **PASS** |
| **06** | Derived Lineage Audit | Recursive check of CF4, CF4++, grids for circular MeerKAT data | **PASS** |
| **07** | Code-Level Access Denial | Machine-enforced exceptions in `DataGateway` for `TRAINING` mode | **PASS** |
| **08** | Tuning Leakage Audit | Verification that all hyperparameters were sealed pre-reveal | **PASS** |
| **09** | Cache & Environment Audit | Removal of temporary, cached, or untracked holdout artifacts | **PASS** |
| **10** | Freeze Canary Tamper Test | Active detection of unauthorized modifications to predictions | **PASS** |
| **11** | Negative Control Run | Demonstration of exact byte invariance when HOLDOUT is isolated | **PASS** |
| **12** | Final Certification | Cryptographic signing of TRAIN_CLEAN snapshot and audit log | **PASS** |

---

## 3. The 39 HIZOA Overlap Benchmark Resolution
In Kraan-Korteweg et al. 2024 (MNRAS 531, 3486), the authors explicitly document that 39 HIZOA galaxies fall within the Vela-SMGPS footprint (260° <= l <= 290°, -2° <= b <= +1°).
Our independent audit of `hizoa_s_full.csv`:
- Total Southern ZoA galaxies: 883
- Galaxies in Vela-SMGPS footprint: **Exactly 39**
- Quarantined: **100% (39/39 galaxies)** transferred to `exclusion_list.parquet`
- Residual training count in footprint: **0 galaxies**.

---

## 4. Final Certification
All 12 leakage tests passed without warnings or discrepancies. The dataset `datasets/processed/TRAIN_CLEAN/train_clean_combined.parquet` is certified uncontaminated and authorized for frozen reconstruction.
