"""Verification engine for XRPL and XRPL EVM Sidechain research run anchors."""

import json
from pathlib import Path
from typing import Optional, Union, Dict, Any, List
from pydantic import BaseModel, Field

from xrpl.clients import JsonRpcClient
from xrpl.models.requests import Tx
from xrpl.models.response import ResponseStatus
from xrpl.utils import hex_to_str

from research.ledger.canonicalize import (
    build_canonical_anchor_manifest,
    compute_anchor_payload_hash,
)
from research.ledger.receipt import get_receipt, get_dual_receipt
from research.ledger.xrpl_client import get_xrpl_client
from research.ledger.anchor import STAGE_ORDER, get_preceding_stage
from research.ledger.evm_client import get_evm_client, EVMClient


class VerificationResult(BaseModel):
    """Structured report of an anchor verification audit across XRPL and XRPL EVM Sidechain."""
    run_id: str
    stage: str
    status: str  # VALIDATED_SUCCESS, RUN_INTEGRITY_FAILURE, TESTNET_HISTORY_UNAVAILABLE, MISSING_RECEIPT
    local_hash: str
    ledger_hash: Optional[str] = None
    tx_hash: Optional[str] = None
    ledger_index: Optional[int] = None
    validated: bool = False
    transaction_result: Optional[str] = None
    previous_tx_hash: Optional[str] = None
    checks: Dict[str, bool] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)
    audit_report: str = ""
    # EVM Sidechain verification fields
    evm_verified: Optional[bool] = None
    evm_tx_hash: Optional[str] = None
    evm_block_number: Optional[int] = None
    evm_contract_address: Optional[str] = None
    dual_anchored: bool = False

    def is_valid(self) -> bool:
        return self.status == "VALIDATED_SUCCESS"


