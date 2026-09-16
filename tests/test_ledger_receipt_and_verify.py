"""Unit tests for receipt persistence, secret isolation, and anchor verification edge cases."""

import json
from unittest.mock import MagicMock
from xrpl.models.response import Response, ResponseStatus
from xrpl.utils import str_to_hex

from research.ledger.receipt import AnchorReceipt, save_receipt, get_receipt
from research.ledger.verify import verify_anchor
from research.ledger.canonicalize import (
    build_canonical_anchor_manifest,
    compute_anchor_payload_hash,
)


def create_synthetic_run_dir(tmp_path, run_id="VELA-TEST"):
    run_dir = tmp_path / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    manifest_data = {
        "run_id": run_id,
        "git_commit": "e84f2910",
        "manifest_sha256": "aaaa1111222233334444555566667777888899990000aaaa1111222233334444",
        "datasets": [{"dataset_id": "test_ds", "sha256": "112233"}],
        "outputs": {"density_peak": 1.45},
    }
    with open(run_dir / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)

    with open(run_dir / "config.yaml", "w", encoding="utf-8") as f:
        f.write("test_config: true\n")

    return run_dir


def test_secret_never_written_into_receipt(tmp_path):
    run_dir = create_synthetic_run_dir(tmp_path, "RUN_SEC")

    receipt = AnchorReceipt(
        run_id="RUN_SEC",
        stage="PREDICTION_FROZEN",
        manifest_sha256="1111",
        anchor_payload_sha256="2222",
        git_commit="abc",
        account="rClassicAddressOnly12345",
        tx_hash="TXHASH123456",
        ledger_index=1000,
        validated=True,
        transaction_result="tesSUCCESS",
        submitted_at="2026-09-15T00:00:00Z",
        validated_at="2026-09-15T00:00:05Z",
    )

    save_receipt(receipt, run_dir)

    receipt_file = run_dir / "xrpl_receipt.json"
    content = receipt_file.read_text(encoding="utf-8")

    # Assert no secret markers exist
    for forbidden in ["secret", "private_key", "seed", "sEd", "sno"]:
        assert f'"{forbidden}"' not in content.lower()


def test_missing_receipt_rejected(tmp_path):
    create_synthetic_run_dir(tmp_path, "RUN_NO_RCPT")

    res = verify_anchor(
        run_id="RUN_NO_RCPT",
        stage="PREDICTION_FROZEN",
        runs_root=tmp_path,
    )
    assert not res.is_valid()
    assert res.status == "MISSING_RECEIPT"
    assert "No XRPL receipt found" in res.errors[0]
    assert "✗ RUN INTEGRITY FAILURE" in res.audit_report


def test_frozen_run_cannot_mutate_after_anchoring(tmp_path):
    run_dir = create_synthetic_run_dir(tmp_path, "RUN_MUTATE_CHECK")

    payload = build_canonical_anchor_manifest(run_dir, stage="PREDICTION_FROZEN")
    payload_hash = compute_anchor_payload_hash(payload)

    receipt = AnchorReceipt(
        run_id="RUN_MUTATE_CHECK",
        stage="PREDICTION_FROZEN",
        manifest_sha256="aaaa",
        anchor_payload_sha256=payload_hash,
        git_commit="abc",
        account="rClassic",
        tx_hash="TX123",
        ledger_index=10,
        validated=True,
        transaction_result="tesSUCCESS",
        submitted_at="2026-09-15T00:00:00Z",
        validated_at="2026-09-15T00:00:05Z",
    )
    save_receipt(receipt, run_dir)

    # Now mutate manifest on disk
    with open(run_dir / "manifest.json", "w", encoding="utf-8") as f:
        json.dump({"run_id": "RUN_MUTATE_CHECK", "tampered": True}, f)

    res = verify_anchor(
        run_id="RUN_MUTATE_CHECK",
        stage="PREDICTION_FROZEN",
        runs_root=tmp_path,
    )

    assert not res.is_valid()
    assert res.checks["local_receipt_hash_matches"] is False
    assert any("mutated" in e for e in res.errors)


