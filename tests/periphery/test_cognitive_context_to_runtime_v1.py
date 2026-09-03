"""
W1 — Tests substantifs: ContextPacketV2 -> runtime_wiring.ContextPacket (cognitive join).
"""
from __future__ import annotations
import pytest
from periphery.context.context_packet_builder_v2 import ContextPacketV2, build_context_packet_v2
from periphery.context.cognitive_context_to_runtime import (
    build_cognitive_runtime_packet,
    context_packet_validation_projection,
    BOUNDARY,
    SOURCE_STATUS,
    CLAIM_SCOPE,
)
from periphery.context.context_packet_validator import validate_context_packet
from periphery.x108_ingress.x108_context_boundary import check_x108_context_boundary
from runtime_wiring.packet_types import ContextPacket


def _make_v2(
    query: str = "test query",
    dominant_trees=None,
    memory_status: str = "CANDIDATE_ONLY",
    risk_flags=None,
    unknowns=None,
    contradictions=None,
    context_items=None,
) -> ContextPacketV2:
    return build_context_packet_v2(
        query=query,
        language="fr",
        context_items=["Brody dit: contexte pertinent"] if context_items is None else context_items,
        source_refs=["ref://tree_signal/test"],
        dominant_trees=[1, 7, 13] if dominant_trees is None else dominant_trees,
        memory_status=memory_status,
        risk_flags=["RISK_LOW"] if risk_flags is None else risk_flags,
        unknowns=["unknown_var_x"] if unknowns is None else unknowns,
        contradictions=[] if contradictions is None else contradictions,
    )


def _make_packet(signal_id: str = "sig-test-001") -> ContextPacket:
    return build_cognitive_runtime_packet(_make_v2(), signal_id)

def test_dominant_trees_preserved():
    v2 = _make_v2(dominant_trees=[2, 5, 11, 34])
    p = build_cognitive_runtime_packet(v2, "sig-trees")
    assert p.payload["dominant_trees"] == [2, 5, 11, 34]

def test_memory_status_preserved():
    v2 = _make_v2(memory_status="CANDIDATE_ONLY")
    p = build_cognitive_runtime_packet(v2, "sig-mem")
    assert p.payload["memory_status"] == "CANDIDATE_ONLY"

def test_risk_flags_preserved():
    v2 = _make_v2(risk_flags=["RISK_HIGH", "CONTRADICTION_DETECTED"])
    p = build_cognitive_runtime_packet(v2, "sig-risk")
    assert "RISK_HIGH" in p.payload["risk_flags"]
    assert "CONTRADICTION_DETECTED" in p.payload["risk_flags"]

def test_risk_flags_in_labels():
    v2 = _make_v2(risk_flags=["RISK_MEDIUM"])
    p = build_cognitive_runtime_packet(v2, "sig-lbl")
    assert "RISK:RISK_MEDIUM" in p.labels

def test_unknowns_preserved():
    v2 = _make_v2(unknowns=["unknown_alpha", "unknown_beta"])
    p = build_cognitive_runtime_packet(v2, "sig-unk")
    assert p.payload["unknowns"] == ["unknown_alpha", "unknown_beta"]

def test_contradictions_preserved():
    v2 = _make_v2(contradictions=["tree_3 vs tree_7"])
    p = build_cognitive_runtime_packet(v2, "sig-contra")
    assert "tree_3 vs tree_7" in p.payload["contradictions"]

def test_context_items_brody_preserved():
    v2 = _make_v2(context_items=["Brody: reponse contextuelle"])
    p = build_cognitive_runtime_packet(v2, "sig-brody")
    assert "Brody: reponse contextuelle" in p.payload["context_items"]

def test_action_id_set_to_signal_id():
    p = build_cognitive_runtime_packet(_make_v2(), "sig-actionid-42")
    assert p.payload["action_id"] == "sig-actionid-42"

def test_context_id_format():
    p = _make_packet("sig-001")
    assert p.context_id.startswith("cp-cognitive-")

