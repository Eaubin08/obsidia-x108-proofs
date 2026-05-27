"""Readonly HTTP client for ObsidiaShell Graphiti V20 frozen gateway.

This module never writes to Graphiti, Neo4j, memory, kernel, or X108.
It only reads frozen context from the local ObsidiaShell gateway when available.
"""

from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from typing import Any


DEFAULT_GRAPHITI_V20_BASE = "http://127.0.0.1:8011"


def graphiti_v20_base_url() -> str:
    return os.getenv("GRAPHITI_V20_HTTP_BASE", DEFAULT_GRAPHITI_V20_BASE).rstrip("/")


def _readonly_envelope(payload: dict[str, Any], *, proxy_source: str) -> dict[str, Any]:
    data = dict(payload)
    data.setdefault("readonly", True)
    data.setdefault("advisory_only", True)
    data.setdefault("emits_act", False)
    data.setdefault("emits_verdict", False)
    data.setdefault("decision_authority", "KX108_ONLY")
    data.setdefault("memory_write", False)
    data.setdefault("kernel_mutation", False)
    data.setdefault("x108_mutation", False)
    data.setdefault("graphiti_write", False)
    data.setdefault("neo4j_write", False)
    data.setdefault("real_action", False)
    data.setdefault("proxy_source", proxy_source)
    return data


def graphiti_v20_get(path: str, params: dict[str, Any] | None = None, timeout: float = 2.5) -> dict[str, Any] | None:
    """GET JSON from ObsidiaShell Graphiti V20. Return None if unavailable."""
    base = graphiti_v20_base_url()
    query = ""
    if params:
        clean_params = {k: v for k, v in params.items() if v is not None}
        query = "?" + urllib.parse.urlencode(clean_params)

    url = f"{base}{path}{query}"

    try:
        req = urllib.request.Request(url, method="GET", headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
        payload = json.loads(raw.decode("utf-8"))
        if isinstance(payload, dict):
            return _readonly_envelope(payload, proxy_source="GRAPHITI_V20_HTTP")
        return _readonly_envelope({"payload": payload}, proxy_source="GRAPHITI_V20_HTTP")
    except Exception as exc:
        return _readonly_envelope(
            {
                "ok": False,
                "source": "GRAPHITI_V20_HTTP_UNAVAILABLE",
                "error": type(exc).__name__,
                "message": str(exc),
            },
            proxy_source="BACKEND_STUB",
        )


def graphiti_v20_available(payload: dict[str, Any] | None) -> bool:
    if not payload:
        return False
    if payload.get("proxy_source") != "GRAPHITI_V20_HTTP":
        return False
    if payload.get("ok") is False:
        return False
    return True
