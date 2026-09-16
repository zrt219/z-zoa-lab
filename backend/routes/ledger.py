"""REST API endpoints for XRPL Testnet research run notarization."""

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
    check_testnet_connectivity,
    bootstrap_testnet_account,
    get_account_status,
    XRPLAnchorError,
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


@router.get("/status")
def ledger_status():
    """Get XRPL Testnet connectivity and configured research account status."""
    conn = check_testnet_connectivity()
    creds = load_testnet_credentials(base_dir=BASE_DIR)
    address = creds.get("address")

    account_info = None
    if address:
        account_info = get_account_status(address=address)

    return {
        "connectivity": conn,
        "network": "XRPL Testnet",
        "network_id": 1,
        "account_address": address,
        "account_info": account_info,
        "disclaimer": "DEVELOPMENT RECORD XRPL TESTNET NOT A PERMANENT PUBLICATION ARCHIVE",
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
    """Anchor a frozen research run onto XRPL Testnet."""
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


@router.post("/verify")
def verify_experiment_anchor(req: VerifyRequest):
    """Verify cryptographic integrity and XRPL ledger validation for a run anchor."""
    result = verify_anchor(
        run_id=req.run_id,
        stage=req.stage,
        runs_root=RUNS_DIR,
    )
    return result.model_dump()


@router.post("/verify-chain")
def verify_experiment_chain(req: VerifyChainRequest):
    """Verify entire chronological research chain for a run."""
    return verify_chain(
        run_id=req.run_id,
        runs_root=RUNS_DIR,
    )
