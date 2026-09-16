# Leakage test 10 — Freeze-manifest and canary test

Before the true freeze, verify that the freeze mechanism detects tampering.

1. Create a test prediction run.
2. Freeze it and record hashes.
3. Modify one config value, one input file copy, and one prediction byte/file in separate canary tests.
4. Confirm validation authorization fails in every case.
5. Restore clean state and verify the original frozen artifacts pass.

Also verify that the freeze manifest records source commit, dependency versions, data hashes, random seeds, metric spec, null spec, and selection-function version.
