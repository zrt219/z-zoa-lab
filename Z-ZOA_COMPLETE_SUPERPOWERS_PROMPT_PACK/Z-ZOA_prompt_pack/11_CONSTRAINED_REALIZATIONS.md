# /goal — Add an ensemble / constrained-realization layer for uncertainty

Upgrade the baseline reconstruction from a single field to an ensemble suitable for probabilistic statements.

## Outputs

For N realizations compute and save:
- per-voxel mean density;
- per-voxel density standard deviation;
- optional velocity-component means/stds;
- probability that density exceeds configured threshold(s);
- ensemble metadata and random seeds.

Begin with a computationally practical N for development, then provide a config allowing a publication run (for example ~200 or more if justified and feasible).

## Validation

Use mocks to test whether nominal probability levels are calibrated. Check ensemble convergence as N increases. Record numerical failures instead of silently dropping them.

Do not access HOLDOUT in this phase.
