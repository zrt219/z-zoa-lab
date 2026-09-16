# /goal — Implement survey footprints, masks, and first-order selection functions

Paper-grade null tests cannot treat an empty location as an empty universe. Build explicit survey geometry and completeness metadata.

Start with the datasets required for Vela Experiment 001:
- HIZOA training geometry/completeness metadata;
- Vela-SMGPS holdout footprint and velocity range;
- Vela-HI geometry for later validation;
- 2MRS angular/redshift selection metadata;
- CF4 sampling metadata where applicable.

## Deliverables

Create reusable mask/selection objects that can answer:

```text
is_inside_footprint(l,b)
valid_velocity_range(cz)
relative_detection_weight(...)
quality_cut(...)
```

Distinguish exactly known selection rules from approximations. Every approximation must be documented and configurable.

Create unit tests at footprint boundaries and a selection-function report. Do not use holdout occupancy to tune selection parameters.
