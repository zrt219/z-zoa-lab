# Normalization Report: hizoa_s_full

- Survey: HIZOA-S (Parkes Southern ZoA)
- Release: Staveley-Smith et al. 2016, AJ 151, 52
- Input rows: 883
- Output rows: 883
- Normalized output: `hizoa_s_full_normalized.parquet`
- Output columns: source_row_id, canonical_object_id, ra_deg, dec_deg, gal_l_deg, gal_b_deg, sgl_deg, sgb_deg, cz_value_kms, cz_frame, redshift, distance_mpc, distance_err_mpc, distance_modulus, distance_modulus_err, hi_flux, w50_kms, survey, release, quality_flags
- RA range: [97.9554, 287.5913] deg
- Dec range: [-68.0442, 4.0467] deg
- Galactic l range: [1.0366, 359.4126] deg
- Galactic b range: [-5.7711, 5.7382] deg
- Velocity range (cz): [224.0, 11883.0] km/s
- Coordinate system: Astropy ICRS -> Galactic (l,b) -> Supergalactic (SGL, SGB)
- Frame tags preserved: {'HELIOCENTRIC'}
