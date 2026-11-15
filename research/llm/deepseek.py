"""DeepSeek chat-completions client for Z-ZOA audit reporting.

Design constraints (deliberate, do not relax without discussion):

1. The API key is read from the environment ONLY.  It is never written to a
   file, never logged, and never included in an exception message.
2. Every failure mode (missing key, network error, timeout, malformed
   response) degrades to returning ``None`` so callers fall back to their
   deterministic offline path.  A missing key must never break a pipeline.
3. Enrichment text is advisory only.  It is never used to produce a
   numerical result, a pass/fail verdict, or an exit code.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-chat"
DEFAULT_TIMEOUT_S = 60.0


def _load_dotenv(path: Optional[Path] = None) -> None:
    """Load simple KEY=VALUE lines from .env without overriding real env vars."""
    candidate = path or Path(__file__).resolve().parents[2] / ".env"
    if not candidate.exists():
        return
    try:
        for raw in candidate.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and value and key not in os.environ:
                os.environ[key] = value
    except OSError:
        # An unreadable .env is not fatal; env vars alone are sufficient.
        return


def api_key() -> Optional[str]:
    """Return the configured DeepSeek key, or None.  Never logs the value."""
    _load_dotenv()
    key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    return key or None


def is_configured() -> bool:
    return api_key() is not None


def redact(text: str, key: Optional[str] = None) -> str:
    """Defensive scrub so a key can never reach a log or a saved report."""
    secret = key or api_key()
    if secret and len(secret) >= 8:
        return text.replace(secret, "[REDACTED]")
    return text


def chat(
    messages: List[Dict[str, str]],
    *,
    model: Optional[str] = None,
    temperature: float = 0.2,
    max_tokens: int = 2000,
    timeout_s: float = DEFAULT_TIMEOUT_S,
) -> Optional[str]:
    """Send a chat completion request to DeepSeek.

    Returns the assistant text on success, or ``None`` on any failure.
    Never raises for network/key problems.
    """
    key = api_key()
    if not key:
        return None

    base = os.environ.get("DEEPSEEK_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    model_name = model or os.environ.get("DEEPSEEK_MODEL", DEFAULT_MODEL)

    try:
        import httpx
    except ImportError:
        return None

    payload: Dict[str, Any] = {
        "model": model_name,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }

    try:
        with httpx.Client(timeout=timeout_s) as client:
            resp = client.post(
                f"{base}/chat/completions",
                headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            if resp.status_code != 200:
                return None
            data = resp.json()
            return data["choices"][0]["message"]["content"]
    except Exception as exc:  # noqa: BLE001 - deliberate: degrade, never crash
        # Scrub defensively in case a httpx message echoes request headers.
        _ = redact(str(exc))
        return None


def enrich_audit(findings_json: Dict[str, Any]) -> Optional[str]:
    """Ask DeepSeek for a short executive summary of an audit findings object.

    Returns None when unconfigured or when the call fails.
    """
    system = (
        "You are an external scientific-software auditor. You will receive a JSON "
        "findings record for a cosmology research codebase. Write a concise "
        "executive summary (max 180 words) in plain prose. Rules: state only what "
        "the JSON supports; do not invent numbers; preserve each finding's "
        "verification status; never describe the repository as passing, verified, "
        "or publication-ready unless every listed gate is clean. Flag the highest "
        "risk item first."
    )
    user = json.dumps(findings_json, indent=2)
    return chat(
        [
            {"role": "system", "content": system},
            {"role": "user", "content": f"Audit findings JSON:\n\n{user}"},
        ]
    )
