"""
SecretBoundary — ensures no secret is ever exposed to an agent or LLM.
Gateway only access. Secrets stay inside the boundary.
"""
from __future__ import annotations

_REDACTED = "[REDACTED_BY_SECRET_BOUNDARY]"

_SECRET_KEYS = {
    "api_key", "secret", "token", "password", "credential",
    "private_key", "auth", "bearer", "access_key", "secret_key",
    "client_secret", "webhook_secret", "signing_key",
}


def redact_secrets(payload: dict) -> dict:
    result = {}
    for k, v in payload.items():
        if any(sk in k.lower() for sk in _SECRET_KEYS):
            result[k] = _REDACTED
        elif isinstance(v, dict):
            result[k] = redact_secrets(v)
        else:
            result[k] = v
    return result


def assert_no_secret_in_agent_payload(payload: dict) -> None:
    for k in payload:
        if any(sk in k.lower() for sk in _SECRET_KEYS):
            if payload[k] != _REDACTED:
                raise AssertionError(f"SECRET_BOUNDARY_VIOLATION:key={k}")
