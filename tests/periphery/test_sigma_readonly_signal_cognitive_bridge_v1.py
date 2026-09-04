"""
W6b -- Tests: enrich_context_packet_v2_with_sigma_signal -> ContextPacketV2.
30 tests.
"""
from __future__ import annotations
import hashlib
import pytest
from sigma.sigma_readonly_signal import SigmaReadonlySignal, build_sigma_readonly_signal
from periphery.context.context_packet_builder_v2 import ContextPacketV2, build_context_packet_v2
from periphery.context.sigma_readonly_signal_cognitive_bridge import (
    enrich_context_packet_v2_with_sigma_signal,
)
from periphery.context.cognitive_x108_admission import admit_cognitive_context
from runtime_wiring.packet_types import DecisionTicketDryRun

def _sha16(ref):
    return hashlib.sha256(ref.encode()).hexdigest()[:16]


def _signal(
    signal_id="sig-w6b-test",
    contradictions=None, missing_context=None, proof_status="OK",
    readonly=True, advisory_only=True, context_signal_only=True,
    can_decide=False, can_emit_act=False, emits_act=False, emits_verdict=False,
    memory_write=False, graphiti_write=False, neo4j_write=False,
    kernel_mutation=False, x108_mutation=False, decision_authority="KX108_ONLY",
):
    return SigmaReadonlySignal(
        signal_id=signal_id,
        contradictions=list(contradictions) if contradictions is not None else [],
        missing_context=list(missing_context) if missing_context is not None else [],
        proof_status=proof_status, readonly=readonly, advisory_only=advisory_only,
        context_signal_only=context_signal_only, can_decide=can_decide,
        can_emit_act=can_emit_act, emits_act=emits_act, emits_verdict=emits_verdict,
        memory_write=memory_write, graphiti_write=graphiti_write,
        neo4j_write=neo4j_write, kernel_mutation=kernel_mutation,
        x108_mutation=x108_mutation, decision_authority=decision_authority,
    )


def _v2(source_refs=None, contradictions=None, unknowns=None, risk_flags=None,
        context_items=None, dominant_trees=None, memory_status=None):
    return build_context_packet_v2(
        query="test W6b sigma signal", language="fr",
        context_items=context_items or ["item existant"],
        source_refs=source_refs or [], dominant_trees=dominant_trees or [2, 5],
        memory_status=memory_status or "CANDIDATE_ONLY",
        risk_flags=risk_flags or ["RISK_LOW"],
        unknowns=unknowns or ["u1"], contradictions=contradictions or ["c1"],
    )


def test_signal_id_added_to_source_refs():
    result = enrich_context_packet_v2_with_sigma_signal(_v2(), _signal(signal_id="sig-w6b-prov"))
    assert "sig-w6b-prov" in result.source_refs


def test_source_hash_parallel_exact():
    result = enrich_context_packet_v2_with_sigma_signal(_v2(), _signal(signal_id="sig-w6b-hash"))
    idx = result.source_refs.index("sig-w6b-hash")
    assert result.source_hashes[idx] == _sha16("sig-w6b-hash")
    assert len(result.source_refs) == len(result.source_hashes)


def test_contradictions_merge_additive():
    result = enrich_context_packet_v2_with_sigma_signal(
        _v2(contradictions=["PRIOR"]), _signal(contradictions=["NEW1", "NEW2"]))
    assert "PRIOR" in result.contradictions
    assert "NEW1" in result.contradictions and "NEW2" in result.contradictions


def test_contradictions_no_dup():
    result = enrich_context_packet_v2_with_sigma_signal(
        _v2(contradictions=["C_EXISTING"]), _signal(contradictions=["C_EXISTING", "C_NEW"]))
    assert result.contradictions.count("C_EXISTING") == 1
    assert "C_NEW" in result.contradictions


def test_contradictions_order_stable_existing_first():
    result = enrich_context_packet_v2_with_sigma_signal(
        _v2(contradictions=["PRIOR1", "PRIOR2"]), _signal(contradictions=["NEW1"]))
    assert result.contradictions[:2] == ["PRIOR1", "PRIOR2"]
    assert result.contradictions[2] == "NEW1"


def test_empty_signal_contradictions():
    result = enrich_context_packet_v2_with_sigma_signal(
        _v2(contradictions=["c_prev"]), _signal(contradictions=[], missing_context=[]))
    assert result.contradictions == ["c_prev"]
    assert "sig-w6b-test" in result.source_refs


def test_deterministic():
    v2, sig = _v2(), _signal(signal_id="sig-det", contradictions=["C1"])
    r1 = enrich_context_packet_v2_with_sigma_signal(v2, sig)
    r2 = enrich_context_packet_v2_with_sigma_signal(v2, sig)
    assert r1.source_refs == r2.source_refs
    assert r1.contradictions == r2.contradictions


def test_original_packet_not_mutated():
    v2 = _v2(contradictions=["original"])
    refs_before, cont_before = list(v2.source_refs), list(v2.contradictions)
    enrich_context_packet_v2_with_sigma_signal(v2, _signal(contradictions=["new"]))
    assert v2.source_refs == refs_before and v2.contradictions == cont_before


def test_decision_authority_preserved():
    assert enrich_context_packet_v2_with_sigma_signal(_v2(), _signal()).decision_authority == "KX108_ONLY"


def test_allowed_to_act_preserved_false():
    assert enrich_context_packet_v2_with_sigma_signal(_v2(), _signal()).allowed_to_act is False


