# /goal — MASTER Z-ZOA leakage audit and reveal-gating sequence

Run the complete leakage-control program for Vela Experiment 001. Some tests must happen **before freeze**, while others require a frozen candidate. Do not force them into naive numeric order.

## Objective

Demonstrate, as far as reasonably possible, that the confirmatory reconstruction and analysis were produced without using the scientific information intended for validation in Vela-SMGPS (and Vela-HI where configured).

## AUDIT rule

Crossmatch/leakage AUDIT may read TRAIN candidates and HOLDOUT only to identify duplicate information, ancestry, or access paths. It must not tune reconstruction parameters, select thresholds from holdout performance, reconstruct with the holdout, or calculate the confirmatory holdout result.

# Stage A — Pre-freeze data and environment audit

Run:

1. `01_FILE_HASH_AND_ROLE_INTEGRITY.md`
2. `02_EXACT_ID_DUPLICATE_SCAN.md`
3. `03_SKY_POSITION_CROSSMATCH.md`
4. `04_REDSHIFT_VELOCITY_CROSSMATCH.md`
5. `05_HIZOA_VELA_39_KNOWN_OVERLAPS.md`
6. `06_DERIVED_PRODUCT_LINEAGE_AUDIT.md`
7. `07_HOLDOUT_CODE_ACCESS_TEST.md`
8. `08_TUNING_LEAKAGE_TEST.md`
9. `09_CACHE_ARTIFACT_ENVIRONMENT_LEAKAGE.md`
10. `13_OS_LEVEL_HOLDOUT_SANDBOX.md`
11. `14_TRANSITIVE_TAINT_LINEAGE.md`
12. `16_SIDE_CHANNEL_METADATA_SCAN.md`

Also require the 3D Lab holdout-safety report if the viewer is enabled.

Output a `PRE_FREEZE_LEAKAGE_STATUS.json`. If any mandatory test fails, set:

```text
BLOCKED_BY_LEAKAGE
```

and do not freeze.

# Stage B — Create frozen candidate

Run the root prompt:

```text
12_FREEZE_PREDICTION.md
```

This creates `FROZEN_CANDIDATE`, not yet authorized reveal.

# Stage C — Post-freeze integrity tests

Run:

1. `10_FREEZE_MANIFEST_AND_CANARY.md`
2. `11_NEGATIVE_CONTROL_RUN.md`
3. `15_PREREGISTERED_ANALYSIS_HASH_LOCK.md`
4. `17_CONTROLLED_REVEAL_GATE.md`
5. `18_CLEANROOM_FROM_ZERO_REPRODUCTION.md`

If XRPL anchoring is required, also require successful `PREDICTION_FROZEN` anchor verification from `12A_XRPL_TESTNET_RUN_ANCHORING.md`.

# Stage D — Final report/certificate

Run:

```text
12_FINAL_LEAKAGE_REPORT.md
```

The final certificate must hash all Stage A/C outputs plus the frozen prediction/analysis spec and 3D safety report.

## Global PASS condition

A PASS requires:
- reproducible exclusion list;
- immutable TRAIN_CLEAN snapshot;
- no known holdout-derived products in training lineage;
- TRAIN cannot open HOLDOUT through loader, API, 3D viewer, cache, direct path, or OS sandbox;
- no confirmatory parameters/metrics were chosen using holdout outcomes;
- analysis specification is hash-locked;
- frozen prediction passes tamper/canary tests;
- clean-room run reproduces the pre-reveal prediction without HOLDOUT mounted;
- controlled reveal gate rejects tampered states;
- final report declares residual limitations honestly.

Only a final PASS may promote the run to:

```text
FROZEN_VERIFIED
```
