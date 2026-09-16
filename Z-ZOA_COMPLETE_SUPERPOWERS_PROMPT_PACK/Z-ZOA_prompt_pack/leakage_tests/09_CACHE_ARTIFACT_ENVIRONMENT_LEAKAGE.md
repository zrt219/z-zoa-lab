# Leakage test 09 — Cache/artifact/environment leakage

Search the repository and runtime environment for stale holdout-derived artifacts that training code could accidentally reuse.

Inspect:
- `.cache`, temp folders, notebook checkpoints;
- DuckDB/SQLite databases;
- Parquet/CSV intermediates;
- serialized NumPy arrays/pickles;
- generated features;
- model/reconstruction checkpoints;
- web-backend caches;
- prior `runs/` directories;
- environment variables or config paths.

Any untracked artifact with unknown lineage is forbidden from the confirmatory training run.

Create a clean-room run option that starts with an empty cache and explicit input allowlist.
