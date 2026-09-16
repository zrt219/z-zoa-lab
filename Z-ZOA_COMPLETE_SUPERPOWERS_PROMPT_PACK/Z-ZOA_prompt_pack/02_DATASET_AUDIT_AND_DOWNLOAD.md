# /goal — Audit the Z-ZOA datasets and download only what is missing

Inspect the current `datasets/`, project root, download kits, ZIPs, FITS files, catalogues, and manifests. Do not assume a file is missing just because it is not in the preferred folder.

## Required target inventory

Verify presence and integrity of:

### TRAIN candidates
- Cosmicflows-4 individual distances
- CF4 groups
- CF4 group velocities
- 2MRS main redshift catalogue
- HIZOA-S catalogue and notes/readme

### HOLDOUT candidates
- Vela-SMGPS full 843-object catalogue
- Vela-HI full 719-object catalogue
- GA-SMGPS 477-object catalogue for a later experiment

### COMPARISON_ONLY / reference
- official CF4 density grid
- official CF4 velocity grid
- official CF4 density uncertainty/error grid
- official CF4 velocity uncertainty/error grid
- CF4++ mean/RMS fields if available
- WALLABY Pilot DR2 source catalogue if available

## Rules

1. Never overwrite an original science file.
2. Never replace an unavailable dataset with synthetic/fake rows.
3. Verify file type, size, readability, expected row count where possible, and SHA-256.
4. Record authoritative source URL/DOI and citation.
5. If a duplicate exists, hash both and report whether they are byte-identical.
6. If a ZIP contains the authoritative file, preserve the ZIP and extract a copy into an immutable raw directory.
7. Do not download raw MeerKAT/WALLABY cubes for Paper 1 unless specifically required later.

## Output

Create:

```text
datasets/manifests/inventory.json
datasets/manifests/inventory.csv
datasets/manifests/missing.json
datasets/manifests/checksums.sha256
```

The inventory must include dataset role, release/version, source, local paths, checksum, byte size, row count, and status.

Download only confirmed missing catalogue/reference products. At the end print a concise table of PRESENT / DOWNLOADED / FAILED / MANUAL-ACCESS-REQUIRED.

Stop after the verified inventory is complete. Do not start analysis.
