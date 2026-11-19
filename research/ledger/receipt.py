"""XRPL and XRPL EVM Sidechain research run receipt structures and storage."""

import json
from pathlib import Path
from typing import Optional, Dict, Any, Union
from pydantic import BaseModel, Field


TESTNET_DISCLAIMER = (
    "DEVELOPMENT RECORD XRPL TESTNET & XRPL EVM SIDECHAIN NOT A PERMANENT PUBLICATION ARCHIVE"
)


class DualAnchorReceipt(BaseModel):
    """Immutable receipt certifying run anchoring on both XRPL Native Testnet and XRPL EVM Sidechain."""
    project: str = Field(default="Z-ZOA")
    run_id: str
    stage: str
    manifest_sha256: str
    anchor_payload_sha256: str
    git_commit: str
    xrpl_native: Dict[str, Any]
    xrpl_evm: Optional[Dict[str, Any]] = None
    submitted_at: str
    validated_at: str
    disclaimer: str = Field(default=TESTNET_DISCLAIMER)
    canonical_manifest: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class AnchorReceipt(BaseModel):
    """Receipt certifying run anchoring on XRPL Testnet with dual-ledger EVM sidechain support."""
    project: str = Field(default="Z-ZOA")
    network: str = Field(default="XRPL Testnet")
    network_id: int = Field(default=1)
    run_id: str
    stage: str
    manifest_sha256: str
    anchor_payload_sha256: str
    git_commit: str
    account: str
    tx_hash: str
    ledger_index: int
    validated: bool
    transaction_result: str
    previous_tx_hash: Optional[str] = None
    submitted_at: str
    validated_at: str
    disclaimer: str = Field(default=TESTNET_DISCLAIMER)
    canonical_manifest: Optional[Dict[str, Any]] = None
    xrpl_native: Optional[Dict[str, Any]] = None
    xrpl_evm: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()

    def get_dual_representation(self) -> Dict[str, Any]:
        """Generate structured dual-ledger receipt containing xrpl_native and xrpl_evm nodes."""
        native_node = self.xrpl_native or {
            "tx_hash": self.tx_hash,
            "ledger_index": self.ledger_index,
            "account": self.account,
            "validated": self.validated,
            "transaction_result": self.transaction_result,
            "network": self.network,
            "network_id": self.network_id,
            "explorer_url": f"https://testnet.xrpl.org/transactions/{self.tx_hash}",
        }
        evm_node = self.xrpl_evm
        return {
            "project": self.project,
            "run_id": self.run_id,
            "stage": self.stage,
            "manifest_sha256": self.manifest_sha256,
            "anchor_payload_sha256": self.anchor_payload_sha256,
            "git_commit": self.git_commit,
            "xrpl_native": native_node,
            "xrpl_evm": evm_node,
            "submitted_at": self.submitted_at,
            "validated_at": self.validated_at,
            "disclaimer": self.disclaimer,
            "canonical_manifest": self.canonical_manifest,
        }


def save_receipt(receipt: AnchorReceipt, run_dir: Union[str, Path]) -> Path:
    """
    Save receipt to disk:
    1. runs/{run_id}/xrpl_receipt_{stage}.json (stage-specific record)
    2. runs/{run_id}/xrpl_receipt.json (latest receipt pointer)
    3. runs/{run_id}/anchor_receipts_{stage}.json (stage-specific dual receipt)
    4. runs/{run_id}/anchor_receipts.json (latest dual receipt pointer)
    5. Update or write runs/{run_id}/checksums.sha256
    """
    run_path = Path(run_dir)
    run_path.mkdir(parents=True, exist_ok=True)

    # Validate secret is not leaked
    receipt_data = receipt.model_dump()
    json_str = json.dumps(receipt_data)
    for forbidden in ["secret", "private_key", "seed", "sEd", "sno"]:
        if f'"{forbidden}"' in json_str.lower():
            raise ValueError(f"CRITICAL: Attempted to serialize secret field '{forbidden}' into receipt!")

    # 1. Stage-specific receipt
    stage_file = run_path / f"xrpl_receipt_{receipt.stage}.json"
    with open(stage_file, "w", encoding="utf-8") as f:
        json.dump(receipt_data, f, indent=2)

    # 2. Latest receipt
    latest_file = run_path / "xrpl_receipt.json"
    with open(latest_file, "w", encoding="utf-8") as f:
        json.dump(receipt_data, f, indent=2)

    # 3. Dual-ledger representations
    dual_data = receipt.get_dual_representation()
    dual_stage_file = run_path / f"anchor_receipts_{receipt.stage}.json"
    with open(dual_stage_file, "w", encoding="utf-8") as f:
        json.dump(dual_data, f, indent=2)

    dual_latest_file = run_path / "anchor_receipts.json"
    with open(dual_latest_file, "w", encoding="utf-8") as f:
        json.dump(dual_data, f, indent=2)

    # 4. Update checksums.sha256
    _update_run_checksums(run_path)

    return stage_file


def _update_run_checksums(run_path: Path):
    """Compute and write checksums.sha256 for all standard run files."""
    import hashlib

    files_to_hash = [
        "manifest.json",
        "config.yaml",
        "results.json",
        "xrpl_receipt.json",
        "anchor_receipts.json",
    ]
    lines = []
    for fname in files_to_hash:
        p = run_path / fname
        if p.exists():
            h = hashlib.sha256(p.read_bytes()).hexdigest()
            lines.append(f"{h}  {fname}\n")

    if lines:
        with open(run_path / "checksums.sha256", "w", encoding="utf-8") as f:
            f.writelines(lines)


def get_receipt(
    run_id: str,
    stage: Optional[str] = None,
    runs_root: Optional[Union[str, Path]] = None,
) -> Optional[AnchorReceipt]:
    """Retrieve receipt for a run and optional stage."""
    root = Path(runs_root) if runs_root else Path("runs")
    run_path = root / run_id

    if stage:
        target = run_path / f"xrpl_receipt_{stage}.json"
        if target.exists():
            with open(target, "r", encoding="utf-8") as f:
                return AnchorReceipt(**json.load(f))

    # Fallback to latest xrpl_receipt.json
    latest = run_path / "xrpl_receipt.json"
    if latest.exists():
        with open(latest, "r", encoding="utf-8") as f:
            data = json.load(f)
            if stage is None or data.get("stage") == stage:
                return AnchorReceipt(**data)

    return None


def get_dual_receipt(
    run_id: str,
    stage: Optional[str] = None,
    runs_root: Optional[Union[str, Path]] = None,
) -> Optional[Dict[str, Any]]:
    """Retrieve dual-ledger receipt (anchor_receipts.json) recording both xrpl_native and xrpl_evm."""
    root = Path(runs_root) if runs_root else Path("runs")
    run_path = root / run_id

    if stage:
        target = run_path / f"anchor_receipts_{stage}.json"
        if target.exists():
            with open(target, "r", encoding="utf-8") as f:
                return json.load(f)

    latest = run_path / "anchor_receipts.json"
    if latest.exists():
        with open(latest, "r", encoding="utf-8") as f:
            data = json.load(f)
            if stage is None or data.get("stage") == stage:
                return data

    # If anchor_receipts.json doesn't exist yet, derive from get_receipt if available
    rec = get_receipt(run_id, stage=stage, runs_root=runs_root)
    if rec:
        return rec.get_dual_representation()

    return None
