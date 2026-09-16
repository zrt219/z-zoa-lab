# /goal — FINAL Z-ZOA end-to-end acceptance run

This is the final project gate. Do not add new features here. Verify that the system built by the previous prompts behaves as one coherent research instrument.

## Part A — Clean environment

From a clean clone/environment:
1. install dependencies using documented instructions;
2. run default test suite;
3. initialize an empty dataset registry;
4. verify Calculation Room opens honestly with no fake data;
5. verify 3D Lab has no unauthorized layers.

## Part B — Synthetic full rehearsal

Create a deterministic synthetic/mock universe with known hidden structure and clearly label it `SYNTHETIC TEST DATA`.

Run the complete pipeline:

```text
register synthetic TRAIN + synthetic HOLDOUT
-> audit/decontaminate
-> normalize units/coordinates
-> mock validation
-> reconstruction
-> constrained realizations/uncertainty
-> export authorized pre-reveal 3D bundle
-> run leakage suite
-> freeze prediction
-> optional XRPL Testnet anchor
-> verify HOLDOUT is still locked until all configured gates pass
-> reveal synthetic holdout
-> score against preregistered metrics/nulls
-> hybrid reconstruction
-> robustness sweep
-> post-reveal 3D comparison
-> paper tables/figures
-> reproducibility bundle
-> draft manuscript shell
```

Because truth is known, verify the pipeline's metrics against expected ranges and document any failure.

## Part C — Leakage attack rehearsal

Attempt:
- direct holdout file access in TRAIN;
- API access;
- 3D Lab access;
- cache reuse;
- contaminated derived-product use;
- config mutation after freeze;
- prediction mutation after freeze;
- invalid XRPL receipt where anchoring is required.

Every attack must be rejected and logged.

## Part D — Reproduction

Delete generated caches and rebuild the synthetic frozen prediction from the clean config/input allowlist.

Compare:
- resolved config hash;
- dataset hashes;
- core deterministic output hashes or documented numerical tolerances;
- metrics;
- generated tables.

Create `acceptance/FINAL_ACCEPTANCE_REPORT.md` and JSON with PASS/FAIL for every criterion.

## Part E — Real-experiment readiness

Do not reveal real Vela HOLDOUT data here. Instead verify that the real experiment config can reach the pre-reveal gate using only allowed data and that the next allowed action is exactly:

```text
FREEZE REAL PREDICTION
-> PASS LEAKAGE CERTIFICATE
-> ANCHOR IF REQUIRED
-> AUTHORIZED REVEAL
```

## Final pass condition

The project is ready for the real paper experiment only if:
- all automated suites pass;
- synthetic end-to-end rehearsal passes;
- leakage attack rehearsal passes;
- clean-room reproduction passes;
- Calculation Room and 3D Lab enforce the same stage policy;
- no real holdout information was exposed during this acceptance run;
- paper factory outputs are reproducible from run artifacts.

If any condition fails, do not call the project complete. Fix the failing subsystem and rerun the affected gates.
