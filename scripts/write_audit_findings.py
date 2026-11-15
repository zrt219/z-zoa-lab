"""Record Z-ZOA repository audit findings, optionally enriched by DeepSeek.

This script deliberately separates two concerns:

  * ``record``  - deterministically write/refresh the machine-readable findings
                  JSON and its Markdown sibling.  Works fully offline; exit 0.
  * ``enrich``  - attach a DeepSeek-written executive summary as an appendix.
                  Optional.  Fails soft: if no key is configured or the API call
                  fails, the deterministic report is still produced and the
                  script exit code is unaffected.

The enrichment text is NEVER allowed to state a pass/fail verdict, and it is
never used to compute a number.

Usage
-----
    python scripts/write_audit_findings.py                 # offline record only
    python scripts/write_audit_findings.py --enrich        # + DeepSeek appendix
    python scripts/write_audit_findings.py --enrich --dry-run   # show prompt, no call
    python scripts/write_audit_findings.py --check         # verify files are current
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "docs"
FINDINGS_JSON = DOCS_DIR / "REPO_AUDIT_FINDINGS.json"
FINDINGS_MD = DOCS_DIR / "REPO_AUDIT_FINDINGS.md"

GENERATED_MARKER = "<!-- Z-ZOA-AUDIT-GENERATED: do not edit by hand; run scripts/write_audit_findings.py -->"


def load_findings() -> Dict[str, Any]:
    if not FINDINGS_JSON.exists():
        raise SystemExit(f"Findings source missing: {FINDINGS_JSON}")
    return json.loads(FINDINGS_JSON.read_text(encoding="utf-8"))


def render_markdown(findings: Dict[str, Any], enrichment: str | None) -> str:
    gate = findings["gate_status"]
    lines: list[str] = [
        GENERATED_MARKER,
        "",
        f"# Z-ZOA Repository Audit Findings",
        "",
        f"**Audit ID**: `{findings['audit_id']}`  ",
        f"**Date**: {findings['audit_date']}  ",
        f"**Machine-readable sibling**: [`REPO_AUDIT_FINDINGS.json`](REPO_AUDIT_FINDINGS.json)  ",
        "",
        "> **Verification legend** - `VERIFIED` = independently recomputed or observed by "
        "running a command in the audit session. `OBSERVED` = read from a stored artifact "
        "without re-execution. `DOC_MISMATCH` = two tracked documents contradict each other.",
        "",
        "---",
        "",
        "## 1. Summary",
        "",
        findings["summary"],
        "",
        "---",
        "",
        "## 2. Gate status",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| Raw exit code | **{gate['raw_exit_code']}** |",
        f"| Passed | {gate['passed']} |",
        f"| Errors | {gate['errors']} |",
        f"| Failed | {gate['failed']} |",
        f"| Root cause | {gate['root_cause']} |",
        f"| Test functions on disk | {gate['actual_test_function_count']} |",
        f"| README claims | \"{gate['claim_in_readme']}\" |",
        f"| `AGENTS.md` claims | \"{gate['claim_in_agents_md']}\" |",
        "",
        "**Explicit non-claim**: the erroring tests were **not** independently confirmed passing.",
        "",
        "---",
        "",
        "## 3. Findings",
        "",
        "| ID | Severity | Status | Title |",
        "|---|---|---|---|",
    ]
    for f in findings["findings"]:
        lines.append(f"| {f['id']} | {f['severity']} | {f['status']} | {f['title']} |")

    lines += ["", "### Detail", ""]
    for f in findings["findings"]:
        lines += [
            f"#### {f['id']} - {f['title']}",
            "",
            f"**Status**: `{f['status']}`  **Severity**: `{f['severity']}`",
            "",
            f"**Evidence**: {f['evidence']}",
            "",
            f"**Impact**: {f['impact']}",
            "",
            f"**Recommendation**: {f['recommendation']}",
            "",
        ]

    lines += [
        "---",
        "",
        "## 4. What was confirmed sound",
        "",
        "| Claim | Status | Detail |",
        "|---|---|---|",
    ]
    for c in findings["confirmed_sound"]:
        lines.append(f"| {c['claim']} | **{c['status']}** | {c['detail']} |")

    lines += ["", "---", "", "## 5. Not verified in this audit", ""]
    lines += [f"- {item}" for item in findings["not_verified"]]

    lines += ["", "---", "", "## 6. Recommended order of work", ""]
    ordered = sorted(
        findings["findings"],
        key=lambda f: {"high": 0, "medium": 1, "low": 2}.get(f["severity"], 3),
    )
    for i, f in enumerate(ordered, start=1):
        lines.append(f"{i}. **{f['id']}** ({f['severity']}) - {f['recommendation']}")

    if enrichment:
        lines += [
            "",
            "---",
            "",
            "## Appendix A - DeepSeek executive summary (advisory, non-authoritative)",
            "",
            "> This section is machine-generated prose. It is **not** evidence and carries no "
            "verdict authority. The findings above are the record of truth.",
            "",
            enrichment.strip(),
            "",
        ]

    return "\n".join(lines) + "\n"


def write_report(enrichment: str | None) -> None:
    findings = load_findings()
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    if enrichment:
        findings["deepseek_enrichment"] = {
            "present": True,
            "advisory_only": True,
            "text": enrichment.strip(),
        }
        FINDINGS_JSON.write_text(
            json.dumps(findings, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    md = render_markdown(findings, enrichment)
    FINDINGS_MD.write_text(md, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--enrich", action="store_true", help="Add a DeepSeek-written appendix")
    parser.add_argument("--dry-run", action="store_true", help="With --enrich: print prompt, no API call")
    parser.add_argument("--check", action="store_true", help="Verify the Markdown matches the JSON")
    args = parser.parse_args(argv)

    if args.check:
        findings = load_findings()
        expected = render_markdown(findings, None)
        if not FINDINGS_MD.exists():
            print(f"STALE: {FINDINGS_MD.name} does not exist", file=sys.stderr)
            return 1
        actual = FINDINGS_MD.read_text(encoding="utf-8")
        if GENERATED_MARKER in actual and actual != expected:
            print("STALE: Markdown does not match the JSON findings source", file=sys.stderr)
            return 1
        print("CURRENT: findings Markdown matches its JSON source")
        return 0

    enrichment: str | None = None
    if args.enrich:
        if str(REPO_ROOT) not in sys.path:
            sys.path.insert(0, str(REPO_ROOT))
        from research.llm import deepseek

        if not deepseek.is_configured():
            print(
                "NOTE: DEEPSEEK_API_KEY not set; writing deterministic report without enrichment.\n"
                "      Copy .env.example to .env and set the key to enable the appendix.",
                file=sys.stderr,
            )
        elif args.dry_run:
            print("DRY RUN: would send the findings JSON to DeepSeek; no API call made.")
            print(f"       key present: yes  model: {__import__('os').environ.get('DEEPSEEK_MODEL', 'deepseek-chat')}")
        else:
            findings = load_findings()
            enrichment = deepseek.enrich_audit(findings)
            if enrichment is None:
                print(
                    "NOTE: DeepSeek call failed or returned no content; "
                    "writing deterministic report without enrichment.",
                    file=sys.stderr,
                )
            else:
                enrichment = deepseek.redact(enrichment)

    write_report(enrichment)
    print(f"Wrote {FINDINGS_MD.relative_to(REPO_ROOT)}")
    print(f"Source {FINDINGS_JSON.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
