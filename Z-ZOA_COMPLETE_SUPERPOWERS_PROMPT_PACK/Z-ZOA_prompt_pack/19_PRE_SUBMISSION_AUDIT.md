# /goal — Perform a referee-style pre-submission audit

Act as a skeptical astronomy referee and reproducibility reviewer.

Audit:
- novelty claims;
- catalogue versions and citations;
- coordinate/velocity frames;
- units and uncertainty propagation;
- selection functions;
- training/holdout contamination;
- leakage audit completeness;
- frozen prediction integrity;
- null model appropriateness;
- robustness and multiple-testing concerns;
- comparison-product contamination;
- figure/table reproducibility;
- data/code availability;
- manuscript claims versus actual evidence.

Produce a blocking/non-blocking issue list. For every blocking issue, identify the exact code/data/manuscript artifact that must change.

Do not recommend submission until all blocking issues are cleared and the central run reproduces from the bundle.
