# /goal — Add XRPL Testnet research-run anchoring

Add a small research-integrity service that fingerprints frozen Z-ZOA stages and records the fingerprint in an XRPL **Testnet** transaction.

This is not cryptocurrency functionality. It is a development-time chronology/integrity receipt.

## Scope

Implement:

```text
research/ledger/
  canonicalize
  anchor
  receipt
  verify
  xrpl_client
```

Follow actual repository conventions.

Public behavior:

```text
anchor_run(run_id, stage)
verify_anchor(run_id, stage)
verify_chain(run_id)
get_receipt(run_id, stage)
```

## Deterministic anchor payload

Construct a canonical JSON payload from fields such as:
- schema version;
- project `Z-ZOA`;
- run ID;
- stage;
- git commit;
- resolved-config SHA-256;
- dataset-manifest SHA-256;
- results/prediction-manifest SHA-256;
- leakage-certificate SHA-256 when relevant;
- previous XRPL transaction hash.

Canonicalization must use documented UTF-8 JSON with stable key ordering/separators. Hash with SHA-256.

## XRPL transaction

Use XRPL Testnet only. Prefer the standard `xrpl-py` library.

Use a minimal no-op transaction capable of carrying a compact Memo, such as a no-option `AccountSet`, following current XRPL library/protocol rules.

Memo logical content should remain tiny, for example:

```json
{"p":"Z-ZOA","r":"VELA-0017","s":"PREDICTION_FROZEN","h":"<sha256>","prev":"<tx>"}
```

Encode fields according to XRPL requirements. Never put datasets or full manifests on-ledger.

## Reliable finality

Do not mark an anchor complete at submission. Require:
- transaction hash persisted;
- lookup by hash;
- `validated == true`;
- final result `tesSUCCESS`;
- ledger index recorded.

States:

```text
UNSUBMITTED
SUBMITTED_PENDING
VALIDATED_SUCCESS
VALIDATED_FAILED
EXPIRED_OR_MISSING
TESTNET_HISTORY_UNAVAILABLE
```

## Holdout gate

For experiments with `require_freeze_anchor_before_reveal=true`, HOLDOUT reveal requires:
- frozen manifest valid;
- leakage certificate valid;
- local anchor payload hash matches receipt;
- XRPL transaction is validated success;
- memo hash matches local frozen hash.

Otherwise holdout remains locked.

## Secret policy

Never store XRPL private keys/secrets in:
- git;
- receipts;
- run manifests;
- browser/frontend state;
- logs;
- screenshots;
- tests.

Use environment/local secret storage. Public address may be recorded.

## Testnet caveat

Clearly label receipts as development records. Testnet history may reset/disappear; distinguish that from tamper detection.

## UI

Add a restrained `RESEARCH ANCHOR` area to the Calculation Room run inspector:

```text
Network      XRPL TESTNET
Stage        PREDICTION_FROZEN
Run hash     ...
Transaction  ...
Ledger       ...
Status       VALIDATED
Chain        VERIFIED
```

No wallet dashboard, trading, token, NFT, price, or crypto animation features.

## Tests

Test canonicalization, hash mutation detection, memo round-trip, pending/failed rejection, wrong hash, wrong previous transaction, missing receipt, secret non-persistence, holdout unlock gating, and Testnet-reset handling.

Live Testnet integration tests must be optional and separate from the default suite.

## Completion gate

First demonstrate end-to-end with a synthetic frozen run, then mutate a copy of its manifest and prove verification fails. Do not anchor the real Vela run until this passes.
