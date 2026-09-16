# Leakage test 07 — Code-level holdout access denial

Prove the software boundary, not just the folder convention.

Tests must attempt to access HOLDOUT through:
- normal dataset loader;
- direct path;
- registry lookup;
- wildcard/glob discovery;
- symlink if supported;
- archive extraction helper;
- cached dataframe/object;
- parent dataset traversal;
- API endpoint if the app exposes data remotely.

In TRAIN mode every attempt must fail with a specific holdout-access exception and be logged.

AUDIT and VALIDATE access must require their own explicit context/token/state.
