# /goal — Add read-only run comparison to the 3D Lab

Build a comparison mode for two authorized Z-ZOA run artifacts.

Primary use cases:
- baseline vs constrained reconstruction;
- prediction vs hybrid reconstruction;
- different robustness settings;
- mean vs uncertainty context.

## Rules

Comparison must never alter either source run. All comparison products must be either:
1. precomputed by the scientific backend and stored as derived artifacts with parents, or
2. strictly visualization-only differences that are labeled as such and never used as paper metrics.

Paper-grade Delta density/velocity/uncertainty must come from the scientific pipeline, not a shader.

## Interface

Provide:
- Run A selector;
- Run B selector;
- synchronized camera;
- side-by-side mode;
- overlay mode where scientifically readable;
- difference-artifact mode when a backend Delta artifact exists;
- metadata panel explaining both run IDs/config hashes.

## Safety

Do not allow a pre-reveal TRAIN/FROZEN run to be compared against HOLDOUT-containing data unless the experiment stage authorizes validation/reveal.

## Tests

Test stage authorization, synchronized coordinates, correct run labels, and inability to mutate either run.
