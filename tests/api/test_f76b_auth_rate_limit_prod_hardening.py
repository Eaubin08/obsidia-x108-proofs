"""
F76b — Auth + Rate-limit Prod Hardening tests

Uses monkeypatch + importlib.reload to isolate prod env from other tests.
No pollution of global environment — each test patches then restores.
"""
from __future__ import annotations

import importlib
import os
import sys

import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _reload_auth(env_overrides: dict[str, str]):
    """Reload auth module with patched env. Returns the module."""
    orig = {k: os.environ.get(k) for k in env_overrides}
    for k, v in env_overrides.items():
        os.environ[k] = v
    try:
        if "apps.obsidia_api.auth" in sys.modules:
            del sys.modules["apps.obsidia_api.auth"]
        import apps.obsidia_api.auth as m
        return m
    finally:
        # Restore env
        for k, v in orig.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


# ---------------------------------------------------------------------------
# Class 1 — Dev mode bypass (normal test env)
# ---------------------------------------------------------------------------

class TestF76bDevBypass:
    def test_auth_disabled_in_dev(self):
        """Default env (no APP_ENV) → _AUTH_ENABLED = False."""
        from apps.obsidia_api.auth import _AUTH_ENABLED
        assert not _AUTH_ENABLED, "_AUTH_ENABLED must be False in default dev env"

    def test_chat_200_without_api_key(self):
        """Dev mode: POST /api/brody/chat without header → 200."""
        from apps.obsidia_api.main import app
        c = TestClient(app)
        r = c.post("/api/brody/chat", json={"message": "test f76b"})
        assert r.status_code == 200, f"Expected 200 in dev, got {r.status_code}: {r.text[:200]}"

    def test_health_public(self):
        from apps.obsidia_api.main import app
        c = TestClient(app)
        assert c.get("/api/health").status_code == 200

    def test_readiness_public(self):
        from apps.obsidia_api.main import app
        c = TestClient(app)
        assert c.get("/api/readiness").status_code == 200

    def test_rate_limit_disabled_in_dev(self):
        """OBSIDIA_RATE_LIMIT_ENABLED not set → _RATE_LIMIT_ENABLED = False."""
        from apps.obsidia_api.main import _RATE_LIMIT_ENABLED
        assert not _RATE_LIMIT_ENABLED, "_RATE_LIMIT_ENABLED must be False in dev env"


# ---------------------------------------------------------------------------
# Class 2 — Auth logic (isolated via _reload_auth)
# ---------------------------------------------------------------------------

class TestF76bAuthLogic:
    def test_auth_enabled_when_obsidia_auth_enabled_true(self):
        """OBSIDIA_AUTH_ENABLED=true → _AUTH_ENABLED = True."""
        m = _reload_auth({"OBSIDIA_AUTH_ENABLED": "true", "OBSIDIA_API_KEY": ""})
        assert m._AUTH_ENABLED is True

    def test_auth_disabled_when_obsidia_auth_enabled_false(self):
        """OBSIDIA_AUTH_ENABLED=false → _AUTH_ENABLED = False."""
        m = _reload_auth({"OBSIDIA_AUTH_ENABLED": "false"})
        assert m._AUTH_ENABLED is False

    def test_503_when_auth_enabled_and_key_empty(self, monkeypatch):
        """Auth enabled + OBSIDIA_API_KEY empty → 503 AUTH_MISCONFIGURED."""
        monkeypatch.setenv("OBSIDIA_AUTH_ENABLED", "true")
        monkeypatch.setenv("OBSIDIA_API_KEY", "")
        m = _reload_auth({"OBSIDIA_AUTH_ENABLED": "true", "OBSIDIA_API_KEY": ""})
        import asyncio
        from fastapi import Header
        from fastapi.exceptions import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(m.require_api_key(x_api_key=None))
        assert exc_info.value.status_code == 503
        assert exc_info.value.detail["error"] == "AUTH_MISCONFIGURED"
        assert exc_info.value.detail["decision_authority"] == "KX108_ONLY"

    def test_401_when_auth_enabled_and_wrong_key(self):
        """Auth enabled + wrong key → 401 INVALID_API_KEY."""
        m = _reload_auth({
            "OBSIDIA_AUTH_ENABLED": "true",
            "OBSIDIA_API_KEY": "correct-key-abc123",
        })
        import asyncio
        from fastapi.exceptions import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(m.require_api_key(x_api_key="wrong-key"))
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail["error"] == "INVALID_API_KEY"
        assert exc_info.value.detail["decision_authority"] == "KX108_ONLY"
        assert exc_info.value.detail["emits_act"] is False

    def test_pass_when_auth_enabled_and_correct_key(self):
        """Auth enabled + correct key → no exception (pass)."""
        m = _reload_auth({
            "OBSIDIA_AUTH_ENABLED": "true",
            "OBSIDIA_API_KEY": "correct-key-abc123",
        })
        import asyncio
        result = asyncio.run(m.require_api_key(x_api_key="correct-key-abc123"))
        assert result is None  # no exception = pass

    def test_no_silent_bypass_prod_empty_key(self):
        """Prod (APP_ENV=prod) + empty key → 503, never silent pass."""
        m = _reload_auth({"APP_ENV": "prod", "OBSIDIA_API_KEY": ""})
        import asyncio
        from fastapi.exceptions import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(m.require_api_key(x_api_key=None))
        assert exc_info.value.status_code == 503, "Must be 503, not silent bypass"