def verify_anchor(
    run_id: str,
    stage: str,
    runs_root: Optional[Union[str, Path]] = None,
    client: Optional[JsonRpcClient] = None,
    evm_client: Optional[EVMClient] = None,
) -> VerificationResult:
    """
    Verify cryptographic integrity and ledger finality for a run stage:
    1. Rebuild local canonical anchor payload and compute current local SHA-256.
    2. Open saved XRPL & dual-ledger receipts.
    3. Query XRPL Testnet using tx_hash; confirm validated == true and TransactionResult == tesSUCCESS.
    4. Decode XRPL memo and compare ledger hash with local hash.
    5. Query XRPL EVM Sidechain (ResearchNotary) and verify smart contract state.
    6. Verify previous transaction link in the research chain.
    """
    root = Path(runs_root) if runs_root else Path("runs")
    run_dir = root / run_id

    checks: Dict[str, bool] = {
        "local_run_exists": False,
        "receipt_found": False,
        "local_receipt_hash_matches": False,
        "transaction_validated": False,
        "transaction_result_success": False,
        "local_hash_matches_ledger": False,
        "previous_anchor_verified": False,
        "run_integrity_verified": False,
        "evm_stage_verified": False,
    }
    errors: List[str] = []

    # 1. Local run check
    if not run_dir.exists() or not (run_dir / "manifest.json").exists():
        errors.append(f"Run directory or manifest.json not found for run '{run_id}' at {run_dir}")
        return _build_result(
            run_id=run_id,
            stage=stage,
            status="RUN_INTEGRITY_FAILURE",
            local_hash="",
            checks=checks,
            errors=errors,
        )
    checks["local_run_exists"] = True

    # 2. Receipt check
    receipt = get_receipt(run_id, stage=stage, runs_root=root)
    if not receipt:
        errors.append(f"No XRPL receipt found for run '{run_id}', stage '{stage}'")
        return _build_result(
            run_id=run_id,
            stage=stage,
            status="MISSING_RECEIPT",
            local_hash="",
            checks=checks,
            errors=errors,
        )
    checks["receipt_found"] = True

    # Check for dual-ledger receipt data
    dual_data = get_dual_receipt(run_id, stage=stage, runs_root=root)
    evm_info = (receipt.xrpl_evm or (dual_data.get("xrpl_evm") if dual_data else None)) or {}

    # 3. Rebuild local canonical payload
    try:
        local_payload = build_canonical_anchor_manifest(
            run_dir=run_dir,
            stage=stage,
            previous_tx_hash=receipt.previous_tx_hash,
        )
        local_hash = compute_anchor_payload_hash(local_payload)
    except Exception as e:
        errors.append(f"Failed to rebuild local canonical payload: {e}")
        return _build_result(
            run_id=run_id,
            stage=stage,
            status="RUN_INTEGRITY_FAILURE",
            local_hash="",
            tx_hash=receipt.tx_hash,
            checks=checks,
            errors=errors,
        )

    # Local receipt payload hash match
    if local_hash == receipt.anchor_payload_sha256:
        checks["local_receipt_hash_matches"] = True
    else:
        errors.append(
            f"Local run files have mutated since receipt was written!\n"
            f"Expected SHA-256 (from receipt): {receipt.anchor_payload_sha256}\n"
            f"Current local SHA-256:            {local_hash}"
        )

    # 4. Query XRPL Testnet
    xrpl_client = client or get_xrpl_client()
    try:
        tx_req = Tx(transaction=receipt.tx_hash)
        resp = xrpl_client.request(tx_req)
    except Exception as e:
        errors.append(f"XRPL Testnet query exception: {e}")
        return _build_result(
            run_id=run_id,
            stage=stage,
            status="NETWORK_QUERY_ERROR",
            local_hash=local_hash,
            tx_hash=receipt.tx_hash,
            checks=checks,
            errors=errors,
        )

    if resp.status != ResponseStatus.SUCCESS:
        err_type = resp.result.get("error", "unknown") if hasattr(resp, "result") else "unknown"
        if err_type in ["txnNotFound", "lgrNotFound"]:
            # Testnet reset or ledger history pruning occurred
            return _build_result(
                run_id=run_id,
                stage=stage,
                status="TESTNET_HISTORY_UNAVAILABLE",
                local_hash=local_hash,
                tx_hash=receipt.tx_hash,
                checks=checks,
                errors=[
                    f"XRPL Testnet transaction {receipt.tx_hash} not found on current ledger.\n"
                    f"NOTE: XRPL Testnet was likely reset or pruned. This is NOT a tampering event."
                ],
            )
        else:
            errors.append(f"XRPL Testnet returned error: {resp.result.get('error_message', err_type)}")
            return _build_result(
                run_id=run_id,
                stage=stage,
                status="RUN_INTEGRITY_FAILURE",
                local_hash=local_hash,
                tx_hash=receipt.tx_hash,
                checks=checks,
                errors=errors,
            )

    tx_data = resp.result
    # XRPL transaction validation check
    is_validated = bool(tx_data.get("validated", False))
    meta = tx_data.get("meta") or tx_data.get("metaData") or {}
    tx_result = meta.get("TransactionResult") or tx_data.get("TransactionResult")
    ledger_idx = tx_data.get("ledger_index") or meta.get("ledger_index")

    if is_validated:
        checks["transaction_validated"] = True
    else:
        errors.append("Transaction is recorded but not yet validated in a closed ledger.")

    if tx_result == "tesSUCCESS":
        checks["transaction_result_success"] = True
    else:
        errors.append(f"Transaction result was '{tx_result}', expected 'tesSUCCESS'")

    # 5. Extract and decode memo
    ledger_hash: Optional[str] = None
    memo_prev: Optional[str] = None
    memos = tx_data.get("Memos") or tx_data.get("memos") or (tx_data.get("tx_json") or {}).get("Memos") or []

    memo_found = False
    for m in memos:
        inner = m.get("Memo") or m.get("memo") or m
        m_type_hex = inner.get("MemoType") or inner.get("memo_type") or ""
        m_data_hex = inner.get("MemoData") or inner.get("memo_data") or ""
        try:
            m_type = hex_to_str(m_type_hex) if m_type_hex else ""
            if "z-zoa" in m_type.lower():
                m_data_str = hex_to_str(m_data_hex)
                m_obj = json.loads(m_data_str)
                ledger_hash = m_obj.get("h")
                memo_prev = m_obj.get("prev") or None
                memo_found = True
                break
        except Exception:
            continue

    if not memo_found or not ledger_hash:
        errors.append("Could not find or decode valid Z-ZOA anchor memo in XRPL transaction.")
    else:
        if ledger_hash == local_hash:
            checks["local_hash_matches_ledger"] = True
        else:
            errors.append(
                f"Ledger anchor hash mismatch!\n"
                f"Local hash:  {local_hash}\n"
                f"Ledger hash: {ledger_hash}"
            )

    # 6. Verify previous transaction link in chain
    expected_prev = receipt.previous_tx_hash
    if not expected_prev and not memo_prev:
        checks["previous_anchor_verified"] = True
    elif expected_prev and memo_prev and expected_prev == memo_prev:
        checks["previous_anchor_verified"] = True
    else:
        errors.append(
            f"Previous transaction link mismatch! Expected: '{expected_prev}', Memo has: '{memo_prev}'"
        )

    # 7. Verify XRPL EVM Sidechain Contract state
    evm_c = evm_client or get_evm_client()
    evm_verified = False
    evm_tx_hash = evm_info.get("tx_hash")
    evm_block_num = evm_info.get("block_number")
    evm_contract = evm_info.get("contract_address")
    dual_anchored = False

    if evm_tx_hash:
        dual_anchored = True
        is_evm_match, _ = evm_c.verify_stage(
            run_id=run_id,
            stage=stage,
            expected_hash=local_hash,
            runs_root=root,
        )
        if is_evm_match:
            checks["evm_stage_verified"] = True
            evm_verified = True
        else:
            checks["evm_stage_verified"] = False
            evm_verified = False
            errors.append(f"XRPL EVM Sidechain contract payload hash mismatch or stage unanchored for stage '{stage}'")

    # Final integrity determination
    all_critical_passed = (
        checks["local_run_exists"]
        and checks["receipt_found"]
        and checks["local_receipt_hash_matches"]
        and checks["transaction_validated"]
        and checks["transaction_result_success"]
        and checks["local_hash_matches_ledger"]
        and checks["previous_anchor_verified"]
        and (not dual_anchored or checks.get("evm_stage_verified", False))
    )
    checks["run_integrity_verified"] = all_critical_passed

    status = "VALIDATED_SUCCESS" if all_critical_passed else "RUN_INTEGRITY_FAILURE"

    return _build_result(
        run_id=run_id,
        stage=stage,
        status=status,
        local_hash=local_hash,
        ledger_hash=ledger_hash,
        tx_hash=receipt.tx_hash,
        ledger_index=ledger_idx,
        validated=is_validated,
        transaction_result=tx_result,
        previous_tx_hash=expected_prev,
        checks=checks,
        errors=errors,
        evm_verified=evm_verified if dual_anchored else None,
        evm_tx_hash=evm_tx_hash,
        evm_block_number=evm_block_num,
        evm_contract_address=evm_contract,
        dual_anchored=dual_anchored,
    )


