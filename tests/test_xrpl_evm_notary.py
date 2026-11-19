"""Tests for XRPL EVM Sidechain integration, ResearchNotary contract, and dual-anchoring."""

import json
from pathlib import Path
import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from backend.main import app
from research.ledger import (
    AnchorReceipt,
    DualAnchorReceipt,
    save_receipt,
    get_receipt,
    get_dual_receipt,
    verify_anchor,
    get_evm_client,
    check_evm_connectivity,
    XRPL_EVM_CHAIN_ID,
    DEFAULT_CONTRACT_ADDRESS,
)
from research.ledger.evm_client import MockEVMState, EVMClient
from xrpl.models.response import Response, ResponseStatus
from xrpl.utils import str_to_hex


def create_test_run(tmp_path: Path, run_id: str = "VELA-EVM-TEST") -> Path:
    run_dir = tmp_path / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "run_id": run_id,
        "git_commit": "e84f2910",
        "manifest_sha256": "aaaa1111222233334444555566667777888899990000aaaa1111222233334444",
        "datasets": [{"dataset_id": "test_ds", "sha256": "112233"}],
        "outputs": {"density_peak": 1.45},
    }
    with open(run_dir / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    with open(run_dir / "config.yaml", "w", encoding="utf-8") as f:
        f.write("test_config: true\n")

    return run_dir


def test_evm_client_connectivity_and_constants():
    """Verify EVM client constants and offline/CI connectivity fallback."""
    client = get_evm_client()
    assert client.chain_id == 1440002
    assert client.contract_address == DEFAULT_CONTRACT_ADDRESS

    conn = client.check_connectivity()
    assert "network" in conn
    assert conn["chain_id"] in (1440000, 1440002)
    assert conn["contract_address"] == DEFAULT_CONTRACT_ADDRESS


def test_research_notary_abi_file_validity():
    """Verify that contracts/ResearchNotary.json exists and contains correct ABI."""
    base_dir = Path(__file__).resolve().parent.parent
    abi_file = base_dir / "contracts" / "ResearchNotary.json"
    assert abi_file.exists(), "ResearchNotary.json should exist"

    with open(abi_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["contractName"] == "ResearchNotary"
    assert data["chainId"] == 1440002
    assert "abi" in data
    fn_names = [item["name"] for item in data["abi"] if item.get("type") == "function"]
    assert "anchorStage" in fn_names
    assert "getStage" in fn_names
    assert "isStageAnchored" in fn_names
    assert "verifyPayloadHash" in fn_names
    assert "getRunLatestStage" in fn_names


def test_mock_evm_sequential_stage_progression():
    """Verify sequential stage validation and immutability in EVM state engine."""
    evm = MockEVMState()
    run_id = "RUN_SEQ_001"
    hash0 = "0x" + "a" * 64
    hash1 = "0x" + "b" * 64

    # 1. Out of order stage should fail
    with pytest.raises(ValueError, match="Invalid stage progression"):
        evm.anchor(run_id, "PREDICTION_FROZEN", hash1)

    # 2. Stage 0 succeeds
    rec0 = evm.anchor(run_id, "TRAIN_START", hash0)
    assert rec0["stage"] == "TRAIN_START"
    assert rec0["chain_id"] == 1440002
    assert evm.is_anchored(run_id, "TRAIN_START")

    # 3. Stage 1 now succeeds
    rec1 = evm.anchor(run_id, "PREDICTION_FROZEN", hash1, previous_hash=rec0["tx_hash"])
    assert rec1["stage"] == "PREDICTION_FROZEN"
    assert evm.is_anchored(run_id, "PREDICTION_FROZEN")

    # 4. Tampering: Re-anchoring same stage with conflicting hash fails
    tamper_hash = "0x" + "f" * 64
    with pytest.raises(ValueError, match="already anchored with differing hash"):
        evm.anchor(run_id, "PREDICTION_FROZEN", tamper_hash)

    # 5. Idempotent re-anchoring with identical hash succeeds
    rec1_repeat = evm.anchor(run_id, "PREDICTION_FROZEN", hash1)
    assert rec1_repeat["tx_hash"] == rec1["tx_hash"]

    # 6. Verify hash query
    assert evm.verify_hash(run_id, "PREDICTION_FROZEN", hash1)
    assert not evm.verify_hash(run_id, "PREDICTION_FROZEN", tamper_hash)


def test_dual_ledger_receipt_storage_and_retrieval(tmp_path):
    """Verify dual-ledger receipt storage and structure in anchor_receipts.json."""
    run_dir = create_test_run(tmp_path, "RUN_DUAL_RCPT")

    receipt = AnchorReceipt(
        run_id="RUN_DUAL_RCPT",
        stage="PREDICTION_FROZEN",
        manifest_sha256="1111222233334444555566667777888899990000aaaa11112222333344445555",
        anchor_payload_sha256="222233334444555566667777888899990000aaaa111122223333444455556666",
        git_commit="e84f2910",
        account="rClassic12345",
        tx_hash="TX_NATIVE_12345",
        ledger_index=849201,
        validated=True,
        transaction_result="tesSUCCESS",
        submitted_at="2026-10-20T00:00:00Z",
        validated_at="2026-10-20T00:00:04Z",
        xrpl_native={
            "network": "XRPL Testnet",
            "network_id": 1,
            "tx_hash": "TX_NATIVE_12345",
            "ledger_index": 849201,
            "account": "rClassic12345",
            "validated": True,
            "transaction_result": "tesSUCCESS",
        },
        xrpl_evm={
            "network": "XRPL EVM Sidechain Testnet",
            "chain_id": 1440002,
            "contract_address": DEFAULT_CONTRACT_ADDRESS,
            "tx_hash": "0x" + "e" * 64,
            "block_number": 1442005,
            "notarizer": "rClassic12345",
            "status": 1,
        },
    )

    save_receipt(receipt, run_dir)

    # Assert both xrpl_receipt.json and anchor_receipts.json exist
    assert (run_dir / "xrpl_receipt.json").exists()
    assert (run_dir / "anchor_receipts.json").exists()

    # Load dual receipt
    dual_rcpt = get_dual_receipt("RUN_DUAL_RCPT", runs_root=tmp_path)
    assert dual_rcpt is not None
    assert "xrpl_native" in dual_rcpt
    assert "xrpl_evm" in dual_rcpt
    assert dual_rcpt["xrpl_native"]["tx_hash"] == "TX_NATIVE_12345"
    assert dual_rcpt["xrpl_evm"]["chain_id"] == 1440002
    assert dual_rcpt["xrpl_evm"]["contract_address"] == DEFAULT_CONTRACT_ADDRESS


def test_dual_anchoring_verification(tmp_path):
    """Test full verify_anchor flow with both Layer 1 and EVM Sidechain checks."""
    run_id = "RUN_VERIFY_EVM"
    run_dir = create_test_run(tmp_path, run_id)

    from research.ledger.canonicalize import build_canonical_anchor_manifest, compute_anchor_payload_hash

    payload = build_canonical_anchor_manifest(run_dir, stage="PREDICTION_FROZEN")
    local_hash = compute_anchor_payload_hash(payload)

    # Anchor to EVM mock state first
    evm_c = get_evm_client()
    # Ensure stage 0 exists
    evm_c.anchor_stage(run_id, "TRAIN_START", "0x" + "0" * 64)
    evm_rec = evm_c.anchor_stage(run_id, "PREDICTION_FROZEN", local_hash)

    # Create and save receipt
    receipt = AnchorReceipt(
        run_id=run_id,
        stage="PREDICTION_FROZEN",
        manifest_sha256=payload.get("manifest_sha256", ""),
        anchor_payload_sha256=local_hash,
        git_commit="e84f2910",
        account="rClassicAddress",
        tx_hash="AABBCC112233",
        ledger_index=900,
        validated=True,
        transaction_result="tesSUCCESS",
        submitted_at="2026-10-20T00:00:00Z",
        validated_at="2026-10-20T00:00:04Z",
        xrpl_evm=evm_rec,
    )
    save_receipt(receipt, run_dir)

    # Mock XRPL Layer 1 client
    memo_dict = {"p": "Z-ZOA", "r": run_id, "s": "PREDICTION_FROZEN", "h": local_hash, "prev": ""}
    memo_json = json.dumps(memo_dict, separators=(",", ":"))

    mock_l1 = MagicMock()
    mock_l1.request.return_value = Response(
        status=ResponseStatus.SUCCESS,
        result={
            "validated": True,
            "ledger_index": 900,
            "meta": {"TransactionResult": "tesSUCCESS"},
            "Memos": [
                {
                    "Memo": {
                        "MemoType": str_to_hex("z-zoa/anchor"),
                        "MemoFormat": str_to_hex("json"),
                        "MemoData": str_to_hex(memo_json),
                    }
                }
            ],
        },
    )

    res = verify_anchor(run_id, "PREDICTION_FROZEN", runs_root=tmp_path, client=mock_l1, evm_client=evm_c)

    assert res.is_valid()
    assert res.status == "VALIDATED_SUCCESS"
    assert res.dual_anchored is True
    assert res.evm_verified is True
    assert "✓ XRPL EVM CONTRACT VERIFIED" in res.audit_report


def test_backend_evm_api_endpoints():
    """Test FastAPI ledger endpoints for EVM status, contract, and stage verification."""
    client = TestClient(app)

    # 1. /ledger/status includes EVM info
    resp = client.get("/ledger/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "evm_connectivity" in data
    assert data["evm_chain_id"] == 1440002
    assert "evm_contract_address" in data

    # 2. /ledger/evm/status
    resp_evm = client.get("/ledger/evm/status")
    assert resp_evm.status_code == 200
    evm_data = resp_evm.json()
    assert evm_data["chain_id"] in (1440000, 1440002)

    # 3. /ledger/evm/contract
    resp_c = client.get("/ledger/evm/contract")
    assert resp_c.status_code == 200
    c_data = resp_c.json()
    assert c_data["contractName"] == "ResearchNotary"
    assert c_data["chainId"] == 1440002

    # 4. /ledger/evm/verify-stage
    resp_v = client.post(
        "/ledger/evm/verify-stage",
        json={"run_id": "VELA-API-TEST", "stage": "PREDICTION_FROZEN", "payload_hash": "0x1234"},
    )
    assert resp_v.status_code == 200
    v_data = resp_v.json()
    assert "verified" in v_data
    assert v_data["chain_id"] == 1440002


def test_freeze_manifest_canonicalize_and_anchor(tmp_path):
    """Verify that runs with freeze_manifest.json (e.g. VELA-001) can be canonicalized and anchored."""
    from research.ledger import anchor_run
    from unittest.mock import patch

    run_id = "VELA-FREEZE-TEST"
    run_dir = tmp_path / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    freeze_data = {
        "manifest_type": "Z-ZOA_PREDICTION_FREEZE_MANIFEST",
        "run_id": run_id,
        "frozen_at_utc": "2026-10-20T00:00:00Z",
        "git_commit": "df3536ec918a",
        "train_clean_catalog_path": "datasets/processed/TRAIN_CLEAN/train_clean_combined.parquet",
        "train_clean_catalog_sha256": "57f13296510e2c1fc7a2262981dcab7a90b006e5cabfd8100272a4c965d2edf6",
        "file_hashes": {
            "prediction_mean.npy": "1db50f1ea922a439b52d895e2b44cf36e150763f79b80c756753a0c264729995"
        },
        "manifest_seal_sha256": "2514714ce4522b3e4d817f72610a63ad2a8334d109dfbfb5ef4ddc85fa94b9a2",
    }
    with open(run_dir / "freeze_manifest.json", "w", encoding="utf-8") as f:
        json.dump(freeze_data, f, indent=2)

    mock_res = MagicMock()
    mock_res.result = {
        "validated": True,
        "ledger_index": 12345,
        "meta": {"TransactionResult": "tesSUCCESS"},
        "hash": "TX_FREEZE_123",
    }
    mock_wallet = MagicMock()
    mock_wallet.classic_address = "rTestFreezeClassic"
    mock_client = MagicMock()

    with patch("research.ledger.anchor.submit_and_wait", return_value=mock_res):
        rcpt = anchor_run(
            run_id=run_id,
            stage="PREDICTION_FROZEN",
            runs_root=tmp_path,
            client=mock_client,
            wallet=mock_wallet,
        )

    assert rcpt.run_id == run_id
    assert rcpt.stage == "PREDICTION_FROZEN"
    assert rcpt.xrpl_evm is not None
    assert rcpt.xrpl_evm["chain_id"] == 1440002
    assert (run_dir / "anchor_receipts.json").exists()


def test_native_only_receipt_does_not_falsely_fail_evm(tmp_path):
    """Verify that a native-only receipt (xrpl_evm=None) is verified without false EVM mismatch errors."""
    run_dir = create_test_run(tmp_path, "RUN_NATIVE_ONLY")
    from research.ledger.canonicalize import build_canonical_anchor_manifest, compute_anchor_payload_hash

    payload = build_canonical_anchor_manifest(run_dir, stage="PREDICTION_FROZEN")
    local_hash = compute_anchor_payload_hash(payload)

    receipt = AnchorReceipt(
        run_id="RUN_NATIVE_ONLY",
        stage="PREDICTION_FROZEN",
        manifest_sha256=payload.get("manifest_sha256", ""),
        anchor_payload_sha256=local_hash,
        git_commit="e84f2910",
        account="rClassicAddress",
        tx_hash="TX_NATIVE_ONLY_123",
        ledger_index=555,
        validated=True,
        transaction_result="tesSUCCESS",
        submitted_at="2026-10-20T00:00:00Z",
        validated_at="2026-10-20T00:00:04Z",
        xrpl_evm=None,
    )
    save_receipt(receipt, run_dir)

    mock_l1 = MagicMock()
    mock_l1.request.return_value = Response(
        status=ResponseStatus.SUCCESS,
        result={
            "validated": True,
            "ledger_index": 555,
            "meta": {"TransactionResult": "tesSUCCESS"},
            "Memos": [
                {
                    "Memo": {
                        "MemoType": str_to_hex("z-zoa/anchor"),
                        "MemoFormat": str_to_hex("json"),
                        "MemoData": str_to_hex(
                            json.dumps({"p": "Z-ZOA", "r": "RUN_NATIVE_ONLY", "s": "PREDICTION_FROZEN", "h": local_hash, "prev": ""})
                        ),
                    }
                }
            ],
        },
    )

    res = verify_anchor("RUN_NATIVE_ONLY", "PREDICTION_FROZEN", runs_root=tmp_path, client=mock_l1)
    assert res.is_valid()
    assert res.dual_anchored is False
    assert res.evm_verified is None
    assert not any("EVM" in err for err in res.errors)


def test_mock_evm_disk_hydration(tmp_path):
    """Verify that a fresh MockEVMState instance hydrates from saved anchor_receipts.json."""
    run_dir = create_test_run(tmp_path, "RUN_HYDRATE_TEST")
    hash_val = "0x" + "c" * 64
    dual_data = {
        "project": "Z-ZOA",
        "run_id": "RUN_HYDRATE_TEST",
        "stage": "PREDICTION_FROZEN",
        "manifest_sha256": "1111",
        "anchor_payload_sha256": hash_val,
        "git_commit": "e84f2910",
        "xrpl_native": {"tx_hash": "TX1"},
        "xrpl_evm": {
            "network": "XRPL EVM Sidechain Testnet",
            "chain_id": 1440002,
            "contract_address": DEFAULT_CONTRACT_ADDRESS,
            "payload_hash": hash_val,
            "tx_hash": "0x" + "d" * 64,
            "block_number": 1442099,
        },
        "submitted_at": "2026-10-20T00:00:00Z",
        "validated_at": "2026-10-20T00:00:05Z",
    }
    with open(run_dir / "anchor_receipts.json", "w", encoding="utf-8") as f:
        json.dump(dual_data, f, indent=2)

    fresh_evm = MockEVMState()
    # Initially not in memory
    assert "RUN_HYDRATE_TEST" not in fresh_evm._runs

    # Hydrates on demand
    rec = fresh_evm.get_stage("RUN_HYDRATE_TEST", "PREDICTION_FROZEN", runs_root=tmp_path)
    assert rec is not None
    assert rec["payload_hash"] == hash_val
    assert fresh_evm.verify_hash("RUN_HYDRATE_TEST", "PREDICTION_FROZEN", hash_val, runs_root=tmp_path)


def test_evm_tamper_rejection_in_verify_anchor(tmp_path):
    """Verify that if EVM on-chain/mock state does not match payload hash, verification fails."""
    run_id = "RUN_TAMPER_EVM"
    run_dir = create_test_run(tmp_path, run_id)
    from research.ledger.canonicalize import build_canonical_anchor_manifest, compute_anchor_payload_hash

    payload = build_canonical_anchor_manifest(run_dir, stage="PREDICTION_FROZEN")
    local_hash = compute_anchor_payload_hash(payload)

    # In EVM client, anchor a conflicting/tampered payload hash
    evm_c = get_evm_client()
    evm_c.anchor_stage(run_id, "TRAIN_START", "0x" + "0" * 64)
    tampered_hash = "0x" + "f" * 64
    evm_rec = evm_c.anchor_stage(run_id, "PREDICTION_FROZEN", tampered_hash)

    # Save a receipt that claims dual anchoring
    receipt = AnchorReceipt(
        run_id=run_id,
        stage="PREDICTION_FROZEN",
        manifest_sha256=payload.get("manifest_sha256", ""),
        anchor_payload_sha256=local_hash,
        git_commit="e84f2910",
        account="rClassicAddress",
        tx_hash="TX_L1_VALID_123",
        ledger_index=950,
        validated=True,
        transaction_result="tesSUCCESS",
        submitted_at="2026-10-20T00:00:00Z",
        validated_at="2026-10-20T00:00:04Z",
        xrpl_evm=evm_rec,
    )
    save_receipt(receipt, run_dir)

    # Mock L1 response as valid
    memo_dict = {"p": "Z-ZOA", "r": run_id, "s": "PREDICTION_FROZEN", "h": local_hash, "prev": ""}
    memo_json = json.dumps(memo_dict, separators=(",", ":"))
    mock_l1 = MagicMock()
    mock_l1.request.return_value = Response(
        status=ResponseStatus.SUCCESS,
        result={
            "validated": True,
            "ledger_index": 950,
            "meta": {"TransactionResult": "tesSUCCESS"},
            "Memos": [
                {
                    "Memo": {
                        "MemoType": str_to_hex("z-zoa/anchor"),
                        "MemoFormat": str_to_hex("json"),
                        "MemoData": str_to_hex(memo_json),
                    }
                }
            ],
        },
    )

    res = verify_anchor(run_id, "PREDICTION_FROZEN", runs_root=tmp_path, client=mock_l1, evm_client=evm_c)

    # Must fail because EVM contract state has differing hash!
    assert not res.is_valid()
    assert res.status == "RUN_INTEGRITY_FAILURE"
    assert res.dual_anchored is True
    assert res.evm_verified is False
    assert any("XRPL EVM Sidechain contract" in err for err in res.errors)


def test_evm_latest_stage_query_and_api(tmp_path):
    """Test get_run_latest_stage on MockEVMState, EVMClient, and FastAPI route."""
    evm = MockEVMState()
    run_id = "RUN_LATEST_STAGE_TEST"

    # 1. Unanchored run returns -1
    assert evm.get_run_latest_stage(run_id) == -1

    # 2. After stage 0 (TRAIN_START) anchored, returns 0
    evm.anchor(run_id, "TRAIN_START", "0x" + "1" * 64)
    assert evm.get_run_latest_stage(run_id) == 0

    # 3. After stage 1 (PREDICTION_FROZEN) anchored, returns 1
    evm.anchor(run_id, "PREDICTION_FROZEN", "0x" + "2" * 64)
    assert evm.get_run_latest_stage(run_id) == 1

    # 4. EVMClient get_run_latest_stage matches
    client = get_evm_client()
    client.mock_state = evm
    assert client.get_run_latest_stage(run_id) == 1

    # 5. API endpoint /ledger/evm/latest-stage/{run_id}
    api_client = TestClient(app)
    resp = api_client.get(f"/ledger/evm/latest-stage/{run_id}")
    assert resp.status_code == 200
    d = resp.json()
    assert d["run_id"] == run_id
    assert "latest_stage_index" in d
    assert d["chain_id"] == 1440002


def test_anchor_run_with_anchor_evm_false(tmp_path):
    """Verify that setting anchor_evm=False bypasses EVM anchoring cleanly."""
    from research.ledger import anchor_run
    from unittest.mock import patch

    run_id = "RUN_NO_EVM_TEST"
    run_dir = create_test_run(tmp_path, run_id)

    mock_res = MagicMock()
    mock_res.result = {
        "validated": True,
        "ledger_index": 777,
        "meta": {"TransactionResult": "tesSUCCESS"},
        "hash": "TX_NO_EVM",
    }
    mock_wallet = MagicMock()
    mock_wallet.classic_address = "rNoEvmAddress"
    mock_client = MagicMock()

    with patch("research.ledger.anchor.submit_and_wait", return_value=mock_res):
        rcpt = anchor_run(
            run_id=run_id,
            stage="PREDICTION_FROZEN",
            runs_root=tmp_path,
            client=mock_client,
            wallet=mock_wallet,
            anchor_evm=False,
        )

    assert rcpt.run_id == run_id
    assert rcpt.xrpl_evm is None
    assert (run_dir / "xrpl_receipt.json").exists()


def test_verify_chain_with_evm_sidechain(tmp_path):
    """Test verify_chain across both XRPL L1 and EVM Sidechain."""
    from research.ledger import verify_chain

    run_id = "RUN_CHAIN_EVM"
    run_dir = create_test_run(tmp_path, run_id)
    from research.ledger.canonicalize import build_canonical_anchor_manifest, compute_anchor_payload_hash

    payload0 = build_canonical_anchor_manifest(run_dir, stage="TRAIN_START")
    hash0 = compute_anchor_payload_hash(payload0)

    evm_c = get_evm_client()
    evm_rec0 = evm_c.anchor_stage(run_id, "TRAIN_START", hash0)

    rcpt0 = AnchorReceipt(
        run_id=run_id,
        stage="TRAIN_START",
        manifest_sha256=payload0.get("manifest_sha256", ""),
        anchor_payload_sha256=hash0,
        git_commit="e84f2910",
        account="rClassicChain",
        tx_hash="TX_CHAIN_0",
        ledger_index=101,
        validated=True,
        transaction_result="tesSUCCESS",
        submitted_at="2026-10-20T00:00:00Z",
        validated_at="2026-10-20T00:00:04Z",
        xrpl_evm=evm_rec0,
    )
    save_receipt(rcpt0, run_dir)

    memo_dict0 = {"p": "Z-ZOA", "r": run_id, "s": "TRAIN_START", "h": hash0, "prev": ""}
    memo_json0 = json.dumps(memo_dict0, separators=(",", ":"))

    mock_l1 = MagicMock()
    mock_l1.request.return_value = Response(
        status=ResponseStatus.SUCCESS,
        result={
            "validated": True,
            "ledger_index": 101,
            "meta": {"TransactionResult": "tesSUCCESS"},
            "Memos": [
                {
                    "Memo": {
                        "MemoType": str_to_hex("z-zoa/anchor"),
                        "MemoFormat": str_to_hex("json"),
                        "MemoData": str_to_hex(memo_json0),
                    }
                }
            ],
        },
    )

    res_chain = verify_chain(
        run_id=run_id,
        stages=["TRAIN_START"],
        runs_root=tmp_path,
        client=mock_l1,
        evm_client=evm_c,
    )

    assert res_chain["chain_valid"] is True
    assert res_chain["stages_verified"] == 1
    assert res_chain["status"] == "CHAIN_VERIFIED"


