# /goal — Build the White Calculation Room interface

Build the primary Z-ZOA research workspace as a minimalist white scientific calculation environment. This UI is an interface to the scientific Python core; it is never the source of truth.

Use `visual_refs/02_white_calculation_room.png` only as design inspiration. Do not copy fake values from the sketch into production data.

## Visual direction

The experience should feel like:

```text
white laboratory
+ numerical research notebook
+ calm scientific workstation
```

Avoid:
- cosmic backgrounds;
- 3D scenes on this route;
- marketing hero sections;
- glowing AI aesthetics;
- dense SaaS card grids;
- fake demo galaxies;
- decorative statistics that are not backed by live run artifacts.

## Main workspace

Create a responsive Calculation Room with these logical sections:

```text
Experiment
Data
Cosmology
Calculator
Runs
Audit
```

The exact navigation pattern may follow the existing frontend architecture.

### Experiment
Show:
- experiment ID/name;
- stage/state;
- target region;
- selected config;
- dataset roles;
- seed;
- git commit when available;
- whether holdout access is locked.

### Data
Show registered datasets only. For every dataset expose:
- registry ID;
- role;
- release/version;
- row count;
- checksum status;
- units/frames summary;
- provenance status;
- parent lineage for derived products;
- warning state.

Do not display HOLDOUT scientific contents in TRAIN mode.

### Cosmology
Expose the explicit run cosmology, not global hidden defaults:
- H0;
- Om0;
- Ode0/flatness as applicable;
- model/reference label;
- velocity frame.

If changing a setting changes the scientific config, require creation of a new run/config revision rather than silently editing an already-frozen run.

### Calculator
Integrate the tools produced by `01B_SCIENTIFIC_CALCULATOR_SUITE.md`.

### Runs
Show immutable run history with states such as:

```text
DRAFT
RUNNING
COMPLETE
FROZEN
VALIDATED
FAILED
```

For frozen runs show hashes and integrity status.

### Audit
Show provenance, warnings, access-denial events, freeze state, leakage certificate state, and XRPL receipt status when configured.

## Backend rule

No important number may be fabricated by the frontend. The UI fetches typed responses from the backend or reads static frozen run artifacts through approved endpoints.

## UX for errors

Scientific warnings must be visible and specific. Examples:
- missing unit;
- mixed velocity frames;
- checksum mismatch;
- unknown parent lineage;
- holdout access denied;
- frozen run mutation attempt.

Never convert those into generic "something went wrong" messages only.

## Tests

Add frontend/backend tests proving:
- no fake fallback data appear when the backend has no datasets;
- HOLDOUT rows are not exposed in TRAIN mode;
- a frozen run cannot be edited through the UI;
- unit/frame warnings render correctly;
- a known calculator call displays the backend result and provenance;
- keyboard/mobile layouts remain usable.

## Completion gate

The Calculation Room must work with an empty registry, a synthetic test registry, and at least one properly registered real public dataset without changing UI code.
