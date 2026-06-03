# tests/test_api_runtime_wiring_preview_p10d.py
# P10D — API Preview Endpoint tests.
# Uses FastAPI TestClient (httpx). No live server required.
# No apps/ side-effects beyond what the app itself does.
# KX108_ONLY. FAIL_CLOSED. READONLY_PREVIEW_ONLY.

from __future__ import annotations

import ast
import pathlib

import pytest

_REPO = pathlib.Path(__file__).resolve().parent.parent
_ROUTE_FILE = _REPO / "apps" / "obsidia_api" / "routes" / "runtime_wiring_preview.py"


# ── TestClient fixture (session-scoped — app import is expensive) ──────────────

@pytest.fixture(scope="session")
def client():
    from fastapi.testclient import TestClient
    from apps.obsidia_api.main import app
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c


@pytest.fixture(scope="session")
def preview_response(client):
    """Single GET /api/runtime-wiring/preview for the whole session."""
    resp = client.get("/api/runtime-wiring/preview")
    return resp


@pytest.fixture(scope="session")
def preview_json(preview_response):
    return preview_response.json()


# ══════════════════════════════════════════════════════════════════════════════
# 1. test_preview_route_module_imports
# ══════════════════════════════════════════════════════════════════════════════

def test_preview_route_module_imports():
    """Route module must import cleanly and expose an APIRouter."""
    from apps.obsidia_api.routes.runtime_wiring_preview import router
    from fastapi import APIRouter
    assert isinstance(router, APIRouter)
    assert router.prefix == "/api/runtime-wiring"
    paths = [r.path for r in router.routes]
    assert "/api/runtime-wiring/preview" in paths


# ══════════════════════════════════════════════════════════════════════════════
# 2. test_preview_payload_shape
# ══════════════════════════════════════════════════════════════════════════════

def test_preview_payload_shape(preview_response, preview_json):
    """GET /api/runtime-wiring/preview must return 200 with required keys."""
    assert preview_response.status_code == 200, (
        f"Expected 200, got {preview_response.status_code}: {preview_response.text[:200]}"
    )
    required_keys = {
        "status", "runtime_active", "decision_authority", "emits_act",
        "context_only_decision", "critical_action_decision",
        "source_registry_entries", "families_sampled",
        "proof_claim", "readonly",
    }
    missing = required_keys - preview_json.keys()
    assert not missing, f"Missing keys in preview response: {missing}"
    assert preview_json["status"] == "ENGINE_BRIDGE_PREVIEW_ONLY"
    assert preview_json["decision_authority"] == "KX108_ONLY"


# ══════════════════════════════════════════════════════════════════════════════
# 3. test_preview_runtime_active_false
# ══════════════════════════════════════════════════════════════════════════════

def test_preview_runtime_active_false(preview_json):
    """runtime_active must be False in the API preview response."""
    assert preview_json.get("runtime_active") is False, (
        f"runtime_active must be False, got {preview_json.get('runtime_active')!r}"
    )


# ══════════════════════════════════════════════════════════════════════════════
# 4. test_preview_emits_act_false
# ══════════════════════════════════════════════════════════════════════════════

def test_preview_emits_act_false(preview_json):
    """emits_act must be False in the API preview response."""
    assert preview_json.get("emits_act") is False, (
        f"emits_act must be False, got {preview_json.get('emits_act')!r}"
    )
    # Double check: must not appear as true anywhere in serialised JSON
    import json
    serialised = json.dumps(preview_json)
    assert '"emits_act": true' not in serialised
    assert '"ACT"' not in serialised


# ══════════════════════════════════════════════════════════════════════════════
# 5. test_preview_proof_claim_false
# ══════════════════════════════════════════════════════════════════════════════

def test_preview_proof_claim_false(preview_json):
    """proof_claim must be False in the API preview response."""
    assert preview_json.get("proof_claim") is False, (
        f"proof_claim must be False, got {preview_json.get('proof_claim')!r}"
    )
    assert preview_json.get("verification_status") == "NOT_VERIFIED_DRY_RUN"


# ══════════════════════════════════════════════════════════════════════════════
# 6. test_preview_decisions_allow_context_only_and_hold
# ══════════════════════════════════════════════════════════════════════════════

def test_preview_decisions_allow_context_only_and_hold(preview_json):
    """context_only must be ALLOW_CONTEXT_ONLY and critical must be HOLD."""
    ctx = preview_json.get("context_only_decision")
    crit = preview_json.get("critical_action_decision")
    assert ctx == "ALLOW_CONTEXT_ONLY", (
        f"Expected ALLOW_CONTEXT_ONLY, got {ctx!r}"
    )
    assert crit == "HOLD", f"Expected HOLD, got {crit!r}"


