"""Astronomical coordinate transformation kernels using Astropy."""

from typing import Optional, Tuple
import astropy.units as u
from astropy.coordinates import (
    SkyCoord,
    ICRS,
    Galactic,
    Supergalactic,
    CartesianRepresentation,
)
from astropy.units import Quantity

from research.units.validation import ensure_quantity
from research.coordinates.frames import CoordinateFrame


def icrs_to_galactic(
    ra: Quantity,
    dec: Quantity,
    distance: Optional[Quantity] = None
) -> Tuple[Quantity, Quantity, Optional[Quantity]]:
    """Transform ICRS equatorial coordinates (RA, Dec) to Galactic coordinates (l, b)."""
    ra = ensure_quantity(ra, u.deg, "ra")
    dec = ensure_quantity(dec, u.deg, "dec")
    if distance is not None:
        distance = ensure_quantity(distance, u.Mpc, "distance")
        coord = SkyCoord(ra=ra, dec=dec, distance=distance, frame="icrs")
        gal = coord.galactic
        return gal.l.to(u.deg), gal.b.to(u.deg), gal.distance.to(distance.unit)

    coord = SkyCoord(ra=ra, dec=dec, frame="icrs")
    gal = coord.galactic
    return gal.l.to(u.deg), gal.b.to(u.deg), None


def galactic_to_icrs(
    l: Quantity,
    b: Quantity,
    distance: Optional[Quantity] = None
) -> Tuple[Quantity, Quantity, Optional[Quantity]]:
    """Transform Galactic coordinates (l, b) to ICRS equatorial (RA, Dec)."""
    l = ensure_quantity(l, u.deg, "l")
    b = ensure_quantity(b, u.deg, "b")
    if distance is not None:
        distance = ensure_quantity(distance, u.Mpc, "distance")
        coord = SkyCoord(l=l, b=b, distance=distance, frame="galactic")
        icrs = coord.icrs
        return icrs.ra.to(u.deg), icrs.dec.to(u.deg), icrs.distance.to(distance.unit)

    coord = SkyCoord(l=l, b=b, frame="galactic")
    icrs = coord.icrs
    return icrs.ra.to(u.deg), icrs.dec.to(u.deg), None


def galactic_to_supergalactic(
    l: Quantity,
    b: Quantity,
    distance: Optional[Quantity] = None
) -> Tuple[Quantity, Quantity, Optional[Quantity]]:
    """Transform Galactic coordinates (l, b) to Supergalactic coordinates (SGL, SGB)."""
    l = ensure_quantity(l, u.deg, "l")
    b = ensure_quantity(b, u.deg, "b")
    if distance is not None:
        distance = ensure_quantity(distance, u.Mpc, "distance")
        coord = SkyCoord(l=l, b=b, distance=distance, frame="galactic")
        sg = coord.supergalactic
        return sg.sgl.to(u.deg), sg.sgb.to(u.deg), sg.distance.to(distance.unit)

    coord = SkyCoord(l=l, b=b, frame="galactic")
    sg = coord.supergalactic
    return sg.sgl.to(u.deg), sg.sgb.to(u.deg), None


def supergalactic_to_galactic(
    sgl: Quantity,
    sgb: Quantity,
    distance: Optional[Quantity] = None
) -> Tuple[Quantity, Quantity, Optional[Quantity]]:
    """Transform Supergalactic coordinates (SGL, SGB) to Galactic coordinates (l, b)."""
    sgl = ensure_quantity(sgl, u.deg, "sgl")
    sgb = ensure_quantity(sgb, u.deg, "sgb")
    if distance is not None:
        distance = ensure_quantity(distance, u.Mpc, "distance")
        coord = SkyCoord(sgl=sgl, sgb=sgb, distance=distance, frame="supergalactic")
        gal = coord.galactic
        return gal.l.to(u.deg), gal.b.to(u.deg), gal.distance.to(distance.unit)

    coord = SkyCoord(sgl=sgl, sgb=sgb, frame="supergalactic")
    gal = coord.galactic
    return gal.l.to(u.deg), gal.b.to(u.deg), None


def spherical_to_cartesian(
    lon: Quantity,
    lat: Quantity,
    distance: Quantity,
    frame: CoordinateFrame = CoordinateFrame.GALACTIC
) -> Tuple[Quantity, Quantity, Quantity]:
    """
    Transform spherical coordinates (lon, lat, distance) into 3D Cartesian coordinates.
    Returns (x, y, z) in distance units.
    """
    lon = ensure_quantity(lon, u.deg, "lon")
    lat = ensure_quantity(lat, u.deg, "lat")
    distance = ensure_quantity(distance, u.Mpc, "distance")

    if frame == CoordinateFrame.ICRS:
        coord = SkyCoord(ra=lon, dec=lat, distance=distance, frame="icrs")
    elif frame == CoordinateFrame.GALACTIC:
        coord = SkyCoord(l=lon, b=lat, distance=distance, frame="galactic")
    elif frame == CoordinateFrame.SUPERGALACTIC:
        coord = SkyCoord(sgl=lon, sgb=lat, distance=distance, frame="supergalactic")
    else:
        raise ValueError(f"Unsupported frame for spherical to cartesian conversion: {frame}")

    cart = coord.cartesian
    return cart.x.to(distance.unit), cart.y.to(distance.unit), cart.z.to(distance.unit)


def cartesian_to_spherical(
    x: Quantity,
    y: Quantity,
    z: Quantity,
    frame: CoordinateFrame = CoordinateFrame.GALACTIC
) -> Tuple[Quantity, Quantity, Quantity]:
    """
    Transform 3D Cartesian coordinates (x, y, z) back to spherical (lon, lat, distance).
    Returns (lon, lat, distance) as Quantities.
    """
    x = ensure_quantity(x, u.Mpc, "x")
    y = ensure_quantity(y, u.Mpc, "y")
    z = ensure_quantity(z, u.Mpc, "z")

    cart = CartesianRepresentation(x=x, y=y, z=z)
    if frame == CoordinateFrame.ICRS:
        coord = SkyCoord(cart, frame="icrs")
        return coord.ra.to(u.deg), coord.dec.to(u.deg), coord.distance.to(x.unit)
    elif frame == CoordinateFrame.GALACTIC:
        coord = SkyCoord(cart, frame="galactic")
        return coord.l.to(u.deg), coord.b.to(u.deg), coord.distance.to(x.unit)
    elif frame == CoordinateFrame.SUPERGALACTIC:
        coord = SkyCoord(cart, frame="supergalactic")
        return coord.sgl.to(u.deg), coord.sgb.to(u.deg), coord.distance.to(x.unit)
    else:
        raise ValueError(f"Unsupported frame for cartesian to spherical conversion: {frame}")
