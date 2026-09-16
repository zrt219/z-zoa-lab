# Leakage test 16 — Side-channel / metadata leakage scan

Search for holdout-derived information outside the obvious HOLDOUT catalogue files.

Inspect:
- filenames and folder names;
- row counts and summaries;
- logs and generated reports;
- notebooks and checkpoint folders;
- DuckDB/SQLite tables;
- Parquet/Arrow metadata;
- frontend static assets;
- API caches;
- browser-test fixtures/snapshots;
- saved 3D bundles;
- prior screenshots/annotations;
- shell/generated config histories in the project workspace;
- previous hybrid/validation run artifacts.

Classify each finding as:

```text
SAFE_METADATA
AUDIT_ONLY
HOLDOUT_DERIVED
UNKNOWN
```

HOLDOUT_DERIVED and UNKNOWN artifacts must not be reachable by TRAIN.

Save `leakage/16_side_channel_scan.json` and `.md`.
