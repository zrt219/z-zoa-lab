# Leakage test 12 — Final report and certification

Combine all leakage-test outputs into one `leakage/FINAL_LEAKAGE_REPORT.md` plus machine-readable JSON.

## Report sections

- experiment/run candidate ID;
- training candidate datasets;
- holdout dataset/version/hash;
- known overlap findings;
- exclusions applied;
- resulting TRAIN_CLEAN row counts/hashes;
- derived-product contamination findings;
- software access-control tests;
- tuning audit;
- cache/environment audit;
- negative-control result;
- unresolved ambiguities;
- final status: PASS / FAIL / PASS_WITH_DECLARED_LIMITATIONS.

A PASS should create `leakage/leakage_certificate.json` containing hashes of the TRAIN_CLEAN snapshot and all audit outputs. The later freeze command must require this certificate.

Do not claim that the experiment is historically blind. Describe it accurately as a leakage-controlled out-of-sample/holdout validation unless a genuinely prospective dataset is used.
