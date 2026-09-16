"""Test holdout boundary and leakage defense."""

import pytest
from research.catalogs.registry import CatalogRegistry
from research.holdouts.guard import DataGateway, ExecutionContext, ExecutionMode
from research.holdouts.exceptions import (
    HoldoutLeakageViolationError,
    UnfrozenValidationViolationError,
)


def test_holdout_leakage_blocked_in_training():
    reg = CatalogRegistry("datasets/manifests/catalog_registry.json")
    gateway = DataGateway(reg)

    training_ctx = ExecutionContext(
        run_id="TEST_RUN_TRAIN",
        mode=ExecutionMode.TRAINING,
    )

    # vela_smgps_sample has role HOLDOUT
    with pytest.raises(HoldoutLeakageViolationError, match="LEAKAGE DEFENSE SHUTDOWN"):
        gateway.request_dataset("vela_smgps_sample", training_ctx)


def test_holdout_blocked_in_unfrozen_validation():
    reg = CatalogRegistry("datasets/manifests/catalog_registry.json")
    gateway = DataGateway(reg)

    unfrozen_ctx = ExecutionContext(
        run_id="TEST_RUN_VAL_NO_TOKEN",
        mode=ExecutionMode.VALIDATION,
        freeze_token=None,
    )

    with pytest.raises(UnfrozenValidationViolationError, match="INTEGRITY DEFENSE SHUTDOWN"):
        gateway.request_dataset("vela_smgps_sample", unfrozen_ctx)


def test_holdout_allowed_in_frozen_validation():
    reg = CatalogRegistry("datasets/manifests/catalog_registry.json")
    gateway = DataGateway(reg)

    valid_token = "a" * 64  # valid sha256 token length
    frozen_ctx = ExecutionContext(
        run_id="TEST_RUN_VAL_FROZEN",
        mode=ExecutionMode.VALIDATION,
        freeze_token=valid_token,
    )

    df = gateway.request_dataset("vela_smgps_sample", frozen_ctx)
    assert df.height == 4
