"""Calculation routes exposing cosmological and kinematic kernels."""

from fastapi import APIRouter, HTTPException
import astropy.units as u
from research.cosmology.models import COSMOLOGY_PRESETS
from research.velocities.peculiar import calculate_peculiar_velocity
from research.coordinates.transforms import (
    icrs_to_galactic,
    galactic_to_icrs,
    galactic_to_supergalactic,
    supergalactic_to_galactic,
    spherical_to_cartesian,
)
from research.coordinates.frames import CoordinateFrame
from backend.schemas.api_models import PeculiarVelocityRequest, CoordinateTransformRequest

router = APIRouter(prefix="/calculate", tags=["calculate"])


@router.post("/peculiar-velocity")
def compute_vpec(req: PeculiarVelocityRequest):
    if req.cosmology_name not in COSMOLOGY_PRESETS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown cosmology '{req.cosmology_name}'. Valid: {list(COSMOLOGY_PRESETS.keys())}",
        )

    cosmo = COSMOLOGY_PRESETS[req.cosmology_name]
    cz_q = req.cz_kms * (u.km / u.s)
    dist_q = req.distance_mpc * u.Mpc
    cz_err_q = (req.cz_err_kms * (u.km / u.s)) if req.cz_err_kms is not None else None
    dist_err_q = (req.distance_err_mpc * u.Mpc) if req.distance_err_mpc is not None else None

    try:
        res = calculate_peculiar_velocity(
            cz=cz_q,
            distance=dist_q,
            cosmo=cosmo,
            method=req.method,
            cz_err=cz_err_q,
            distance_err=dist_err_q,
            mu_err=req.mu_err,
        )
        return res.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/transform-coordinates")
def transform_coords(req: CoordinateTransformRequest):
    lon_q = req.lon_deg * u.deg
    lat_q = req.lat_deg * u.deg
    dist_q = (req.distance_mpc * u.Mpc) if req.distance_mpc is not None else None

    frame = req.source_frame.upper()

    try:
        if frame == "ICRS":
            l, b, d = icrs_to_galactic(lon_q, lat_q, dist_q)
            sgl, sgb, _ = galactic_to_supergalactic(l, b, d)
            res = {
                "source": {"frame": "ICRS", "ra_deg": req.lon_deg, "dec_deg": req.lat_deg},
                "galactic": {"l_deg": round(l.value, 6), "b_deg": round(b.value, 6)},
                "supergalactic": {"sgl_deg": round(sgl.value, 6), "sgb_deg": round(sgb.value, 6)},
            }
        elif frame == "GALACTIC":
            ra, dec, d = galactic_to_icrs(lon_q, lat_q, dist_q)
            sgl, sgb, _ = galactic_to_supergalactic(lon_q, lat_q, dist_q)
            res = {
                "source": {"frame": "GALACTIC", "l_deg": req.lon_deg, "b_deg": req.lat_deg},
                "icrs": {"ra_deg": round(ra.value, 6), "dec_deg": round(dec.value, 6)},
                "supergalactic": {"sgl_deg": round(sgl.value, 6), "sgb_deg": round(sgb.value, 6)},
            }
        elif frame == "SUPERGALACTIC":
            l, b, d = supergalactic_to_galactic(lon_q, lat_q, dist_q)
            ra, dec, _ = galactic_to_icrs(l, b, d)
            res = {
                "source": {"frame": "SUPERGALACTIC", "sgl_deg": req.lon_deg, "sgb_deg": req.lat_deg},
                "galactic": {"l_deg": round(l.value, 6), "b_deg": round(b.value, 6)},
                "icrs": {"ra_deg": round(ra.value, 6), "dec_deg": round(dec.value, 6)},
            }
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported frame '{req.source_frame}'")

        if dist_q is not None:
            x, y, z = spherical_to_cartesian(lon_q, lat_q, dist_q, frame=CoordinateFrame[frame])
            res["cartesian_xyz"] = {
                "x_mpc": round(x.value, 4),
                "y_mpc": round(y.value, 4),
                "z_mpc": round(z.value, 4),
            }

        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
