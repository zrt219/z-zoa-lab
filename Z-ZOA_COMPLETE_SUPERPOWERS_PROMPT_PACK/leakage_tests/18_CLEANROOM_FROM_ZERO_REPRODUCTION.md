# Leakage test 18 — Clean-room from-zero reproduction

Perform the strongest pre-reveal reproducibility/leakage check.

## Procedure

1. Start from a clean checkout/environment.
2. Do not mount HOLDOUT data.
3. Mount only approved TRAIN_CLEAN inputs by explicit allowlist.
4. Recreate dependencies from the lock/environment definition.
5. Run the frozen prediction config from zero caches.
6. Compare the new run to the candidate frozen run.

Compare:
- resolved config hash;
- input dataset hashes;
- code commit;
- canonical method parameters;
- deterministic output hashes where expected;
- otherwise documented numerical tolerances for stochastic/numerical stages;
- prediction statistics;
- warnings.

## Pass condition

A second researcher/environment can regenerate the pre-reveal scientific prediction without having the holdout data available.

Save `leakage/18_cleanroom_reproduction_report.json` and `.md`.
