# Leakage test 11 — Negative control

Run a negative-control workflow designed to catch accidental hidden access.

Examples:
- replace the true HOLDOUT registry entry with a deliberately inaccessible dummy path while running TRAIN; training should produce exactly the same result;
- change holdout-only metadata that should be invisible to TRAIN and verify training hashes remain unchanged;
- remove the entire HOLDOUT directory from the filesystem and rerun TRAIN; output hashes should remain unchanged.

If training output changes, investigate and fail the leakage audit.
