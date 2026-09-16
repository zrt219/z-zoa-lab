# Leakage test 04 — Position + velocity/redshift consistency

Take positional match candidates and compare redshift/velocity values in a common documented frame where possible.

Report:
- angular separation;
- original velocity/redshift and frame for each catalogue;
- converted comparison values;
- delta velocity;
- uncertainties;
- match classification: CONFIRMED / PROBABLE / AMBIGUOUS / REJECTED.

Never silently convert frames without logging the method.

Confirmed/probable matches carrying the same redshift constraint must be excluded from the training snapshot for a redshift-based holdout validation.
