# /goal — Build a reproducibility bundle for Z-ZOA Paper 1

Create a command that packages everything another researcher needs to reproduce the central numerical claims, subject to dataset licensing.

Include:
- exact environment/dependency lock;
- source commit;
- configs;
- run/freeze manifests;
- dataset registry and checksums;
- scripts/CLI commands;
- exclusion lists and leakage report;
- validation metrics and null distributions;
- generated tables/figures and their source data;
- README with exact run order;
- data-availability notes for files that cannot be redistributed.

Do not redistribute third-party files when licensing forbids it; instead provide verified retrieval instructions and expected hashes/metadata.

Test the bundle from a clean environment if possible.
