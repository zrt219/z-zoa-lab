"""Holdout security and boundary enforcement exceptions."""


class HoldoutSecurityError(Exception):
    """Base exception for holdout boundary violations."""
    pass


class HoldoutLeakageViolationError(HoldoutSecurityError, PermissionError):
    """
    CRITICAL VIOLATION: An experiment in TRAINING or RECONSTRUCTION mode
    attempted to access a protected HOLDOUT catalogue.
    """
    pass


class UnfrozenValidationViolationError(HoldoutSecurityError, PermissionError):
    """
    VIOLATION: An attempt was made to access a HOLDOUT catalogue in VALIDATION mode
    without supplying a valid cryptographic freeze token from a prior training run.
    """
    pass


class UnauthorizedComparisonViolationError(HoldoutSecurityError, PermissionError):
    """
    VIOLATION: An attempt was made to include COMPARISON_ONLY data (e.g. official grids)
    into a training / reconstruction pipeline.
    """
    pass


class AnchorVerificationHoldoutViolationError(HoldoutSecurityError, PermissionError):
    """
    CRITICAL ANCHOR VIOLATION: An attempt was made to access or reveal a HOLDOUT catalogue
    for an experiment requiring XRPL anchoring before PREDICTION_FROZEN validation on ledger.
    """
    pass


class UnphysicalCosmologyError(ValueError):
    """
    CRITICAL COSMOLOGICAL SCALE SANITY VIOLATION:
    Peculiar velocities v_pec exceed physical cosmic infall limits (v_rms in [300, 600] km/s,
    v_max <= 2,500 km/s, or v > 0.01c).
    """
    pass

