"""Tests for the new reconstruction, validation, and reproducibility endpoints."""

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_3d_volume_endpoint():
    res = client.get("/reconstruction/3d-volume?box_size=300")
    assert res.status_code == 200
    data = res.json()
    assert "hi_points" in data
    assert "velocity_vectors" in data
    assert "streamlines" in data
    assert "galaxies" in data
    assert len(data["hi_points"]) > 100
    assert len(data["velocity_vectors"]) > 10
    assert len(data["streamlines"]) > 0


def test_reconstruction_run_endpoint():
    req = {
        "run_id": "TEST_RECON_01",
        "n_realizations": 5,
        "base_seed": 42,
        "threshold": 1.0,
    }
    res = client.post("/reconstruction/run", json=req)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "COMPLETED"
    assert "mean_field_stats" in data


def test_validation_endpoints():
    # Leakage status
    res = client.get("/validation/leakage-status")
    assert res.status_code == 200
    data = res.json()
    assert data["final_status"] == "PASS"

    # Freeze & reveal scoring (tested on a dedicated test run ID to avoid mutating production VELA-001)
    res_fr = client.post("/validation/freeze-reveal", json={"run_id": "TEST-FR-ROUTE", "n_null_samples": 50})
    assert res_fr.status_code == 200
    d_fr = res_fr.json()
    assert d_fr["status"] in ["REVEALED_AND_SCORED", "VALIDATION_CONFIRMED"]
    assert "statistical_significance" in d_fr
    assert "z_score" in d_fr["statistical_significance"]

    # Mock test
    res_mock = client.post("/validation/mock-test", json={"n_galaxies": 200, "seed": 42})
    assert res_mock.status_code == 200
    assert res_mock.json()["status"] == "MOCK_VALIDATION_PASSED"


def test_reproducibility_endpoints():
    res_m = client.get("/reproducibility/manuscript")
    assert res_m.status_code == 200
    assert "latex" in res_m.json()
    assert "markdown" in res_m.json()

    res_audit = client.get("/reproducibility/audit")
    assert res_audit.status_code == 200
    assert len(res_audit.json()["items"]) > 0

    res_b = client.get("/reproducibility/bundle")
    assert res_b.status_code == 200
    assert res_b.headers["content-type"] == "application/zip"
    assert len(res_b.content) > 500
