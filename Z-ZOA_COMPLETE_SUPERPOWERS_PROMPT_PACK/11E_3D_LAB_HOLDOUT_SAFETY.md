# /goal — Make the 3D Lab incapable of leaking the holdout before reveal

Treat visualization as a potential scientific side channel. Harden the 3D Lab so it cannot undermine the Vela holdout experiment.

## Threat model

Prevent pre-reveal exposure through:
- direct HOLDOUT catalogue endpoints;
- hidden layers;
- layer counts/metadata that reveal the holdout;
- cached browser/backend artifacts;
- precomputed hybrid fields;
- comparison-only reconstructions that already assimilated MeerKAT;
- labels/annotations derived from holdout information;
- API query parameters;
- static public files bundled by the frontend;
- source maps/test fixtures containing real holdout rows.

## Authorization

The backend must decide what artifacts are authorized. Frontend hiding alone is insufficient.

In TRAIN/FROZEN-before-reveal:
- HOLDOUT datasets are absent from the authorized bundle list;
- holdout-derived lineage is denied;
- hybrid/contaminated comparison products are denied;
- response metadata must not expose row counts or summaries of hidden datasets unless explicitly approved for the audit protocol.

## Cache policy

Stage changes must invalidate or namespace caches. A user who visited a post-reveal run previously must not be able to retrieve those cached artifacts while operating a clean pre-reveal experiment context.

## Test suite

Attempt to leak holdout information through:
- direct URL/API requests;
- guessed artifact IDs;
- stale browser cache;
- backend cache;
- run comparison;
- downloadable bundle paths;
- debug endpoints;
- search/filter APIs;
- metadata-only calls.

All must fail before authorized reveal.

## Negative control

Remove/move the HOLDOUT directory from the runtime and verify the 3D Lab's pre-reveal behavior and available authorized layers are unchanged.

## Completion gate

Produce `leakage/3d_lab_holdout_safety_report.json` and `.md`. The global leakage certificate must include its hash.
