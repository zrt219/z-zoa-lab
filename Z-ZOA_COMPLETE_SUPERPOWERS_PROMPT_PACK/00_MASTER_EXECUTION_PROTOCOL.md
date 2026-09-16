# /goal — MASTER EXECUTION PROTOCOL FOR Z-ZOA LAB

You are implementing the Z-ZOA Lab as research software that may support a peer-reviewed astronomy paper. Treat every phase as production scientific software, not a visual demo.

## Project objective

Build one coherent project with two deliberately separated environments:

1. **White Calculation Room** — the scientific source of truth. It ingests registered real datasets, performs calculations/reconstruction/statistics, protects holdouts, creates frozen run artifacts, and generates paper outputs.
2. **3D Lab Companion** — a read-only scientific explorer. It visualizes only Calculation Room artifacts that are explicitly authorized for the current research stage. It cannot alter scientific inputs, tune parameters, or bypass holdout controls.

The paper-driving experiment is:

```text
TRAIN_CLEAN
  -> reconstruct WITHOUT selected MeerKAT Vela holdout
  -> quantify uncertainty
  -> freeze prediction + config + method + hashes
  -> pass leakage suite
  -> anchor frozen run to XRPL Testnet when configured
  -> reveal holdout
  -> score against preregistered metrics and survey-matched nulls
  -> add MeerKAT
  -> hybrid reconstruction
  -> measure Delta density / Delta velocity / Delta uncertainty
  -> robustness checks
  -> paper figures/tables/reproducibility bundle/manuscript
```

## Non-negotiable engineering rules

- Inspect the current repository before every phase. Reuse working code rather than duplicating it.
- Do not invent astronomy data, catalog rows, citations, constants, survey properties, or successful results.
- Synthetic data are allowed only in explicitly labeled mock/test workflows.
- Raw downloaded datasets are immutable.
- Scientific quantities retain units and reference-frame metadata.
- Every derived artifact records parents/provenance and hashes.
- HOLDOUT data cannot be accessed in TRAIN mode.
- The 3D Lab cannot read HOLDOUT data before authorized reveal.
- No scientific result may exist only in frontend state or a screenshot.
- Every important computation emits machine-readable artifacts.
- Use tests first for scientific kernels and access-control boundaries.
- Run the smallest relevant test suite after each change and the full suite at phase gates.
- Never claim a phase is complete without showing verification output.
- Never silently weaken a requirement because a dependency or download is difficult.

## Superpowers workflow

For each prompt:

1. Inspect relevant files, tests, configs, and recent changes.
2. State the exact design/change you intend to make.
3. For a new subsystem or major interface, stop for approval if it has not already been approved.
4. Implement test-first.
5. Run verification.
6. Report exact files changed and exact outputs generated.
7. Commit with a focused commit message if the repo is under git and the user has asked the agent to commit.
8. Do not continue into the next numbered prompt automatically unless explicitly told to run the full pack.

## Scientific stage states

The project must understand these states:

```text
SETUP
AUDIT
TRAIN
TRAIN_CLEAN
FROZEN
VALIDATE
HYBRID
PAPER
```

Access policy must be explicit. A frontend route or direct filesystem path must not bypass it.

## Product structure target

Adapt to the actual repository, but preserve these responsibility boundaries:

```text
research/              # pure scientific Python core
  catalogs/
  coordinates/
  cosmology/
  velocities/
  reconstruction/
  statistics/
  validation/
  holdouts/
  provenance/
  ledger/

experiments/           # experiment definitions and runners
configs/               # versioned configs
runs/                  # immutable/frozen run outputs
scripts/               # one-off reproducible utilities
backend/               # thin API around research core
frontend/              # Calculation Room + 3D Lab UI

tests/
  unit/
  integration/
  scientific/
  security/

docs/
```

## Definition of done for the entire project

Do not call Z-ZOA "done" until `20_FINAL_END_TO_END_ACCEPTANCE.md` passes. The end state must demonstrate a complete synthetic rehearsal of the real paper workflow, and then be ready to run the real Vela experiment without redesigning the architecture.
