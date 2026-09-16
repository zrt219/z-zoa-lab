# Z-ZOA Complete Lab Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use the prompts in `RUN_ORDER.md` as reviewer-sized gates.

**Goal:** Build a reproducible Z-ZOA Calculation Room, scientific calculator, leakage-controlled reconstruction workflow, read-only 3D Lab Companion, run-integrity anchoring, and paper-production pipeline.

**Architecture:** Scientific calculations live in an independently testable Python core. The Calculation Room orchestrates and inspects that core; the 3D Lab consumes versioned read-only artifacts; holdout authorization is enforced by backend/filesystem policy rather than frontend hiding. Paper outputs derive only from frozen run artifacts.

**Tech Stack:** Python scientific stack (Astropy/NumPy/SciPy/PyArrow/Pydantic/pytest or existing equivalents), FastAPI if already adopted, React/TypeScript/Vite if already adopted, Three.js for 3D companion if compatible, XRPL Testnet through `xrpl-py` for optional research anchoring.

**Spec:** `00_MASTER_EXECUTION_PROTOCOL.md`

## Global Constraints

- No invented observational data.
- Raw datasets immutable.
- HOLDOUT denied during TRAIN.
- Scientific units/reference frames explicit.
- Every derived artifact has provenance + hashes.
- 3D Lab is read-only with respect to science.
- Confirmatory analysis decisions freeze before holdout reveal.
- XRPL anchoring is integrity/chronology metadata only.
- Paper outputs are generated from verified run artifacts.

---

### Task 1: Calculation Room foundation

**Prompt files:** `01_PROJECT_BOOTSTRAP_GOAL.md`, `01A_WHITE_CALCULATION_ROOM_UI.md`, `01B_SCIENTIFIC_CALCULATOR_SUITE.md`, `01C_EXPERIMENT_RUNNER_AND_MANIFESTS.md`, `01D_TEST_HARNESS_AND_CI.md`

**Produces:** callable scientific calculator functions, thin UI/API, reproducible run manifests, default CI/test gates.

**Review gate:** synthetic deterministic run replays successfully and no fake fallback data appear.

### Task 2: Data provenance and holdout boundary

**Prompt files:** `02_DATASET_AUDIT_AND_DOWNLOAD.md` through `08_SELECTION_FUNCTIONS_AND_MASKS.md`

**Produces:** registered real datasets, `TRAIN_CLEAN`, explicit survey masks/selection functions, CF4 baseline validation.

**Review gate:** all paper inputs have source/version/hash/role/units/frame/lineage and HOLDOUT cannot be loaded in TRAIN.

### Task 3: Reconstruction engine

**Prompt files:** `09_MOCK_UNIVERSE_VALIDATION.md`, `10_RECONSTRUCTION_ENGINE_PHASE1.md`, `11_CONSTRAINED_REALIZATIONS.md`

**Produces:** baseline reconstruction, ensemble mean/uncertainty/probability, mock recovery report.

**Review gate:** known synthetic hidden structure is recovered within documented metrics before real reveal.

### Task 4: 3D Lab Companion

**Prompt files:** `11A_3D_LAB_COMPANION_FOUNDATION.md` through `11E_3D_LAB_HOLDOUT_SAFETY.md`

**Produces:** versioned export contract, scientific viewer layers, read-only comparisons, leakage-safe authorization.

**Review gate:** synthetic frozen run renders correctly and holdout attack tests fail closed.

### Task 5: Freeze and research-integrity gates

**Prompt files:** `12_FREEZE_PREDICTION.md`, `12A_XRPL_TESTNET_RUN_ANCHORING.md`, `leakage_tests/*`

**Produces:** immutable frozen prediction, analysis hash lock, leakage certificate, optional validated XRPL Testnet receipt, clean-room reproduction evidence.

**Review gate:** holdout remains inaccessible unless every configured gate verifies.

### Task 6: Confirmatory Vela validation and hybrid reconstruction

**Prompt files:** `13_REVEAL_AND_SCORE_MEERKAT.md`, `14_HYBRID_RECONSTRUCTION.md`, `14A_3D_LAB_HYBRID_COMPARISON.md`, `15_ROBUSTNESS_SWEEPS.md`

**Produces:** preserved confirmatory holdout score, survey-matched null statistics, hybrid deltas, robustness outputs.

**Review gate:** post-reveal exploratory analyses are versioned separately and cannot overwrite confirmatory results.

### Task 7: Paper factory and external reproducibility

**Prompt files:** `16_PAPER_OUTPUT_FACTORY.md` through `19A_REPO_AND_PRODUCT_POLISH.md`

**Produces:** figures/tables, reproducibility bundle, manuscript draft, pre-submission audit, externally understandable repository.

**Review gate:** all manuscript numbers/figures trace back to run IDs and machine-readable artifacts.

### Task 8: Final end-to-end acceptance

**Prompt file:** `20_FINAL_END_TO_END_ACCEPTANCE.md`

**Produces:** final synthetic rehearsal, leakage attack report, clean-room reproduction report, real-experiment pre-reveal readiness status.

**Review gate:** `acceptance/FINAL_ACCEPTANCE_REPORT.md` = PASS for all mandatory criteria.
