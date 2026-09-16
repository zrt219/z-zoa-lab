# Leakage test 18 — Cleanroom from-zero reproduction

Execute the ultimate nuclear-option test of computational reproducibility and isolation.

## Objective

Prove that the entire scientific prediction can be reproduced from zero in a completely sanitized, isolated workspace containing strictly the source code and registered `TRAIN_CLEAN` inputs, without access to any existing caches, intermediate products, environment variables, or holdout files.

## Requirements

1. **Isolated Workspace Provisioning**: Create an ephemeral directory (e.g. via `tempfile.TemporaryDirectory`).
2. **Minimal Allowlist Copying**: Copy exclusively:
   - versioned pipeline code (`research/`, `zzoa/`);
   - configurations (`configs/`);
   - verified `TRAIN_CLEAN` inputs (`datasets/processed/TRAIN_CLEAN/train_clean_combined.parquet`).
   Strictly exclude `datasets/HOLDOUT/`, `runs/`, `.cache/`, `.pytest_cache/`, and temporary scratch directories.
3. **Execution From Scratch**: Re-run the full 3D reconstruction and constrained realization ensemble in the cleanroom directory.
4. **Digest Verification**: Compare generated prediction array SHA-256 digests ($\langle \delta \rangle$, $\sigma_\delta$, $P(\delta > 1.0)$) against the original frozen run manifest.
5. **Pass Condition**: The cleanroom reproduction must match the original outputs within machine-precision numerical tolerances ($\Delta < 10^{-12}$).

Save `leakage/18_cleanroom_reproduction.json` and `.md`.
