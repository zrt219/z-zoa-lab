# /goal — Freeze the Z-ZOA Vela prediction before validation

Create the formal freeze command for Experiment 001.

## Required pre-freeze state

Before freezing, require:
- dataset registry and hashes verify;
- immutable `TRAIN_CLEAN` snapshot exists;
- pre-freeze leakage/decontamination audit has passed for file roles, duplicates, crossmatches, known HIZOA/Vela overlaps, derived lineage, TRAIN access denial, tuning history, caches/side channels, OS sandbox, and transitive taint;
- 3D Lab pre-reveal safety report passes if the viewer is enabled;
- reconstruction ensemble is complete;
- selection masks/functions are fixed;
- source code commit and dirty-tree status are recorded;
- confirmatory metrics/null procedure are written and ready to hash-lock;
- HOLDOUT scientific contents have not been available to TRAIN.

Do not require tests that logically need a frozen artifact until after the freeze is created.

## Freeze operation

Resolve the final config and create immutable frozen artifacts such as:

```text
runs/<run_id>/
  freeze_manifest.json
  config.resolved.yaml
  prediction_mean.*
  prediction_sigma.*
  prediction_probability.*
  analysis_spec.json
  metrics_spec.json
  null_spec.json
  checksums.sha256
```

`analysis_spec.json` must capture the confirmatory hypotheses, metrics, thresholds, smoothing/grid choices, masks, null procedure, exclusion rules, and multiple-testing policy where applicable.

Canonicalize/hash the analysis spec and include its SHA-256 in the freeze manifest.

## Immutability

After freeze:
- frozen files become read-only/immutable by application policy;
- any change creates a new run ID;
- validation authorization must verify all frozen hashes;
- 3D Lab may read only authorized pre-reveal exports from this frozen run.

## Post-freeze tests still required before reveal

The freeze is a **candidate** until these pass:
- freeze canary/tamper test;
- negative-control run;
- preregistered analysis hash-lock verification;
- controlled reveal-gate test;
- clean-room from-zero reproduction;
- final leakage certificate regeneration;
- XRPL `PREDICTION_FROZEN` validation if the experiment requires it.

Use statuses:

```text
FROZEN_CANDIDATE
FROZEN_VERIFIED
```

Only print:

```text
PREDICTION FROZEN AND VERIFIED — VALIDATION MAY BEGIN
```

after every configured post-freeze gate passes.
