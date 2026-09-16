"""Research run anchoring engine targeting XRPL Testnet."""

import json
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional, Union, Dict, Any

from xrpl.clients import JsonRpcClient
from xrpl.models.transactions import AccountSet, Memo
from xrpl.transaction import submit_and_wait
from xrpl.utils import str_to_hex
from xrpl.wallet import Wallet

from research.ledger.canonicalize import (
    build_canonical_anchor_manifest,
    compute_anchor_payload_hash,
)
from research.ledger.receipt import AnchorReceipt, save_receipt, get_receipt
from research.ledger.xrpl_client import (
    get_xrpl_client,
    get_testnet_wallet,
    TESTNET_NETWORK_ID,
)


class ResearchStage(str, Enum):
    TRAIN_START = "TRAIN_START"
    PREDICTION_FROZEN = "PREDICTION_FROZEN"
    HOLDOUT_REVEAL = "HOLDOUT_REVEAL"
    VALIDATION_COMPLETE = "VALIDATION_COMPLETE"
    HYBRID_COMPLETE = "HYBRID_COMPLETE"
    PAPER_CANDIDATE = "PAPER_CANDIDATE"


class AnchorStatus(str, Enum):
    UNSUBMITTED = "UNSUBMITTED"
    SUBMITTED_PENDING = "SUBMITTED_PENDING"
    VALIDATED_SUCCESS = "VALIDATED_SUCCESS"
    VALIDATED_FAILED = "VALIDATED_FAILED"
    EXPIRED_OR_MISSING = "EXPIRED_OR_MISSING"
    LOCAL_COMPLETE_UNANCHORED = "LOCAL_COMPLETE_UNANCHORED"
    TESTNET_HISTORY_UNAVAILABLE = "TESTNET_HISTORY_UNAVAILABLE"


STAGE_ORDER = [
    ResearchStage.TRAIN_START.value,
    ResearchStage.PREDICTION_FROZEN.value,
    ResearchStage.HOLDOUT_REVEAL.value,
    ResearchStage.VALIDATION_COMPLETE.value,
    ResearchStage.HYBRID_COMPLETE.value,
    ResearchStage.PAPER_CANDIDATE.value,
]


class XRPLAnchorError(Exception):
    """Exception raised when XRPL anchoring encounters an unrecoverable failure."""
    def __init__(self, message: str, status: AnchorStatus = AnchorStatus.LOCAL_COMPLETE_UNANCHORED):
        super().__init__(message)
        self.status = status


def get_preceding_stage(stage: str) -> Optional[str]:
    """Return the name of the canonically preceding research stage."""
    try:
        idx = STAGE_ORDER.index(stage)
        if idx > 0:
            return STAGE_ORDER[idx - 1]
    except ValueError:
        pass
    return None


