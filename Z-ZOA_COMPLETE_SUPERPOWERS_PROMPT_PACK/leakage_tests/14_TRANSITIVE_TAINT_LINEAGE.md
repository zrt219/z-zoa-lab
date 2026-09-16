# Leakage test 14 — Transitive taint / ancestry scan

Audit the complete parent graph for every TRAIN and reference-derived artifact.

## Rule

If ANY ancestor is:
- HOLDOUT;
- a hybrid/MeerKAT-assimilated reconstruction;
- derived from an unknown/unregistered parent;
- generated after holdout reveal without a clean pre-reveal lineage;

then mark the artifact:

```text
TAINTED_FOR_CONFIRMATORY_VELA
```

and deny it to the confirmatory TRAIN/FROZEN run.

## Requirements

- walk lineage recursively, not just one parent level;
- detect cycles/unknown nodes;
- output a machine-readable DAG report;
- show the exact contamination path for every rejected artifact.

Save `leakage/14_transitive_taint_report.json` and `.md`.
