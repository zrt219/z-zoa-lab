"""Tests for XRPL anchor enforcement on holdout reveal and validation access."""

import json
from unittest.mock import MagicMock
import pytest
from xrpl.models.response import Response, ResponseStatus
from xrpl.utils import str_to_hex

from research.catalogs.registry import CatalogRegistry
from research.holdouts.guard import DataGateway, ExecutionContext, ExecutionMode, reveal_holdout
from research.holdouts.exceptions import (
    HoldoutLeakageViolationError,
    AnchorVerificationHoldoutViolationError,
)
from research.ledger.receipt import AnchorReceipt, save_receipt
from research.ledger.canonicalize import (
    build_canonical_anchor_manifest,
    compute_anchor_payload_hash,
)


@pytest.fixture
def setup_run_and_registry(tmp_path):
    reg = CatalogRegistry("datasets/manifests/catalog_registry.json")
    runs_dir = tmp_path / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)

    run_id = "VELA_ANCHOR_EXP"
    run_dir = runs_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    token = "97b6a941e7f9185a539a9fcf7ff4fa65b058c6792372d6ca0cb646f88219abf2"
    manifest_data = {
        "run_id": run_id,
        "git_commit": "df3536e",
        "manifest_sha256": token,
        "datasets": [{"dataset_id": "cf4_sample"}],
        "outputs": {"status": "frozen"},
    }
    with open(run_dir / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)

    with open(run_dir / "config.yaml", "w", encoding="utf-8") as f:
        f.write("test: true\n")

    gateway = DataGateway(reg, base_dir=".")

    return {
        "reg": reg,
        "gateway": gateway,
        "runs_dir": runs_dir,
        "run_dir": run_dir,
        "run_id": run_id,
        "token": token,
    }


def test_holdout_denied_without_anchor_receipt(setup_run_and_registry):
    ctx_info = setup_run_and_registry
    gateway = ctx_info["gateway"]
    run_id = ctx_info["run_id"]
    token = ctx_info["token"]
    runs_dir = ctx_info["runs_dir"]

    # require_freeze_anchor=True without any receipt on disk
    ctx = ExecutionContext(
        run_id=run_id,
        mode=ExecutionMode.VALIDATION,
        freeze_token=token,
        require_freeze_anchor=True,
        runs_root=str(runs_dir),
    )

    with pytest.raises(AnchorVerificationHoldoutViolationError, match="Missing XRPL PREDICTION_FROZEN receipt"):
        gateway.request_dataset("vela_smgps_sample", ctx)


def test_holdout_denied_when_anchor_unvalidated(setup_run_and_registry):
    ctx_info = setup_run_and_registry
    gateway = ctx_info["gateway"]
    run_id = ctx_info["run_id"]
    token = ctx_info["token"]
    run_dir = ctx_info["run_dir"]
    runs_dir = ctx_info["runs_dir"]

    payload = build_canonical_anchor_manifest(run_dir, stage="PREDICTION_FROZEN")
    anchor_hash = compute_anchor_payload_hash(payload)

    # Receipt exists but validated=False
    receipt = AnchorReceipt(
        run_id=run_id,
        stage="PREDICTION_FROZEN",
        manifest_sha256=token,
        anchor_payload_sha256=anchor_hash,
        git_commit="df3536e",
        account="rClassicAddress",
        tx_hash="TX_PENDING",
        ledger_index=0,
        validated=False,
        transaction_result="tesSUCCESS",
        submitted_at="2026-09-15T00:00:00Z",
        validated_at="2026-09-15T00:00:05Z",
    )
    save_receipt(receipt, run_dir)

    ctx = ExecutionContext(
        run_id=run_id,
        mode=ExecutionMode.VALIDATION,
        freeze_token=token,
        require_freeze_anchor=True,
        runs_root=str(runs_dir),
    )

    with pytest.raises(AnchorVerificationHoldoutViolationError, match="not marked validated"):
        gateway.request_dataset("vela_smgps_sample", ctx)


def test_holdout_denied_when_anchor_result_failed(setup_run_and_registry):
    ctx_info = setup_run_and_registry
    gateway = ctx_info["gateway"]
    run_id = ctx_info["run_id"]
    token = ctx_info["token"]
    run_dir = ctx_info["run_dir"]
    runs_dir = ctx_info["runs_dir"]

    payload = build_canonical_anchor_manifest(run_dir, stage="PREDICTION_FROZEN")
    anchor_hash = compute_anchor_payload_hash(payload)

    # Receipt exists and validated=True, but result is tecINSUFFICIENT_FUNDS
    receipt = AnchorReceipt(
        run_id=run_id,
        stage="PREDICTION_FROZEN",
        manifest_sha256=token,
        anchor_payload_sha256=anchor_hash,
        git_commit="df3536e",
        account="rClassicAddress",
        tx_hash="TX_FAILED",
        ledger_index=123,
        validated=True,
        transaction_result="tecINSUFFICIENT_FUNDS",
        submitted_at="2026-09-15T00:00:00Z",
        validated_at="2026-09-15T00:00:05Z",
    )
    save_receipt(receipt, run_dir)

    ctx = ExecutionContext(
        run_id=run_id,
        mode=ExecutionMode.VALIDATION,
        freeze_token=token,
        require_freeze_anchor=True,
        runs_root=str(runs_dir),
    )

    with pytest.raises(AnchorVerificationHoldoutViolationError, match="expected 'tesSUCCESS'"):
        gateway.request_dataset("vela_smgps_sample", ctx)