def test_unvalidated_transaction_rejected(tmp_path):
    run_dir = create_synthetic_run_dir(tmp_path, "RUN_UNVAL")
    payload = build_canonical_anchor_manifest(run_dir, stage="PREDICTION_FROZEN")
    anchor_hash = compute_anchor_payload_hash(payload)

    receipt = AnchorReceipt(
        run_id="RUN_UNVAL",
        stage="PREDICTION_FROZEN",
        manifest_sha256="aaaa",
        anchor_payload_sha256=anchor_hash,
        git_commit="abc",
        account="rClassic",
        tx_hash="TX_UNVAL",
        ledger_index=10,
        validated=True,
        transaction_result="tesSUCCESS",
        submitted_at="2026-09-15T00:00:00Z",
        validated_at="2026-09-15T00:00:05Z",
    )
    save_receipt(receipt, run_dir)

    mock_client = MagicMock()
    # Ledger returns validated = False
    mock_resp = Response(
        status=ResponseStatus.SUCCESS,
        result={
            "validated": False,
            "meta": {"TransactionResult": "tesSUCCESS"},
            "Memos": [{
                "Memo": {
                    "MemoType": str_to_hex("z-zoa/anchor"),
                    "MemoData": str_to_hex(json.dumps({"h": anchor_hash, "r": "RUN_UNVAL", "s": "PREDICTION_FROZEN"})),
                }
            }],
        },
    )
    mock_client.request.return_value = mock_resp

    res = verify_anchor(
        run_id="RUN_UNVAL",
        stage="PREDICTION_FROZEN",
        runs_root=tmp_path,
        client=mock_client,
    )
    assert not res.is_valid()
    assert res.checks["transaction_validated"] is False
    assert any("not yet validated" in e for e in res.errors)


def test_non_tesSUCCESS_transaction_rejected(tmp_path):
    run_dir = create_synthetic_run_dir(tmp_path, "RUN_FAILED_TX")
    payload = build_canonical_anchor_manifest(run_dir, stage="PREDICTION_FROZEN")
    anchor_hash = compute_anchor_payload_hash(payload)

    receipt = AnchorReceipt(
        run_id="RUN_FAILED_TX",
        stage="PREDICTION_FROZEN",
        manifest_sha256="aaaa",
        anchor_payload_sha256=anchor_hash,
        git_commit="abc",
        account="rClassic",
        tx_hash="TX_FAILED",
        ledger_index=10,
        validated=True,
        transaction_result="tesSUCCESS",
        submitted_at="2026-09-15T00:00:00Z",
        validated_at="2026-09-15T00:00:05Z",
    )
    save_receipt(receipt, run_dir)

    mock_client = MagicMock()
    mock_resp = Response(
        status=ResponseStatus.SUCCESS,
        result={
            "validated": True,
            "meta": {"TransactionResult": "tecINSUFFICIENT_FUNDS"},
            "Memos": [{
                "Memo": {
                    "MemoType": str_to_hex("z-zoa/anchor"),
                    "MemoData": str_to_hex(json.dumps({"h": anchor_hash, "r": "RUN_FAILED_TX", "s": "PREDICTION_FROZEN"})),
                }
            }],
        },
    )
    mock_client.request.return_value = mock_resp

    res = verify_anchor(
        run_id="RUN_FAILED_TX",
        stage="PREDICTION_FROZEN",
        runs_root=tmp_path,
        client=mock_client,
    )
    assert not res.is_valid()
    assert res.checks["transaction_result_success"] is False
    assert any("tecINSUFFICIENT_FUNDS" in e for e in res.errors)


def test_wrong_memo_hash_rejected(tmp_path):
    run_dir = create_synthetic_run_dir(tmp_path, "RUN_WRONG_HASH")
    payload = build_canonical_anchor_manifest(run_dir, stage="PREDICTION_FROZEN")
    anchor_hash = compute_anchor_payload_hash(payload)

    receipt = AnchorReceipt(
        run_id="RUN_WRONG_HASH",
        stage="PREDICTION_FROZEN",
        manifest_sha256="aaaa",
        anchor_payload_sha256=anchor_hash,
        git_commit="abc",
        account="rClassic",
        tx_hash="TX_WRONG_HASH",
        ledger_index=10,
        validated=True,
        transaction_result="tesSUCCESS",
        submitted_at="2026-09-15T00:00:00Z",
        validated_at="2026-09-15T00:00:05Z",
    )
    save_receipt(receipt, run_dir)

    mock_client = MagicMock()
    # Ledger memo has completely different hash
    mock_resp = Response(
        status=ResponseStatus.SUCCESS,
        result={
            "validated": True,
            "meta": {"TransactionResult": "tesSUCCESS"},
            "Memos": [{
                "Memo": {
                    "MemoType": str_to_hex("z-zoa/anchor"),
                    "MemoData": str_to_hex(json.dumps({"h": "deadbeef" * 8, "r": "RUN_WRONG_HASH", "s": "PREDICTION_FROZEN"})),
                }
            }],
        },
    )
    mock_client.request.return_value = mock_resp

    res = verify_anchor(
        run_id="RUN_WRONG_HASH",
        stage="PREDICTION_FROZEN",
        runs_root=tmp_path,
        client=mock_client,
    )
    assert not res.is_valid()
    assert res.checks["local_hash_matches_ledger"] is False
    assert any("mismatch" in e.lower() for e in res.errors)


