"""
C8 -- Tests for agent_result_cognitive_bridge.

Covers:
- additive mappings
- provenance
- intra-input/context deduplication
- stable order
- immutability
- governance
- GateHint
- W1
- canonical W2/KX108 admission
"""

from __future__ import annotations

import hashlib

import pytest

from periphery.agent_contracts import AgentLayer, AgentResult
from periphery.common import PeripheralSignalPacket
from periphery.context.context_packet_builder_v2 import (
    ContextPacketV2,
    build_context_packet_v2,
)
from periphery.context.agent_result_cognitive_bridge import (
    enrich_context_packet_v2_with_agent_result,
)
from periphery.context.cognitive_context_to_runtime import (
    build_cognitive_runtime_packet,
)
from periphery.context.cognitive_x108_admission import (
    admit_cognitive_context,
)


def _sha16(ref: str) -> str:
    return hashlib.sha256(ref.encode()).hexdigest()[:16]


def _make_packet(
    action_id: str = "act-c8-001",
    domain: str = "bank",
    unknowns: list[str] | None = None,
    risk_flags: list[str] | None = None,
    contradictions: list[str] | None = None,
    evidence_refs: list[str] | None = None,
    recommended_gate: str = "NONE",
    can_emit_act: bool = False,
) -> PeripheralSignalPacket:
    return PeripheralSignalPacket(
        action_id=action_id,
        domain=domain,
        unknowns=unknowns if unknowns is not None else ["UNKNOWN_C8"],
        risk_flags=risk_flags if risk_flags is not None else ["RISK_C8"],
        contradictions=(
            contradictions
            if contradictions is not None
            else ["CONTRADICTION_C8"]
        ),
        evidence_refs=(
            evidence_refs
            if evidence_refs is not None
            else ["proof:c8-evidence"]
        ),
        recommended_gate=recommended_gate,
        can_emit_act=can_emit_act,
    )


def _make_result(
    agent_id: str = "data_purity",
    layer: AgentLayer = AgentLayer.DATA,
    **packet_kwargs,
) -> AgentResult:
    return AgentResult(
        agent_id=agent_id,
        layer=layer,
        packet=_make_packet(**packet_kwargs),
        notes=["test note"],
    )


def _make_context(
    source_refs: list[str] | None = None,
    unknowns: list[str] | None = None,
    risk_flags: list[str] | None = None,
    contradictions: list[str] | None = None,
) -> ContextPacketV2:
    return build_context_packet_v2(
        query="c8 test query",
        language="fr",
        context_items=["contexte test C8"],
        source_refs=source_refs if source_refs is not None else ["ref://preexisting"],
        unknowns=unknowns if unknowns is not None else [],
        risk_flags=risk_flags if risk_flags is not None else [],
        contradictions=contradictions if contradictions is not None else [],
    )


def test_nominal_enrichment_returns_context_packet_v2():
    enriched = enrich_context_packet_v2_with_agent_result(
        _make_context(),
        _make_result(),
    )
    assert isinstance(enriched, ContextPacketV2)


def test_unknowns_are_merged():
    enriched = enrich_context_packet_v2_with_agent_result(
        _make_context(unknowns=["EXISTING_UNKNOWN"]),
        _make_result(unknowns=["NEW_UNKNOWN"]),
    )
    assert enriched.unknowns == ["EXISTING_UNKNOWN", "NEW_UNKNOWN"]


def test_risk_flags_are_merged():
    enriched = enrich_context_packet_v2_with_agent_result(
        _make_context(risk_flags=["EXISTING_RISK"]),
        _make_result(risk_flags=["NEW_RISK"]),
    )
    assert enriched.risk_flags == ["EXISTING_RISK", "NEW_RISK"]


def test_contradictions_are_merged():
    enriched = enrich_context_packet_v2_with_agent_result(
        _make_context(contradictions=["EXISTING_CONTRADICTION"]),
        _make_result(contradictions=["NEW_CONTRADICTION"]),
    )
    assert enriched.contradictions == [
        "EXISTING_CONTRADICTION",
        "NEW_CONTRADICTION",
    ]


def test_evidence_refs_appear_in_source_refs():
    enriched = enrich_context_packet_v2_with_agent_result(
        _make_context(),
        _make_result(evidence_refs=["proof:e2e-ref"]),
    )
    assert "proof:e2e-ref" in enriched.source_refs


def test_source_hashes_are_sha16_exact():
    enriched = enrich_context_packet_v2_with_agent_result(
        _make_context(source_refs=[]),
        _make_result(
            agent_id="data_purity",
            action_id="act-c8-001",
            evidence_refs=[],
        ),
    )
    assert _sha16("agent:data_purity") in enriched.source_hashes
    assert _sha16("action:act-c8-001") in enriched.source_hashes


def test_agent_id_is_in_source_refs():
    enriched = enrich_context_packet_v2_with_agent_result(
        _make_context(source_refs=[]),
        _make_result(agent_id="provenance", evidence_refs=[]),
    )
    assert "agent:provenance" in enriched.source_refs


