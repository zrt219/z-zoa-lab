# /goal — Run robustness and sensitivity sweeps without p-hacking

Run pre-declared sensitivity tests around the completed Vela result.

Vary scientifically justified choices such as:
- smoothing scale;
- grid resolution;
- distance/velocity cuts;
- reasonable selection-function variants;
- reconstruction regularization/prior settings;
- random seed / ensemble size;
- training catalogue inclusion variants that remain leakage-safe.

Do not search arbitrary settings for the largest significance. Report the full sweep and show whether the central conclusion is stable.

Create a robustness matrix with one row per run containing config hash, effect size, p-value/interval, and major field statistics.
