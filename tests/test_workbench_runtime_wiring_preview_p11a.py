# tests/test_workbench_runtime_wiring_preview_p11a.py
# P11A — Workbench UI Preview Bridge tests.
# Static checks on HTML/TSX files + API route smoke. No browser. No build step.
# KX108_ONLY. READONLY_PREVIEW_ONLY. FAIL_CLOSED.

from __future__ import annotations

import ast
import pathlib

import pytest

_REPO = pathlib.Path(__file__).resolve().parent.parent
_HTML  = _REPO / "apps" / "obsidia-workbench" / "runtime_wiring_preview.html"
_VIEW  = _REPO / "apps" / "obsidia-workbench" / "src" / "views" / "RuntimeWiringPreviewView.tsx"
_APP   = _REPO / "apps" / "obsidia-workbench" / "src" / "App.tsx"
_SIDEBAR = _REPO / "apps" / "obsidia-workbench" / "src" / "components" / "LeftSidebar.tsx"
_VITE  = _REPO / "apps" / "obsidia-workbench" / "vite.config.ts"


# ══════════════════════════════════════════════════════════════════════════════
# 1. test_api_preview_endpoint_still_imports
# ══════════════════════════════════════════════════════════════════════════════

def test_api_preview_endpoint_still_imports():
    """API preview route module still imports cleanly after P11A changes."""
    from apps.obsidia_api.routes.runtime_wiring_preview import router
    from fastapi import APIRouter
    assert isinstance(router, APIRouter)
    paths = [r.path for r in router.routes]
    assert "/api/runtime-wiring/preview" in paths


# ══════════════════════════════════════════════════════════════════════════════
# 2. test_ui_preview_file_exists
# ══════════════════════════════════════════════════════════════════════════════

def test_ui_preview_file_exists():
    """Both the standalone HTML and the React view must exist."""
    assert _HTML.exists(), f"Missing: {_HTML}"
    assert _VIEW.exists(), f"Missing: {_VIEW}"


# ══════════════════════════════════════════════════════════════════════════════
# 3. test_ui_preview_mentions_kx108_only
# ══════════════════════════════════════════════════════════════════════════════

def test_ui_preview_mentions_kx108_only():
    """Both UI files must mention KX108_ONLY."""
    html_src = _HTML.read_text(encoding="utf-8")
    tsx_src  = _VIEW.read_text(encoding="utf-8")
    assert "KX108_ONLY" in html_src, "HTML does not mention KX108_ONLY"
    assert "KX108_ONLY" in tsx_src,  "TSX does not mention KX108_ONLY"


# ══════════════════════════════════════════════════════════════════════════════
# 4. test_ui_preview_mentions_no_act
# ══════════════════════════════════════════════════════════════════════════════

def test_ui_preview_mentions_no_act():
    """Both UI files must contain 'No ACT' or similar explicit no-act notice."""
    html_src = _HTML.read_text(encoding="utf-8")
    tsx_src  = _VIEW.read_text(encoding="utf-8")
    assert "No ACT" in html_src or "no act" in html_src.lower(), \
        "HTML does not contain explicit No ACT notice"
    assert "No ACT" in tsx_src or "no act" in tsx_src.lower(), \
        "TSX does not contain explicit No ACT notice"


# ══════════════════════════════════════════════════════════════════════════════
# 5. test_ui_preview_mentions_runtime_active_false
# ══════════════════════════════════════════════════════════════════════════════

def test_ui_preview_mentions_runtime_active_false():
    """UI files must reference 'runtime_active' and not claim it is true."""
    html_src = _HTML.read_text(encoding="utf-8")
    tsx_src  = _VIEW.read_text(encoding="utf-8")
    assert "runtime_active" in html_src, "HTML does not reference runtime_active"
    assert "runtime_active" in tsx_src,  "TSX does not reference runtime_active"
    # Must never assert runtime_active = true as a positive display value
    assert "runtime_active: true" not in html_src
    assert "runtime_active: true" not in tsx_src


# ══════════════════════════════════════════════════════════════════════════════
# 6. test_ui_preview_mentions_allow_context_only_and_hold
# ══════════════════════════════════════════════════════════════════════════════

def test_ui_preview_mentions_allow_context_only_and_hold():
    """UI files must reference both ALLOW_CONTEXT_ONLY and HOLD decisions."""
    html_src = _HTML.read_text(encoding="utf-8")
    tsx_src  = _VIEW.read_text(encoding="utf-8")
    assert "ALLOW_CONTEXT_ONLY" in html_src, "HTML missing ALLOW_CONTEXT_ONLY"
    assert "HOLD"                in html_src, "HTML missing HOLD"
    assert "ALLOW_CONTEXT_ONLY" in tsx_src,  "TSX missing ALLOW_CONTEXT_ONLY"
    assert "HOLD"                in tsx_src,  "TSX missing HOLD"


