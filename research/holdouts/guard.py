"""Holdout security guard and gated DataGateway."""

from enum import Enum
from pathlib import Path
from typing import Optional, Union, Any, Set, Dict, List
import polars as pl
from pydantic import BaseModel, Field

from research.catalogs.schema import DatasetRole, DatasetMetadata
from research.catalogs.registry import CatalogRegistry
from research.catalogs.loader import load_dataset_table
from research.holdouts.exceptions import (
    HoldoutLeakageViolationError,
    UnfrozenValidationViolationError,
    UnauthorizedComparisonViolationError,
)


class ExecutionMode(str, Enum):
    TRAINING = "TRAINING"
    VALIDATION = "VALIDATION"
    AUDIT = "AUDIT"


class ExecutionContext(BaseModel):
    """Execution context defining caller intent, run ID, and freeze guarantees."""
    run_id: str = Field(..., description="Unique run/experiment identifier")
    mode: ExecutionMode = Field(..., description="Operational execution mode")
    freeze_token: Optional[str] = Field(
        default=None,
        description="SHA-256 hash of sealed training manifest required for validation access"
    )
    notes: Optional[str] = Field(default=None)
    require_freeze_anchor: bool = Field(
        default=False,
        description="If True, requires verified XRPL PREDICTION_FROZEN anchor on ledger before granting HOLDOUT access"
    )
    runs_root: Optional[str] = Field(
        default=None,
        description="Optional path to runs directory for anchor verification"
    )


class DataGateway:
    """
    Cryptographically and architecturally gated access point to all observational data.
    Direct file reads by training/reconstruction algorithms are forbidden.
    """

    def __init__(self, registry: CatalogRegistry, base_dir: Union[str, Path] = "."):
        self.registry = registry
        self.base_dir = Path(base_dir)

    def request_dataset(
        self,
        dataset_id: str,
        context: ExecutionContext
    ) -> pl.DataFrame:
        """
        Request dataset access under a specific execution context.
        Raises loud security violations if holdout boundaries are breached.
        """
        metadata = self.registry.get(dataset_id)

        # 1. Enforce Holdout Boundary
        if metadata.role == DatasetRole.HOLDOUT:
            if context.mode == ExecutionMode.TRAINING:
                raise HoldoutLeakageViolationError(
                    f"\n[LEAKAGE DEFENSE SHUTDOWN] Security violation in run '{context.run_id}':\n"
                    f"Dataset '{dataset_id}' is designated as a protected HOLDOUT catalogue.\n"
                    f"Access is strictly DENIED during TRAINING / RECONSTRUCTION mode.\n"
                    f"Reconstruction models must remain completely blind to out-of-sample holdouts."
                )

            if context.mode == ExecutionMode.VALIDATION:
                if not context.freeze_token or len(context.freeze_token.strip()) < 32:
                    raise UnfrozenValidationViolationError(
                        f"\n[INTEGRITY DEFENSE SHUTDOWN] Validation violation in run '{context.run_id}':\n"
                        f"Dataset '{dataset_id}' is a protected HOLDOUT catalogue.\n"
                        f"Validation requires a cryptographically sealed training manifest SHA-256 token.\n"
                        f"Received invalid or missing freeze token: '{context.freeze_token}'."
                    )

                if context.require_freeze_anchor:
                    from research.holdouts.exceptions import AnchorVerificationHoldoutViolationError
                    from research.ledger.receipt import get_receipt
                    from research.ledger.canonicalize import (
                        build_canonical_anchor_manifest,
                        compute_anchor_payload_hash,
                    )

                    root = Path(context.runs_root) if context.runs_root else self.base_dir / "runs"
                    run_dir = root / context.run_id
                    manifest_file = run_dir / "manifest.json"

                    # 1. frozen_manifest_exists
                    if not manifest_file.exists():
                        raise AnchorVerificationHoldoutViolationError(
                            f"HOLDOUT access DENIED: Run manifest does not exist at {manifest_file}"
                        )

                    # 2. frozen_manifest_hash_matches
                    import json
                    with open(manifest_file, "r", encoding="utf-8") as f:
                        m_data = json.load(f)
                    local_manifest_hash = m_data.get("manifest_sha256")
                    if local_manifest_hash != context.freeze_token:
                        raise AnchorVerificationHoldoutViolationError(
                            f"HOLDOUT access DENIED: Manifest hash '{local_manifest_hash}' "
                            f"does not match freeze token '{context.freeze_token}'"
                        )

                    # 3. xrpl_receipt_exists
                    receipt = get_receipt(context.run_id, stage="PREDICTION_FROZEN", runs_root=root)
                    if not receipt:
                        raise AnchorVerificationHoldoutViolationError(
                            f"HOLDOUT access DENIED: Missing XRPL PREDICTION_FROZEN receipt for run '{context.run_id}'"
                        )

                    # 4. receipt.stage == PREDICTION_FROZEN
                    if receipt.stage != "PREDICTION_FROZEN":
                        raise AnchorVerificationHoldoutViolationError(
                            f"HOLDOUT access DENIED: Receipt stage is '{receipt.stage}', expected 'PREDICTION_FROZEN'"
                        )

                    # 5. receipt.validated == true
                    if not receipt.validated:
                        raise AnchorVerificationHoldoutViolationError(
                            f"HOLDOUT access DENIED: XRPL receipt for '{context.run_id}' is not marked validated"
                        )

                    # 6. receipt.transaction_result == tesSUCCESS
                    if receipt.transaction_result != "tesSUCCESS":
                        raise AnchorVerificationHoldoutViolationError(
                            f"HOLDOUT access DENIED: XRPL transaction result is '{receipt.transaction_result}', expected 'tesSUCCESS'"
                        )

                    # 7. ledger memo hash == local frozen hash
                    local_payload = build_canonical_anchor_manifest(
                        run_dir=run_dir,
                        stage="PREDICTION_FROZEN",
                        previous_tx_hash=receipt.previous_tx_hash,
                    )
                    local_anchor_hash = compute_anchor_payload_hash(local_payload)
                    if receipt.anchor_payload_sha256 != local_anchor_hash:
                        raise AnchorVerificationHoldoutViolationError(
                            f"HOLDOUT access DENIED: Receipt anchor payload hash '{receipt.anchor_payload_sha256}' "
                            f"does not match local canonical hash '{local_anchor_hash}'"
                        )

        # 2. Enforce recursive parent lineage check for TRAINING mode
        if context.mode == ExecutionMode.TRAINING:
            def _check_lineage(meta: DatasetMetadata, visited: set):
                for p_id in (meta.parent_dataset_ids or []):
                    if p_id in visited:
                        continue
                    visited.add(p_id)
                    try:
                        p_meta = self.registry.get(p_id)
                        if p_meta.role == DatasetRole.HOLDOUT:
                            raise HoldoutLeakageViolationError(
                                f"\n[LEAKAGE DEFENSE SHUTDOWN] Lineage violation in run '{context.run_id}':\n"
                                f"Parent dataset '{p_id}' of '{dataset_id}' is a protected HOLDOUT.\n"
                                f"Access is strictly DENIED in TRAINING mode."
                            )
                        _check_lineage(p_meta, visited)
                    except KeyError:
                        pass
            _check_lineage(metadata, set())

        # 2. Enforce Comparison-Only Boundary
        if metadata.role == DatasetRole.COMPARISON_ONLY:
            if context.mode == ExecutionMode.TRAINING:
                raise UnauthorizedComparisonViolationError(
                    f"\n[INTEGRITY DEFENSE] Dataset '{dataset_id}' is designated COMPARISON_ONLY.\n"
                    f"It cannot be loaded into training / reconstruction pipelines."
                )

        # 3. Load with cryptographic hash verification
        return load_dataset_table(metadata, base_dir=self.base_dir)


