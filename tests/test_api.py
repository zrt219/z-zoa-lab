"""Test FastAPI backend routes."""

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_api_health():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "astropy" in data["versions"]


def test_api_list_catalogs():
    res = client.get("/catalogs/")
    assert res.status_code == 200
    datasets = res.json()
    assert len(datasets) >= 3
    ids = [d["dataset_id"] for d in datasets]
    assert "cf4_sample" in ids
    assert "vela_smgps_sample" in ids


def test_api_inspect_holdout_forbidden_in_training():
    res = client.get("/catalogs/vela_smgps_sample/inspect?mode=TRAINING")
    assert res.status_code == 403
    assert "LEAKAGE DEFENSE" in res.json()["detail"]


def test_api_inspect_holdout_allowed_in_frozen_validation():
    valid_token = "0" * 64
    res = client.get(f"/catalogs/vela_smgps_sample/inspect?mode=VALIDATION&freeze_token={valid_token}")
    assert res.status_code == 200
    data = res.json()
    assert data["total_rows"] == 4


def test_api_calculate_peculiar_velocity():
    payload = {
        "cz_kms": 5801.0,
        "distance_mpc": 71.42,
        "cosmology_name": "CF4_NOMINAL",
        "method": "linear",
    }
    res = client.post("/calculate/peculiar-velocity", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert abs(data["v_pec"]["value"] - 473.0) < 1.0
    assert data["v_pec"]["unit"] == "km / s"


def test_api_coordinate_transform():
    payload = {
        "source_frame": "ICRS",
        "lon_deg": 0.0,
        "lat_deg": 0.0,
        "distance_mpc": 100.0,
    }
    res = client.post("/calculate/transform-coordinates", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "galactic" in data
    assert "supergalactic" in data
    assert "cartesian_xyz" in data


def test_api_ledger_status():
    res = client.get("/ledger/status")
    assert res.status_code == 200
    data = res.json()
    assert data["network"] == "XRPL Testnet"
    assert data["network_id"] == 1
    assert "DEVELOPMENT RECORD" in data["disclaimer"]


def test_api_ledger_receipt_not_found():
    res = client.get("/ledger/receipt/NONEXISTENT_RUN_999")
    assert res.status_code == 404


def test_api_reconstruction_differential():
    res = client.get("/reconstruction/runs/VELA-001/differential?downsample_step=2")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert data["run_id"] == "VELA-001"
    assert "summary" in data
    assert "delta_density" in data["summary"]
    assert "delta_sigma" in data["summary"]
    assert "delta_velocity" in data["summary"]
    assert data["summary"]["delta_density"]["min"] < data["summary"]["delta_density"]["max"]
    assert "voxels" in data
    assert len(data["voxels"]) > 0
    assert "strict_readonly_safety" in data
    assert data["holdout_authorized"] is True
    assert len(data["holdout_galaxies"]) == 39


