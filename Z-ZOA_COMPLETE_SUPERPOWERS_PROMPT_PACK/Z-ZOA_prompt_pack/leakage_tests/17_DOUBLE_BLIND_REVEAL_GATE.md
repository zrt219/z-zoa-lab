# Leakage test 17 — Double-blind unblinding reveal gate

Enforce a particle-physics style cryptographic unblinding gate between training and evaluation.

## Objective

Ensure that the training stage produces a sealed, verified prediction without the computational or logical capability of evaluating holdout science scores, and that a formal unblinding ceremony is required before holdout access is granted.

## Requirements

1. **Dual-Token Unblinding Gate**: A dedicated reveal command (`python -m research.holdouts.reveal_gate`) enforces that access to holdout data is impossible without presenting:
   - a valid, cryptographically verified `freeze_manifest.json` digest;
   - the sealed `preregistered_analysis_plan.json` SHA-256 hash;
   - a certified passing `leakage_certificate.json`.
2. **Post-Freeze Immutability**: If any prediction array byte, model parameter, or input file checksum changed after the freeze manifest was generated, the reveal command aborts unblinding permanently.
3. **Audit Trail**: Successful unblinding generates an immutable `UNBLINDING_RECEIPT` recording UTC timestamp, operator, git commit, and manifest seal.

Save `leakage/17_reveal_gate.json` and `.md`.
