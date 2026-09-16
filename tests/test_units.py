"""Test strict unit enforcement."""

import pytest
import astropy.units as u
from astropy.units import Quantity
from research.units.validation import (
    UnspecifiedUnitError,
    IncompatibleUnitError,
    ensure_quantity,
    quantity_to_dict,
    dict_to_quantity,
)


def test_ensure_quantity_success():
    q = 5000.0 * (u.km / u.s)
    res = ensure_quantity(q, u.km / u.s, "velocity")
    assert isinstance(res, Quantity)
    assert res.value == 5000.0
    assert res.unit == u.km / u.s


def test_naked_float_fails():
    with pytest.raises(UnspecifiedUnitError, match="Scientific Rule #2"):
        ensure_quantity(5000.0, u.km / u.s, "velocity")


def test_none_value_fails():
    with pytest.raises(UnspecifiedUnitError, match="Missing required quantity"):
        ensure_quantity(None, u.km / u.s, "velocity")


def test_incompatible_unit_fails():
    q_dist = 50.0 * u.Mpc
    with pytest.raises(IncompatibleUnitError, match="incompatible with required physical dimension"):
        ensure_quantity(q_dist, u.km / u.s, "velocity")


def test_quantity_serialization_roundtrip():
    q = 74.6 * (u.km / (u.s * u.Mpc))
    d = quantity_to_dict(q)
    assert d["value"] == 74.6
    assert "km" in d["unit"]

    q_back = dict_to_quantity(d)
    assert q_back.value == q.value
    assert q_back.unit == q.unit
