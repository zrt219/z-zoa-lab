"""Holdout protection module for Z-ZOA."""

from research.holdouts.exceptions import (
    HoldoutSecurityError,
    HoldoutLeakageViolationError,
    UnfrozenValidationViolationError,
    UnauthorizedComparisonViolationError,
    AnchorVerificationHoldoutViolationError,
)
from research.holdouts.guard import (
    ExecutionMode,
    ExecutionContext,
    DataGateway,
    reveal_holdout,
)

__all__ = [
    "HoldoutSecurityError",
    "HoldoutLeakageViolationError",
    "UnfrozenValidationViolationError",
    "UnauthorizedComparisonViolationError",
    "AnchorVerificationHoldoutViolationError",
    "ExecutionMode",
    "ExecutionContext",
    "DataGateway",
    "reveal_holdout",
]
