# /goal — Build the Z-ZOA scientific calculator suite

Build a set of small, auditable calculators inside the Calculation Room. These are research utilities for checking individual inputs and equations before they enter larger reconstruction workflows.

The calculator suite must call pure scientific functions from the Python core. Do not implement astronomy math independently in JavaScript when the same calculation exists in Python.

## Calculator 1 — Coordinate converter

Inputs:
- RA/Dec or Galactic l/b;
- optional distance;
- declared coordinate frame/equinox where required.

Outputs:
- ICRS RA/Dec;
- Galactic l/b;
- Supergalactic coordinates;
- Cartesian XYZ / SGX SGY SGZ when distance is present;
- units;
- library/method provenance.

Use Astropy transformations where supported. Test against known Astropy results.

## Calculator 2 — Cosmological distance utility

Inputs:
- redshift z;
- explicit selected cosmology.

Outputs as scientifically appropriate:
- comoving distance;
- luminosity distance;
- angular-diameter distance;
- H(z);
- optional low-z approximation comparison.

The low-z approximation must be clearly labeled as an approximation.

## Calculator 3 — Peculiar-velocity workbench

Provide an initial documented low-z exploratory calculation such as:

```text
v_pec ~= cz - H0*d
```

but structure the API so the final paper estimator can be substituted later.

Inputs must declare:
- redshift/velocity and frame;
- distance and uncertainty;
- H0/cosmology;
- applicable measurement uncertainties.

Outputs:
- calculated value;
- propagated uncertainty according to the implemented model;
- assumptions;
- frame;
- warning if the approximation is outside the configured validity regime.

## Calculator 4 — CF4 grid probe

Given a location in the documented coordinate convention, query registered CF4/CF4++ **comparison products** and return, where available:
- density/delta;
- density uncertainty/RMS;
- vx, vy, vz;
- velocity magnitude;
- velocity uncertainty/RMS;
- grid index/interpolation method;
- source dataset ID/hash.

Respect official scaling/unit conventions. Do not guess undocumented factors.

This calculator must not make a comparison grid a TRAIN input merely because a user queried it.

## Calculator 5 — Angular/3D separation

Given two objects, calculate:
- angular separation;
- radial-distance difference when available;
- 3D Cartesian separation when meaningful;
- velocity/redshift difference in a common documented frame when requested.

This calculator will support leakage/crossmatch auditing.

## Calculator 6 — Uncertainty propagation inspector

Given a supported calculation, show the individual uncertainty terms and how the final uncertainty was obtained. Avoid black-box single-number output.

## API shape

Expose a typed backend API, for example:

```text
POST /api/calculator/coordinates
POST /api/calculator/cosmology
POST /api/calculator/peculiar-velocity
POST /api/calculator/grid-probe
POST /api/calculator/separation
```

Adapt route naming to existing conventions.

Each response includes:

```text
value(s)
unit(s)
method
assumptions
warnings
source/provenance
```

## Tests

Use trusted library/reference values. Include:
- round-trip coordinate tests;
- unit conversion tests;
- frame mismatch rejection;
- invalid redshift/distance handling;
- numerical edge cases;
- CF4 grid boundary behavior;
- uncertainty regression tests.

## UI

Keep it restrained: input column, result column, equation/method note, provenance note. No charts are required.

## Completion gate

Every calculator must be callable from Python, API, and UI, and must give the same numerical result for the same canonical input.
