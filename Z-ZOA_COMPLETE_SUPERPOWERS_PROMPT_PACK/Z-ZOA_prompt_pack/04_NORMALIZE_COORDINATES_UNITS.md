# /goal — Normalize Z-ZOA coordinates, frames, units, and uncertainties

Build a deterministic normalization pipeline for the registered catalogues.

## Requirements

- Preserve original columns unchanged in the immutable raw input.
- Create normalized Parquet outputs with stable source IDs.
- Use Astropy for coordinate transformations where possible.
- Carry explicit units.
- Never silently mix heliocentric, Local Group, CMB, or other velocity frames.
- Record the transformation/version used to convert a value.
- Keep measurement uncertainty and quality flags.

## Standard output columns where available

```text
source_row_id
canonical_object_id
ra_deg
dec_deg
gal_l_deg
gal_b_deg
sgl_deg
sgb_deg
cz_value_kms
cz_frame
redshift
distance_mpc
distance_err_mpc
distance_modulus
distance_modulus_err
hi_flux
w50_kms
survey
release
quality_flags
```

Do not infer unavailable values unless the derivation is documented and separately flagged.

## Validation

Test known coordinate transformations against trusted Astropy results. Check round-trip angular errors. Check unit conversions. Detect impossible ranges, NaN explosions, and duplicate source-row IDs.

Produce a normalization report for every dataset and stop before any reconstruction.