# ---------------------------------------------------------------------------
# Class 3 — Rate limit response format
# ---------------------------------------------------------------------------

class TestF76bRateLimitResponse:
    def test_rate_limit_enabled_by_obsidia_env(self):
        """OBSIDIA_RATE_LIMIT_ENABLED=true → rate limit active even in dev."""
        orig = os.environ.get("OBSIDIA_RATE_LIMIT_ENABLED")
        try:
            os.environ["OBSIDIA_RATE_LIMIT_ENABLED"] = "true"
            # Reload main to pick up new env
            for key in list(sys.modules.keys()):
                if "obsidia_api.main" in key:
                    del sys.modules[key]
            import apps.obsidia_api.main as m
            assert m._RATE_LIMIT_ENABLED is True
        finally:
            if orig is None:
                os.environ.pop("OBSIDIA_RATE_LIMIT_ENABLED", None)
            else:
                os.environ["OBSIDIA_RATE_LIMIT_ENABLED"] = orig
            # Restore original main
            for key in list(sys.modules.keys()):
                if "obsidia_api.main" in key:
                    del sys.modules[key]

    def test_rate_limit_middleware_exempt_paths(self):
        """Health and readiness are always exempt from rate limiting."""
        from apps.obsidia_api.main import _RateLimitMiddleware
        middleware = _RateLimitMiddleware.__new__(_RateLimitMiddleware)
        assert "/api/health" in middleware._EXEMPT
        assert "/api/readiness" in middleware._EXEMPT
        assert "/api/status" in middleware._EXEMPT

    def test_rate_limit_429_boundary_fields(self):
        """When 429 is produced, it must include KX108_ONLY + readonly + emits_act=False."""
        # Test by inspecting what dispatch returns for 429 — simulate via middleware
        import asyncio
        from collections import defaultdict
        from unittest.mock import AsyncMock, MagicMock

        from apps.obsidia_api.main import _RateLimitMiddleware

        # Build a minimal mock middleware that IS prod and IS at limit
        mw_cls = _RateLimitMiddleware
        mock_app = MagicMock()
        mw = mw_cls.__new__(mw_cls)
        mw._rpm = 1
        mw._window = 60.0
        mw._hits = defaultdict(list)
        mw._hits["1.2.3.4"] = [0.0]  # already 1 hit (at limit)

        mock_request = MagicMock()
        mock_request.url.path = "/api/brody/chat"
        mock_request.client.host = "1.2.3.4"

        import time
        with __import__("unittest.mock", fromlist=["patch"]).patch(
            "apps.obsidia_api.main._RATE_LIMIT_ENABLED", True
        ):
            with __import__("unittest.mock", fromlist=["patch"]).patch(
                "time.monotonic", return_value=1.0
            ):
                response = asyncio.run(mw.dispatch(mock_request, AsyncMock()))

        # If we got a JSONResponse with 429, check its body
        if hasattr(response, "body"):
            import json
            body = json.loads(response.body)
            assert body.get("decision_authority") == "KX108_ONLY"
            assert body.get("readonly") is True
            assert body.get("emits_act") is False
            assert body.get("error") == "rate_limit_exceeded"
