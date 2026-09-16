# /goal — Build the reproducible experiment runner and immutable manifests

Build the mechanism that turns Z-ZOA calculations into reproducible research runs.

## Core command

Provide one canonical experiment runner, conceptually:

```text
python -m zzoa run --config configs/<experiment>.yaml
```

Adapt module naming to the actual repo.

## Config requirements

A config must explicitly contain or reference:
- experiment ID;
- stage;
- cosmology;
- velocity/reference-frame policy;
- dataset registry IDs and allowed roles;
- region/mask;
- method;
- method parameters;
- random seed;
- output policy;
- whether freeze anchoring is required.

Do not hide paper-critical scientific choices in source-code constants.

## Run manifest

Every run creates a machine-readable manifest with:
- run ID;
- created timestamp;
- config hash;
- git commit and dirty-tree status if available;
- Python and package versions;
- OS/platform metadata needed for reproducibility;
- dataset IDs, roles, versions, hashes;
- random seeds;
- scientific method version;
- warnings;
- outputs and output hashes;
- stage transitions;
- lineage/parent run IDs;
- final status.

## Output structure

Use a stable structure similar to:

```text
runs/<RUN_ID>/
  manifest.json
  config.resolved.yaml
  checksums.sha256
  logs/
  data/
  arrays/
  metrics/
  tables/
  figures/
  ledger/
```

Only create folders a run actually needs.

## Immutability

- DRAFT/COMPLETE runs may be superseded by a new run.
- FROZEN runs must never be modified in place.
- Any change after freeze must create a new run ID with a parent link.
- Verification must detect changed bytes.

## Replay

Implement a replay/verify command that can:
- load a past resolved config;
- verify input hashes;
- rerun deterministic stages;
- compare output hashes or numerical tolerances;
- produce a clear reproducibility report.

## State machine

Implement explicit allowed transitions. Example:

```text
SETUP -> AUDIT -> TRAIN -> FROZEN -> VALIDATE -> HYBRID -> PAPER
```

Reject illegal transitions such as `TRAIN -> HYBRID` when the experiment requires holdout validation first.

## Tests

Include:
- deterministic run ID/input behavior where specified;
- manifest schema validation;
- dirty working tree recorded, not hidden;
- frozen mutation rejection;
- replay success;
- replay hash mismatch;
- illegal state transition rejection;
- HOLDOUT role rejected in TRAIN configs.

## Completion gate

Create and replay one synthetic calculation run end to end. The second run must reproduce the canonical deterministic outputs and produce an explicit PASS report.
