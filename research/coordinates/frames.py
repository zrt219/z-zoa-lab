"""Coordinate frame enumerations and definitions for Z-ZOA."""

from enum import Enum


class CoordinateFrame(str, Enum):
    ICRS = "ICRS"
    GALACTIC = "GALACTIC"
    SUPERGALACTIC = "SUPERGALACTIC"
    CARTESIAN_ICRS = "CARTESIAN_ICRS"
    CARTESIAN_GALACTIC = "CARTESIAN_GALACTIC"
    CARTESIAN_SUPERGALACTIC = "CARTESIAN_SUPERGALACTIC"
