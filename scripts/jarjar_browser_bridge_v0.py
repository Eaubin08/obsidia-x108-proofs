"""
jarjar_browser_bridge_v0.py -- Authority-free Obsidia -> JarJar browser executor bridge.

No governance. No URL policy. No KX108.
Physical execution evidence only.
"""
from __future__ import annotations
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))


class JarJarBrowserExecutor:
    """
    Thin executor wrapping JarJar BrowserBackend.
    Authority-free: callers (Obsidia governance layer) own all policy.
    """

    EXECUTOR_PROVIDER = "JARJAR"
    EXECUTOR_BACKEND  = "BrowserBackend"

    def __init__(self, browser_backend):
        self._backend = browser_backend

    def read_browser_state(self) -> dict:
        """Read current page identity + state. No navigation. No text content."""
        from jarvis.contracts import ActionRequest
        result = self._backend.execute(ActionRequest("browser.read", {}))
        if not result.ok:
            return {"ok": False, "error": "READ_BROWSER_STATE_FAILED:" + result.message,
                    "executor": self.EXECUTOR_BACKEND}
        data = result.data or {}
        return {
            "ok": True,
            "browser_session_id": data.get("browser_session_id") or "",
            "page_id":            data.get("page_id") or "",
            "url":                data.get("url"),
            "origin":             data.get("origin"),
            "title":              data.get("title"),
            "closed":             data.get("closed"),
            "executor":           self.EXECUTOR_BACKEND,
        }

    def read_page(self, selector=None) -> dict:
        """Read page content with identity. Returns text for governed read."""
        from jarvis.contracts import ActionRequest
        args = {}
        if selector is not None:
            args["selector"] = selector
        result = self._backend.execute(ActionRequest("browser.read", args))
        if not result.ok:
            return {"ok": False, "error": "READ_PAGE_FAILED:" + result.message,
                    "executor": self.EXECUTOR_BACKEND}
        data = result.data or {}
        return {
            "ok": True,
            "browser_session_id": data.get("browser_session_id") or "",
            "page_id":            data.get("page_id") or "",
            "url":                data.get("url"),
            "origin":             data.get("origin"),
            "title":              data.get("title"),
            "closed":             data.get("closed"),
            "text":               data.get("text"),
            "element_count":      data.get("element_count"),
            "selector":           data.get("selector"),
            "executor":           self.EXECUTOR_BACKEND,
        }

    def navigate(self, requested_url: str) -> dict:
        """Execute physical navigation. Returns execution evidence only."""
        from jarvis.contracts import ActionRequest
        result = self._backend.execute(
            ActionRequest("browser.navigate", {"url": requested_url}))
        if not result.ok:
            return {"ok": False, "error": "NAVIGATE_FAILED:" + result.message,
                    "executor": self.EXECUTOR_BACKEND}
        data = result.data or {}
        return {"ok": True,
                "nav_url":    data.get("url"),
                "nav_status": data.get("status"),
                "nav_title":  data.get("title"),
                "executor":   self.EXECUTOR_BACKEND}
