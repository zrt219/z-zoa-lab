# Normalization Report: cf4_sample

- Survey: Cosmicflows-4
- Release: Tully et al. 2023, ApJ 944, 94 (Table 2)
- Input rows: 8
- Output rows: 8
- Normalized output: `cf4_sample_normalized.parquet`
- Output columns: source_row_id, canonical_object_id, ra_deg, dec_deg, gal_l_deg, gal_b_deg, sgl_deg, sgb_deg, cz_value_kms, cz_frame, redshift, distance_mpc, distance_err_mpc, distance_modulus, distance_modulus_err, hi_flux, w50_kms, survey, release, quality_flags
- RA range: [1.0315, 353.6146] deg
- Dec range: [-43.0191, 69.3783] deg
- Galactic l range: [57.1934, 359.3894] deg
- Galactic b range: [-71.3659, 87.8936] deg
- Velocity range (cz): [547.0, 6495.0] km/s
- Coordinate system: Astropy ICRS -> Galactic (l,b) -> Supergalactic (SGL, SGB)
- Frame tags preserved: {'HELIOCENTRIC'}