def test_context_id_deterministic():
    v2 = _make_v2()
    p1 = build_cognitive_runtime_packet(v2, "sig-determ")
    p2 = build_cognitive_runtime_packet(v2, "sig-determ")
    assert p1.context_id == p2.context_id

def test_source_is_cognitive_tree_signal():
    assert _make_packet().source == "COGNITIVE_TREE_SIGNAL"

def test_source_status_candidate_only():
    assert _make_packet().source_status == "CANDIDATE_ONLY"

def test_claim_scope_context_signal_only():
    assert _make_packet().claim_scope == "CONTEXT_SIGNAL_ONLY"

def test_boundary_cognitive_advisory():
    assert _make_packet().boundary == "COGNITIVE_CONTEXT_ADVISORY_ONLY"

def test_readonly_true():
    assert _make_packet().readonly is True

def test_advisory_only_true():
    assert _make_packet().advisory_only is True

def test_emits_act_false():
    assert _make_packet().emits_act is False

def test_emits_decision_false():
    assert _make_packet().emits_decision is False

def test_runtime_allowed_now_false():
    assert _make_packet().runtime_allowed_now is False

def test_decision_authority_kx108_only():
    assert _make_packet().decision_authority == "KX108_ONLY"

def test_payload_allowed_to_decide_false():
    assert _make_packet().payload["_allowed_to_decide"] is False

def test_payload_allowed_to_act_false():
    assert _make_packet().payload["_allowed_to_act"] is False

def test_payload_memory_write_false():
    assert _make_packet().payload["_memory_write"] is False

def test_payload_kernel_mutation_false():
    assert _make_packet().payload["_kernel_mutation"] is False

def test_validate_invariants_does_not_raise():
    _make_packet().validate_invariants()

def test_projection_readonly_true():
    proj = context_packet_validation_projection(_make_packet())
    assert proj["readonly"] is True

def test_projection_context_signal_only_true():
    proj = context_packet_validation_projection(_make_packet())
    assert proj["context_signal_only"] is True

def test_projection_decision_authority():
    proj = context_packet_validation_projection(_make_packet())
    assert proj["decision_authority"] == "KX108_ONLY"

def test_projection_allowed_to_decide_false():
    proj = context_packet_validation_projection(_make_packet())
    assert proj["allowed_to_decide"] is False

def test_projection_memory_write_false():
    proj = context_packet_validation_projection(_make_packet())
    assert proj["memory_write"] is False

def test_validate_context_packet_valid():
    proj = context_packet_validation_projection(_make_packet())
    result = validate_context_packet(proj)
    assert result.valid, f"violations: {result.violations}"

def test_x108_context_boundary_passed():
    proj = context_packet_validation_projection(_make_packet())
    result = check_x108_context_boundary(proj)
    assert result.passed, f"violations: {result.violations}"

def test_fail_wrong_type():
    with pytest.raises(TypeError, match="CONTEXT_PACKET_V2_REQUIRED"):
        build_cognitive_runtime_packet("not a v2", "sig-bad")

def test_fail_empty_signal_id():
    with pytest.raises(ValueError, match="SIGNAL_ID_REQUIRED"):
        build_cognitive_runtime_packet(_make_v2(), "")

def test_fail_whitespace_signal_id():
    with pytest.raises(ValueError, match="SIGNAL_ID_REQUIRED"):
        build_cognitive_runtime_packet(_make_v2(), "   ")

def test_fail_readonly_false():
    v2 = ContextPacketV2(packet_id="x", query="q", language="en", context_items=[], readonly=False)
    with pytest.raises(AssertionError, match="READONLY_VIOLATED"):
        build_cognitive_runtime_packet(v2, "sig-ro")

def test_fail_context_signal_only_false():
    v2 = ContextPacketV2(packet_id="x", query="q", language="en", context_items=[], context_signal_only=False)
    with pytest.raises(AssertionError, match="CONTEXT_SIGNAL_ONLY_VIOLATED"):
        build_cognitive_runtime_packet(v2, "sig-cso")

