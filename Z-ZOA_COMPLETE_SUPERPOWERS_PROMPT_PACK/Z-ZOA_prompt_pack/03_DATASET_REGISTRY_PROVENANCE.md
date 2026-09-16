# /goal — Build the immutable Z-ZOA dataset registry and provenance chain

Create a dataset registry that is authoritative for every scientific run.

## Registry schema

At minimum track:

```text
dataset_id
survey
catalogue_name
release
role
source_url
doi
citation
license
local_raw_path
sha256
bytes
row_count
coordinate_columns
velocity_columns
velocity_frame
distance_columns
uncertainty_columns
quality_columns
ingested_at
parent_dataset_ids
transformation_id
status
```

Roles must be explicit: `TRAIN`, `TRAIN_CLEAN`, `HOLDOUT`, `VALIDATION`, `COMPARISON_ONLY`, `REFERENCE`, `SYNTHETIC_TEST_ONLY`.

## Provenance rules

- Raw files are immutable.
- A normalized catalogue is a new dataset with a parent link to the raw catalogue.
- A decontaminated training catalogue is a new dataset with parent links plus an exclusion-list hash.
- A reconstruction grid records every dataset ID and config hash that contributed to it.
- Derived products that assimilate MeerKAT must be marked as contaminated for a MeerKAT holdout experiment and may only be COMPARISON_ONLY.

Create validation functions that fail runs when required provenance is absent.

Add automated tests for checksum mismatch, missing citation/source, invalid role transitions, and a derived product with incomplete parents.
