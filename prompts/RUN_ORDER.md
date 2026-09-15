# Z-ZOA Complete Run Order

Run one prompt at a time unless you deliberately tell the coding agent to execute a full phase. Do not skip scientific gates.

## Phase 0 — Rules

1. `00_MASTER_EXECUTION_PROTOCOL.md`
2. Read `PROMPT_MAP.md`

## Phase 1 — Calculation Room + calculator foundation

3. `01_PROJECT_BOOTSTRAP_GOAL.md`
4. `01A_WHITE_CALCULATION_ROOM_UI.md`
5. `01B_SCIENTIFIC_CALCULATOR_SUITE.md`
6. `01C_EXPERIMENT_RUNNER_AND_MANIFESTS.md`
7. `01D_TEST_HARNESS_AND_CI.md`

**Gate:** calculation functions work from Python/API/UI; real data are not required to fake an interface; synthetic rehearsal passes.

## Phase 2 — Real datasets, provenance, and holdout boundaries

8. `02_DATASET_AUDIT_AND_DOWNLOAD.md`
9. `03_DATASET_REGISTRY_PROVENANCE.md`
10. `04_NORMALIZE_COORDINATES_UNITS.md`
11. `05_HOLDOUT_ACCESS_CONTROL.md`
12. `06_CROSSMATCH_DECONTAMINATION.md`
13. `07_CF4_BASELINE_VALIDATION.md`
14. `08_SELECTION_FUNCTIONS_AND_MASKS.md`

**Gate:** `TRAIN_CLEAN` can be built reproducibly; every paper-relevant input has source/version/hash/units/frame/lineage.

## Phase 3 — Reconstruction science

15. `09_MOCK_UNIVERSE_VALIDATION.md`
16. `10_RECONSTRUCTION_ENGINE_PHASE1.md`
17. `11_CONSTRAINED_REALIZATIONS.md`

**Gate:** method recovers known synthetic hidden structure with quantified uncertainty before any real Vela reveal.

## Phase 4 — 3D Lab Companion

18. `11A_3D_LAB_COMPANION_FOUNDATION.md`
19. `11B_CALCULATION_TO_3D_DATA_CONTRACT.md`
20. `11C_3D_LAB_SCIENTIFIC_LAYERS.md`
21. `11D_3D_LAB_RUN_COMPARISON.md`
22. `11E_3D_LAB_HOLDOUT_SAFETY.md`

**Gate:** 3D Lab renders only exported authorized artifacts and cannot access HOLDOUT pre-reveal.

## Phase 5 — Freeze, integrity, and leakage

23. Run **Stage A** of `leakage_tests/00_MASTER_LEAKAGE_TEST_RUN.md` (pre-freeze audit).
24. `12_FREEZE_PREDICTION.md` to create `FROZEN_CANDIDATE`.
25. `12A_XRPL_TESTNET_RUN_ANCHORING.md` if anchoring is required/configured.
26. Run **Stages C-D** of `leakage_tests/00_MASTER_LEAKAGE_TEST_RUN.md` (post-freeze integrity + final certificate).

**Gate:** run status is `FROZEN_VERIFIED`; analysis spec + leakage certificate verify; clean-room reproduction passes; holdout remains locked until configured gates pass.

## Phase 6 — Real holdout experiment

27. `13_REVEAL_AND_SCORE_MEERKAT.md`
28. `14_HYBRID_RECONSTRUCTION.md`
29. `14A_3D_LAB_HYBRID_COMPARISON.md`
30. `15_ROBUSTNESS_SWEEPS.md`

**Gate:** confirmatory result is preserved separately from any post-reveal exploratory analyses.

## Phase 7 — Paper and external reproducibility

31. `16_PAPER_OUTPUT_FACTORY.md`
32. `17_REPRODUCIBILITY_BUNDLE.md`
33. `18_MANUSCRIPT_DRAFT.md`
34. `19_PRE_SUBMISSION_AUDIT.md`
35. `19A_REPO_AND_PRODUCT_POLISH.md`

## Phase 8 — Final system gate

36. `20_FINAL_END_TO_END_ACCEPTANCE.md`

Do not call the system paper-ready until this passes.
