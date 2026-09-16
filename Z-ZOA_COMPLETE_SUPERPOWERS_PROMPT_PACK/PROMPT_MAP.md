# Z-ZOA Prompt Map — what each prompt is for

If you are wondering **which prompt builds what**, use this map.

## Calculation Room / calculator

- `01_PROJECT_BOOTSTRAP_GOAL.md` — scientific project foundation and directory boundaries.
- `01A_WHITE_CALCULATION_ROOM_UI.md` — the minimalist white research workspace UI.
- `01B_SCIENTIFIC_CALCULATOR_SUITE.md` — coordinate, cosmology, peculiar-velocity, uncertainty, and grid-query calculators.
- `01C_EXPERIMENT_RUNNER_AND_MANIFESTS.md` — reproducible run engine, configs, logs, manifests, replay.
- `01D_TEST_HARNESS_AND_CI.md` — scientific/security test harness and continuous verification.

## Real data + provenance

- `02_DATASET_AUDIT_AND_DOWNLOAD.md`
- `03_DATASET_REGISTRY_PROVENANCE.md`
- `04_NORMALIZE_COORDINATES_UNITS.md`
- `05_HOLDOUT_ACCESS_CONTROL.md`
- `06_CROSSMATCH_DECONTAMINATION.md`
- `07_CF4_BASELINE_VALIDATION.md`
- `08_SELECTION_FUNCTIONS_AND_MASKS.md`

## Reconstruction science

- `09_MOCK_UNIVERSE_VALIDATION.md`
- `10_RECONSTRUCTION_ENGINE_PHASE1.md`
- `11_CONSTRAINED_REALIZATIONS.md`

## 3D Lab Companion

- `11A_3D_LAB_COMPANION_FOUNDATION.md` — creates the 3D Lab route/shell and read-only architecture.
- `11B_CALCULATION_TO_3D_DATA_CONTRACT.md` — defines exactly how frozen scientific outputs reach the viewer.
- `11C_3D_LAB_SCIENTIFIC_LAYERS.md` — H I points, density, uncertainty, velocity vectors/streamlines, ZoA plane.
- `11D_3D_LAB_RUN_COMPARISON.md` — compare runs without changing them.
- `11E_3D_LAB_HOLDOUT_SAFETY.md` — prevents the viewer from becoming a leakage path.

## Freeze / integrity / leakage

- `12_FREEZE_PREDICTION.md`
- `12A_XRPL_TESTNET_RUN_ANCHORING.md`
- every prompt in `leakage_tests/`

## Main paper experiment

- `13_REVEAL_AND_SCORE_MEERKAT.md`
- `14_HYBRID_RECONSTRUCTION.md`
- `14A_3D_LAB_HYBRID_COMPARISON.md`
- `15_ROBUSTNESS_SWEEPS.md`

## Paper and release

- `16_PAPER_OUTPUT_FACTORY.md`
- `17_REPRODUCIBILITY_BUNDLE.md`
- `18_MANUSCRIPT_DRAFT.md`
- `19_PRE_SUBMISSION_AUDIT.md`
- `19A_REPO_AND_PRODUCT_POLISH.md`
- `20_FINAL_END_TO_END_ACCEPTANCE.md`

## Simplest mental model

```text
Calculation Room = DOES the science
Scientific Calculator = checks individual equations/objects/grids
Reconstruction Engine = builds the hidden-field inference
3D Lab = READS and explores frozen outputs
Leakage Suite = keeps the holdout honest
XRPL = timestamps/fingerprints frozen research stages
Paper Factory = turns verified outputs into manuscript artifacts
```
