# Leakage test 08 — Hyperparameter and human tuning leakage

Audit git history, configs, run logs, notebooks, and experiment notes for evidence that holdout outcomes were used to choose:
- smoothing scale;
- grid resolution;
- thresholds;
- survey cuts;
- priors/regularization;
- feature definitions;
- validation metric definitions;
- null-model settings.

Create a table with each final parameter, when it was fixed, why it was chosen, and whether any holdout information influenced it.

If a parameter was tuned post-reveal, classify the associated result as exploratory, not confirmatory. If necessary, select a fresh untouched validation dataset for a confirmatory test.
