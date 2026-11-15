"""REST API endpoints for XRPL Testnet & XRPL EVM Sidechain research run notarization."""

import json
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from backend.config import RUNS_DIR, BASE_DIR
from research.ledger import (
    anchor_run,
    verify_anchor,
    verify_chain,
    get_receipt,
    get_dual_receipt,
    check_testnet_connectivity,
    check_evm_connectivity,
    get_evm_client,
    bootstrap_testnet_account,
    get_account_status,
    XRPLAnchorError,
    XRPL_EVM_CHAIN_ID,
    DEFAULT_XRPL_EVM_RPC,
    XRPL_EVM_EXPLORER_URL,
    DEFAULT_CONTRACT_ADDRESS,
)
from research.ledger.xrpl_client import load_testnet_credentials


router = APIRouter(prefix="/ledger", tags=["ledger"])


class AnchorRequest(BaseModel):
    run_id: str = Field(..., description="Unique run identifier")
    stage: str = Field(default="PREDICTION_FROZEN", description="Research stage to anchor")
    previous_tx_hash: Optional[str] = Field(default=None, description="Optional previous tx hash in chain")


class VerifyRequest(BaseModel):
    run_id: str = Field(..., description="Unique run identifier")
    stage: str = Field(default="PREDICTION_FROZEN", description="Research stage to verify")


class VerifyChainRequest(BaseModel):
    run_id: str = Field(..., description="Unique run identifier")


class EVMVerifyStageRequest(BaseModel):
    run_id: str = Field(..., description="Unique run identifier")
    stage: str = Field(default="PREDICTION_FROZEN", description="Research stage to verify")
    payload_hash: str = Field(..., description="Expected payload hash (hex string)")


@router.get("/status")
def ledger_status():
    """Get XRPL Testnet Layer 1 and XRPL EVM Sidechain connectivity and research account status."""
    conn_l1 = check_testnet_connectivity()
    conn_evm = check_evm_connectivity()
    creds = load_testnet_credentials(base_dir=BASE_DIR)
    address = creds.get("address")

    account_info = None
    if address:
        account_info = get_account_status(address=address)

    return {
        "connectivity": conn_l1,
        "network": "XRPL Testnet",
        "network_id": 1,
        "account_address": address,
        "account_info": account_info,
        "evm_connectivity": conn_evm,
        "evm_network": "XRPL EVM Sidechain Testnet",
        "evm_chain_id": XRPL_EVM_CHAIN_ID,
        "evm_contract_address": DEFAULT_CONTRACT_ADDRESS,
        "disclaimer": "DEVELOPMENT RECORD XRPL TESTNET & XRPL EVM SIDECHAIN NOT A PERMANENT PUBLICATION ARCHIVE",
    }


@router.get("/evm/status")
def evm_status():
    """Get dedicated status and connectivity for XRPL EVM Sidechain Testnet."""
    return check_evm_connectivity()


@router.get("/evm/contract")
def evm_contract_info():
    """Get ResearchNotary contract address, ABI, and deployment details."""
    contract_path = BASE_DIR / "contracts" / "ResearchNotary.json"
    if contract_path.exists():
        with open(contract_path, "r", encoding="utf-8") as f:
            return json.load(f)

    return {
        "contractName": "ResearchNotary",
        "chainId": XRPL_EVM_CHAIN_ID,
        "network": "XRPL EVM Sidechain Testnet",
        "rpcUrl": DEFAULT_XRPL_EVM_RPC,
        "explorerUrl": XRPL_EVM_EXPLORER_URL,
        "defaultContractAddress": DEFAULT_CONTRACT_ADDRESS,
        "abi": [],
    }


@router.post("/evm/verify-stage")
def evm_verify_stage(req: EVMVerifyStageRequest):
    """Verify on-chain stage notarization status against ResearchNotary on XRPL EVM Sidechain."""
    client = get_evm_client()
    matches, receipt = client.verify_stage(
        run_id=req.run_id,
        stage=req.stage,
        expected_hash=req.payload_hash,
        runs_root=RUNS_DIR,
    )
    return {
        "run_id": req.run_id,
        "stage": req.stage,
        "verified": matches,
        "receipt": receipt,
        "chain_id": XRPL_EVM_CHAIN_ID,
        "network": "XRPL EVM Sidechain Testnet",
    }


@router.get("/evm/latest-stage/{run_id}")
def evm_get_latest_stage(run_id: str):
    """Get highest anchored stage index and name for run_id on XRPL EVM Sidechain."""
    from research.ledger.evm_client import REV_STAGE_MAP
    client = get_evm_client()
    latest_idx = client.get_run_latest_stage(run_id=run_id, runs_root=RUNS_DIR)
    stage_name = REV_STAGE_MAP.get(latest_idx) if latest_idx >= 0 else None
    return {
        "run_id": run_id,
        "latest_stage_index": latest_idx,
        "latest_stage_name": stage_name,
        "chain_id": XRPL_EVM_CHAIN_ID,
    }



@router.post("/bootstrap")
def bootstrap_account():
    """Obtain and fund a dedicated research account using the official XRPL Testnet faucet."""
    try:
        res = bootstrap_testnet_account(base_dir=BASE_DIR)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to bootstrap Testnet account: {e}")


@router.post("/anchor")
def anchor_experiment(req: AnchorRequest):
    """Anchor a frozen research run onto XRPL Testnet and XRPL EVM Sidechain."""
    try:
        receipt = anchor_run(
            run_id=req.run_id,
            stage=req.stage,
            runs_root=RUNS_DIR,
            previous_tx_hash=req.previous_tx_hash,
            base_dir=BASE_DIR,
        )
        return receipt.model_dump()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except XRPLAnchorError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected anchoring failure: {e}")


@router.get("/receipt/{run_id}")
def read_receipt(run_id: str, stage: Optional[str] = Query(None)):
    """Retrieve saved XRPL receipt for a run and optional stage."""
    receipt = get_receipt(run_id=run_id, stage=stage, runs_root=RUNS_DIR)
    if not receipt:
        raise HTTPException(
            status_code=404,
            detail=f"No XRPL receipt found for run '{run_id}' (stage: {stage or 'latest'})"
        )
    return receipt.model_dump()


@router.get("/receipts/{run_id}")
def read_dual_receipts(run_id: str, stage: Optional[str] = Query(None)):
    """Retrieve dual-ledger receipt (anchor_receipts.json) recording both xrpl_native and xrpl_evm."""
    dual_rcpt = get_dual_receipt(run_id=run_id, stage=stage, runs_root=RUNS_DIR)
    if not dual_rcpt:
        raise HTTPException(
            status_code=404,
            detail=f"No dual-ledger receipt found for run '{run_id}' (stage: {stage or 'latest'})"
        )
    return dual_rcpt


@router.post("/verify")
def verify_experiment_anchor(req: VerifyRequest):
    """Verify cryptographic integrity, XRPL Layer 1 memo, and XRPL EVM Sidechain contract state."""
    result = verify_anchor(
        run_id=req.run_id,
        stage=req.stage,
        runs_root=RUNS_DIR,
    )
    return result.model_dump()


@router.post("/verify-chain")
def verify_experiment_chain(req: VerifyChainRequest):
    """Verify entire chronological research chain for a run across both chains."""
    return verify_chain(
        run_id=req.run_id,
        runs_root=RUNS_DIR,
    )
