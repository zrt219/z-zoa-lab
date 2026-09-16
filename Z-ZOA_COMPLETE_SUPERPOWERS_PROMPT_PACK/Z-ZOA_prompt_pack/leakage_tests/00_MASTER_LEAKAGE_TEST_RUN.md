# /goal — MASTER Z-ZOA leakage test run

Run a complete pre-freeze leakage audit for Vela Experiment 001.

## Objective

Prove, as far as reasonably possible, that the reconstruction training snapshot does not contain the scientific information we intend to validate against in Vela-SMGPS (and, where configured, Vela-HI).

## Critical separation

Run this in `AUDIT` mode. AUDIT may read both training candidates and holdout data only for duplicate/crossmatch/lineage detection. It must not fit, tune, reconstruct, or calculate holdout performance.

## Run order

Execute these prompts/tests in order:
1. file/hash/role integrity;
2. exact IDs and alias duplicates;
3. sky-position crossmatch;
4. position + velocity/redshift crossmatch;
5. explicit HIZOA <-> Vela known-overlap test;
6. derived-product lineage audit;
7. code-level holdout access denial;
8. hyperparameter/tuning leakage check;
9. cache/artifact/environment leakage check;
10. freeze-manifest canary test;
11. negative-control run;
12. final leakage report;
13. OS-level physical holdout sandbox;
14. transitive dependency taint scan;
15. preregistered analysis hash lock;
16. side-channel leakage scan;
17. double-blind unblinding reveal gate;
18. cleanroom from-zero reproduction.

## Pass condition

A pass requires:
- a reproducible exclusion list;
- a new immutable `TRAIN_CLEAN` snapshot;
- no known holdout-derived products in the training lineage;
- training cannot open holdout data;
- no configs were chosen using holdout score/performance;
- caches/artifacts cannot leak holdout-derived fields into training;
- the final report lists all residual uncertainties.

If any test fails, stop the scientific run, mark the experiment `BLOCKED_BY_LEAKAGE`, repair the issue, regenerate TRAIN_CLEAN, and rerun this entire suite.
