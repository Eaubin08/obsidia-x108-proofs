"""
Obsidia API — FastAPI application. V5B full closure.
All responses: readonly=True, decision_authority=KX108_ONLY.
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

_APP_ENV = os.getenv("APP_ENV", "dev").lower()
_IS_PROD = _APP_ENV not in ("dev", "development")

# Disable interactive docs outside dev environments (F76 prod guard).
_docs_url    = "/docs"        if not _IS_PROD else None
_redoc_url   = "/redoc"       if not _IS_PROD else None
_openapi_url = "/openapi.json" if not _IS_PROD else None

app = FastAPI(
    title="Obsidia X-108 API",
    version="V5B",
    docs_url=_docs_url,
    redoc_url=_redoc_url,
    openapi_url=_openapi_url,
)

# CORS — set ALLOWED_ORIGINS env var for production.
# Dev default: localhost only (no wildcard).
_ALLOWED_ORIGINS_ENV = os.getenv("ALLOWED_ORIGINS", "")
_ALLOWED_ORIGINS = (
    [o.strip() for o in _ALLOWED_ORIGINS_ENV.split(",") if o.strip()]
    if _ALLOWED_ORIGINS_ENV
    else ["http://localhost:3000", "http://localhost:8000", "http://127.0.0.1:8000"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# ── Rate limiting (F76b) ─────────────────────────────────────
import time
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as _Req
from starlette.responses import JSONResponse as _JSONResp

_RATE_LIMIT_ENABLED = (
    _IS_PROD
    or os.getenv("OBSIDIA_RATE_LIMIT_ENABLED", "").lower() == "true"
)


class _RateLimitMiddleware(BaseHTTPMiddleware):
    """Per-IP rate limiting. Active when APP_ENV=prod or OBSIDIA_RATE_LIMIT_ENABLED=true."""

    _EXEMPT = {"/api/health", "/api/readiness", "/api/status", "/"}

    def __init__(self, app_, rpm: int = 60):
        super().__init__(app_)
        self._rpm = rpm
        self._window = 60.0
        self._hits: dict = defaultdict(list)

    async def dispatch(self, request: _Req, call_next):
        if not _RATE_LIMIT_ENABLED or request.url.path in self._EXEMPT:
            return await call_next(request)
        ip = request.client.host if request.client else "unknown"
        now = time.monotonic()
        self._hits[ip] = [t for t in self._hits[ip] if now - t < self._window]
        if len(self._hits[ip]) >= self._rpm:
            return _JSONResp(
                {
                    "error": "rate_limit_exceeded",
                    "retry_after": 60,
                    "decision_authority": "KX108_ONLY",
                    "readonly": True,
                    "emits_act": False,
                },
                status_code=429,
            )
        self._hits[ip].append(now)
        return await call_next(request)


app.add_middleware(_RateLimitMiddleware, rpm=int(os.getenv("RATE_LIMIT_RPM", "60")))

# Import all route modules
from apps.obsidia_api.routes.status import router as status_router
from apps.obsidia_api.routes.brody import router as brody_router
from apps.obsidia_api.routes.translation import router as translation_router
from apps.obsidia_api.routes.os_trad_ir_reverse import router as os_trad_ir_reverse_router
from apps.obsidia_api.routes.context import router as context_router
from apps.obsidia_api.routes.memory import router as memory_router
from apps.obsidia_api.routes.gencoin import router as gencoin_router
from apps.obsidia_api.routes.graphiti import router as graphiti_router
from apps.obsidia_api.routes.x108 import router as x108_router
from apps.obsidia_api.routes.os3 import router as os3_router
from apps.obsidia_api.routes.worldcalls import router as worldcalls_router
from apps.obsidia_api.routes.blockchain import router as blockchain_router
from apps.obsidia_api.routes.audit import router as audit_router
from apps.obsidia_api.routes.periphery_ops import router as periphery_ops_router
from apps.obsidia_api.routes.brody_monitoring import router as brody_monitoring_router
from apps.obsidia_api.routes.runtime_freeze import router as runtime_freeze_router
from apps.obsidia_api.routes.bus import router as bus_router
from apps.obsidia_api.routes.sigma_monitoring import router as sigma_monitoring_router
from apps.obsidia_api.routes.runtime_wiring_preview import router as runtime_wiring_preview_router
from apps.obsidia_api.routes.source_runtime_status import router as source_runtime_status_router
from apps.obsidia_api.routes.os_map import router as os_map_router

for r in [status_router, brody_router, translation_router, os_trad_ir_reverse_router, context_router,
           memory_router, gencoin_router, graphiti_router, x108_router,
           os3_router, worldcalls_router, blockchain_router, audit_router,
           periphery_ops_router, brody_monitoring_router, runtime_freeze_router, bus_router,
           sigma_monitoring_router, runtime_wiring_preview_router, source_runtime_status_router,
           os_map_router]:
    app.include_router(r)


@app.get("/")
async def root():
    return {"service": "obsidia-api", "version": "V5B", "mode": "readonly_dryrun", "decision_authority": "KX108_ONLY"}
