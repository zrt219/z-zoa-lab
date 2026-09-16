# Leakage test 01 — File/hash/role integrity

Enumerate every file reachable by the training process.

For each file report:
- dataset registry ID;
- role;
- SHA-256;
- size;
- parents/lineage;
- path;
- whether the TRAIN process can read it.

Fail if:
- any `HOLDOUT` or contaminated derived product is reachable by TRAIN;
- an input hash differs from the registry;
- a training file has unknown provenance;
- a symlink/archive/cache bypasses the intended role boundary.

Save `leakage/01_file_role_integrity.json` and `.md`.
