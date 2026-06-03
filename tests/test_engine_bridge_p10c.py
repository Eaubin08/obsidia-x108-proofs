# tests/test_engine_bridge_p10c.py
# P10C — Engine Bridge Readonly Adapter tests.
# Verifies: import isolation, safety invariants, bridge output, API preview.
# No apps/ import. No periphery/ import. No network. No filesystem write.
# KX108_ONLY. FAIL_CLOSED.

from __future__ import annotations

import ast
import pathlib
import subprocess
import sys

import pytest

# ── Repo root path ─────────────────────────────────────────────────────────────
_REPO = pathlib.Path(__file__).resolve().parent.parent
_BRIDGE_DIR = _REPO / "runtime_wiring" / "engine_bridge"
_BRIDGE_PY_FILES = [
    _BRIDGE_DIR / "__init__.py",
    _BRIDGE_DIR / "bridge_types.py",
    _BRIDGE_DIR / "readonly_engine_bridge.py",
    _BRIDGE_DIR / "api_adapter_preview.py",
]

# ── Lazy-load bridge preview (session-scoped, expensive due to 14MB registry) ──

@pytest.fixture(scope="session")
def engine_bridge_preview():
    """Build one EngineBridgePreview for the full session."""
    from runtime_wiring.engine_bridge.readonly_engine_bridge import build_engine_bridge_preview
    return build_engine_bridge_preview()


@pytest.fixture(scope="session")
def api_payload(engine_bridge_preview):
    """Extract the API preview payload from the session-scoped preview."""
    return engine_bridge_preview.api_payload_preview


# ══════════════════════════════════════════════════════════════════════════════
# 1. test_bridge_modules_import_without_apps_or_periphery
# ══════════════════════════════════════════════════════════════════════════════

def test_bridge_modules_import_without_apps_or_periphery():
    """All engine_bridge modules must import cleanly with no apps/periphery side effects."""
    import runtime_wiring.engine_bridge.bridge_types as bt
    import runtime_wiring.engine_bridge.api_adapter_preview as ap
    import runtime_wiring.engine_bridge.readonly_engine_bridge as rb
    # Verify the public API is present
    assert hasattr(bt, "EngineBridgePreview")
    assert hasattr(bt, "EngineBridgeSafetyStatus")
    assert hasattr(ap, "validate_api_preview_payload")
    assert hasattr(rb, "build_engine_bridge_preview")
    assert hasattr(rb, "validate_engine_bridge_safety")


# ══════════════════════════════════════════════════════════════════════════════
# 2. test_bridge_types_invariants_pass
# ══════════════════════════════════════════════════════════════════════════════

def test_bridge_types_invariants_pass():
    """Valid construction of all bridge dataclasses passes without error."""
    from runtime_wiring.engine_bridge.bridge_types import (
        EngineBridgeInput,
        EngineBridgeOutput,
        EngineBridgePreview,
        EngineBridgeSafetyStatus,
    )
    safety = EngineBridgeSafetyStatus()
    assert safety.readonly is True
    assert safety.emits_act is False
    assert safety.runtime_active is False
    assert safety.decision_authority == "KX108_ONLY"

    inp = EngineBridgeInput(
        source_pipeline="TEST",
        registry_entries_count=14779,
        families=["A", "B", "C", "D"],
        context_only_decision="ALLOW_CONTEXT_ONLY",
        critical_action_decision="HOLD",
    )
    assert inp.runtime_active is False
    assert inp.emits_act is False
    assert inp.apps_mutation is False

    out = EngineBridgeOutput(
        bridge_status="ENGINE_BRIDGE_PREVIEW_ONLY",
        source_pipeline="TEST",
        registry_entries_count=14779,
        input_family_count=4,
        context_packets_count=4,
        context_only_decision="ALLOW_CONTEXT_ONLY",
        critical_action_decision="HOLD",
        safety=safety,
    )
    assert out.engine_mutation is False
    assert out.periphery_mutation is False

    preview = EngineBridgePreview(bridge_input=inp, bridge_output=out)
    assert preview.is_safe() is True