def _build_result(
    run_id: str,
    stage: str,
    status: str,
    local_hash: str,
    ledger_hash: Optional[str] = None,
    tx_hash: Optional[str] = None,
    ledger_index: Optional[int] = None,
    validated: bool = False,
    transaction_result: Optional[str] = None,
    previous_tx_hash: Optional[str] = None,
    checks: Optional[Dict[str, bool]] = None,
    errors: Optional[List[str]] = None,
    evm_verified: Optional[bool] = None,
    evm_tx_hash: Optional[str] = None,
    evm_block_number: Optional[int] = None,
    evm_contract_address: Optional[str] = None,
    dual_anchored: bool = False,
) -> VerificationResult:
    checks = checks or {}
    errors = errors or []

    # Format audit report strictly matching specification
    short_local = f"{local_hash[:16]}..." if local_hash else "--"
    short_ledger = f"{ledger_hash[:16]}..." if ledger_hash else "--"
    short_tx = f"{tx_hash[:16]}..." if tx_hash else "--"
    short_evm = f"{evm_tx_hash[:16]}..." if evm_tx_hash else "--"

    report_lines = [
        f"RUN {run_id}",
        f"Stage {stage}",
        f"Local SHA-256 {short_local}",
        f"Ledger SHA-256 {short_ledger}",
        f"XRPL L1 transaction {short_tx}",
        f"Ledger index {ledger_index if ledger_index is not None else '--'}",
    ]

    if dual_anchored:
        report_lines.append(f"XRPL EVM transaction {short_evm}")
        report_lines.append(f"EVM Block number {evm_block_number or '--'}")

    if status == "VALIDATED_SUCCESS":
        report_lines.extend([
            "✓ TRANSACTION VALIDATED (XRPL Layer 1)",
            "✓ LOCAL HASH MATCHES LEDGER",
            "✓ PREVIOUS ANCHOR VERIFIED",
        ])
        if dual_anchored and evm_verified:
            report_lines.append("✓ XRPL EVM CONTRACT VERIFIED (Sidechain 1440002)")
        report_lines.append("✓ RUN INTEGRITY VERIFIED")
    elif status == "TESTNET_HISTORY_UNAVAILABLE":
        report_lines.extend([
            "? TESTNET_HISTORY_UNAVAILABLE (XRPL Testnet reset/pruning detected)",
            "! Local run manifest and cryptographic receipt preserved.",
        ])
    else:
        report_lines.append("✗ RUN INTEGRITY FAILURE")
        for err in errors:
            report_lines.append(f"  - {err}")

    audit_report = "\n".join(report_lines)

    return VerificationResult(
        run_id=run_id,
        stage=stage,
        status=status,
        local_hash=local_hash,
        ledger_hash=ledger_hash,
        tx_hash=tx_hash,
        ledger_index=ledger_index,
        validated=validated,
        transaction_result=transaction_result,
        previous_tx_hash=previous_tx_hash,
        checks=checks,
        errors=errors,
        audit_report=audit_report,
        evm_verified=evm_verified,
        evm_tx_hash=evm_tx_hash,
        evm_block_number=evm_block_number,
        evm_contract_address=evm_contract_address,
        dual_anchored=dual_anchored,
    )


