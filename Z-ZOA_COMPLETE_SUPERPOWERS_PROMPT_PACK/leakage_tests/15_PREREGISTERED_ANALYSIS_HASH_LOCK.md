# Leakage test 15 — Preregistered analysis hash lock

Before reveal, freeze the confirmatory analysis specification separately from the reconstructed field.

The frozen analysis spec must include:
- primary hypothesis;
- primary metric(s);
- secondary metric(s);
- survey footprint/mask version;
- smoothing/grid scale(s) designated confirmatory;
- overdensity/probability thresholds if used;
- null-catalogue generation procedure;
- number of null realizations;
- random seed policy;
- exclusion rules;
- significance calculation;
- multiple-testing correction if applicable;
- what counts as exploratory after reveal.

Canonicalize and SHA-256 hash this file. Record the hash in the freeze manifest and XRPL anchor payload when anchoring is enabled.

After reveal, any analysis change creates a new explicitly `EXPLORATORY` analysis version. It must never overwrite the confirmatory result.

Save `leakage/15_analysis_lock_report.json` and `.md`.
