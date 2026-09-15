# Z-ZOA Complete Prompt Library

This file concatenates the complete Z-ZOA prompt pack for easy GitHub browsing. Use `RUN_ORDER.md` and `PROMPT_MAP.md` to navigate the individual phases.


---

<!-- SOURCE: 00_MASTER_EXECUTION_PROTOCOL.md -->

# /goal â€” MASTER EXECUTION PROTOCOL FOR Z-ZOA LAB

You are implementing the Z-ZOA Lab as research software that may support a peer-reviewed astronomy paper. Treat every phase as production scientific software, not a visual demo.

## Project objective

Build one coherent project with two deliberately separated environments:

1. **White Calculation Room** â€” the scientific source of truth. It ingests registered real datasets, performs calculations/reconstruction/statistics, protects holdouts, creates frozen run artifacts, and generates paper outputs.
2. **3D Lab Companion** â€” a read-only scientific explorer. It visualizes only Calculation Room artifacts that are explicitly authorized for the current research stage. It cannot alter scientific inputs, tune parameters, or bypass holdout controls.

The paper-driving experiment is:

```text
TRAIN_CLEAN
  -> reconstruct WITHOUT selected MeerKAT Vela holdout
  -> quantify uncertainty
  -> freeze prediction + config + method + hashes
  -> pass leakage suite
  -> anchor frozen run to XRPL Testnet when configured
  -> reveal holdout
  -> score against preregistered metrics and survey-matched nulls
  -> add MeerKAT
  -> hybrid reconstruction
  -> measure Delta density / Delta velocity / Delta uncertainty
  -> robustness checks
  -> paper figures/tables/reproducibility bundle/manuscript
```

## Non-negotiable engineering rules

- Inspect the current repository before every phase. Reuse working code rather than duplicating it.
- Do not invent astronomy data, catalog rows, citations, constants, survey properties, or successful results.
- Synthetic data are allowed only in explicitly labeled mock/test workflows.
- Raw downloaded datasets are immutable.
- Scientific quantities retain units and reference-frame metadata.
- Every derived artifact records parents/provenance and hashes.
- HOLDOUT data cannot be accessed in TRAIN mode.
- The 3D Lab cannot read HOLDOUT data before authorized reveal.
- No scientific result may exist only in frontend state or a screenshot.
- Every important computation emits machine-readable artifacts.
- Use tests first for scientific kernels and access-control boundaries.
- Run the smallest relevant test suite after each change and the full suite at phase gates.
- Never claim a phase is complete without showing verification output.
- Never silently weaken a requirement because a dependency or download is difficult.

## Superpowers workflow

For each prompt:

1. Inspect relevant files, tests, configs, and recent changes.
2. State the exact design/change you intend to make.
3. For a new subsystem or major interface, stop for approval if it has not already been approved.
4. Implement test-first.
5. Run verification.
6. Report exact files changed and exact outputs generated.
7. Commit with a focused commit message if the repo is under git and the user has asked the agent to commit.
8. Do not continue into the next numbered prompt automatically unless explicitly told to run the full pack.

## Scientific stage states

The project must understand these states:

```text
SETUP
AUDIT
TRAIN
TRAIN_CLEAN
FROZEN
VALIDATE
HYBRID
PAPER
```

Access policy must be explicit. A frontend route or direct filesystem path must not bypass it.

## Product structure target

Adapt to the actual repository, but preserve these responsibility boundaries:

```text
research/              # pure scientific Python core
  catalogs/
  coordinates/
  cosmology/
  velocities/
  reconstruction/
  statistics/
  validation/
  holdouts/
  provenance/
  ledger/

experiments/           # experiment definitions and runners
configs/               # versioned configs
runs/                  # immutable/frozen run outputs
scripts/               # one-off reproducible utilities
backend/               # thin API around research core
frontend/              # Calculation Room + 3D Lab UI

tests/
  unit/
  integration/
  scientific/
  security/

docs/
```

## Definition of done for the entire project

Do not call Z-ZOA "done" until `20_FINAL_END_TO_END_ACCEPTANCE.md` passes. The end state must demonstrate a complete synthetic rehearsal of the real paper workflow, and then be ready to run the real Vela experiment without redesigning the architecture.

---

<!-- SOURCE: 01A_WHITE_CALCULATION_ROOM_UI.md -->

# /goal â€” Build the White Calculation Room interface

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


---

<!-- SOURCE: 01B_SCIENTIFIC_CALCULATOR_SUITE.md -->

# /goal â€” Build the Z-ZOA scientific calculator suite

Build a set of small, auditable calculators inside the Calculation Room. These are research utilities for checking individual inputs and equations before they enter larger reconstruction workflows.

The calculator suite must call pure scientific functions from the Python core. Do not implement astronomy math independently in JavaScript when the same calculation exists in Python.

## Calculator 1 â€” Coordinate converter

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