def test_action_id_is_in_source_refs():
    enriched = enrich_context_packet_v2_with_agent_result(
        _make_context(source_refs=[]),
        _make_result(action_id="act-xyz-999", evidence_refs=[]),
    )
    assert "action:act-xyz-999" in enriched.source_refs


def test_no_duplicate_source_refs_vs_context():
    enriched = enrich_context_packet_v2_with_agent_result(
        _make_context(source_refs=["agent:data_purity"]),
        _make_result(agent_id="data_purity", evidence_refs=[]),
    )
    assert enriched.source_refs.count("agent:data_purity") == 1


def test_no_duplicate_unknowns_vs_context():
    enriched = enrich_context_packet_v2_with_agent_result(
        _make_context(unknowns=["SHARED_UNKNOWN"]),
        _make_result(unknowns=["SHARED_UNKNOWN"]),
    )
    assert enriched.unknowns.count("SHARED_UNKNOWN") == 1


def test_no_duplicate_risk_flags_vs_context():
    enriched = enrich_context_packet_v2_with_agent_result(
        _make_context(risk_flags=["SHARED_RISK"]),
        _make_result(risk_flags=["SHARED_RISK"]),
    )
    assert enriched.risk_flags.count("SHARED_RISK") == 1


def test_no_duplicate_contradictions_vs_context():
    enriched = enrich_context_packet_v2_with_agent_result(
        _make_context(contradictions=["SHARED_CONTRADICTION"]),
        _make_result(contradictions=["SHARED_CONTRADICTION"]),
    )
    assert enriched.contradictions.count("SHARED_CONTRADICTION") == 1


def test_no_duplicate_intra_incoming_unknowns():
    enriched = enrich_context_packet_v2_with_agent_result(
        _make_context(unknowns=[]),
        _make_result(unknowns=["REPEATED", "REPEATED", "UNIQUE"]),
    )
    assert enriched.unknowns == ["REPEATED", "UNIQUE"]


def test_no_duplicate_intra_incoming_risk_flags():
    enriched = enrich_context_packet_v2_with_agent_result(
        _make_context(risk_flags=[]),
        _make_result(risk_flags=["R1", "R1", "R2"]),
    )
    assert enriched.risk_flags == ["R1", "R2"]


def test_no_duplicate_intra_incoming_contradictions():
    enriched = enrich_context_packet_v2_with_agent_result(
        _make_context(contradictions=[]),
        _make_result(contradictions=["C1", "C1", "C2"]),
    )
    assert enriched.contradictions == ["C1", "C2"]


def test_no_duplicate_intra_incoming_evidence_refs():
    enriched = enrich_context_packet_v2_with_agent_result(
        _make_context(source_refs=[]),
        _make_result(
            agent_id="data_purity",
            action_id="act-c8-001",
            evidence_refs=["proof:dup", "proof:dup", "proof:other"],
        ),
    )
    assert enriched.source_refs.count("proof:dup") == 1
    assert "proof:other" in enriched.source_refs


def test_source_refs_order_is_stable():
    enriched = enrich_context_packet_v2_with_agent_result(
        _make_context(source_refs=["ref://first"]),
        _make_result(
            agent_id="data_purity",
            action_id="act-c8-001",
            evidence_refs=["proof:second"],
        ),
    )

    assert enriched.source_refs == [
        "ref://first",
        "agent:data_purity",
        "action:act-c8-001",
        "proof:second",
    ]


def test_enrichment_is_deterministic():
    ctx = _make_context()
    result = _make_result()

    first = enrich_context_packet_v2_with_agent_result(ctx, result)
    second = enrich_context_packet_v2_with_agent_result(ctx, result)

    assert first == second


def test_original_context_not_mutated():
    ctx = _make_context(
        unknowns=["PRE_UNKNOWN"],
        risk_flags=["PRE_RISK"],
        contradictions=["PRE_CONTRADICTION"],
    )

    before_refs = list(ctx.source_refs)
    before_unknowns = list(ctx.unknowns)
    before_risk = list(ctx.risk_flags)
    before_contradictions = list(ctx.contradictions)

    enrich_context_packet_v2_with_agent_result(
        ctx,
        _make_result(unknowns=["NEW_UNKNOWN"]),
    )

    assert ctx.source_refs == before_refs
    assert ctx.unknowns == before_unknowns
    assert ctx.risk_flags == before_risk
    assert ctx.contradictions == before_contradictions


def test_original_result_not_mutated():
    result = _make_result(
        unknowns=["AGENT_UNKNOWN"],
        risk_flags=["AGENT_RISK"],
        contradictions=["AGENT_CONTRADICTION"],
        evidence_refs=["proof:orig"],
    )

    before_unknowns = list(result.packet.unknowns)
    before_risks = list(result.packet.risk_flags)
    before_contradictions = list(result.packet.contradictions)
    before_refs = list(result.packet.evidence_refs)

    enrich_context_packet_v2_with_agent_result(
        _make_context(),
        result,
    )

    assert result.packet.unknowns == before_unknowns
    assert result.packet.risk_flags == before_risks
    assert result.packet.contradictions == before_contradictions
    assert result.packet.evidence_refs == before_refs