def test_wrong_previous_transaction_rejected(tmp_path):
    run_dir = create_synthetic_run_dir(tmp_path, "RUN_WRONG_PREV")
    payload = build_canonical_anchor_manifest(run_dir, stage="PREDICTION_FROZEN", previous_tx_hash="PREV_TX_AAA")
    anchor_hash = compute_anchor_payload_hash(payload)

    receipt = AnchorReceipt(
        run_id="RUN_WRONG_PREV",
        stage="PREDICTION_FROZEN",
        manifest_sha256="aaaa",
        anchor_payload_sha256=anchor_hash,
        git_commit="abc",
        account="rClassic",
        tx_hash="TX_CURRENT",
        ledger_index=10,
        validated=True,
        transaction_result="tesSUCCESS",
        previous_tx_hash="PREV_TX_AAA",
        submitted_at="2026-09-15T00:00:00Z",
        validated_at="2026-09-15T00:00:05Z",
    )
    save_receipt(receipt, run_dir)

    mock_client = MagicMock()
    # Ledger memo has wrong previous transaction link
    mock_resp = Response(
        status=ResponseStatus.SUCCESS,
        result={
            "validated": True,
            "meta": {"TransactionResult": "tesSUCCESS"},
            "Memos": [{
                "Memo": {
                    "MemoType": str_to_hex("z-zoa/anchor"),
                    "MemoData": str_to_hex(json.dumps({
                        "h": anchor_hash,
                        "r": "RUN_WRONG_PREV",
                        "s": "PREDICTION_FROZEN",
                        "prev": "WRONG_PREV_BBB"
                    })),
                }
            }],
        },
    )
    mock_client.request.return_value = mock_resp

    res = verify_anchor(
        run_id="RUN_WRONG_PREV",
        stage="PREDICTION_FROZEN",
        runs_root=tmp_path,
        client=mock_client,
    )
    assert not res.is_valid()
    assert res.checks["previous_anchor_verified"] is False
    assert any("Previous transaction link mismatch" in e for e in res.errors)


def test_testnet_history_unavailable_handled_separately_from_mismatch(tmp_path):
    run_dir = create_synthetic_run_dir(tmp_path, "RUN_RESET")
    payload = build_canonical_anchor_manifest(run_dir, stage="PREDICTION_FROZEN")
    anchor_hash = compute_anchor_payload_hash(payload)

    receipt = AnchorReceipt(
        run_id="RUN_RESET",
        stage="PREDICTION_FROZEN",
        manifest_sha256="aaaa",
        anchor_payload_sha256=anchor_hash,
        git_commit="abc",
        account="rClassic",
        tx_hash="TX_RESET",
        ledger_index=10,
        validated=True,
        transaction_result="tesSUCCESS",
        submitted_at="2026-09-15T00:00:00Z",
        validated_at="2026-09-15T00:00:05Z",
    )
    save_receipt(receipt, run_dir)

    mock_client = MagicMock()
    # Testnet reset / txnNotFound error
    mock_resp = Response(
        status=ResponseStatus.ERROR,
        result={
            "error": "txnNotFound",
            "error_code": 29,
            "error_message": "Transaction not found.",
        },
    )
    mock_client.request.return_value = mock_resp

    res = verify_anchor(
        run_id="RUN_RESET",
        stage="PREDICTION_FROZEN",
        runs_root=tmp_path,
        client=mock_client,
    )
    # MUST NOT be categorized as tampering or RUN_INTEGRITY_FAILURE
    assert res.status == "TESTNET_HISTORY_UNAVAILABLE"
    assert "TESTNET_HISTORY_UNAVAILABLE" in res.audit_report
    assert "TAMPERING" not in res.audit_report
