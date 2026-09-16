# Leakage test 17 — Controlled reveal gate

Prove that holdout reveal is a one-way, explicitly authorized stage transition.

## Reveal authorization requires

- frozen run manifest exists and verifies;
- leakage certificate PASS or declared allowed status;
- analysis-spec hash lock verifies;
- no frozen file has changed;
- XRPL `PREDICTION_FROZEN` receipt verifies if configured as required;
- user/command explicitly requests transition to VALIDATE.

## Test failures

Attempt reveal after changing separately:
- one config value;
- one prediction byte;
- one dataset hash;
- analysis spec;
- leakage certificate;
- required XRPL receipt.

Every attempt must fail before HOLDOUT contents are returned.

After successful reveal, record a reveal event with timestamp, parent freeze hash, and stage transition in the run manifest/ledger.

Save `leakage/17_reveal_gate_report.json` and `.md`.
