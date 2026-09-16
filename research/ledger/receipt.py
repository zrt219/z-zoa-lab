"""XRPL research run receipt structures and storage."""

import json
from pathlib import Path
from typing import Optional, Dict, Any, Union
from pydantic import BaseModel, Field


TESTNET_DISCLAIMER = (
    "DEVELOPMENT RECORD XRPL TESTNET NOT A PERMANENT PUBLICATION ARCHIVE"
)


class AnchorReceipt(BaseModel):
    """Immutable receipt certifying a run anchor on XRPL Testnet."""
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

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


def save_receipt(receipt: AnchorReceipt, run_dir: Union[str, Path]) -> Path:
    """
    Save receipt to disk:
    1. runs/{run_id}/xrpl_receipt_{stage}.json (stage-specific record)
    2. runs/{run_id}/xrpl_receipt.json (latest receipt pointer)
    3. Update or write runs/{run_id}/checksums.sha256
    """
    run_path = Path(run_dir)
    run_path.mkdir(parents=True, exist_ok=True)

    # Validate secret is not leaked
    receipt_data = receipt.model_dump()
    json_str = json.dumps(receipt_data)
    for forbidden in ["secret", "private_key", "seed", "sEd", "sno"]:
        # Ensure common secret prefixes/keys aren't stored
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

    # 3. Update checksums.sha256
    _update_run_checksums(run_path)

    return stage_file


def _update_run_checksums(run_path: Path):
    """Compute and write checksums.sha256 for all standard run files."""
    import hashlib

    files_to_hash = ["manifest.json", "config.yaml", "results.json", "xrpl_receipt.json"]
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
