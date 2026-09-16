# /goal — Build the Z-ZOA Calculation Room foundation

Create or continue a standalone scientific project called **Z-ZOA Calculation Room**. This project is separate from the existing 3D explorer. It is a white-space calculation/research environment whose job is to produce reproducible numerical results that can eventually support a peer-reviewed astronomy paper.

## First principle

The scientific Python core is the product. The UI is only a thin interface.

Do not add Three.js, WebGL, galaxy point clouds, cosmic maps, animated particles, decorative dashboards, or fake data. Keep the interface white, sparse, mathematical, and quiet.

## Before implementation

Inspect the entire repository and report:
1. current file tree;
2. existing scientific/data modules we can reuse;
3. proposed Phase-1 architecture;
4. exact files you plan to create or modify;
5. dependency choices;
6. testing strategy.

Wait for approval if this repository does not already contain an approved architecture/spec.

## Required architecture

Keep the science independently callable from Python/CLI:

```text
research/
  coordinates/
  cosmology/
  velocities/
  catalogs/
  provenance/
  holdouts/
  validation/
  reconstruction/
  statistics/
experiments/
configs/
datasets/
  raw/
  processed/
  manifests/
runs/
tests/
backend/
frontend/
docs/
```

Use established astronomy/scientific libraries where appropriate: Astropy, NumPy, SciPy, Pandas/Polars, PyArrow/Parquet, Pydantic, pytest. Keep units explicit with `astropy.units`.

## Phase-1 success criteria

The system must be able to:
- register a real catalogue with source URL/DOI, version, checksum, row count, and role;
- preserve raw files as immutable;
- transform RA/Dec <-> Galactic <-> Supergalactic coordinates reproducibly;
- record heliocentric/Local-Group/CMB velocity-frame metadata without silently mixing frames;
- perform documented low-redshift cosmology/peculiar-velocity utility calculations with propagated units and uncertainty;
- designate datasets as TRAIN, HOLDOUT, VALIDATION, or COMPARISON_ONLY;
- reject training access to HOLDOUT datasets;
- create a run manifest containing config, git commit, dependency versions, input hashes, random seed, warnings, and output hashes;
- rerun the same config and obtain numerically identical deterministic outputs.

## Stop gate

Do not build Wiener filtering, constrained realizations, MeerKAT scoring, Bayesian HMC, or paper conclusions yet. Finish and test the calculation foundation first.