# ══════════════════════════════════════════════════════════════════════════════
# 3. test_bridge_types_fail_closed_on_runtime_active
# ══════════════════════════════════════════════════════════════════════════════

def test_bridge_types_fail_closed_on_runtime_active():
    """EngineBridgeSafetyStatus must raise ValueError when runtime_active=True."""
    from runtime_wiring.engine_bridge.bridge_types import EngineBridgeSafetyStatus
    with pytest.raises(ValueError, match="FAIL_CLOSED"):
        EngineBridgeSafetyStatus(runtime_active=True)


# ══════════════════════════════════════════════════════════════════════════════
# 4. test_bridge_types_fail_closed_on_emits_act
# ══════════════════════════════════════════════════════════════════════════════

def test_bridge_types_fail_closed_on_emits_act():
    """EngineBridgeSafetyStatus must raise ValueError when emits_act=True."""
    from runtime_wiring.engine_bridge.bridge_types import EngineBridgeSafetyStatus
    with pytest.raises(ValueError, match="FAIL_CLOSED"):
        EngineBridgeSafetyStatus(emits_act=True)


# ══════════════════════════════════════════════════════════════════════════════
# 5. test_readonly_engine_bridge_preview_builds
# ══════════════════════════════════════════════════════════════════════════════

def test_readonly_engine_bridge_preview_builds(engine_bridge_preview):
    """build_engine_bridge_preview() returns a valid, safe EngineBridgePreview."""
    from runtime_wiring.engine_bridge.bridge_types import EngineBridgePreview
    assert isinstance(engine_bridge_preview, EngineBridgePreview)
    assert engine_bridge_preview.is_safe() is True


# ══════════════════════════════════════════════════════════════════════════════
# 6. test_bridge_preview_registry_counts
# ══════════════════════════════════════════════════════════════════════════════

def test_bridge_preview_registry_counts(engine_bridge_preview):
    """Bridge preview must reflect 14 779 registry entries and 4 families."""
    out = engine_bridge_preview.bridge_output
    assert out.registry_entries_count == 14779, (
        f"Expected 14779 entries, got {out.registry_entries_count}"
    )
    assert out.input_family_count == 4, (
        f"Expected 4 families, got {out.input_family_count}"
    )
    assert engine_bridge_preview.bridge_input.registry_entries_count == 14779
    assert len(engine_bridge_preview.bridge_input.families) == 4


# ══════════════════════════════════════════════════════════════════════════════
# 7. test_bridge_preview_decisions_are_allow_context_only_and_hold
# ══════════════════════════════════════════════════════════════════════════════

def test_bridge_preview_decisions_are_allow_context_only_and_hold(engine_bridge_preview):
    """context_only must be ALLOW_CONTEXT_ONLY and critical_action must be HOLD."""
    out = engine_bridge_preview.bridge_output
    assert out.context_only_decision == "ALLOW_CONTEXT_ONLY", (
        f"Expected ALLOW_CONTEXT_ONLY, got {out.context_only_decision!r}"
    )
    assert out.critical_action_decision == "HOLD", (
        f"Expected HOLD, got {out.critical_action_decision!r}"
    )
    # Also verify at input level
    inp = engine_bridge_preview.bridge_input
    assert inp.context_only_decision == "ALLOW_CONTEXT_ONLY"
    assert inp.critical_action_decision == "HOLD"


# ══════════════════════════════════════════════════════════════════════════════
# 8. test_engine_packets_preview_are_readonly_advisory
# ══════════════════════════════════════════════════════════════════════════════

def test_engine_packets_preview_are_readonly_advisory(api_payload):
    """All engine preview packets must have can_decide=False and emits_act=False."""
    packets = api_payload.get("engine_context_packets_preview", [])
    assert len(packets) == 4, f"Expected 4 engine preview packets, got {len(packets)}"
    for pkt in packets:
        assert pkt.get("can_decide") is False, (
            f"can_decide must be False in {pkt.get('packet_id')}"
        )
        meta = pkt.get("_bridge_meta", {})
        assert meta.get("emits_act") is False, (
            f"emits_act must be False in bridge_meta of {pkt.get('packet_id')}"
        )
        assert meta.get("advisory_only") is True, (
            f"advisory_only must be True in bridge_meta of {pkt.get('packet_id')}"
        )
        assert meta.get("runtime_active") is False
        assert meta.get("decision_authority") == "KX108_ONLY"
        # Engine schema fields must be present
        for field in ("packet_id", "action_id", "status", "content_hash", "signals"):
            assert field in pkt, f"Missing engine field {field!r} in packet"


