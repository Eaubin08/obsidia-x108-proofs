"""
audit_middleware.py
--------------------
Async monitoring middleware for Obsidia V5B.
Captures: status, latency, route, gate_decision, extra_metrics.
Persists to audit_logs/ via asyncio background task — NEVER blocks HTTP response.
decision_authority = KX108_ONLY.
"""
from __future__ import annotations

import asyncio
import json
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from periphery.event_bus import get_bus, EventEnvelope, EventType

_LOG_DIR = Path("audit_logs")
_LOG_DIR.mkdir(parents=True, exist_ok=True)

_BOUNDARY = {
    "readonly": True,
    "emits_act": False,
    "memory_write": False,
    "decision_authority": "KX108_ONLY",
}

_SKIP_PATHS = {"/", "/health", "/docs", "/openapi.json", "/redoc"}


def _log_path() -> Path:
    date = datetime.now(timezone.utc).strftime("%Y%m%d")
    return _LOG_DIR / f"http_audit_{date}.jsonl"


def _write_entry(entry: dict) -> None:
    line = json.dumps(entry, ensure_ascii=False) + "\n"
    with open(_log_path(), "a", encoding="utf-8") as fh:
        fh.write(line)


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Starlette/FastAPI middleware.
    Records request metadata + response status/latency asynchronously.
    The HTTP response is returned BEFORE the audit write task completes.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path in _SKIP_PATHS:
            return await call_next(request)

        trace_id = str(uuid.uuid4())
        t0 = time.monotonic()

        response = await call_next(request)

        latency_ms = round((time.monotonic() - t0) * 1000, 2)
        status = response.status_code

        entry = {
            "trace_id": trace_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "method": request.method,
            "path": request.url.path,
            "status": status,
            "latency_ms": latency_ms,
            "gate_decision": "NONE",
            "extra_metrics": {
                "client": request.client.host if request.client else "unknown",
                "query": str(request.query_params) or "",
            },
            **_BOUNDARY,
        }

        # Publish to bus (non-blocking) — BrodyBridge and SigmaObserver receive this
        env = EventEnvelope(
            topic="http.audit",
            event_type=EventType.AUDIT,
            source="AuditMiddleware",
            payload=entry,
            trace_id=trace_id,
        )
        get_bus().publish_nowait(env)

        asyncio.create_task(_async_write(entry))
        return response


async def _async_write(entry: dict) -> None:
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _write_entry, entry)
