# Leakage test 15 — Preregistered analysis plan hash lock

Lock down analysis parameters, hypotheses, and null generation protocols prior to unsealing.

## Objective

Prevent unconscious or post-hoc researcher tuning ("p-hacking" or "researcher degrees of freedom") by locking and hashing a formal pre-registration document prior to unblinding the holdout.

## Requirements

1. **Pre-Registration Contract**: Before unsealing holdout coordinates, create a sealed specification (`docs/preregistered_analysis_plan.json` and companion `PREREGISTRATION.md`) specifying:
   - primary and secondary hypotheses;
   - exact smoothing scale ($R_s$) and grid resolution ($\Delta x$);
   - tracer selection cuts and velocity windows ($cz_{\max}$);
   - exact mathematical formulas for test statistics ($\langle \delta \rangle$, occupancy, cross-correlation);
   - random seeds and null distribution generation models ($W(cz)$);
   - significance thresholds ($\alpha$).
2. **Cryptographic Seal**: Compute and log the SHA-256 digest of the pre-registration contract.
3. **Exploratory Gating**: Any post-reveal evaluation that deviates from the locked plan is automatically flagged as `EXPLORATORY_ANALYSIS` and permanently barred from confirmatory result tables.

Save `leakage/15_preregistration_lock.json` and `.md`.