# ══════════════════════════════════════════════════════════════════════════════
# 7. test_ui_preview_does_not_import_source_packs
# ══════════════════════════════════════════════════════════════════════════════

def test_ui_preview_does_not_import_source_packs():
    """UI files must not reference _source_packs."""
    html_src = _HTML.read_text(encoding="utf-8")
    tsx_src  = _VIEW.read_text(encoding="utf-8")
    assert "_source_packs" not in html_src, "HTML references _source_packs"
    assert "_source_packs" not in tsx_src,  "TSX references _source_packs"


# ══════════════════════════════════════════════════════════════════════════════
# 8. test_ui_preview_does_not_reference_zip_extraction_true
# ══════════════════════════════════════════════════════════════════════════════

def test_ui_preview_does_not_reference_zip_extraction_true():
    """UI files must not claim zip_extraction = true."""
    html_src = _HTML.read_text(encoding="utf-8")
    tsx_src  = _VIEW.read_text(encoding="utf-8")
    assert "zip_extraction: true" not in html_src
    assert "zip_extraction: true" not in tsx_src
    assert "zip_extraction=true"  not in html_src
    assert "zip_extraction=true"  not in tsx_src


# ══════════════════════════════════════════════════════════════════════════════
# 9. test_no_packages_created
# ══════════════════════════════════════════════════════════════════════════════

def test_no_packages_created():
    """packages/ must not exist at repo root."""
    assert not (_REPO / "packages").exists(), "packages/ boundary violation"


# ══════════════════════════════════════════════════════════════════════════════
# 10. test_existing_api_preview_tests_still_pass_reference
# ══════════════════════════════════════════════════════════════════════════════

def test_existing_api_preview_tests_still_pass_reference():
    """P10D test file must still exist and parse cleanly."""
    p10d = _REPO / "tests" / "test_api_runtime_wiring_preview_p10d.py"
    assert p10d.exists(), "test_api_runtime_wiring_preview_p10d.py is missing"
    ast.parse(p10d.read_text(encoding="utf-8"), filename=str(p10d))


# ══════════════════════════════════════════════════════════════════════════════
# Extra: workbench integration checks
# ══════════════════════════════════════════════════════════════════════════════

def test_app_tsx_imports_runtime_wiring_view():
    """App.tsx must import RuntimeWiringPreviewView."""
    app_src = _APP.read_text(encoding="utf-8")
    assert "RuntimeWiringPreviewView" in app_src, \
        "App.tsx does not import RuntimeWiringPreviewView"
    assert "runtime-wiring" in app_src, \
        "App.tsx does not render runtime-wiring view"


def test_sidebar_includes_runtime_wiring_viewid():
    """LeftSidebar.tsx ViewId type must include 'runtime-wiring'."""
    sidebar_src = _SIDEBAR.read_text(encoding="utf-8")
    assert "runtime-wiring" in sidebar_src, \
        "LeftSidebar.tsx does not include 'runtime-wiring' in ViewId"


def test_vite_config_has_runtime_wiring_proxy():
    """vite.config.ts must include a proxy for /api/runtime-wiring."""
    vite_src = _VITE.read_text(encoding="utf-8")
    assert "/api/runtime-wiring" in vite_src, \
        "vite.config.ts does not proxy /api/runtime-wiring"


def test_html_preview_fetches_correct_endpoint():
    """HTML standalone must fetch /api/runtime-wiring/preview."""
    html_src = _HTML.read_text(encoding="utf-8")
    assert "/api/runtime-wiring/preview" in html_src


def test_tsx_view_fetches_correct_endpoint():
    """React view must reference /api/runtime-wiring/preview."""
    tsx_src = _VIEW.read_text(encoding="utf-8")
    assert "/api/runtime-wiring/preview" in tsx_src


def test_html_safety_flags_referenced():
    """HTML must reference all six safety lock labels."""
    html_src = _HTML.read_text(encoding="utf-8")
    for flag in ("zip_extraction", "source_pack_import", "world_action",
                 "memory_write", "graph_write", "packages_created"):
        assert flag in html_src, f"HTML missing safety flag: {flag}"


def test_tsx_safety_flags_referenced():
    """React TSX must reference the six safety lock labels."""
    tsx_src = _VIEW.read_text(encoding="utf-8")
    for flag in ("zip_extraction", "source_pack_import", "world_action",
                 "memory_write", "graph_write", "packages_created"):
        assert flag in tsx_src, f"TSX missing safety flag: {flag}"
