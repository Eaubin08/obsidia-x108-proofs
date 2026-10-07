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

    def inspect_link(self, selector: str) -> dict:
        """Inspect one candidate link. No activation, no generic click."""
        from jarvis.contracts import ActionRequest
        result = self._backend.execute(
            ActionRequest("browser.inspect_element", {"selector": selector}))
        if not result.ok:
            return {"ok": False, "error": "INSPECT_LINK_FAILED:" + result.message,
                    "executor": self.EXECUTOR_BACKEND}
        data = result.data or {}
        out = {"ok": True, "executor": self.EXECUTOR_BACKEND}
        out.update(data)
        return out

    def activate_link(self, link_identity: dict) -> dict:
        """Activate an approved link identity. This is not click(selector)."""
        from jarvis.contracts import ActionRequest
        result = self._backend.execute(
            ActionRequest("browser.activate_link", dict(link_identity or {})))
        if not result.ok:
            return {"ok": False, "error": "ACTIVATE_LINK_FAILED:" + result.message,
                    "executor": self.EXECUTOR_BACKEND}
        data = result.data or {}
        out = {"ok": True, "executor": self.EXECUTOR_BACKEND}
        out.update(data)
        return out

    def inspect_disclosure(self, selector: str) -> dict:
        """Inspect one supported disclosure target. No activation."""
        from jarvis.contracts import ActionRequest
        result = self._backend.execute(
            ActionRequest("browser.inspect_disclosure", {"selector": selector}))
        if not result.ok:
            return {"ok": False, "error": "INSPECT_DISCLOSURE_FAILED:" + result.message,
                    "executor": self.EXECUTOR_BACKEND}
        data = result.data or {}
        out = {"ok": True, "executor": self.EXECUTOR_BACKEND}
        out.update(data)
        return out

    def set_disclosure(self, disclosure_identity: dict, target_expanded: bool) -> dict:
        """Set an approved disclosure target state. This is not click(selector)."""
        from jarvis.contracts import ActionRequest
        args = dict(disclosure_identity or {})
        args["target_expanded"] = target_expanded
        result = self._backend.execute(ActionRequest("browser.set_disclosure", args))
        if not result.ok:
            return {"ok": False, "error": "SET_DISCLOSURE_FAILED:" + result.message,
                    "executor": self.EXECUTOR_BACKEND}
        data = result.data or {}
        out = {"ok": True, "executor": self.EXECUTOR_BACKEND}
        out.update(data)
        return out

    def inspect_checkbox(self, selector: str) -> dict:
        """Inspect one supported checkbox target. No mutation."""
        from jarvis.contracts import ActionRequest
        result = self._backend.execute(
            ActionRequest("browser.inspect_checkbox", {"selector": selector}))
        if not result.ok:
            return {"ok": False, "error": "INSPECT_CHECKBOX_FAILED:" + result.message,
                    "executor": self.EXECUTOR_BACKEND}
        data = result.data or {}
        out = {"ok": True, "executor": self.EXECUTOR_BACKEND}
        out.update(data)
        return out

    def set_checkbox(self, checkbox_identity: dict, target_checked: bool) -> dict:
        """Set an approved checkbox target state. This is not click(selector)."""
        from jarvis.contracts import ActionRequest
        args = dict(checkbox_identity or {})
        args["target_checked"] = target_checked
        result = self._backend.execute(ActionRequest("browser.set_checked", args))
        if not result.ok:
            return {"ok": False, "error": "SET_CHECKBOX_FAILED:" + result.message,
                    "executor": self.EXECUTOR_BACKEND}
        data = result.data or {}
        out = {"ok": True, "executor": self.EXECUTOR_BACKEND}
        out.update(data)
        return out

    def inspect_radio(self, selector: str) -> dict:
        """Inspect one supported radio target. No mutation."""
        from jarvis.contracts import ActionRequest
        result = self._backend.execute(
            ActionRequest("browser.inspect_radio", {"selector": selector}))
        if not result.ok:
            return {"ok": False, "error": "INSPECT_RADIO_FAILED:" + result.message,
                    "executor": self.EXECUTOR_BACKEND}
        data = result.data or {}
        out = {"ok": True, "executor": self.EXECUTOR_BACKEND}
        out.update(data)
        return out

    def select_radio(self, radio_identity: dict) -> dict:
        """Select an approved radio target. This is not click(selector)."""
        from jarvis.contracts import ActionRequest
        result = self._backend.execute(ActionRequest("browser.select_radio", dict(radio_identity or {})))
        if not result.ok:
            return {"ok": False, "error": "SELECT_RADIO_FAILED:" + result.message,
                    "executor": self.EXECUTOR_BACKEND}
        data = result.data or {}
        out = {"ok": True, "executor": self.EXECUTOR_BACKEND}
        out.update(data)
        return out

    def inspect_select(self, selector: str) -> dict:
        """Inspect one supported select target. No mutation."""
        from jarvis.contracts import ActionRequest
        result = self._backend.execute(
            ActionRequest("browser.inspect_select", {"selector": selector}))
        if not result.ok:
            return {"ok": False, "error": "INSPECT_SELECT_FAILED:" + result.message,
                    "executor": self.EXECUTOR_BACKEND}
        data = result.data or {}
        out = {"ok": True, "executor": self.EXECUTOR_BACKEND}
        out.update(data)
        return out

    def select_option(self, select_identity: dict, option_identity: dict) -> dict:
        """Select an approved option target. This is not a generic select/click."""
        from jarvis.contracts import ActionRequest
        args = dict(select_identity or {})
        args["option_identity"] = dict(option_identity or {})
        result = self._backend.execute(ActionRequest("browser.select_option", args))
        if not result.ok:
            return {"ok": False, "error": "SELECT_OPTION_FAILED:" + result.message,
                    "executor": self.EXECUTOR_BACKEND}
        data = result.data or {}
        out = {"ok": True, "executor": self.EXECUTOR_BACKEND}
        out.update(data)
        return out

    def inspect_field(self, selector: str) -> dict:
        """Inspect one supported text field target. No mutation and no plaintext value."""
        from jarvis.contracts import ActionRequest
        result = self._backend.execute(
            ActionRequest("browser.inspect_field", {"selector": selector}))
        if not result.ok:
            return {"ok": False, "error": "INSPECT_FIELD_FAILED:" + result.message,
                    "executor": self.EXECUTOR_BACKEND}
        data = result.data or {}
        out = {"ok": True, "executor": self.EXECUTOR_BACKEND}
        out.update(data)
        return out

    def set_field_value(self, field_identity: dict, target_value: str) -> dict:
        """Set an approved field value. This is not generic fill/submit."""
        from jarvis.contracts import ActionRequest
        args = dict(field_identity or {})
        args["target_value"] = target_value
        result = self._backend.execute(ActionRequest("browser.set_field_value", args))
        if not result.ok:
            return {"ok": False, "error": "SET_FIELD_VALUE_FAILED:" + result.message,
                    "executor": self.EXECUTOR_BACKEND}
        data = result.data or {}
        out = {"ok": True, "executor": self.EXECUTOR_BACKEND}
        out.update(data)
        return out

    def inspect_form_submission(self, form_selector: str, submitter_selector: str) -> dict:
        """Inspect one bounded GET form submission target. No mutation."""
        from jarvis.contracts import ActionRequest
        result = self._backend.execute(ActionRequest("browser.inspect_form_submission", {
            "form_selector": form_selector,
            "submitter_selector": submitter_selector,
        }))
        if not result.ok:
            return {"ok": False, "error": "INSPECT_FORM_SUBMISSION_FAILED:" + result.message,
                    "executor": self.EXECUTOR_BACKEND}
        data = result.data or {}
        out = {"ok": True, "executor": self.EXECUTOR_BACKEND}
        out.update(data)
        return out

    def submit_get_navigation(self, form_submission_identity: dict) -> dict:
        """Activate an approved GET form submitter. This is not generic submit/click."""
        from jarvis.contracts import ActionRequest
        result = self._backend.execute(
            ActionRequest("browser.submit_get_navigation", dict(form_submission_identity or {})))
        if not result.ok:
            return {"ok": False, "error": "SUBMIT_GET_NAVIGATION_FAILED:" + result.message,
                    "executor": self.EXECUTOR_BACKEND,
                    "execution_state": "NOT_DISPATCHED"}
        data = result.data or {}
        out = {"ok": True, "executor": self.EXECUTOR_BACKEND}
        out.update(data)
        return out

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
