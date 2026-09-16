# Leakage test 16 — Side-channel leakage scan

Detect and scrub holdout metadata, intermediate caches, logs, and side-channel remnants.

## Objective

Ensure that no residual traces or metadata concerning the holdout dataset (e.g. coordinates, row counts, filenames, index tables, cache entries) exist in secondary channels that could indirectly influence training code or configurations.

## Requirements

1. **Broad-Spectrum Multi-Layer Scan**: Recursively inspect:
   - shell history files (PowerShell `ConsoleHost_history.txt`, bash history);
   - active process environment variables and paths;
   - embedded databases (DuckDB, SQLite, Parquet indices);
   - temporary build caches (`.pytest_cache/`, `__pycache__/`, `.cache/`);
   - run logs, previous result JSONs, and notebook checkpoints.
2. **Detection Logic**: Flag any occurrence of holdout keywords, coordinates ($260^\circ \le \ell \le 290^\circ$, $-2^\circ \le b \le +1^\circ$), or holdout detection totals ($843$, $719$) in training execution paths.
3. **Clean-Slate Dry Run**: Prove that when all temporary caches and logs are completely purged, the training reconstruction executes to completion with identical deterministic outputs.

Save `leakage/16_side_channel_scan.json` and `.md`.
