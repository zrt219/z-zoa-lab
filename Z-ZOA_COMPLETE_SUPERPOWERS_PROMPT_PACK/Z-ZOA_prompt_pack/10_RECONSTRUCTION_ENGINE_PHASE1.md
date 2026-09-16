# /goal — Implement the first paper-capable Z-ZOA reconstruction engine

Build the simplest scientifically defensible reconstruction needed for the first Vela holdout experiment. Do not jump directly to Nusser-style million-parameter Bayesian HMC.

## Required properties

- consumes only `TRAIN_CLEAN` datasets;
- uses explicit config for cosmology, smoothing scale, grid, distance cuts, and random seed;
- emits a 3D density estimate and, if supported by the chosen method, a velocity estimate;
- propagates observational uncertainty as honestly as the method permits;
- is deterministic when configured deterministically;
- records full provenance and hashes;
- has mock-universe tests.

Prefer a transparent baseline method first. If implementing a Wiener-filter / constrained-realization method, document equations, priors, covariance assumptions, boundary conditions, and numerical solver choices.

## Output contract

Every reconstruction run must produce machine-readable arrays plus a manifest and a method summary. No result may exist only in a UI.