## Calculator 2 â€” Cosmological distance utility

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

## Calculator 3 â€” Peculiar-velocity workbench

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

## Calculator 4 â€” CF4 grid probe

Given a location in the documented coordinate convention, query registered CF4/CF4++ **comparison products** and return, where available:
- density/delta;
- density uncertainty/RMS;
- vx, vy, vz;
- velocity uncertainty;
- grid interpolation method;
- source product version/hash.

Implement the official grid convention/scaling explicitly. Test a set of known grid cells to catch axis/ordering/scaling mistakes.

## Calculator 5 â€” Uncertainty propagation sandbox

Given explicit input values + uncertainties, show the propagation step used by a supported calculation.

Show:
- equation/method;
- partial derivatives/Jacobian where appropriate;
- input contributions;
- final Ïƒ;
- assumptions (independent vs. correlated errors).

## Calculator 6 â€” 3-D distance / neighbor inspector

For two registered objects or two explicit points, calculate:
- angular separation;
- 3-D separation when distances are available;
- delta cz;
- crossmatch status for audit workflows.

Do not allow this tool to browse HOLDOUT in TRAIN mode.

## Shared rules

All calculators must:
- require units where physical units are relevant;
- require reference frames where relevant;
- reject ambiguous numeric inputs;
- return machine-readable JSON and human-readable formatted output;
- record the function/method version;
- show warnings;
- be tested against trusted reference values.

## PPI sketch

The exact signatures may adapt to the existing codebase, but preserve the separation between:

```text
research.coordinates.transform(.)
research.cosmology.distances(..)
research.velocities.estimate(..)
research.uncertainty.propagate(..)
research.reference_grids.dool(..)
```

The frontend calls backend endpoints that wrap these functions.

Once built, add a **"Copy reproducible calculation record"** action that exports inputs, assumptions, results, units, method version, and warnings â€” not a screenshot.

---

<!-- SOURCE: 01C_EXPERIMENT_RUNNER_AND_MANIFESTS.md -->

# /goal â€” Build the Z-ZOA experiment runner and run manifests

Build the system that turns a registered experiment config into a recorded, replayable run.


## Experiment config

Define a strict schema containing at least:

```text
experiment_id
stage
target_region
cosmology
dataset_ids
dataset_roles
velocity_frames
random_seed
method_name
method_parameters
selection_function_ids
mask_ids
output_policy
require_leakage_certificate
require_freeze_anchor
```

Configs are versioned. Never edit the resolved config of a completed/frozen run.

## Run manifest

At run start, record:
- run ID;
- UTC created_at;
- git commit + dirty-worktree status;
- resolved config hash;
- dataset IDs, roles, file hashes, parent lineage;
- Python + package versions;
- OS/platform;
- random seed;
- cosmology;
- frames;
- method + version;
- warnings;
- outputs and output hashes;
- stage transitions;
- lineage/parent run IDs;
- final status.

## Output structure

Use a stable structure similar to:

```text
runs/<RUN_ID>/
  manifest.json
  config.resolved.yaml
  checksums.sha256
  logs/
  data/
  arrays/
  metrics/
  tables/
  figures/
  ledger/
```

Only create folders a run actually needs.

## Immutability

- DRAFT/COMPLETE runs may be superseded by a new run.
- FROZEN runs must never be modified in place.
- Any change after freeze must create a new run ID with a parent link.
- Verification must detect changed bytes.

## Replay

Implement a replay/verify command that can:
- load a past resolved config;
- verify checksums;
- rerun deterministic stages;
- compare output hashes or numerical tolerances;
- produce a clear reproducibility report.

## State machine

Implement explicit allowed transitions. Example:

