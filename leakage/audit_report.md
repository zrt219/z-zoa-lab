# Z-ZOA Leakage Audit & Decontamination Report

## Executive Summary
A multi-tier crossmatch and holdout decontamination audit was performed to guarantee that no observational constraints overlapping the MeerKAT Vela-SMGPS holdout footprint are accessible to reconstruction training.

## Decontamination Metrics
- **HIZOA-S**: 883 input rows -> 39 excluded -> 844 clean rows.
- **CF4 Sample**: 8 input rows -> 0 excluded -> 8 clean rows.
- **2MRS Sample**: 50 input rows -> 0 excluded -> 50 clean rows.
- **Total Excluded Contaminants**: 39
- **TRAIN_CLEAN Combined Rows**: 902

## Known Overlap Sanity Check (Prompt 06 & Leakage Test 05)
- Statement in Kraan-Korteweg et al. 2024: 39 HIZOA galaxies in Vela-SMGPS footprint.
- Audit finding: Exactly **39** HIZOA-S galaxies identified in [260° <= l <= 290°, -2° <= b <= +1°].
- Exclusion status: 100% of these 39 galaxies quarantined to `exclusion_list.parquet` and stripped from `TRAIN_CLEAN`.

## Resulting Artifacts
- `leakage/audit_matches.parquet`
- `leakage/exclusion_list.parquet`
- `leakage/audit_summary.json`
- `leakage/05_hizoa_vela_overlap.parquet`
- `datasets/processed/TRAIN_CLEAN/train_clean_combined.parquet`
