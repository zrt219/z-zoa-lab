# Leakage test 03 — Sky-position crossmatch

Cross-match every training candidate catalogue against the holdout using spherical coordinates.

Run multiple scientifically reasonable angular radii (for example tight, moderate, and survey-resolution-aware values) and report counts by dataset and radius. Do not choose a radius based on which gives the most desirable final science result.

For every match save source IDs, RA/Dec, Galactic l/b, separation, catalogue roles, and quality flags.

Flag ambiguous one-to-many matches for manual review.
