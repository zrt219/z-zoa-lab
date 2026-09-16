# /goal — Build mock-universe validation before touching the real holdout score

Create synthetic controlled experiments where the true hidden density field is known.

## Purpose

Test whether the proposed reconstruction/validation machinery can recover structure across a masked ZoA-like region without manufacturing filaments.

## Minimum tests

- generate or load a reproducible synthetic 3D density/velocity field;
- sample mock tracers with known selection effects;
- mask a Galactic-plane-like band;
- reconstruct from unmasked/training information;
- compare reconstruction to known truth;
- vary noise, tracer density, mask width, smoothing scale, and seed.

## Metrics

Report at minimum:
- field correlation;
- RMSE or normalized error;
- peak/overdensity recovery;
- false-positive rate;
- uncertainty calibration if ensemble outputs exist.

Clearly label all synthetic products `SYNTHETIC_TEST_ONLY`.

The goal is to validate the method, not to make the mock look like Vela.
