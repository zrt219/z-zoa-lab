# Z-ZOA Research Run Anchoring (XRPL Testnet Notarization)

## 1. Overview & Core Philosophy

Z-ZOA calculates a SHA-256 fingerprint of a frozen research run and records that fingerprint in an XRPL Testnet transaction. The transaction does not contain the scientific dataset. It contains only enough information to later demonstrate that a particular frozen run hash had been committed to the ledger before subsequent research stages were performed.

```
scientific run
      ↓
compute SHA-256 fingerprint
      ↓
write fingerprint to XRPL Testnet (minimal no-op AccountSet + Memo)
      ↓
receive & await validated transaction hash (TransactionResult == tesSUCCESS)
      ↓
store transaction hash & receipt beside the run (xrpl_receipt.json)
```

### Critical Scientific Scope

- **XRPL is not part of the astronomy calculation.** It never influences reconstruction, density estimates, peculiar velocities, selection functions, null tests, statistical significance, holdout scoring, or cosmology.
- **Integrity vs Scientific Correctness**: XRPL anchoring demonstrates integrity and chronology of bytes. It does **not** demonstrate that the scientific methodology or astronomical conclusions are correct.
- **Testnet Resets & Archival Caveat**: XRPL Testnet is a development network and subject to periodic resets. Final publication preservation must additionally use conventional research repositories and archival mechanisms (e.g. Zenodo, CDS, Git tags).
- **Offline / Failure Fallback**: XRPL network outages must never corrupt or modify scientific results. If XRPL is unreachable, the run remains frozen locally with status `LOCAL_COMPLETE_UNANCHORED`. Anchoring can be retried at any time without altering the run hash.

---

## 2. Research Stages & Chronological Sequence

The notarization layer supports the following stages in strict chronological order:

1. `TRAIN_START` — Initialization of training and model setup.
2. `PREDICTION_FROZEN` — Sealed prediction manifest frozen prior to holdout evaluation.
3. `HOLDOUT_REVEAL` — Unlocking and ingestion of masked out-of-sample datasets (e.g. MeerKAT HI).
4. `VALIDATION_COMPLETE` — Out-of-sample comparison and kinematic scoring finalized.
5. `HYBRID_COMPLETE` — Integrated joint reconstruction finalized.
6. `PAPER_CANDIDATE` — Publication candidate frozen for manuscript production.

Each stage references the immediately preceding transaction hash (`previous_tx_hash`), forming an immutable chronological chain:

```
TRAIN_START (tx: 1111...)
      ↓
PREDICTION_FROZEN (prev: 1111..., tx: 2222...)
      ↓ (GATE: holdout access locked until 2222... is validated on ledger)
HOLDOUT_REVEAL (prev: 2222..., tx: 3333...)
      ↓
VALIDATION_COMPLETE (prev: 3333..., tx: 4444...)
```

---

## 3. Holdout Protection Gate Integration

For research runs configured with `require_freeze_anchor_before_reveal: true`, the gated `DataGateway` and `reveal_holdout()` enforce strict precondition checks:

```python
# All of the following must evaluate to True before HOLDOUT access is granted:
frozen_manifest_exists
AND frozen_manifest_hash_matches
AND xrpl_receipt_exists
AND receipt.stage == "PREDICTION_FROZEN"
AND receipt.validated == True
AND receipt.transaction_result == "tesSUCCESS"
AND ledger memo hash == local frozen hash
```

If any condition fails, access is denied with `AnchorVerificationHoldoutViolationError`.

---

## 4. Canonical Anchor Manifest & Cryptographic Hashing

To ensure bit-for-bit repeatability across platforms, the anchor payload is canonicalized with:
- UTF-8 encoding
- Alphabetically sorted object keys
- Compact separators (`','` and `':'`) with no incidental whitespace
- Documented schema version (`schema_version: 1`)

```json
{
  "schema_version": 1,
  "project": "Z-ZOA",
  "run_id": "VELA-0017",
  "stage": "PREDICTION_FROZEN",
  "git_commit": "df3536e...",
  "manifest_sha256": "97b6a941...",
  "config_sha256": "4a123f...",
  "dataset_manifest_sha256": "c8e19b...",
  "results_manifest_sha256": "e3b0c4...",
  "previous_tx_hash": "4F8A73..."
}
```

The SHA-256 of this canonical byte string represents the authoritative `anchor_payload_sha256`.

---

## 5. XRPL Transaction Structure & Memo Format

To prevent unnecessary ledger state bloat and adhere to XRPL's 1 KB memo limit:
- **Transaction Type**: Minimal no-op `AccountSet` (no account flags or settings changed).
- **Memos Field**:
  - `MemoType`: Hex-encoded ASCII `"z-zoa/anchor"`
  - `MemoFormat`: Hex-encoded ASCII `"json"`
  - `MemoData`: Hex-encoded compact JSON object:
    ```json
    {"p":"Z-ZOA","r":"VELA-0017","s":"PREDICTION_FROZEN","h":"<anchor_payload_sha256>","prev":"<previous_tx_hash>"}
    ```
- Total serialized memo size is approximately 380 bytes (well under the 1 KB limit).

---

## 6. Secret Isolation & Key Management

- **Signing Credentials**: Loaded exclusively from:
  - Environment variables: `XRPL_TESTNET_SECRET` (or `XRPL_TESTNET_SEED`)
  - Local gitignored file: `.secrets/xrpl_testnet.json`
- **Strict Prohibition**: Private keys and seeds are never committed to Git, never logged, and never included in `manifest.json`, `xrpl_receipt.json`, or frontend API responses.

---

## 7. Command Line Interface (CLI)

```bash
# Check connectivity and testnet balance
python -m zzoa ledger status

# Bootstrap a dedicated testnet research account via faucet
python -m zzoa ledger bootstrap-account

# Anchor a frozen research run
python -m zzoa ledger anchor --run VELA-0017 --stage PREDICTION_FROZEN

# Verify an anchor against XRPL Testnet
python -m zzoa ledger verify --run VELA-0017 --stage PREDICTION_FROZEN

# Audit the complete chronological research chain
python -m zzoa ledger verify-chain --run VELA-0017
```

---

## 8. Testnet Reset Recovery

When an XRPL Testnet reset occurs:
- The local `xrpl_receipt.json` remains intact as a permanent local development record.
- Verification detects that the transaction hash is no longer present on the testnet ledger and returns `TESTNET_HISTORY_UNAVAILABLE` rather than `RUN_INTEGRITY_FAILURE` or `TAMPERING_DETECTED`.
- The run can be re-anchored to the new testnet using the exact same canonical run hash.
