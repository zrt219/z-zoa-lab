# /goal — Freeze the Z-ZOA Vela prediction before validation

Create a formal freeze command for Experiment 001.

## Freeze prerequisites

- all leakage tests pass;
- training input is an immutable `TRAIN_CLEAN` snapshot;
- reconstruction code commit is clean/recorded;
- config is final;
- metrics to be used after reveal are defined;
- null-generation procedure is defined;
- selection masks are fixed;
- reconstruction ensemble is complete;
- no HOLDOUT data were available to the TRAIN process.

## Frozen artifacts

Create:

```text
runs/<run_id>/freeze_manifest.json
runs/<run_id>/prediction_mean.*
runs/<run_id>/prediction_sigma.*
runs/<run_id>/prediction_probability.*
runs/<run_id>/metrics_spec.json
runs/<run_id>/null_spec.json
runs/<run_id>/checksums.sha256
```

The freeze manifest must hash the code/config/input/output state. Any subsequent change to a scientific config or prediction file invalidates the freeze.

Print a prominent message: `PREDICTION FROZEN — VALIDATION MAY BEGIN` only after verification succeeds.
