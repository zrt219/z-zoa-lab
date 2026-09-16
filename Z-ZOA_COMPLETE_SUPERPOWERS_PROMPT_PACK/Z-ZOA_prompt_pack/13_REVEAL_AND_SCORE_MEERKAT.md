# /goal — Reveal the Vela-SMGPS holdout and score the frozen prediction

This command is allowed only when a valid frozen prediction exists.

## Rules

- Do not change reconstruction hyperparameters after seeing the holdout.
- If a bug is found, invalidate the run, document the reason, repair it, rerun from TRAIN, and create a new run ID before validation.
- Keep confirmatory metrics separate from any exploratory post-reveal analyses.

## Primary validation

Evaluate the frozen reconstructed field at the withheld Vela-SMGPS galaxy locations and compare against survey-matched random/null catalogues that respect the footprint, redshift/velocity range, and adopted selection model.

Compute pre-specified metrics such as:
- mean reconstructed overdensity at holdout positions;
- fraction in high-probability overdensity voxels;
- spatial cross-correlation;
- predefined wall/filament recovery metrics;
- probability calibration / occupancy by prediction bin;
- null p-values and effect sizes.

Save raw scores, null distributions, summary tables, and a validation report. Do not rely on visual similarity.
