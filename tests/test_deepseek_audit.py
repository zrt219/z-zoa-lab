"""Tests for the DeepSeek client and the audit-findings writer.

The default path here never touches the network: no key is configured in CI,
so everything must degrade softly and the writer must still exit 0.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from research.llm import deepseek

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import write_audit_findings as waf  # noqa: E402


@pytest.fixture
def no_key(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.setattr(deepseek, "_load_dotenv", lambda path=None: None)
    return monkeypatch


def test_unconfigured_reports_false(no_key):
    assert deepseek.is_configured() is False
    assert deepseek.api_key() is None


def test_chat_without_key_returns_none(no_key):
    assert deepseek.chat([{"role": "user", "content": "hello"}]) is None


def test_chat_network_failure_returns_none_not_raises(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-not-a-real-key-000000")
    monkeypatch.setattr(deepseek, "_load_dotenv", lambda path=None: None)
    monkeypatch.setenv("DEEPSEEK_BASE_URL", "http://127.0.0.1:9")  # discard port
    assert deepseek.chat([{"role": "user", "content": "x"}], timeout_s=1.0) is None


def test_redact_scrubs_configured_key(monkeypatch):
    secret = "sk-abcdefghijklmnopqrstuvwxyz"
    monkeypatch.setenv("DEEPSEEK_API_KEY", secret)
    monkeypatch.setattr(deepseek, "_load_dotenv", lambda path=None: None)
    scrubbed = deepseek.redact(f"leaked {secret} here")
    assert secret not in scrubbed
    assert "[REDACTED]" in scrubbed


def test_findings_json_is_valid_and_complete():
    findings = json.loads(waf.FINDINGS_JSON.read_text(encoding="utf-8"))
    for key in ("audit_id", "summary", "gate_status", "findings", "confirmed_sound", "not_verified"):
        assert key in findings, f"missing required key: {key}"

    ids = [f["id"] for f in findings["findings"]]
    assert len(ids) == len(set(ids)), "duplicate finding IDs"

    for f in findings["findings"]:
        for key in ("id", "severity", "title", "status", "evidence", "impact", "recommendation"):
            assert f.get(key), f"{f.get('id')} missing {key}"
        assert f["status"] in {"VERIFIED", "OBSERVED", "DOC_MISMATCH"}
        assert f["severity"] in {"high", "medium", "low"}


def test_gate_status_does_not_claim_a_clean_pass():
    """Guard the AGENTS.md 3.5 invariant: exit 1 must never be reported as PASSED."""
    findings = json.loads(waf.FINDINGS_JSON.read_text(encoding="utf-8"))
    gate = findings["gate_status"]
    assert gate["raw_exit_code"] != 0
    md = waf.render_markdown(findings, None)
    assert "Raw exit code | **1**" in md
    assert "Explicit non-claim" in md


def test_render_is_deterministic():
    findings = json.loads(waf.FINDINGS_JSON.read_text(encoding="utf-8"))
    assert waf.render_markdown(findings, None) == waf.render_markdown(findings, None)


def test_offline_record_exits_zero(no_key):
    assert waf.main([]) == 0


def test_enrich_without_key_still_exits_zero(no_key):
    assert waf.main(["--enrich"]) == 0


def test_dry_run_makes_no_api_call(monkeypatch):
    calls: list = []
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-not-a-real-key-000000")
    monkeypatch.setattr(deepseek, "_load_dotenv", lambda path=None: None)
    monkeypatch.setattr(deepseek, "enrich_audit", lambda *a, **k: calls.append(1) or "should not run")
    assert waf.main(["--enrich", "--dry-run"]) == 0
    assert calls == []


def test_enrichment_appended_as_advisory_appendix():
    findings = json.loads(waf.FINDINGS_JSON.read_text(encoding="utf-8"))
    md = waf.render_markdown(findings, "The auditor notes two high-severity items.")
    assert "Appendix A" in md
    assert "advisory, non-authoritative" in md
    assert md.index("## 3. Findings") < md.index("Appendix A")


def test_check_mode_passes_on_written_report(no_key):
    assert waf.main([]) == 0
    assert waf.main(["--check"]) == 0