def reveal_holdout(
    run_id: str,
    dataset_id: str,
    gateway: DataGateway,
    freeze_token: Optional[str] = None,
    require_freeze_anchor: bool = True,
    runs_root: Optional[Union[str, Path]] = None,
    client: Optional[Any] = None,
) -> pl.DataFrame:
    """
    Secure gated entry point for revealing holdout datasets.
    For anchor-required experiments, strictly forbids reveal until:
    - validated == True
    - TransactionResult == tesSUCCESS
    - ledger memo hash == local frozen hash
    """
    from research.holdouts.exceptions import AnchorVerificationHoldoutViolationError
    from research.ledger.verify import verify_anchor

    root = Path(runs_root) if runs_root else gateway.base_dir / "runs"
    run_dir = root / run_id
    manifest_file = run_dir / "manifest.json"

    if not manifest_file.exists():
        raise AnchorVerificationHoldoutViolationError(
            f"reveal_holdout() DENIED: Run directory '{run_dir}' missing manifest.json"
        )

    import json
    with open(manifest_file, "r", encoding="utf-8") as f:
        manifest_data = json.load(f)

    actual_freeze_token = manifest_data.get("manifest_sha256")
    if freeze_token and freeze_token != actual_freeze_token:
        raise AnchorVerificationHoldoutViolationError(
            f"reveal_holdout() DENIED: Provided freeze token does not match run manifest."
        )
    token_to_use = freeze_token or actual_freeze_token

    if require_freeze_anchor:
        # Full ledger verification
        ver_res = verify_anchor(
            run_id=run_id,
            stage="PREDICTION_FROZEN",
            runs_root=root,
            client=client,
        )
        if not ver_res.is_valid():
            raise AnchorVerificationHoldoutViolationError(
                f"reveal_holdout() DENIED for run '{run_id}': PREDICTION_FROZEN anchor validation failed.\n"
                f"Status: {ver_res.status}\n"
                f"Errors: {'; '.join(ver_res.errors)}"
            )

    ctx = ExecutionContext(
        run_id=run_id,
        mode=ExecutionMode.VALIDATION,
        freeze_token=token_to_use,
        require_freeze_anchor=require_freeze_anchor,
        runs_root=str(root),
    )

    return gateway.request_dataset(dataset_id, ctx)