# ══════════════════════════════════════════════════════════════════════════════
# 9. test_api_preview_payload_shape
# ══════════════════════════════════════════════════════════════════════════════

def test_api_preview_payload_shape(api_payload):
    """API preview payload must contain all required top-level keys."""
    required_keys = {
        "status", "dry_run", "runtime_active", "readonly", "emits_act",
        "decision_authority", "proof_claim", "context_only_decision",
        "critical_action_decision", "source_registry_entries",
        "families_sampled", "context_packets_count",
        "engine_context_packets_preview", "safety",
    }
    missing = required_keys - api_payload.keys()
    assert not missing, f"Missing keys in API preview payload: {missing}"
    assert api_payload["status"] == "ENGINE_BRIDGE_PREVIEW_ONLY"
    assert api_payload["decision_authority"] == "KX108_ONLY"
    assert api_payload["dry_run"] is True
    assert api_payload["source_registry_entries"] == 14779
    assert api_payload["families_sampled"] == 4
    assert api_payload["context_packets_count"] == 4


# ══════════════════════════════════════════════════════════════════════════════
# 10. test_api_preview_never_claims_runtime_active
# ══════════════════════════════════════════════════════════════════════════════

def test_api_preview_never_claims_runtime_active(api_payload):
    """API preview must have runtime_active=False at all levels."""
    assert api_payload.get("runtime_active") is False
    safety = api_payload.get("safety", {})
    assert safety.get("runtime_active") is False
    for pkt in api_payload.get("engine_context_packets_preview", []):
        meta = pkt.get("_bridge_meta", {})
        assert meta.get("runtime_active") is False, (
            f"runtime_active=True found in packet {pkt.get('packet_id')}"
        )


# ══════════════════════════════════════════════════════════════════════════════
# 11. test_api_preview_never_emits_act
# ══════════════════════════════════════════════════════════════════════════════

def test_api_preview_never_emits_act(api_payload):
    """emits_act must be False everywhere in the API preview payload."""
    import json
    # Top-level flag
    assert api_payload.get("emits_act") is False
    # Safety block
    safety = api_payload.get("safety", {})
    assert safety.get("emits_act") is False
    # No true value for emits_act anywhere in the serialised payload
    payload_str = json.dumps(api_payload, default=str)
    assert '"emits_act": true' not in payload_str, (
        "emits_act=true found in serialised API preview payload"
    )
    # ACT decision must never appear as a standalone value
    assert '"ACT"' not in payload_str, (
        '"ACT" decision token found in serialised API preview payload'
    )


# ══════════════════════════════════════════════════════════════════════════════
# 12. test_api_preview_never_claims_proof
# ══════════════════════════════════════════════════════════════════════════════

def test_api_preview_never_claims_proof(api_payload):
    """proof_claim must be False at all levels of the preview payload."""
    assert api_payload.get("proof_claim") is False
    safety = api_payload.get("safety", {})
    assert safety.get("proof_claim", False) is False
    assert api_payload.get("verification_status") == "NOT_VERIFIED_DRY_RUN"


# ══════════════════════════════════════════════════════════════════════════════
# 13. test_no_apps_periphery_imports_in_engine_bridge
# ══════════════════════════════════════════════════════════════════════════════

