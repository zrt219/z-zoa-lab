# /goal — Cross-match and decontaminate training catalogues against the Vela holdout

Build a dedicated leakage-audit crossmatch pipeline. This step is allowed to compare TRAIN candidates with HOLDOUT solely to identify duplicated information and create training exclusions.

## Crossmatch layers

1. Exact catalogue/source identifiers and aliases.
2. Sky-position match with configurable angular radii.
3. Sky-position + velocity/redshift consistency.
4. Known cross-survey aliases where provided by catalogue notes.
5. Parent/derived-product lineage contamination.

## Important known check

The published Vela-SMGPS paper reports 39 HIZOA detections within its survey area and states that Vela-SMGPS recovered all of them. Therefore a HIZOA-trained / Vela-SMGPS-held-out experiment must explicitly identify and exclude overlapping HIZOA information from the training snapshot. Do not hardcode 39 as the answer; use it as an external sanity check and investigate any discrepancy.

Also cross-match 2MRS/other training catalogues to ensure a holdout galaxy does not already have an equivalent redshift constraint under another identifier.

## Outputs

```text
leakage/audit_matches.parquet
leakage/exclusion_list.parquet
leakage/audit_summary.json
leakage/audit_report.md
datasets/processed/TRAIN_CLEAN/<...>
```

The report must show match method, separation, velocity difference, source IDs, reason for exclusion, and parent datasets.

Do not calculate holdout recovery performance in this phase.