def verify_chain(
    run_id: str,
    stages: Optional[List[str]] = None,
    runs_root: Optional[Union[str, Path]] = None,
    client: Optional[JsonRpcClient] = None,
    evm_client: Optional[EVMClient] = None,
) -> Dict[str, Any]:
    """
    Verify an entire chronological research chain for a run across both XRPL L1 and EVM Sidechain.
    """
    root = Path(runs_root) if runs_root else Path("runs")
    target_stages = stages or STAGE_ORDER

    results: List[VerificationResult] = []
    chain_broken = False
    prior_tx_hash: Optional[str] = None

    for stage_name in target_stages:
        rcpt = get_receipt(run_id, stage=stage_name, runs_root=root)
        if not rcpt:
            continue

        res = verify_anchor(run_id, stage_name, runs_root=root, client=client, evm_client=evm_client)
        results.append(res)

        if not res.is_valid():
            chain_broken = True

        if prior_tx_hash is not None and res.previous_tx_hash != prior_tx_hash:
            chain_broken = True
            res.errors.append(
                f"Chain linkage break at stage '{stage_name}': expected previous '{prior_tx_hash}', got '{res.previous_tx_hash}'"
            )

        prior_tx_hash = res.tx_hash

    overall_valid = len(results) > 0 and not chain_broken

    return {
        "run_id": run_id,
        "stages_verified": len(results),
        "chain_valid": overall_valid,
        "status": "CHAIN_VERIFIED" if overall_valid else "CHAIN_BROKEN_OR_INCOMPLETE",
        "stage_results": [r.model_dump() for r in results],
        "audit_report": "\n\n".join([r.audit_report for r in results]),
    }
