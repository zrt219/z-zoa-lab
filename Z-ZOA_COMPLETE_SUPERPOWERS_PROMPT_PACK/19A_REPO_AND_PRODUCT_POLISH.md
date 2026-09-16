# /goal — Final repository and product polish without changing the science

After scientific functionality and paper outputs pass, clean the project for external inspection.

## Repository

Ensure:
- README accurately describes implemented behavior vs planned behavior;
- setup instructions work from a clean clone;
- dataset download/registration instructions do not redistribute restricted third-party data incorrectly;
- `.gitignore` excludes secrets, raw large datasets, caches, local DBs, Testnet secrets, and generated junk;
- example configs are safe and clearly synthetic where applicable;
- licenses/third-party notices are present;
- no dead code paths or obsolete fake demo data remain;
- no holdout catalogue rows are accidentally committed.

## Calculation Room

Check:
- empty states;
- scientific warnings;
- calculator provenance;
- run history;
- freeze/read-only behavior;
- XRPL status wording;
- mobile/basic accessibility.

## 3D Lab

Check:
- layer legends;
- units/frames displayed;
- mock/downsampling labels;
- stage authorization;
- no holdout leakage;
- graceful WebGL failure message.

## Documentation

Add a concise architecture diagram and researcher workflow:

```text
download/register -> audit -> calculate -> reconstruct -> freeze -> leakage audit -> reveal -> score -> hybrid -> paper
```

## Constraint

Do not change scientific thresholds, parameters, metric definitions, or results during polish. Any scientific change requires a new run and appropriate robustness/revalidation.
