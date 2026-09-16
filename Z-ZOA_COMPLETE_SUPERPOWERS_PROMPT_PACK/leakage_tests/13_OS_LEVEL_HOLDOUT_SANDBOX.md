# Leakage test 13 — OS-level HOLDOUT sandbox

Prove that TRAIN does not merely *choose not to* read the holdout; make the holdout physically unreadable to the training process.

## Required test

Run the frozen-training workflow in a clean environment/container/process namespace where:
- HOLDOUT paths are not mounted or are permission-denied;
- known holdout environment variables are absent;
- network access to configured holdout catalogue endpoints is disabled where practical;
- only an explicit TRAIN_CLEAN allowlist is mounted/readable.

Training outputs must match the normal clean training run within the deterministic/hash or documented numerical tolerance policy.

## Fail if
- training crashes because it secretly expects a holdout path;
- output changes because holdout metadata is missing;
- the process can open HOLDOUT by absolute path, symlink, parent traversal, or alternate mount.

Save `leakage/13_os_sandbox_report.json` and `.md`.
