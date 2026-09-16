# /goal — Validate our numerical conventions against official CF4 reference products

Before attempting a novel reconstruction, prove that the Calculation Room interprets CF4 data correctly.

Use the official CF4 catalogues and public density/velocity/error grids as REFERENCE or COMPARISON_ONLY.

## Validate

- catalogue schema and expected row counts;
- coordinate convention and supergalactic orientation;
- FITS axis ordering, grid origin, extent, and voxel scale;
- velocity component ordering/sign convention;
- documented scaling factors from the official release;
- density sign/normalization;
- uncertainty grid interpretation;
- interpolation/query behavior at known points.

Build small numerical regression tests and a human-readable `cf4_reference_validation.md` report.

This phase is not a claim that we reproduced the CF4 inference. It is a convention/IO validation step.
