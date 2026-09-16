# /goal — Build the Z-ZOA scientific test harness and CI gates

Create a test structure that makes scientific regressions, access-control failures, and reproducibility failures visible before they contaminate a paper run.

## Test groups

Organize tests by purpose rather than one giant folder:

```text
unit               pure functions and schemas
scientific         trusted-value and numerical-regression tests
integration        datasets -> run artifacts -> API
security           HOLDOUT boundaries and frozen-run immutability
reproducibility    replay/hash/canonicalization tests
frontend           Calculation Room / 3D Lab behavior
network            optional external/Testnet integration tests
```

Follow the existing project conventions where possible.

## Required test markers

Separate tests that require:
- network;
- large datasets;
- GPU;
- XRPL Testnet;
- optional 3D/browser stack.

The default fast suite must not depend on network availability.

## CI minimum

Configure CI to run on pull requests/commits as appropriate:
- lint/format checks already adopted by the repo;
- static/type checks if the project uses them;
- fast unit/scientific/security tests;
- frontend tests;
- a small deterministic synthetic end-to-end run;
- artifact upload of test/repro reports when useful.

Never commit secrets or real Testnet private keys into CI.

## Golden-value policy

For scientific reference values:
- state where the expected value comes from;
- store the expected units;
- use scientifically justified tolerances;
- never widen a tolerance only to make a failing test pass without explanation.

## Completion gate

Deliberately introduce a temporary local test failure in a throwaway branch/change to verify the gate catches it, then restore clean code and show the entire default suite passing.