def test_holdout_denied_when_memo_hash_mismatches(setup_run_and_registry):
    ctx_info = setup_run_and_registry
    gateway = ctx_info["gateway"]
    run_id = ctx_info["run_id"]
    token = ctx_info["token"]
    run_dir = ctx_info["run_dir"]
    runs_dir = ctx_info["runs_dir"]

    # Receipt has forged hash
    receipt = AnchorReceipt(
        run_id=run_id,
        stage="PREDICTION_FROZEN",
        manifest_sha256=token,
        anchor_payload_sha256="wrong_anchor_hash_0000000000000000000000000000000000000000000000",
        git_commit="df3536e",
        account="rClassicAddress",
        tx_hash="TX_HASH_BAD",
        ledger_index=123,
        validated=True,
        transaction_result="tesSUCCESS",
        submitted_at="2026-09-15T00:00:00Z",
        validated_at="2026-09-15T00:00:05Z",
    )
    save_receipt(receipt, run_dir)

    ctx = ExecutionContext(
        run_id=run_id,
        mode=ExecutionMode.VALIDATION,
        freeze_token=token,
        require_freeze_anchor=True,
        runs_root=str(runs_dir),
    )

    with pytest.raises(AnchorVerificationHoldoutViolationError, match="does not match local canonical hash"):
        gateway.request_dataset("vela_smgps_sample", ctx)


def test_holdout_allowed_when_anchor_fully_verified(setup_run_and_registry):
    ctx_info = setup_run_and_registry
    gateway = ctx_info["gateway"]
    run_id = ctx_info["run_id"]
    token = ctx_info["token"]
    run_dir = ctx_info["run_dir"]
    runs_dir = ctx_info["runs_dir"]

    payload = build_canonical_anchor_manifest(run_dir, stage="PREDICTION_FROZEN")
    anchor_hash = compute_anchor_payload_hash(payload)

    receipt = AnchorReceipt(
        run_id=run_id,
        stage="PREDICTION_FROZEN",
        manifest_sha256=token,
        anchor_payload_sha256=anchor_hash,
        git_commit="df3536e",
        account="rClassicAddress",
        tx_hash="TX_PERFECT",
        ledger_index=12345,
        validated=True,
        transaction_result="tesSUCCESS",
        submitted_at="2026-09-15T00:00:00Z",
        validated_at="2026-09-15T00:00:05Z",
    )
    save_receipt(receipt, run_dir)

    ctx = ExecutionContext(
        run_id=run_id,
        mode=ExecutionMode.VALIDATION,
        freeze_token=token,
        require_freeze_anchor=True,
        runs_root=str(runs_dir),
    )

    df = gateway.request_dataset("vela_smgps_sample", ctx)
    assert df.height == 4


def test_reveal_holdout_function_enforces_live_ledger_check(setup_run_and_registry):
    ctx_info = setup_run_and_registry
    gateway = ctx_info["gateway"]
    run_id = ctx_info["run_id"]
    token = ctx_info["token"]
    run_dir = ctx_info["run_dir"]
    runs_dir = ctx_info["runs_dir"]

    payload = build_canonical_anchor_manifest(run_dir, stage="PREDICTION_FROZEN")
    anchor_hash = compute_anchor_payload_hash(payload)

    receipt = AnchorReceipt(
        run_id=run_id,
        stage="PREDICTION_FROZEN",
        manifest_sha256=token,
        anchor_payload_sha256=anchor_hash,
        git_commit="df3536e",
        account="rClassicAddress",
        tx_hash="TX_REVEAL_TEST",
        ledger_index=12345,
        validated=True,
        transaction_result="tesSUCCESS",
        submitted_at="2026-09-15T00:00:00Z",
        validated_at="2026-09-15T00:00:05Z",
    )
    save_receipt(receipt, run_dir)

    # 1. Fail path: mock client returns transaction not validated
    mock_client = MagicMock()
    mock_client.request.return_value = Response(
        status=ResponseStatus.SUCCESS,
        result={"validated": False, "meta": {"TransactionResult": "tesSUCCESS"}},
    )

    with pytest.raises(AnchorVerificationHoldoutViolationError, match="PREDICTION_FROZEN anchor validation failed"):
        reveal_holdout(
            run_id=run_id,
            dataset_id="vela_smgps_sample",
            gateway=gateway,
            runs_root=runs_dir,
            client=mock_client,
            require_freeze_anchor=True,
        )

    # 2. Success path: mock client returns validated tesSUCCESS with matching memo
    mock_client.request.return_value = Response(
        status=ResponseStatus.SUCCESS,
        result={
            "validated": True,
            "meta": {"TransactionResult": "tesSUCCESS", "ledger_index": 12345},
            "ledger_index": 12345,
            "Memos": [{
                "Memo": {
                    "MemoType": str_to_hex("z-zoa/anchor"),
                    "MemoData": str_to_hex(json.dumps({
                        "p": "Z-ZOA",
                        "r": run_id,
                        "s": "PREDICTION_FROZEN",
                        "h": anchor_hash,
                        "prev": ""
                    })),
                }
            }],
        },
    )

    df = reveal_holdout(
        run_id=run_id,
        dataset_id="vela_smgps_sample",
        gateway=gateway,
        runs_root=runs_dir,
        client=mock_client,
        require_freeze_anchor=True,
    )
    assert df.height == 4