def test_decision_authority_is_kx108_only():
    enriched = enrich_context_packet_v2_with_agent_result(
        _make_context(),
        _make_result(),
    )
    assert enriched.decision_authority == "KX108_ONLY"


def test_allowed_to_act_is_false():
    enriched = enrich_context_packet_v2_with_agent_result(
        _make_context(),
        _make_result(),
    )
    assert enriched.allowed_to_act is False


def test_allowed_to_decide_is_false():
    enriched = enrich_context_packet_v2_with_agent_result(
        _make_context(),
        _make_result(),
    )
    assert enriched.allowed_to_decide is False


def test_memory_write_is_false():
    enriched = enrich_context_packet_v2_with_agent_result(
        _make_context(),
        _make_result(),
    )
    assert enriched.memory_write is False


def test_kernel_mutation_is_false():
    enriched = enrich_context_packet_v2_with_agent_result(
        _make_context(),
        _make_result(),
    )
    assert enriched.kernel_mutation is False


def test_recommended_gate_none_produces_no_gate_flag():
    enriched = enrich_context_packet_v2_with_agent_result(
        _make_context(risk_flags=[]),
        _make_result(
            recommended_gate="NONE",
            risk_flags=[],
        ),
    )
    assert not any(
        flag.startswith("GATE_HINT:")
        for flag in enriched.risk_flags
    )


def test_recommended_gate_hold_produces_gate_flag():
    enriched = enrich_context_packet_v2_with_agent_result(
        _make_context(risk_flags=[]),
        _make_result(
            recommended_gate="HOLD",
            risk_flags=[],
        ),
    )
    assert "GATE_HINT:HOLD" in enriched.risk_flags


def test_recommended_gate_block_candidate_produces_gate_flag():
    enriched = enrich_context_packet_v2_with_agent_result(
        _make_context(risk_flags=[]),
        _make_result(
            recommended_gate="BLOCK_CANDIDATE",
            risk_flags=[],
        ),
    )
    assert "GATE_HINT:BLOCK_CANDIDATE" in enriched.risk_flags


def test_fail_closed_bad_context_type():
    with pytest.raises(
        TypeError,
        match="CONTEXT_PACKET_V2_TYPE_REQUIRED",
    ):
        enrich_context_packet_v2_with_agent_result(
            object(),
            _make_result(),
        )


def test_fail_closed_bad_result_type():
    with pytest.raises(
        TypeError,
        match="AGENT_RESULT_TYPE_REQUIRED",
    ):
        enrich_context_packet_v2_with_agent_result(
            _make_context(),
            object(),
        )


def test_fail_closed_can_emit_act_true():
    result = _make_result(can_emit_act=True)

    with pytest.raises(AssertionError):
        enrich_context_packet_v2_with_agent_result(
            _make_context(),
            result,
        )


def test_w1_compatibility():
    enriched = enrich_context_packet_v2_with_agent_result(
        _make_context(),
        _make_result(),
    )

    runtime_packet = build_cognitive_runtime_packet(
        enriched,
        signal_id="c8-w1-test",
    )

    runtime_packet.validate_invariants()


def test_w2_canonical_admission():
    # Use a clean context signal: this test proves traversal, not
    # Guard reaction to intentionally injected risk/contradiction fixtures.
    result = _make_result(
        unknowns=[],
        risk_flags=[],
        contradictions=[],
        evidence_refs=[],
        recommended_gate="NONE",
    )

    enriched = enrich_context_packet_v2_with_agent_result(
        _make_context(
            source_refs=[],
            unknowns=[],
            risk_flags=[],
            contradictions=[],
        ),
        result,
    )

    ticket = admit_cognitive_context(
        enriched,
        signal_id="c8-w2-canonical-test",
        critical_action_requested=False,
    )

    assert ticket.decision in (
        "ALLOW_CONTEXT_ONLY",
        "HOLD",
        "BLOCK",
    )
    assert ticket.decision_authority == "KX108_ONLY"
    assert ticket.emits_act is False
    ticket.validate_invariants()


def test_source_refs_and_hashes_are_parallel():
    enriched = enrich_context_packet_v2_with_agent_result(
        _make_context(source_refs=[]),
        _make_result(
            agent_id="data_purity",
            action_id="act-c8-001",
            evidence_refs=["proof:e1", "proof:e2"],
        ),
    )

    assert len(enriched.source_refs) == len(enriched.source_hashes)

    for ref, digest in zip(
        enriched.source_refs,
        enriched.source_hashes,
    ):
        assert _sha16(ref) == digest