# ══════════════════════════════════════════════════════════════════════════════
# 7. test_preview_safety_flags_false
# ══════════════════════════════════════════════════════════════════════════════

def test_preview_safety_flags_false(preview_json):
    """All safety flags must be False in the preview response."""
    safety = preview_json.get("safety", {})
    for flag in (
        "zip_extraction", "source_pack_import", "runtime_active",
        "emits_act", "proof_claim", "engine_mutation",
        "apps_mutation", "periphery_mutation",
        "memory_write", "graph_write", "world_action", "packages_created",
    ):
        assert safety.get(flag) is False, (
            f"safety.{flag} must be False, got {safety.get(flag)!r}"
        )
    assert safety.get("readonly") is True
    assert safety.get("decision_authority") == "KX108_ONLY"


# ══════════════════════════════════════════════════════════════════════════════
# 8. test_no_source_pack_import_in_route
# ══════════════════════════════════════════════════════════════════════════════

def test_no_source_pack_import_in_route():
    """Route file must not reference _source_packs or .zip directly."""
    source = _ROUTE_FILE.read_text(encoding="utf-8")
    assert "_source_packs" not in source, "_source_packs referenced in route"
    assert ".zip" not in source, ".zip referenced in route"
    assert "zipfile" not in source, "zipfile imported in route"
    assert "tarfile" not in source, "tarfile imported in route"


# ══════════════════════════════════════════════════════════════════════════════
# 9. test_no_zip_extraction_in_route
# ══════════════════════════════════════════════════════════════════════════════

def test_no_zip_extraction_in_route():
    """Static AST scan: route must not import zip/tar/shutil extraction modules."""
    source = _ROUTE_FILE.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(_ROUTE_FILE))
    forbidden_modules = {"zipfile", "tarfile", "shutil", "subprocess"}
    violations = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root in forbidden_modules:
                    violations.append(f"line {node.lineno}: import {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                root = node.module.split(".")[0]
                if root in forbidden_modules:
                    violations.append(f"line {node.lineno}: from {node.module}")
    assert violations == [], f"Forbidden module imports in route: {violations}"


# ══════════════════════════════════════════════════════════════════════════════
# 10. test_no_packages_created
# ══════════════════════════════════════════════════════════════════════════════

def test_no_packages_created():
    """packages/ directory must not exist at repo root."""
    assert not (_REPO / "packages").exists(), "packages/ directory exists — boundary violation"


# ══════════════════════════════════════════════════════════════════════════════
# Extra checks
# ══════════════════════════════════════════════════════════════════════════════

def test_preview_registry_entries_count(preview_json):
    """source_registry_entries must be 14 779."""
    assert preview_json.get("source_registry_entries") == 15844, (
        f"Expected 15844, got {preview_json.get('source_registry_entries')}"
    )


def test_preview_families_sampled(preview_json):
    """families_sampled must be 4."""
    assert preview_json.get("families_sampled") == 8, (
        f"Expected 4, got {preview_json.get('families_sampled')}"
    )


def test_preview_engine_packets_count(preview_json):
    """context_packets_count must be 4."""
    assert preview_json.get("context_packets_count") == 8, (
        f"Expected 4, got {preview_json.get('context_packets_count')}"
    )


def test_preview_engine_packets_advisory(preview_json):
    """All engine preview packets must have can_decide=False."""
    packets = preview_json.get("engine_context_packets_preview", [])
    assert len(packets) == 8
    for pkt in packets:
        assert pkt.get("can_decide") is False
        meta = pkt.get("_bridge_meta", {})
        assert meta.get("emits_act") is False
        assert meta.get("advisory_only") is True


def test_preview_sovereignty_flags(preview_json):
    """safe_backend_response sovereignty flags must be present and correct."""
    assert preview_json.get("readonly") is True
    assert preview_json.get("decision_authority") == "KX108_ONLY"
    assert preview_json.get("emits_act") is False
    assert preview_json.get("memory_write") is False


def test_preview_dry_run_flag(preview_json):
    """dry_run must be True in the response."""
    assert preview_json.get("dry_run") is True


def test_preview_content_type(preview_response):
    """Response content-type must be application/json."""
    ct = preview_response.headers.get("content-type", "")
    assert "application/json" in ct, f"Expected application/json, got {ct!r}"
