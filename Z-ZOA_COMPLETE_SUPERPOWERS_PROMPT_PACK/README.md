# Z-ZOA Complete Superpowers Prompt Pack

This is the consolidated prompt suite for taking **Z-ZOA Lab** from an early research-software project to a paper-capable system with:

- White Calculation Room;
- scientific calculator suite;
- real dataset registry/provenance;
- holdout/leakage protection;
- CF4 validation;
- mock-universe validation;
- reconstruction + constrained realizations;
- 3D Lab Companion;
- frozen prediction workflow;
- XRPL Testnet run anchoring;
- Vela MeerKAT reveal/score experiment;
- hybrid reconstruction;
- robustness sweeps;
- paper figures/tables;
- reproducibility bundle;
- manuscript draft;
- final end-to-end acceptance.

## Start here

1. Give your coding agent `00_MASTER_EXECUTION_PROTOCOL.md`.
2. Keep `PROMPT_MAP.md` nearby when you need to know which prompt owns a feature.
3. Follow `RUN_ORDER.md` exactly.
4. Run **one prompt at a time** unless you intentionally want the agent to execute an entire approved phase.
5. Do not reveal the real Vela holdout early just because later prompts exist in this folder.

## The three things people keep mixing up

### Calculation Room

The scientific workstation. It owns configs, datasets, calculations, runs, manifests, reconstruction, statistics, auditing, freeze state, and paper artifacts.

### Scientific Calculator

A set of small auditable tools *inside* the Calculation Room: coordinate conversion, cosmological distance calculations, peculiar-velocity workbench, CF4 grid probe, separation/crossmatch calculations, and uncertainty inspection.

### 3D Lab Companion

A read-only visual explorer of **authorized exported run artifacts**. It does not create the scientific result and cannot unlock HOLDOUT data.

## Core scientific experiment

```text
TRAIN_CLEAN
 -> reconstruction without selected MeerKAT
 -> uncertainty ensemble
 -> freeze prediction + analysis spec
 -> leakage suite
 -> optional XRPL Testnet anchor
 -> reveal MeerKAT
 -> quantitative score vs survey-aware nulls
 -> hybrid reconstruction
 -> Delta density / velocity / uncertainty
 -> robustness
 -> paper
```

## Leakage suite

`leakage_tests/` now contains 18 defense layers, including:
- file roles/hashes;
- ID/alias duplicates;
- sky-position matches;
- redshift/velocity matches;
- HIZOA-Vela overlap sanity check;
- derived-product lineage;
- code access denial;
- tuning audit;
- cache/environment scan;
- freeze canaries;
- negative controls;
- OS-level holdout sandbox;
- transitive taint scan;
- preregistered analysis hash lock;
- side-channel metadata scan;
- controlled reveal gate;
- clean-room from-zero reproduction.

## Visual references

`visual_refs/` contains the notebook-style sketches created for the project. They are design references only and include illustrative values. Production code must use real backend/run artifacts.

## Important wording

Unless a truly prospective untouched survey release is used, describe the first Vela experiment as a **leakage-controlled out-of-sample/holdout validation**, not a historically blind discovery.

## Final gate

Do not call the system complete until `20_FINAL_END_TO_END_ACCEPTANCE.md` passes.
