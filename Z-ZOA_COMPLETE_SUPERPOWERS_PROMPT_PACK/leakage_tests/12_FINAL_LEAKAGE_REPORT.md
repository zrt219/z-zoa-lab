# Leakage test 12 — Final leakage report and certificate

Run this **last**, after the pre-freeze audit, frozen candidate, post-freeze integrity tests, and required XRPL verification.

Combine every leakage-control output into:

```text
leakage/FINAL_LEAKAGE_REPORT.md
leakage/FINAL_LEAKAGE_REPORT.json
leakage/leakage_certificate.json
```

## Report sections

- experiment/run ID;
- exact frozen run/config hash;
- training candidate datasets;
- final TRAIN_CLEAN dataset IDs/row counts/hashes;
- holdout dataset/version/hash;
- exact-ID/alias findings;
- positional/redshift match findings;
- HIZOA/Vela overlap findings;
- exclusions applied;
- derived/transitive-lineage contamination findings;
- software/API/3D access-control tests;
- tuning/preregistration audit;
- cache/side-channel audit;
- OS sandbox result;
- freeze canary result;
- negative-control result;
- controlled reveal-gate result;
- clean-room reproduction result;
- XRPL anchor verification result if required;
- unresolved ambiguities/limitations;
- final status.

Allowed final statuses:

```text
PASS
PASS_WITH_DECLARED_LIMITATIONS
FAIL
```

`PASS_WITH_DECLARED_LIMITATIONS` must not be silently treated as PASS by later code; the validation command must require an explicit policy allowing the declared limitations.

## Certificate

`leakage_certificate.json` must contain hashes of:
- TRAIN_CLEAN manifest;
- exclusion list;
- frozen prediction manifest;
- frozen analysis spec;
- every mandatory leakage report;
- 3D Lab safety report if enabled;
- XRPL receipt if required.

The validation/reveal command must verify this certificate before returning HOLDOUT scientific content.

Do not claim historical blindness. Unless a truly prospective untouched dataset is used, describe the experiment as leakage-controlled out-of-sample/holdout validation.
