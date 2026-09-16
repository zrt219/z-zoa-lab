"""Strict unit enforcement module for Z-ZOA calculations."""

from typing import Any, Union
import astropy.units as u
from astropy.units import Quantity, Unit, UnitBase


class UnspecifiedUnitError(TypeError):
    """Raised when a calculation input lacks mandatory physical units."""
    pass


class IncompatibleUnitError(ValueError):
    """Raised when a quantity has dimensions incompatible with the physical equation."""
    pass


def ensure_quantity(
    val: Any,
    expected_unit: Union[UnitBase, str, None] = None,
    parameter_name: str = "parameter"
) -> Quantity:
    """
    Ensure the provided value is an astropy.units.Quantity.
    Naked floats, ints, or lists without units will raise UnspecifiedUnitError.
    If expected_unit is provided, the quantity will be validated for equivalency.
    """
    if val is None:
        raise UnspecifiedUnitError(f"Missing required quantity for '{parameter_name}'.")

    if not isinstance(val, Quantity):
        raise UnspecifiedUnitError(
            f"Parameter '{parameter_name}' must be an astropy.units.Quantity. "
            f"Got naked type '{type(val).__name__}' ({val}). "
            f"Scientific Rule #2: Units are not optional."
        )

    if expected_unit is not None:
        target_unit = Unit(expected_unit)
        if not val.unit.is_equivalent(target_unit):
            raise IncompatibleUnitError(
                f"Parameter '{parameter_name}' has unit '{val.unit}', which is incompatible "
                f"with required physical dimension '{target_unit}'."
            )

    return val


def quantity_to_dict(q: Quantity) -> dict[str, Any]:
    """Convert an Astropy Quantity to a serialized dict representation."""
    if not isinstance(q, Quantity):
        raise UnspecifiedUnitError("Cannot serialize non-Quantity.")
    val = q.value
    if hasattr(val, "tolist"):
        val = val.tolist()
    elif isinstance(val, (int, float)):
        val = float(val)
    return {
        "value": val,
        "unit": str(q.unit.to_string()),
    }


def dict_to_quantity(d: dict[str, Any]) -> Quantity:
    """Deserialize a dictionary with 'value' and 'unit' into an Astropy Quantity."""
    if not isinstance(d, dict) or "value" not in d or "unit" not in d:
        raise ValueError("Serialized quantity must be a dict with 'value' and 'unit'.")
    unit_obj = Unit(d["unit"])
    return Quantity(d["value"], unit=unit_obj)
