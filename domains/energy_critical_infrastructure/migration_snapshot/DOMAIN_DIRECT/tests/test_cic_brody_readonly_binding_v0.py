"""
Tests — CIC Brody Readonly Binding V0
Tests 8-9 : Brody reçoit cic_readonly_context, pas de clé interdite.
"""
from __future__ import annotations

import pytest

from apps.obsidia_api.brody_cic_context_adapter import (
    _FORBIDDEN_INJECT_KEYS,
    build_brody_cic_packet,
    inject_cic_into_runtime_packet,
)


# Test 8
def test_brody_receives_cic_readonly_context():
    packet = build_brody_cic_packet()
    assert "cic_readonly_context" in packet
    ctx = packet["cic_readonly_context"]
    assert ctx["readonly"] is True
    assert ctx["decision_authority"] == "KX108_ONLY"


# Test 9
def test_brody_does_not_receive_forbidden_keys_from_cic():
    packet = build_brody_cic_packet()
    for key in _FORBIDDEN_INJECT_KEYS:
        assert key not in packet, f"Clé interdite trouvée dans le packet Brody: {key}"


def test_inject_into_runtime_packet_adds_cic_readonly_context():
    runtime = {"status": "BRODY_RUNTIME_CONTEXT_READY", "some_data": True}
    result = inject_cic_into_runtime_packet(runtime)
    assert "cic_readonly_context" in result
    assert result["cic_readonly_context"]["readonly"] is True


def test_inject_raises_on_forbidden_key():
    forbidden_runtime = {"decision": {"result": "ALLOW"}}
    with pytest.raises(ValueError, match="clé interdite"):
        inject_cic_into_runtime_packet(forbidden_runtime)


def test_brody_cic_inject_key_is_cic_readonly_context():
    packet = build_brody_cic_packet()
    ctx = packet["cic_readonly_context"]
    assert ctx["inject_key"] == "cic_readonly_context"


def test_brody_boundary_can_decide_is_false():
    packet = build_brody_cic_packet()
    boundary = packet["cic_readonly_context"]["brody_boundary"]
    assert boundary["can_decide"] is False
    assert boundary["can_authorize"] is False
    assert boundary["can_block"] is False
    assert boundary["can_emit_act"] is False
    assert boundary["can_write_memory"] is False
    assert boundary["can_mutate_kernel"] is False


def test_brody_boundary_can_display_is_true():
    packet = build_brody_cic_packet()
    boundary = packet["cic_readonly_context"]["brody_boundary"]
    assert boundary["can_display_confirmed_metrics"] is True
    assert boundary["can_display_central_rules"] is True
    assert boundary["can_display_projection_not_prediction"] is True
    assert boundary["can_display_memory_not_sovereign"] is True
