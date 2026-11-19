# Normalization Report: wallaby_dr2

- Survey: ASKAP WALLABY
- Release: Murugeshan et al. 2024, PASA, 41, e088
- Input rows: 3454
- Output rows: 3454
- Normalized output: `wallaby_dr2_normalized.parquet`
- Output columns: source_row_id, canonical_object_id, ra_deg, dec_deg, gal_l_deg, gal_b_deg, sgl_deg, sgb_deg, cz_value_kms, cz_frame, redshift, distance_mpc, distance_err_mpc, distance_modulus, distance_modulus_err, hi_flux, w50_kms, survey, release, quality_flags
- RA range: [145.4119, 260.0309] deg
- Dec range: [-62.7267, 8.5731] deg
- Galactic l range: [262.2087, 332.9156] deg
- Galactic b range: [-13.7589, 71.3481] deg
- Velocity range (cz): [526.5, 26347.1] km/s
- Coordinate system: Astropy ICRS -> Galactic (l,b) -> Supergalactic (SGL, SGB)
- Frame tags preserved: {'BARYCENTRIC'}
