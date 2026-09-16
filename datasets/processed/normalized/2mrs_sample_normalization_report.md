# Normalization Report: 2mrs_sample

- Survey: 2MRS
- Release: Huchra et al. 2012 / Macri et al. 2019
- Input rows: 50
- Output rows: 50
- Normalized output: `2mrs_sample_normalized.parquet`
- Output columns: source_row_id, canonical_object_id, ra_deg, dec_deg, gal_l_deg, gal_b_deg, sgl_deg, sgb_deg, cz_value_kms, cz_frame, redshift, distance_mpc, distance_err_mpc, distance_modulus, distance_modulus_err, hi_flux, w50_kms, survey, release, quality_flags
- RA range: [10.0920, 339.2671] deg
- Dec range: [-63.8575, 69.8124] deg
- Galactic l range: [93.7221, 332.2240] deg
- Galactic b range: [-87.9645, 88.3573] deg
- Velocity range (cz): [-300.0, 2281.0] km/s
- Coordinate system: Astropy ICRS -> Galactic (l,b) -> Supergalactic (SGL, SGB)
- Frame tags preserved: {'HELIOCENTRIC'}
