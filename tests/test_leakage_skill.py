"""Unit tests for the z-zoa-leakage-audit skill and CLI."""

from pathlib import Path
import subprocess
import sys
import pytest


@pytest.fixture
def repo_root():
    return Path(__file__).resolve().parent.parent


def test_leakage_skill_cli_quarantine_check(repo_root):
    cli_path = repo_root / ".agents" / "skills" / "z-zoa-leakage-audit" / "scripts" / "z_zoa_leakage_audit_cli.py"
    assert cli_path.exists()

    res = subprocess.run(
        [sys.executable, str(cli_path), "quarantine-check"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0
    assert '"quarantine_status": "CLEAN"' in res.stdout
    assert '"quarantined_count": 39' in res.stdout


def test_leakage_skill_cli_attack_sim(repo_root):
    cli_path = repo_root / ".agents" / "skills" / "z-zoa-leakage-audit" / "scripts" / "z_zoa_leakage_audit_cli.py"

    res = subprocess.run(
        [sys.executable, str(cli_path), "attack-sim"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0
    assert '"rehearsal_result": "ALL_ATTACKS_BLOCKED"' in res.stdout
    assert '"attacks_blocked": 4' in res.stdout


def test_leakage_skill_cli_verify_cert(repo_root):
    cli_path = repo_root / ".agents" / "skills" / "z-zoa-leakage-audit" / "scripts" / "z_zoa_leakage_audit_cli.py"

    res = subprocess.run(
        [sys.executable, str(cli_path), "verify-cert"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0
    assert '"status": "VALID"' in res.stdout
    assert '"tests_passed": 18' in res.stdout
