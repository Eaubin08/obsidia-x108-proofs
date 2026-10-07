"""B6 optional Brody consumer seam: run_brody_real_response_pipeline is unchanged without a packet."""
from __future__ import annotations

from app.harness.state_explicit import WorkingStateRegistry, assemble_context, sens_state_entries
from apps.obsidia_api.brody_real_response_pipeline import run_brody_real_response_pipeline

_VOLATILE = {"action_id", "timestamp"}
_MATRIX = {"categories": ["PURE_RESPONSE"], "matrix": {"PURE_RESPONSE": {"brody_may": ["repondre"]}}}


def test_default_path_is_unchanged_and_packet_is_attached_verbatim():
    plain = run_brody_real_response_pipeline("Lance P.")
    r = WorkingStateRegistry()
    for e in sens_state_entries("Lance P."):
        r.register(e)
    packet = assemble_context("Lance P.", r, capability_matrix=_MATRIX).to_dict()
    seamed = run_brody_real_response_pipeline("Lance P.", state_context_packet=packet)
    assert "b6_state_context_packet" not in plain
    assert seamed["b6_state_context_packet"] == packet
    assert set(plain) - _VOLATILE == set(seamed) - _VOLATILE - {"b6_state_context_packet"}
    for k in ("decision_authority", "emits_act", "memory_write", "allowed_to_act", "kernel_mutation"):
        assert plain[k] == seamed[k]
    assert seamed["decision_authority"] == "KX108_ONLY" and seamed["emits_act"] is False
