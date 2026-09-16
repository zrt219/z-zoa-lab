# Leakage test 13 — OS-level physical holdout sandbox

Prove physical and environmental isolation of holdout data during the training run.

## Objective

Ensure that the protected `HOLDOUT/` data is not merely blocked by application-level Python checks, but is physically inaccessible at the operating-system boundary during training.

## Requirements

1. **Filesystem Isolation**: The training process executes in an isolated environment or ephemeral workspace where `datasets/HOLDOUT/` is not mounted, not readable, or secured with restrictive OS access control locks (e.g. read denial ACLs on Windows, `chmod 000` on POSIX).
2. **Network Isolation**: Outbound network requests to external astronomical catalogue endpoints (e.g. VizieR, CADC TAP, NED, MAST) are disabled or blocked at the socket/loopback level during the frozen training pass.
3. **Trap Verification**: Any attempt by training code or third-party dependencies to open holdout paths must fail at the OS/filesystem boundary with logged access-denied errors.
4. **Clean Verification**: Training completes solely using verified `TRAIN_CLEAN` inputs.

Save `leakage/13_os_sandbox_test.json` and `.md`.