def test_allowed_to_decide_preserved_false():
    assert enrich_context_packet_v2_with_sigma_signal(_v2(), _signal()).allowed_to_decide is False


def test_unknowns_unchanged_missing_context_not_mapped():
    result = enrich_context_packet_v2_with_sigma_signal(
        _v2(unknowns=["u1"]),
        _signal(missing_context=["UNKNOWN_CHANNEL", "MISSING_COUNTERPARTY"]))
    assert result.unknowns == ["u1"]
    assert "UNKNOWN_CHANNEL" not in result.unknowns


def test_proof_status_not_mapped_anywhere():
    for status in ("OK", "MISSING", "PARTIAL", "FAILED", "UNKNOWN"):
        result = enrich_context_packet_v2_with_sigma_signal(
            _v2(contradictions=["c1"]), _signal(proof_status=status, contradictions=[]))
        assert status not in str(result.risk_flags)
        assert status not in str(result.unknowns)
        assert result.contradictions == ["c1"]


def test_context_items_unchanged():
    result = enrich_context_packet_v2_with_sigma_signal(
        _v2(context_items=["item A", "item B"]), _signal())
    assert result.context_items == ["item A", "item B"]


def test_dominant_trees_unchanged():
    assert enrich_context_packet_v2_with_sigma_signal(
        _v2(dominant_trees=[3, 7, 12]), _signal()).dominant_trees == [3, 7, 12]


def test_memory_status_unchanged():
    assert enrich_context_packet_v2_with_sigma_signal(_v2(), _signal()).memory_status == "CANDIDATE_ONLY"


def test_risk_flags_unchanged():
    result = enrich_context_packet_v2_with_sigma_signal(
        _v2(risk_flags=["RISK_LOW", "AUDIT_HIGH"]), _signal())
    assert result.risk_flags == ["RISK_LOW", "AUDIT_HIGH"]


def test_signal_id_not_duplicated_if_already_present():
    result = enrich_context_packet_v2_with_sigma_signal(
        _v2(source_refs=["sig-already"]), _signal(signal_id="sig-already"))
    assert result.source_refs.count("sig-already") == 1


def test_w1_compatibility():
    from periphery.context.cognitive_context_to_runtime import build_cognitive_runtime_packet
    enriched = enrich_context_packet_v2_with_sigma_signal(_v2(), _signal(signal_id="sig-w6b-w1"))
    packet = build_cognitive_runtime_packet(enriched, "sig-w6b-w1")
    packet.validate_invariants()
    assert packet.advisory_only is True and packet.emits_act is False


def test_e2e_enrich_then_admit():
    sig = _signal(signal_id="sig-w6b-e2e", contradictions=["SIGMA_OBSERVATION"])
    enriched = enrich_context_packet_v2_with_sigma_signal(_v2(contradictions=[]), sig)
    assert "sig-w6b-e2e" in enriched.source_refs
    ticket = admit_cognitive_context(enriched, "sig-w6b-e2e")
    assert isinstance(ticket, DecisionTicketDryRun)
    assert ticket.decision in ("ALLOW_CONTEXT_ONLY", "HOLD", "BLOCK")
    ticket.validate_invariants()


def test_fail_closed_bad_signal_type():
    with pytest.raises(TypeError, match="SIGMA_READONLY_SIGNAL_TYPE_REQUIRED"):
        enrich_context_packet_v2_with_sigma_signal(_v2(), "not a signal")


def test_fail_closed_bad_context_type():
    with pytest.raises(TypeError, match="CONTEXT_PACKET_V2_TYPE_REQUIRED"):
        enrich_context_packet_v2_with_sigma_signal("not a context", _signal())


def test_fail_closed_readonly():
    with pytest.raises(AssertionError, match="READONLY_VIOLATED"):
        enrich_context_packet_v2_with_sigma_signal(_v2(), _signal(readonly=False))


def test_fail_closed_advisory_only():
    with pytest.raises(AssertionError, match="ADVISORY_ONLY_VIOLATED"):
        enrich_context_packet_v2_with_sigma_signal(_v2(), _signal(advisory_only=False))


def test_fail_closed_emits_act():
    with pytest.raises(AssertionError, match="EMITS_ACT_VIOLATED"):
        enrich_context_packet_v2_with_sigma_signal(_v2(), _signal(emits_act=True))


def test_fail_closed_memory_write():
    with pytest.raises(AssertionError, match="MEMORY_WRITE_VIOLATED"):
        enrich_context_packet_v2_with_sigma_signal(_v2(), _signal(memory_write=True))


def test_fail_closed_kernel_mutation():
    with pytest.raises(AssertionError, match="KERNEL_MUTATION_VIOLATED"):
        enrich_context_packet_v2_with_sigma_signal(_v2(), _signal(kernel_mutation=True))


def test_fail_closed_signal_id_empty():
    with pytest.raises(ValueError, match="SIGNAL_ID_EMPTY"):
        enrich_context_packet_v2_with_sigma_signal(_v2(), _signal(signal_id=""))


def test_no_sigma_execution_symbols_in_bridge():
    import periphery.context.sigma_readonly_signal_cognitive_bridge as mod
    assert "DomainAggregate" not in mod.__dict__
    assert "AgentVote" not in mod.__dict__


def test_no_agent_layer_symbols_in_bridge():
    import periphery.context.sigma_readonly_signal_cognitive_bridge as mod
    assert "AgentResult" not in mod.__dict__
    assert "AgentLayer" not in mod.__dict__