def test_no_apps_periphery_imports_in_engine_bridge():
    """Static AST scan: engine_bridge/*.py must not import apps or periphery."""
    forbidden_roots = ("apps", "periphery")
    violations: list[str] = []

    for py_file in _BRIDGE_PY_FILES:
        if not py_file.exists():
            continue
        source = py_file.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source, filename=str(py_file))
        except SyntaxError as exc:
            violations.append(f"{py_file.name}: SyntaxError — {exc}")
            continue

        for node in ast.walk(tree):
            # import apps.xxx  or  import periphery.xxx
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".")[0]
                    if root in forbidden_roots:
                        violations.append(
                            f"{py_file.name}:{node.lineno}: import {alias.name}"
                        )
            # from apps.xxx import ...  or  from periphery.xxx import ...
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    root = node.module.split(".")[0]
                    if root in forbidden_roots:
                        violations.append(
                            f"{py_file.name}:{node.lineno}: from {node.module} import ..."
                        )

    assert violations == [], (
        "Forbidden apps/periphery imports found in engine_bridge:\n"
        + "\n".join(violations)
    )


# ══════════════════════════════════════════════════════════════════════════════
# 14. test_no_packages_created
# ══════════════════════════════════════════════════════════════════════════════

def test_no_packages_created():
    """packages/ directory must not exist at repo root."""
    assert not (_REPO / "packages").exists(), (
        "packages/ directory exists — boundary violation"
    )


# ══════════════════════════════════════════════════════════════════════════════
# 15. test_existing_p8c_p9b_still_pass_reference
# ══════════════════════════════════════════════════════════════════════════════

def test_existing_p8c_p9b_still_pass_reference():
    """P8C and P9B test modules must still be importable without error (regression guard)."""
    # We do not re-run them here (session fixture already loaded the registry once);
    # we verify the test files exist and can be parsed.
    p8c = _REPO / "tests" / "test_runtime_wiring_p8c.py"
    p9b = _REPO / "tests" / "test_source_registry_p9b.py"
    assert p8c.exists(), "test_runtime_wiring_p8c.py is missing"
    assert p9b.exists(), "test_source_registry_p9b.py is missing"
    # Parse both to confirm no syntax errors
    for f in (p8c, p9b):
        try:
            ast.parse(f.read_text(encoding="utf-8"), filename=str(f))
        except SyntaxError as exc:
            pytest.fail(f"{f.name} has a SyntaxError: {exc}")


# ══════════════════════════════════════════════════════════════════════════════
# Extra: validate_api_preview_payload rejects boundary violations
# ══════════════════════════════════════════════════════════════════════════════

def test_validate_api_preview_rejects_emits_act_true():
    """validate_api_preview_payload must raise ValueError when emits_act=True."""
    from runtime_wiring.engine_bridge.api_adapter_preview import validate_api_preview_payload
    bad_payload = {
        "status": "ENGINE_BRIDGE_PREVIEW_ONLY",
        "dry_run": True,
        "runtime_active": False,
        "readonly": True,
        "emits_act": True,          # violation
        "memory_write": False,
        "kernel_mutation": False,
        "engine_mutation": False,
        "apps_mutation": False,
        "periphery_mutation": False,
        "decision_authority": "KX108_ONLY",
        "proof_claim": False,
        "world_action": False,
        "context_only_decision": "ALLOW_CONTEXT_ONLY",
        "critical_action_decision": "HOLD",
    }
    with pytest.raises(ValueError, match="FAIL_CLOSED"):
        validate_api_preview_payload(bad_payload)


def test_validate_api_preview_rejects_wrong_decision_authority():
    """validate_api_preview_payload must raise ValueError when decision_authority != KX108_ONLY."""
    from runtime_wiring.engine_bridge.api_adapter_preview import validate_api_preview_payload
    bad_payload = {
        "status": "ENGINE_BRIDGE_PREVIEW_ONLY",
        "dry_run": True,
        "runtime_active": False,
        "readonly": True,
        "emits_act": False,
        "memory_write": False,
        "kernel_mutation": False,
        "engine_mutation": False,
        "apps_mutation": False,
        "periphery_mutation": False,
        "decision_authority": "AGENT_OVERRIDE",  # violation
        "proof_claim": False,
        "world_action": False,
        "context_only_decision": "ALLOW_CONTEXT_ONLY",
        "critical_action_decision": "HOLD",
    }
    with pytest.raises(ValueError, match="FAIL_CLOSED"):
        validate_api_preview_payload(bad_payload)


