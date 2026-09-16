# Leakage test 06 — Derived-product lineage audit

Search every training/reference input for products that may already assimilate the holdout survey.

Examples of high-risk inputs:
- CF4++ / hybrid ZoA reconstructions incorporating MeerKAT redshifts;
- density/velocity grids generated from a contaminated catalogue;
- precomputed smoothed fields made after loading the holdout;
- feature tables/caches whose parents are not recorded.

For each derived product recursively walk its parent lineage. If any parent is HOLDOUT or unknown, mark the product `CONTAMINATED_FOR_VELA_HOLDOUT` and deny it to TRAIN.

Comparison-only use after validation is allowed but must remain separate.
