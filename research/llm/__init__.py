"""LLM-assisted analysis utilities for Z-ZOA.

The DeepSeek client here is advisory-only: it can enrich human-readable audit
narrative, but it never produces a numerical result, a pass/fail verdict, or a
process exit code.
"""

from research.llm.deepseek import (
    api_key,
    chat,
    enrich_audit,
    is_configured,
    redact,
)

__all__ = ["api_key", "chat", "enrich_audit", "is_configured", "redact"]
