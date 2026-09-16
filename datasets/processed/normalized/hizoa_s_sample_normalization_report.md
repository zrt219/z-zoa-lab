# Normalization Report: hizoa_s_sample

- Survey: HIZOA-S (Parkes Southern ZoA)
- Release: Staveley-Smith et al. 2016, AJ 151, 52 (Table 2)
- Input rows: 4
- Output rows: 4
- Normalized output: `hizoa_s_sample_normalized.parquet`
- Output columns: source_row_id, canonical_object_id, ra_deg, dec_deg, gal_l_deg, gal_b_deg, sgl_deg, sgb_deg, cz_value_kms, cz_frame, redshift, distance_mpc, distance_err_mpc, distance_modulus, distance_modulus_err, hi_flux, w50_kms, survey, release, quality_flags
- RA range: [146.8500, 242.1000] deg
- Dec range: [-62.1500, -51.3000] deg
- Galactic l range: [278.6191, 331.2007] deg
- Galactic b range: [-2.5072, 0.4263] deg
- Velocity range (cz): [1890.0, 5420.0] km/s
- Coordinate system: Astropy ICRS -> Galactic (l,b) -> Supergalactic (SGL, SGB)
- Frame tags preserved: {'HELIOCENTRIC'}