def anchor_run(
    run_id: str,
    stage: Union[str, ResearchStage],
    runs_root: Optional[Union[str, Path]] = None,
    previous_tx_hash: Optional[str] = None,
    client: Optional[JsonRpcClient] = None,
    wallet: Optional[Wallet] = None,
    base_dir: Optional[Union[str, Path]] = None,
) -> AnchorReceipt:
    """
    Deterministically anchor a frozen research run onto XRPL Testnet.

    Guarantees:
    - Never modifies or corrupts scientific run results if anchoring fails.
    - Uses minimal no-op AccountSet carrying a compact cryptographic memo (< 1 KB).
    - Verifies validated == True and TransactionResult == tesSUCCESS before returning receipt.
    - Saves xrpl_receipt.json and stage receipt beside the run.
    """
    stage_str = stage.value if isinstance(stage, ResearchStage) else str(stage)
    root = Path(runs_root) if runs_root else Path("runs")
    run_dir = root / run_id

    if not run_dir.exists():
        raise FileNotFoundError(f"Cannot anchor run '{run_id}': directory does not exist: {run_dir}")

    manifest_path = run_dir / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Cannot anchor run '{run_id}': 'manifest.json' not found in {run_dir}")

    # Resolve previous tx hash in research chronology if not explicitly passed
    if not previous_tx_hash:
        preceding = get_preceding_stage(stage_str)
        if preceding:
            prior_receipt = get_receipt(run_id, stage=preceding, runs_root=root)
            if prior_receipt and prior_receipt.tx_hash:
                previous_tx_hash = prior_receipt.tx_hash

    # Build canonical payload & cryptographic fingerprint
    canonical_payload = build_canonical_anchor_manifest(
        run_dir=run_dir,
        stage=stage_str,
        previous_tx_hash=previous_tx_hash,
    )
    anchor_hash = compute_anchor_payload_hash(canonical_payload)
    manifest_sha256 = canonical_payload.get("manifest_sha256", "")
    git_commit = canonical_payload.get("git_commit", "UNKNOWN")

    # Connect to client and wallet
    try:
        xrpl_client = client or get_xrpl_client()
        signer_wallet = wallet or get_testnet_wallet(base_dir=base_dir)
    except Exception as e:
        raise XRPLAnchorError(
            f"Signing credential or client setup failed: {e}\n"
            f"Scientific run '{run_id}' remains FROZEN locally with status LOCAL_COMPLETE_UNANCHORED.",
            status=AnchorStatus.LOCAL_COMPLETE_UNANCHORED,
        )

    # Build compact memo: max ~180 chars JSON -> hex
    memo_dict = {
        "p": "Z-ZOA",
        "r": run_id,
        "s": stage_str,
        "h": anchor_hash,
        "prev": previous_tx_hash or "",
    }
    memo_json = json.dumps(memo_dict, separators=(",", ":"))
    memo = Memo(
        memo_type=str_to_hex("z-zoa/anchor"),
        memo_format=str_to_hex("json"),
        memo_data=str_to_hex(memo_json),
    )

    # Minimal no-op AccountSet carrying memo
    tx = AccountSet(
        account=signer_wallet.classic_address,
        memos=[memo],
    )

    submitted_at = datetime.now(timezone.utc).isoformat()

    # Submit and await validation
    try:
        response = submit_and_wait(tx, xrpl_client, signer_wallet)
    except Exception as e:
        raise XRPLAnchorError(
            f"XRPL Testnet submission failed: {e}\n"
            f"Scientific results are untouched. Run remains LOCAL_COMPLETE_UNANCHORED.",
            status=AnchorStatus.LOCAL_COMPLETE_UNANCHORED,
        )

    res = response.result if hasattr(response, "result") else {}
    tx_hash = res.get("hash") or res.get("tx_json", {}).get("hash")
    validated = res.get("validated", False)
    meta = res.get("meta") or res.get("metaData") or {}
    tx_result = meta.get("TransactionResult") or res.get("engine_result", "unknown")
    ledger_index = res.get("ledger_index") or meta.get("ledger_index", 0)

    validated_at = datetime.now(timezone.utc).isoformat()

    if not validated or tx_result != "tesSUCCESS":
        raise XRPLAnchorError(
            f"Transaction failed validation on XRPL Testnet: validated={validated}, result={tx_result}.\n"
            f"Run remains LOCAL_COMPLETE_UNANCHORED.",
            status=AnchorStatus.VALIDATED_FAILED if validated else AnchorStatus.SUBMITTED_PENDING,
        )

    # Construct receipt
    receipt = AnchorReceipt(
        project="Z-ZOA",
        network="XRPL Testnet",
        network_id=TESTNET_NETWORK_ID,
        run_id=run_id,
        stage=stage_str,
        manifest_sha256=manifest_sha256,
        anchor_payload_sha256=anchor_hash,
        git_commit=git_commit,
        account=signer_wallet.classic_address,
        tx_hash=tx_hash,
        ledger_index=int(ledger_index),
        validated=bool(validated),
        transaction_result=str(tx_result),
        previous_tx_hash=previous_tx_hash,
        submitted_at=submitted_at,
        validated_at=validated_at,
        canonical_manifest=canonical_payload,
    )

    save_receipt(receipt, run_dir)
    return receipt
