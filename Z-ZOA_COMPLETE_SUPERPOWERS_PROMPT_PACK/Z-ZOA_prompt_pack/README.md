# Z-ZOA Prompt Pack

This folder contains the full staged prompt sequence for building the **Z-ZOA Calculation Room**, running the first Vela out-of-sample experiment, and producing paper-grade outputs.

## What this pack is for

The goal is not to make another 3D visualization. The goal is to turn the existing Z-ZOA data collection into a reproducible research pipeline that can support a defensible paper:

**Z-ZOA: Out-of-Sample Reconstruction and H I Validation of Large-Scale Structure Across the Galactic Zone of Avoidance**

The core experiment is:

```text
TRAIN_CLEAN
    -> reconstruction without selected MeerKAT holdout
    -> freeze prediction + config + hashes
    -> reveal holdout
    -> quantitative scoring against survey-matched nulls
    -> add holdout
    -> hybrid reconstruction
    -> measure delta density / velocity / uncertainty
```

## Run order

Run the prompts in numeric order. Do not skip the stop gates.

### Foundation
1. `01_PROJECT_BOOTSTRAP_GOAL.md`
2. `02_DATASET_AUDIT_AND_DOWNLOAD.md`
3. `03_DATASET_REGISTRY_PROVENANCE.md`
4. `04_NORMALIZE_COORDINATES_UNITS.md`
5. `05_HOLDOUT_ACCESS_CONTROL.md`
6. `06_CROSSMATCH_DECONTAMINATION.md`

### Baseline science
7. `07_CF4_BASELINE_VALIDATION.md`
8. `08_SELECTION_FUNCTIONS_AND_MASKS.md`
9. `09_MOCK_UNIVERSE_VALIDATION.md`
10. `10_RECONSTRUCTION_ENGINE_PHASE1.md`
11. `11_CONSTRAINED_REALIZATIONS.md`
12. `12_FREEZE_PREDICTION.md`

### Holdout experiment
13. Run every file in `leakage_tests/` in order (00 through 18, covering 6 defense-in-depth boundaries: filesystem, ancestry, analysis decisions, side channels, reveal procedure, and clean-room reproduction).
14. `13_REVEAL_AND_SCORE_MEERKAT.md`
15. `14_HYBRID_RECONSTRUCTION.md`
16. `15_ROBUSTNESS_SWEEPS.md`

### Paper production
17. `16_PAPER_OUTPUT_FACTORY.md`
18. `17_REPRODUCIBILITY_BUNDLE.md`
19. `18_MANUSCRIPT_DRAFT.md`
20. `19_PRE_SUBMISSION_AUDIT.md`

## Non-negotiable rule

The scientific reconstruction must never be tuned against Vela-SMGPS or Vela-HI before the prediction is frozen. The leakage audit may read both sides only to identify duplicated/derived information and produce an exclusion list. It is not allowed to optimize scientific parameters.

## Recommended workflow with Antigravity / coding agent

Paste one prompt at a time. Require the agent to:

- inspect the repository before editing;
- summarize the proposed change before implementation when the prompt asks for it;
- run tests;
- show exact output paths;
- stop at the stated gate;
- never substitute synthetic data for missing real data unless the prompt explicitly asks for a mock test.

See `SOURCES.md` for the scientific sources that motivated the holdout and leakage controls.