def test_build_safe_response_preview_shape(api_payload):
    """build_safe_response_preview wraps the payload in a boundary envelope."""
    from runtime_wiring.engine_bridge.api_adapter_preview import build_safe_response_preview
    wrapped = build_safe_response_preview(api_payload)
    assert wrapped.get("ok") is True
    boundary = wrapped.get("boundary", {})
    assert boundary.get("readonly") is True
    assert boundary.get("emits_act") is False
    assert boundary.get("decision_authority") == "KX108_ONLY"
    assert boundary.get("engine_mutation") is False
    assert boundary.get("apps_mutation") is False
    assert boundary.get("periphery_mutation") is False
    assert "data" in wrapped
    assert wrapped["data"] is api_payload


def test_bridge_types_fail_closed_on_wrong_authority():
    """EngineBridgeSafetyStatus must raise ValueError when decision_authority != KX108_ONLY."""
    from runtime_wiring.engine_bridge.bridge_types import EngineBridgeSafetyStatus
    with pytest.raises(ValueError, match="FAIL_CLOSED"):
        EngineBridgeSafetyStatus(decision_authority="AGENT_SELF")


def test_bridge_types_fail_closed_on_engine_mutation():
    """EngineBridgeOutput must raise ValueError when engine_mutation=True."""
    from runtime_wiring.engine_bridge.bridge_types import EngineBridgeOutput, EngineBridgeSafetyStatus
    safety = EngineBridgeSafetyStatus()
    with pytest.raises(ValueError, match="FAIL_CLOSED"):
        EngineBridgeOutput(
            bridge_status="ENGINE_BRIDGE_PREVIEW_ONLY",
            source_pipeline="TEST",
            registry_entries_count=14779,
            input_family_count=4,
            context_packets_count=4,
            context_only_decision="ALLOW_CONTEXT_ONLY",
            critical_action_decision="HOLD",
            safety=safety,
            engine_mutation=True,   # violation
        )


def test_bridge_types_fail_closed_on_wrong_bridge_status():
    """EngineBridgeOutput must raise ValueError when bridge_status is not ENGINE_BRIDGE_PREVIEW_ONLY."""
    from runtime_wiring.engine_bridge.bridge_types import EngineBridgeOutput, EngineBridgeSafetyStatus
    safety = EngineBridgeSafetyStatus()
    with pytest.raises(ValueError, match="FAIL_CLOSED"):
        EngineBridgeOutput(
            bridge_status="ACTIVE_RUNTIME",   # violation
            source_pipeline="TEST",
            registry_entries_count=14779,
            input_family_count=4,
            context_packets_count=4,
            context_only_decision="ALLOW_CONTEXT_ONLY",
            critical_action_decision="HOLD",
            safety=safety,
        )


def test_summarize_engine_bridge_preview(engine_bridge_preview):
    """summarize_engine_bridge_preview returns a non-empty, informative string."""
    from runtime_wiring.engine_bridge.readonly_engine_bridge import summarize_engine_bridge_preview
    summary = summarize_engine_bridge_preview(engine_bridge_preview)
    assert "ENGINE_BRIDGE_PREVIEW_ONLY" in summary
    assert "14779" in summary
    assert "ALLOW_CONTEXT_ONLY" in summary
    assert "HOLD" in summary
    assert "emits_act=False" in summary


def test_validate_engine_bridge_safety_passes(engine_bridge_preview):
    """validate_engine_bridge_safety must return True on the session preview."""
    from runtime_wiring.engine_bridge.readonly_engine_bridge import validate_engine_bridge_safety
    assert validate_engine_bridge_safety(engine_bridge_preview) is True


def test_bridge_preview_to_dict_is_serialisable(engine_bridge_preview):
    """EngineBridgePreview.to_dict() must produce a JSON-serialisable dict."""
    import json
    d = engine_bridge_preview.to_dict()
    serialised = json.dumps(d, default=str)
    assert "ENGINE_BRIDGE_PREVIEW_ONLY" in serialised
    assert "KX108_ONLY" in serialised
    assert "ALLOW_CONTEXT_ONLY" in serialised
    assert "HOLD" in serialised
