# Normalization Report: vela_smgps_sample

- Survey: MeerKAT Vela-SMGPS
- Release: Kraan-Korteweg et al. 2024, MNRAS 531, 3486
- Input rows: 4
- Output rows: 4
- Normalized output: `vela_smgps_sample_normalized.parquet`
- Output columns: source_row_id, canonical_object_id, ra_deg, dec_deg, gal_l_deg, gal_b_deg, sgl_deg, sgb_deg, cz_value_kms, cz_frame, redshift, distance_mpc, distance_err_mpc, distance_modulus, distance_modulus_err, hi_flux, w50_kms, survey, release, quality_flags
- RA range: [146.8400, 167.5000] deg
- Dec range: [-60.1000, -55.0900] deg
- Galactic l range: [278.6083, 290.6042] deg
- Galactic b range: [-2.5019, 0.5351] deg
- Velocity range (cz): [2848.0, 18450.0] km/s
- Coordinate system: Astropy ICRS -> Galactic (l,b) -> Supergalactic (SGL, SGB)
- Frame tags preserved: {'HELIOCENTRIC'}