def test_fail_wrong_decision_authority():
    v2 = ContextPacketV2(packet_id="x", query="q", language="en", context_items=[], decision_authority="AGENT_DECIDES")
    with pytest.raises(AssertionError, match="DECISION_AUTHORITY_VIOLATED"):
        build_cognitive_runtime_packet(v2, "sig-da")

def test_fail_allowed_to_decide_true():
    v2 = ContextPacketV2(packet_id="x", query="q", language="en", context_items=[], allowed_to_decide=True)
    with pytest.raises(AssertionError, match="ALLOWED_TO_DECIDE_VIOLATED"):
        build_cognitive_runtime_packet(v2, "sig-atd")

def test_fail_allowed_to_act_true():
    v2 = ContextPacketV2(packet_id="x", query="q", language="en", context_items=[], allowed_to_act=True)
    with pytest.raises(AssertionError, match="ALLOWED_TO_ACT_VIOLATED"):
        build_cognitive_runtime_packet(v2, "sig-ata")

def test_fail_kernel_mutation_true():
    v2 = ContextPacketV2(packet_id="x", query="q", language="en", context_items=[], kernel_mutation=True)
    with pytest.raises(AssertionError, match="KERNEL_MUTATION_VIOLATED"):
        build_cognitive_runtime_packet(v2, "sig-km")

def test_fail_memory_write_true():
    v2 = ContextPacketV2(packet_id="x", query="q", language="en", context_items=[], memory_write=True)
    with pytest.raises(AssertionError, match="MEMORY_WRITE_VIOLATED"):
        build_cognitive_runtime_packet(v2, "sig-mw")

def test_falsified_projection_fails_validator():
    proj = context_packet_validation_projection(_make_packet())
    proj["readonly"] = False
    result = validate_context_packet(proj)
    assert not result.valid
    assert any("readonly" in v for v in result.violations)

def test_falsified_projection_fails_boundary():
    proj = context_packet_validation_projection(_make_packet())
    proj["decision_authority"] = "SIGMA_DECIDES"
    result = check_x108_context_boundary(proj)
    assert not result.passed
    assert any("decision_authority" in v for v in result.violations)

def test_no_agent_contract_symbols_imported():
    import periphery.context.cognitive_context_to_runtime as mod
    assert "AgentResult" not in mod.__dict__
    assert "AgentLayer" not in mod.__dict__

def test_return_type_is_runtime_context_packet():
    assert isinstance(_make_packet(), ContextPacket)

def test_builder_v2_backward_compat():
    v2 = build_context_packet_v2(query="ancien appel", language="en")
    assert v2.dominant_trees == []
    assert v2.memory_status == "CANDIDATE_ONLY"
    assert v2.risk_flags == []
    assert v2.unknowns == []
    assert v2.contradictions == []

def test_builder_v2_dominant_trees_forwarded():
    v2 = build_context_packet_v2(query="q", dominant_trees=[3, 9])
    assert v2.dominant_trees == [3, 9]

def test_builder_v2_memory_status_forwarded():
    v2 = build_context_packet_v2(query="q", memory_status="READ_ONLY")
    assert v2.memory_status == "READ_ONLY"

def test_builder_v2_risk_flags_forwarded():
    v2 = build_context_packet_v2(query="q", risk_flags=["RISK_A"])
    assert v2.risk_flags == ["RISK_A"]

def test_builder_v2_unknowns_forwarded():
    v2 = build_context_packet_v2(query="q", unknowns=["u1"])
    assert v2.unknowns == ["u1"]

def test_builder_v2_contradictions_forwarded():
    v2 = build_context_packet_v2(query="q", contradictions=["c1"])
    assert v2.contradictions == ["c1"]

def test_builder_v2_invariants_enforced():
    v2 = build_context_packet_v2(query="q", dominant_trees=[1])
    assert v2.readonly is True
    assert v2.context_signal_only is True
    assert v2.decision_authority == "KX108_ONLY"
    assert v2.allowed_to_decide is False
    assert v2.allowed_to_act is False
    assert v2.kernel_mutation is False
    assert v2.memory_write is False