```text
SETUP 8¦"TD•BâE$”ââe$õ¤TââdÄ”DDRâ…”%$”BâU ¦  ¥&V¦V7B–ÆÆVvÂG&ç6—F–öç27V6‚2E$”ââ…”%$”Fv†VâF†RW‡W&–ÖVçB&WV—&W2†öÆF÷WBfÆ–FF–öâf—'7Bà ¢22FW7G0 ¤–æ6ÇVFS ¢ÒFWFW&Ö–æ—7F–2'Vâ”Bö–çWB&V†f–÷"v†W&R7V6–f–VC°¢ÒÖæ–fW7B66†VÖfÆ–FF–öã°¢ÒF—'G’v÷&¶–ærG&VR&V6÷&FVBÂæ÷B†–FFVã°¢Òg&÷¦Vâ×WFF–öâ&V¦V7F–öã°¢Ò&WÆ’7V66W73°¢Ò&WÆ’†6‚Ö—6ÖF6ƒ°¢Ò–ÆÆVvÂ7FFRG&ç6—F–öâ&V¦V7F–öã°¢Ò„ôÄDõUB&öÆR&V¦V7FVB–âE$”â6öæf–w2à ¢226ö×ÆWF–öâvFP ¤7&VFRæB&WÆ’öæR7–çF†WF–26Æ7VÆF–öâ'VâVæBFòVæBâF†R6V6öæB'Vâ×W7B&W&öGV6RF†R6æöæ–6ÂFWFW&Ö–æ—7F–2÷WGWG2æB&öGV6RâW‡Æ–6—B52&W÷'Bà ¢ÒÒĞ £ÂÒÒ4õU$4S¢EõDU5Eô„$äU55ôäEô4’æÖBÒÓà ¢2övöÂ(	B'V–ÆBF†R¢Õ¤ô66–VçF–f–2FW7B†&æW72æB4’vFW0 ¤7&VFRFW7B7G'V7GW&RF†BÖ¶W266–VçF–f–2&Vw&W76–öç2Â66W72Ö6öçG&öÂf–ÇW&W2ÂæB&W&öGV6–&–Æ—G’f–ÇW&W2f—6–&ÆR&Vf÷&RF†W’6öçFÖ–æFRW"'Vâà ¢22FW7Bw&÷W0 ¤÷&væ—¦RFW7G2'’W'÷6R&F†W"F†âöæRv–çBföÆFW#  ¦FW‡@§Væ—BW&RgVæ7F–öç2æB66†VÖ0¢66–VçF–f–2G'W7FVB×fÇVRæBçVÖW&–6Â×&Vw&W76–öâFW7G0¢–çFVw&F–öâFF6WG2Óâ'Vâ'F–f7G2Óâ¢6V7W&—G’„ôÄDõUB&÷VæF&–W2æBg&÷¦Vâ×'Vâ–Ö×WF&–Æ—G¢&W&öGV6–&–Æ—G’&WÆ’ö†6‚ö6æöæ–6Æ—¦F–öâFW7G0¢g&öçFVæB6Æ7VÆF–öâ&ööÒò4BÆ"&V†f–÷ ¢æWGv÷&²÷F–öæÂW‡FW&æÂõFW7FæWB–çFVw&F–öâFW7G0¦  ¤föÆÆ÷rF†RW†—7F–ær&ö¦V7B6öçfVçF–öç2v†W&R÷76–&ÆRà ¢22&WV—&VBFW7BÖ&¶W'0 ¥6W&FRFW7G2F†B&WV—&S ¢ÒæWGv÷&³°¢ÒÆ&vRFF6WG3°¢ÒuS°¢Ò…%ÂFW7FæWC°¢Ò÷F–öæÂ4Bö'&÷w6W"7F6²à ¥F†RFVfVÇBf7B7V—FR×W7Bæ÷BFWVæBöâæWGv÷&²f–Æ&–Æ—G’à ¢224’Ö–æ–×VĞ ¤6öæf–wW&R4’Fò'VâöâVÆÂ&WVW7G2ö6öÖÖ—G22&÷&–FS ¢ÒÆ–çBöf÷&ÖB6†V6·2Ç&VG’F÷FVB'’F†R&Wó°¢Ò7FF–2÷G—R6†V6·2–bF†R&ö¦V7BW6W2F†VÓ°¢Òf7BVæ—B÷66–VçF–f–2÷6V7W&—G’FW7G3°¢Òg&öçFVæBFW7G3°¢Ò6ÖÆÂFWFW&Ö–æ—7F–27–çF†WF–2VæB×FòÖVæB'Vã°¢Ò'F–f7BWÆöBöbFW7B÷&W&ò&W÷'G2v†VâW6VgVÂà ¤æWfW"6öÖÖ—B6V7&WG2÷"&VÂFW7FæWB&—fFR¶W—2–çFò4’à ¢22vöÆFVâ×fÇVRöÆ–7 ¤f÷"66–VçF–f–2&VfW&Væ6RfÇVW3 ¢Ò7FFRv†W&RF†RW‡V7FVBfÇVR6öÖW2g&öÓ°¢Ò7F÷&RF†RW‡V7FVBVæ—G3°¢ÒW6R66–VçF–f–6ÆÇ’§W7F–f–VBFöÆW&æ6W3°¢ÒæWfW"v–FVâFöÆW&æ6RöæÇ’FòÖ¶Rf–Æ–ærFW7B72v—F†÷WBW‡ÆæF–öâà ¢226ö×ÆWF–öâvFP ¤FVÆ–&W&FVÇ’–çG&öGV6RFV×÷&'’Æö6ÂFW7Bf–ÇW&R–âF‡&÷vv’'&æ6‚ö6†ævRFòfW&–g’F†RvFR6F6†W2—BÂF†Vâ&W7F÷&R6ÆVâ6öFRæB6†÷rF†RVçF—&RFVfVÇB7V—FR76–ærà  ¢ÒÒĞ £ÂÒÒ4õU$4S¢õ$ô¤T5Eô$ôõE5E$ôtôÂæÖBÒÓà ¢2övöÂ(	B'V–ÆBF†R¢Õ¤ô6Æ7VÆF–öâ&ööÒf÷VæFF–öà ¤7&VFR÷"6öçF–çVR7FæFÆöæR66–VçF–f–2&ö¦V7B6ÆÆVB¢¥¢Õ¤ô6Æ7VÆF–öâ&ööÒ¢¢âF†—2&ö¦V7B—26W&FRg&öÒF†RW†—7F–ær4BW‡Æ÷&W"â—B—2v†—FR×76R6Æ7VÆF–öâ÷&W6V&6‚Vçf—&öæÖVçBv†÷6R¦ö"—2Fò&öGV6R&W&öGV6–&ÆRçVÖW&–6Â&W7VÇG2F†B6âWfVçGVÆÇ’7W÷'BVW"×&Wf–WvVB7G&öæö×’W"à ¢22f—'7B&–æ6—ÆP ¥F†R66–VçF–f–2—F†öâ6÷&R—2F†R&öGV7BâF†RT’—2öæÇ’F†–â–çFW&f6Rà ¤Fòæ÷BFBF‡&VRæ§2ÂvV$tÂÂvÆ‡’ö–çB6Æ÷VG2Â6÷6Ö–2Ö2Âæ–ÖFVB'F–6ÆW2ÂFV6÷&F—fRF6†&ö&G2Â÷"f¶RFFâ¶VWF†R–çFW&f6Rv†—FRÂ7'6RÂÖF†VÖF–6ÂÂæBV–WBà ¢22&Vf÷&R–×ÆVÖVçFF–öà ¤–ç7V7BF†RVçF—&R&W÷6—F÷'’æB&W÷'C £â7W'&VçBf–ÆRG&VS°£"âW†—7F–ær66–VçF–f–2öFFÖöGVÆW2vR6â&WW6S°£2â&÷÷6VB†6RÓ&6†—FV7GW&S°£BâW†7Bf–ÆW2–÷RÆâFò7&VFR÷"ÖöF–g“°£RâFWVæFVæ7’6†ö–6W;°£bâFW7F–ær7G&FVw’à ¥v—Bf÷"&÷fÂ–bF†—2&W÷6—F÷'’FöW2æ÷BÇ&VG’6öçF–ââ&÷fVB&6†—FV7GW&R÷7V2à ¢22&WV—&VB&6†—FV7GW&P ¤¶VWF†R66–Væ6R–æFWVæFVçFÇ’6ÆÆ&ÆRg&öÒ—F†öâô4Ä“  ¦FW‡@§&W6V&6‚ğ¢6ö÷&F–æFW2ğ¢6÷6ÖöÆöw’ğ¢fVÆö6—F–W2ğ¢6FÆöw2ğ¢&÷fVææ6Rğ¢†öÆF÷WG2ğ¢fÆ–FF–öâğ¢&V6öç7G'V7F–öâğ¢7FF—7F–72ğ¦W‡W&–ÖVçG2ğ¦6öæf–w2ğ¦FF6WG2ğ¢&rğ¢&ö6W76VBğ¢Öæ–fW7G2ğ§'Vç2ğ§FW7G2ğ¦&6¶VæBğ¦g&öçFVæBğ¦Fö72ğ¦  ¥W6RW7F&Æ—6†VB7G&öæö×’÷66–VçF–f–2Æ–'&&–W2v†W&R&÷&–FS¢7G&÷’ÂçVÕ’Â66•’ÂæF2õöÆ'2Â”'&÷rõ'VWBÂ–FçF–2Â—FW7Bâ¶VWVæ—G2W‡Æ–6—Bv—F‚7G&÷’çVæ—G6à ¢22†6RÓ7V66W727&—FW&– ¥F†R7—7FVÒ×W7B&R&ÆRFó ¢Ò&Vv—7FW"&VÂ6FÆöwVRv—F‚6÷W&6RU$ÂôDô’ÂfW'6–öâÂ6†V6·7VÒÂ&÷r6÷VçBÂæB&öÆS°¢Ò&W6W'fR&rf–ÆW22–Ö×WF&ÆS°¢ÒG&ç6f÷&Ò$ôFV2ÂÓâvÆ7F–2ÂÓâ7WW&vÆ7F–26ö÷&F–æFW2&W&öGV6–&Ç“°¢Ò&V6÷&B†VÆ–ö6VçG&–2ôÆö6ÂÔw&÷Wô4Ô"fVÆö6—G’Ög&ÖRÖWFFFv—F†÷WB6–ÆVçFÇ’Ö—†–ærg&ÖW3°¢ÒW&f÷&ÒFö7VÖVçFVBÆ÷r×&VG6†–gB6÷6ÖöÆöw’÷V7VÆ–"×fVÆö6—G’WF–Æ—G’6Æ7VÆF–öç2v—F‚&÷vFVBVæ—G2æBVæ6W'F–çG“°¢ÒFW6–væFRFF6WG22E$”âÂ„ôÄDõUBÂdÄ”DD”ôâÂ÷"4ôÕ$•4ôåôôäÅ“°¢Ò&V¦V7BG&–æ–ær66W72Fò„ôÄDõUBFF6WG3°¢Ò7&VFR'VâÖæ–fW7B6öçF–æ–ær6öæf–rÂv—B6öÖÖ—BÂFWVæFVæ7’fW'6–öç2Â–çWB†6†W2Â&æFöÒ6VVBÂv&æ–æw2ÂæB÷WGWB†6†W3°¢Ò&W'VâF†R6ÖR6öæf–ræBö'F–âçVÖW&–6ÆÇ’–FVçF–6ÂFWFW&Ö–æ—7F–2÷WGWG2à ¢227F÷vFP ¤Fòæ÷B'V–ÆBv–VæW"f–ÇFW&–ærÂ6öç7G&–æVB&VÆ—¦F–öç2ÂÖVW$´B66÷&–ærÂ&–W6–â„Ô2Â÷"W"6öæ6ÇW6–öç2–WBâf–æ—6‚æBFW7BF†R6Æ7VÆF–öâf÷VæFF–öâf—'7Bà ¢ÒÒĞ £ÂÒÒ4õU$4S¢%ôDD4UEôTD•EôäEôDõtäÄôBæÖBÒÓà ¢2övöÂ(	BVF—BF†R¢Õ¤ôFF6WG2æBF÷væÆöBöæÇ’v†B—2Ö—76–æp ¤–ç7V7BF†R7W'&VçBFF6WG2öÂ&ö¦V7B&ö÷BÂF÷væÆöB¶—G2Â¤•2Âd•E2f–ÆW2Â6FÆöwVW2ÂæBÖæ–fW7G2âFòæ÷B77VÖRf–ÆR—2Ö—76–ær§W7B&V6W6R—B—2æ÷B–âF†R&VfW'&VBföÆFW"à ¢22&WV—&VBF&vWB–çfVçF÷' ¥fW&–g’&W6Væ6RæB–çFVw&—G’öc  ¢222E$”â6æF–FFW0¢Ò6÷6Ö–6fÆ÷w2ÓB–æF—f–GVÂF—7Fæ6W0¢Ò4cBw&÷W0¢Ò4cBw&÷WfVÆö6—F–W0¢Ò$Õ%2Ö–â&VG6†–gB6FÆöwVP¢Ò„•¤ôÕ26FÆöwVRæBæ÷FW2÷&VFÖP ¢222„ôÄDõUB6æF–FFW0¢ÒfVÆÕ4Ôu2gVÆÂƒC2Öö&¦V7B6FÆöwVP¢ÒfVÆÔ„’gVÆÂs’Öö&¦V7B6FÆöwVP¢Òt4Ôu2CsrÖö&¦V7B6FÆöwVRf÷"ÆFW"W‡W&–ÖVç@ ¢2224ôÕ$•4ôåôôäÅ’ò&VfW&Væ6P¢Òöff–6–Â4cBFVç6—G’w&–@¢Òöff–6–Â4cBfVÆö6—G’w&–@¢Òöff–6–Â4cBFVç6—G’Væ6W'F–çG’öW'&÷"w&–@¢Òöff–6–Â4cBfVÆö6—G’Væ6W'F–çG’öW'&÷"w&–@¢Ò4cB²²ÖVâõ$Õ2f–VÆG2–bf–Æ&ÆP¢ÒtÄÄ%’–Æ÷BE#"6÷W&6R6FÆöwVR–bf–Æ&ÆP ¢22'VÆW0 £âæWfW"÷fW'w&—FRâ÷&–v–æÂ66–Væ6Rf–ÆRà£"âæWfW"&WÆ6RâVæf–Æ&ÆRFF6WBv—F‚7–çF†WF–2öf¶R&÷w2à£2âfW&–g’f–ÆRG—RÂ6—¦RÂ&VF&–Æ—G’ÂW‡V7FVB&÷r6÷VçBv†W&R÷76–&ÆRÂæB4„Ó#Sbà£Bâ&V6÷&BWF†÷&—FF—fR6÷W&6RU$ÂôDô’æB6—FF–öâà£Râ–bGWÆ–6FRW†—7G2Â†6‚&÷F‚æB&W÷'Bv†WF†W"F†W’&R'—FRÖ–FVçF–6Âà£bâ–b¤•6öçF–ç2F†RWF†÷&—FF—fRf–ÆRÂ&W6W'fRF†R¤•æBW‡G&7B6÷’–çFòâ–Ö×WF&ÆR&rF—&V7F÷'’à£râFòæ÷BF÷væÆöB&rÖVW$´BõtÄÄ%’7V&W2f÷"W"VæÆW727V6–f–6ÆÇ’&WV—&VBÆFW"à ¢22÷WGW@ ¤7&VFS  ¦FW‡@¦FF6WG2öÖæ–fW7G2ö–çfVçF÷'’æ§6öà¦FF6WG2öÖæ–fW7G2ö–çfVçF÷'’æ77`¦FF6WG2öÖæ–fW7G2öÖ—76–æræ§6öà¦FF6WG2öÖæ–fW7G2ö6†V6·7V×2ç6†#S`¦  ¥F†R–çfVçF÷'’×W7B–æ6ÇVFRFF6WB&öÆRÂ&VÆV6R÷fW'6–öâÂ6÷W&6RÂÆö6ÂF‡2Â6†V6·7VÒÂ'—FR6—¦RÂ&÷r6÷VçBÂæB7FGW2à ¤F÷væÆöBöæÇ’6öæf—&ÖVBÖ—76–ær6FÆöwVR÷&VfW&Væ6R&öGV7G2âBF†RVæB&–çB6öæ6—6RF&ÆRöb$U4TåBòDõtäÄôDTBòd”ÄTBòÔåTÂÔ44U52Õ$UT•$TBà ¥7F÷gFW"F†RfW&–f–VB–çfVçF÷'’—26ö×ÆWFRâFòæ÷B7F'BæÇ—6—2à ¢ÒÒĞ £ÂÒÒ4õU$4S¢5ôDD4UEõ$Tt•5E%•õ$õdTää4RæÖBÒÓà ¢2övöÂ(	B'V–ÆBF†R–Ö×WF&ÆR¢Õ¤ôFF6WB&Vv—7G'’æB&÷fVææ6R6†–à ¤7&VFRFF6WB&Vv—7G'’F†B—2WF†÷&—FF—fRf÷"WfW'’66–VçF–f–2'Vâà ¢22&Vv—7G'’66†VÖ ¤BÖ–æ–×VÒG&6³  ¦FW‡@¦FF6WEö–@§7W'fW¦6FÆöwVUöæÖP§&VÆV6P§&öÆP§6÷W&6U÷W&À¦Fö¦6—FF–öà¦Æ–6Vç6P¦Æö6Å÷&u÷F€§6†#S`¦'—FW0§&÷uö6÷Vç@¦6ö÷&F–æFUö6öÇVÖç0§fVÆö6—G•ö6öÇVÖç0§fVÆö6—G•ög&ÖP¦F—7Fæ6Uö6öÇVÖç0§Væ6W'F–çG•ö6öÇVÖç0§VÆ—G•ö6öÇVÖç0¦–ævW7FVEö@§&VçEöFF6WEö–G0§G&ç6f÷&ÖF–öåö–@§7FGW0¦  ¥&öÆW2×W7B&RW‡Æ–6—C¢E$”æÂE$”åô4ÄTæÂ„ôÄDõUFÂdÄ”DD”ôæÂ4ôÕ$•4ôåôôäÅ–Â$TdU$Tä4VÂ5”åD„UD”5õDU5EôôäÅ–à ¢22&÷fVææ6R'VÆW0 ¢Ò&rf–ÆW2&R–Ö×WF&ÆRà¢Òæ÷&ÖÆ—¦VB6FÆöwVR—2æWrFF6WBv—F‚&VçBÆ–æ²FòF†R&r6FÆöwVRà¢ÒFV6öçFÖ–æFVBG&–æ–ær6FÆöwVR—2æWrFF6WBv—F‚&VçBÆ–æ·2ÇW2âW†6ÇW6–öâÖÆ—7B†6‚à¢Ò&V6öç7G'V7F–öâw&–B&V6÷&G2WfW'’FF6WB”BæB6öæf–r†6‚F†B6öçG&–'WFVBFò—Bà¢ÒFW&—fVB&öGV7G2F†B76–Ö–ÆFRÖVW$´B×W7B&RÖ&¶VB26öçFÖ–æFVBf÷"ÖVW$´B†öÆF÷WBW‡W&–ÖVçBæBÖ’öæÇ’&R4ôÕ$•4ôåôôäÅ’à ¤7&VFRfÆ–FF–öâgVæ7F–öç2F†Bf–Â'Vç2v†Vâ&WV—&VB&÷fVææ6R—2'6VçBà ¤FBWFöÖFVBFW7G2f÷"6†V6·7VÒÖ—6ÖF6‚ÂÖ—76–ær6—FF–öâ÷6÷W&6RÂ–çfÆ–B&öÆRG&ç6—F–öç2ÂæBFW&—fVB&öGV7Bv—F‚–æ6ö×ÆWFR&VçG2à  ¢ÒÒĞ £ÂÒÒ4õU$4S¢Eôäõ$ÔÄ•¤Uô4ôõ$D”äDU5õTä•E2æÖBÒÓà ¢2övöÂ(	Bæ÷&ÖÆ—¦R¢Õ¤ô6ö÷&F–æFW2Âg&ÖW2ÂVæ—G2ÂæBVæ6W'F–çF–W0 ¤'V–ÆBFWFW&Ö–æ—7F–2æ÷&ÖÆ—¦F–öâ—VÆ–æRf÷"F†R&Vv—7FW&VB6FÆöwVW2à ¢22&WV—&VÖVçG0 ¢Ò&W6W'fR÷&–v–æÂ6öÇVÖç2Væ6†ævVB–âF†R–Ö×WF&ÆR&r–çWBà¢Ò7&VFRæ÷&ÖÆ—¦VB'VWB÷WGWG2v—F‚7F&ÆR6÷W&6R”G2à¢ÒW6R7G&÷’f÷"6ö÷&F–æFRG&ç6f÷&ÖF–öç2v†W&R÷76–&ÆRà¢Ò6''’W‡Æ–6—BVæ—G2à¢ÒæWfW"6–ÆVçFÇ’Ö—‚†VÆ–ö6VçG&–2ÂÆö6Âw&÷WÂ4Ô"Â÷"÷F†W"fVÆö6—G’g&ÖW2à¢Ò&V6÷&BF†RG&ç6f÷&ÖF–öâ÷fW'6–öâW6VBFò6öçfW'BfÇVRà¢Ò¶VWÖV7W&VÖVçBVæ6W'F–çG’æBVÆ—G’fÆw2à ¢227FæF&B÷WGWB6öÇVÖç2v†W&Rf–Æ&ÆP ¦FW‡@§6÷W&6U÷&÷uö–@¦6æöæ–6Åöö&¦V7Eö–@§&öFVp¦FV5öFVp¦vÅöÅöFVp¦vÅö%öFVp§6vÅöFVp§6v%öFVp¦7¥÷fÇVUö¶×0¦7¥ög&ÖP§&VG6†–g@¦F—7Fæ6Uö×0¦F—7Fæ6UöW'%ö×0¦F—7Fæ6UöÖöGVÇW0¦F—7Fæ6UöÖöGVÇW5öW' ¦†•öfÇW€§sSö¶×0§7W'fW§&VÆV6P§VÆ—G•öfÆw0¦  ¤Fòæ÷B–æfW"Væf–Æ&ÆRfÇVW2VæÆW72F†RFW&—fF–öâ—2Fö7VÖVçFVBæB6W&FVÇ’fÆvvVBà ¢22fÆ–FF–öà ¥FW7B¶æ÷vâ6ö÷&F–æFRG&ç6f÷&ÖF–öç2v–ç7BG'W7FVB7G&÷’&W7VÇG2â6†V6²&÷VæB×G&—æwVÆ"W'&÷'2â6†V6²Væ—B6öçfW'6–öç2âFWFV7B–×÷76–&ÆR&ævW2ÂæâW‡Æ÷6–öç2ÂæBGWÆ–6FR6÷W&6R×&÷r”G2à ¥&öGV6Ræ÷&ÖÆ—¦F–öâ&W÷'Bf÷"WfW'’FF6WBæB7F÷&Vf÷&Rç’&V6öç7G'V7F–öâà ¢ÒÒĞ £ÂÒÒ4õU$4S¢Uô„ôÄDõUEô44U55ô4ôåE$ôÂæÖBÒÓà ¢2övöÂ(	BÖ¶RF†R¢Õ¤ô†öÆF÷WB&÷VæF'’Ö6†–æRÖVæf÷&6V@ ¤–×ÆVÖVçB†öÆF÷WB6V7W&—G’&÷VæF'’f÷"F†RfVÆW‡W&–ÖVçBà ¢22&WV—&VB&V†f–÷  ¥F†R6VÆV7FVBÖVW$´BfÆ–FF–öâ6FÆöwVR‡2’×W7B&R&Vv—7FW&VB2„ôÄDõUFæB×W7Bæ÷B&R&VF&ÆR'’G&–æ–ær÷&V6öç7G'V7F–öâ6öÖÖæG2à ¤7&VFRGvòW†V7WF–öâ6öçFW‡G3  ¢222TD•B6öçFW‡@¤Ö’&VBE$”âæB„ôÄDõUBöæÇ’f÷"ÆV¶vRFWFV7F–öâæBW†6ÇW6–öâÖÆ—7B7&VF–öââ—B×W7Bæ÷C ¢Òf—B÷"GVæR&V6öç7G'V7F–öâ&ÖWFW'3°¢Ò6ö×WFR66–Væ6RW&f÷&Öæ6RÖWG&–73°¢Ò7&VFRFVç6—G’÷fVÆö6—G’&V6öç7G'V7F–öç2–æf÷&ÖVB'’†öÆF÷WC°¢ÒW‡÷6R†öÆF÷WBÖFW&—fVBGVæ–ær†–çG2FòF†RG&–æ–ær6öæf–rà ¢222E$”â6öçFW‡@¤Ö’&VBöæÇ’&÷fVBE$”åô4ÄTæ–çWG2â„ôÄDõUBF—&V7F÷&–W26†÷VÆB&RVæÖ÷VçFVBÂ–æ66W76–&ÆRÂ÷"FVæ–VBBF†RFFÖÆöFW"Æ–W"à ¢222dÄ”DDR6öçFW‡@¤ÆÆ÷vVBöæÇ’gFW"g&÷¦Vâ&VF–7F–öâÖæ–fW7BW†—7G2æB76W2†6‚fW&–f–6F–öâà ¢22FW7G0 ¥w&—FRFW7G2&÷f–æs ¢ÒE$”âf–Ç2v†Vâ6¶VBf÷"„ôÄDõUC°¢Ò†–FFVâ–æF—&V7B&VçBFF6WB6öçFÖ–æFVB'’„ôÄDõUB—2Ç6ò&V¦V7FVC°¢ÒTD•B6âVÖ—BâW†6ÇW6–öâÆ—7B'WBæ÷B&V6öç7G'V7F–öâ÷WGWC°¢ÒdÄ”DDR&VgW6W2Fò7F'Bv—F†÷WBfÆ–Bg&VW¦RÖæ–fW7C°¢Ò6†æv–ærG&–æ–ær6öæf–rgFW"g&VW¦R–çfÆ–FFW2fÆ–FF–öâWF†÷&—¦F–öâà ¤Ö¶Rf–ÇW&RÆ÷VBæBW‡Æ–6—Bà ¢ÒÒĞ £ÂÒÒ4õU$4S¢eô5$õ54ÔD4…ôDT4ôåDÔ”äD”ôâæÖBÒÓà ¢2övöÂ(	BFV6öçFÖ–æFRF†RfVÆG&–æ–ær6WB&Vf÷&R&V6öç7G'V7F–öà ¤7&VFRFVF–6FVBTD•B—VÆ–æRF†B6â6VRG&–æ–ær6æF–FFW2æBF†RÖVW$´B„ôÄDõUBöæÇ’f÷"F†RW'÷6RöbFWFV7F–ær÷fW&Æà ¢227&÷76ÖF6‚Æ–W'0 ¤–×ÆVÖVçB6W&FR6†V6·2f÷# £âW†7B6÷W&6Rö6FÆöwVR”G2Â–æ6ÇVF–ærÆ–6W3°£"â6·’÷6—F–öâv—F‚6öæf–wW&VBæwVÆ"FöÆW&æ6W3°£2â&VG6†–gBö7¢&÷†–Ö—G’v—F‚Fö7VÖVçFVBFöÆW&æ6S°£Bâ6öÖ&–æVB÷6—F–öâ²7¢Æ–¶VÆ–†ööC°£Râ¶æ÷vâ7W'fW’Ö÷fW&ÆÖWFFFà ¢22„•¤ô7V6–f–26†V6° ¥F†RfVÆÕ4Ôu2W"&W÷'G23’&Wf–÷W6Ç’¶æ÷vâ„•¤ôFWFV7F–öç2–âF†Rfö÷G&–çBæBF†BfVÆÕ4Ôu2&V6÷fW&VBÆÂ3’à ¤Fòæ÷B†&BÖ6öFR&Æ–æB&VÖ÷fÂöb3’—FV×2§W7BFòÖ¶RçVÖ&W"ÖF6‚â&öGV6R&÷fVææ6R×&–6‚ÖF6‚F&ÆRæBfW&–g’F†BF†R–FVçF–f–VB÷fW&Æ—26öç6—7FVçBv—F‚F†RV&Æ—6†VBf7BæB6öÇVÖâ6VÖçF–72â&V6÷&Bç’Ö—6F6‚2âVF—Bf–æF–ærÂæ÷B2&V6öâFòÖæ—VÆFRF‡&W6†öÆG2à ¢226öçFÖ–æFVBFW&—fVB&öGV7G0 ¤VF—Bæ÷BöæÇ’&÷r÷fW&Æ'WBFF6WBÆ–æVvRâç’&öGV7BFW&—fVBg&öÒÖVW$´BÖ76–Ö–ÆFVBw&–Bö6FÆöwVR×W7Bæ÷B&V6öÖRâ–æF—&V7BE$”â–çWBà ¢22÷WGWG0 ¥&öGV6RÖ6†–æR×&VF&ÆRÖF6‚F&ÆRÂ‡VÖâ&W÷'BÂæB–Ö×WF&ÆRW†6ÇW6–öâÆ—7Bv—F‚†6†W2âW6RF†BW†6ÇW6–öâÆ—7BFò7&VFRæWrE$”åô4ÄTæFF6WBv—F‚gVÆÂ&VçBÆ–æVvRà ¤Fòæ÷BFVÆWFR&p