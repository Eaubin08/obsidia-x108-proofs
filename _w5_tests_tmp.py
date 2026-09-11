"""
W5 -- Tests: enrich_context_packet_v2_with_tree_signal -> ContextPacketV2.
27 tests.
"""
from __future__ import annotations
import hashlib
import pytest
from periphery.cognitive_trees.tree_signal_packet import TreeSignalPacket
from periphery.context.context_packet_builder_v2 import ContextPacketV2, build_context_packet_v2
from periphery.context.tree_signal_cognitive_bridge import enrich_context_packet_v2_with_tree_signal
from periphery.context.cognitive_x108_admission import admit_cognitive_context
from runtime_wiring.packet_types import DecisionTicketDryRun


def _sha16(ref):
    return hashlib.sha256(ref.encode()).hexdigest()[:16]


def _packet(signal_id=None, dominant_ids=None, readonly=True, advisory_only=True,
            context_signal_only=True, can_decide=False, can_emit_act=False,
            emits_act=False, emits_verdict=False, memory_write=False,
            graphiti_write=False, neo4j_write=False, kernel_mutation=False,
            x108_mutation=False, decision_authority=None):
    if signal_id is None: signal_id = "sig-w5-test"
    if decision_authority is None: decision_authority = "KX108_ONLY"
    return TreeSignalPacket(
        signal_id=signal_id, vector_id="vec-" + signal_id,
        dominant_ids=dominant_ids if dominant_ids is not None else [0, 6, 12],
        dominant_trees=["ARBRE_1", "ARBRE_7", "ARBRE_13"],
        dominant_count=3, patterns_detected=["LANGUAGE_PATTERN_DETECTED"],
        active_domains=["memory", "governance"],
        memory_relevance=0.5, world_relevance=0.5,
        readonly=readonly, advisory_only=advisory_only,
        context_signal_only=context_signal_only, can_decide=can_decide,
        can_emit_act=can_emit_act, emits_act=emits_act, emits_verdict=emits_verdict,
        memory_write=memory_write, graphiti_write=graphiti_write,
        neo4j_write=neo4j_write, kernel_mutation=kernel_mutation,
        x108_mutation=x108_mutation, decision_authority=decision_authority,
    )


def _v2(dominant_trees=None, source_refs=None, context_items=None):
    return build_context_packet_v2(
        query="test W5 tree signal", language="fr",
        context_items=context_items or ["item existant"],
        source_refs=source_refs or [], dominant_trees=dominant_trees or [],
        memory_status="CANDIDATE_ONLY", risk_flags=["RISK_LOW"],
        unknowns=["u1"], contradictions=["c1"],
    )


# 1. dominant_ids [0] -> dominant_trees [1]
def test_single_dominant_id_maps_to_canonical_tree_id():
    result = enrich_context_packet_v2_with_tree_signal(_v2(), _packet(dominant_ids=[0]))
    assert result.dominant_trees == [1]


# 2. [0, 6, 12] -> [1, 7, 13]
def test_multiple_dominant_ids_mapped_correctly():
    result = enrich_context_packet_v2_with_tree_signal(_v2(), _packet(dominant_ids=[0, 6, 12]))
    assert result.dominant_trees == [1, 7, 13]


# 3. ordre preserve
def test_order_preserved():
    result = enrich_context_packet_v2_with_tree_signal(_v2(), _packet(dominant_ids=[12, 0, 6]))
    assert result.dominant_trees == [13, 1, 7]


# 4. dominant_trees existants preserves
def test_existing_dominant_trees_preserved():
    result = enrich_context_packet_v2_with_tree_signal(
        _v2(dominant_trees=[5]), _packet(dominant_ids=[0])
    )
    assert 5 in result.dominant_trees
    assert 1 in result.dominant_trees


# 5. union dedupliquee (existants en premier)
def test_union_deduplicated():
    result = enrich_context_packet_v2_with_tree_signal(
        _v2(dominant_trees=[1, 5]), _packet(dominant_ids=[0, 6])
    )
    assert result.dominant_trees.count(1) == 1
    assert result.dominant_trees[0] == 1
    assert 5 in result.dominant_trees
    assert 7 in result.dominant_trees


# 6. noms string packet.dominant_trees jamais utilises comme IDs
def test_dominant_trees_strings_not_used_as_ids():
    result = enrich_context_packet_v2_with_tree_signal(_v2(), _packet(dominant_ids=[0]))
    for v in result.dominant_trees:
        assert isinstance(v, int)
    assert "ARBRE_1" not in result.dominant_trees
    assert "ARBRE_7" not in result.dominant_trees


# 7. signal provenance ajoutee dans source_refs
def test_signal_provenance_added_to_source_refs():
    result = enrich_context_packet_v2_with_tree_signal(_v2(), _packet(signal_id="sig-w5-prov"))
    assert "sig-w5-prov" in result.source_refs


# 8. source_hash parallele exact
def test_source_hash_parallel_exact():
    result = enrich_context_packet_v2_with_tree_signal(_v2(), _packet(signal_id="sig-w5-hash"))
    idx = result.source_refs.index("sig-w5-hash")
    assert result.source_hashes[idx] == _sha16("sig-w5-hash")
    assert len(result.source_refs) == len(result.source_hashes)


# 9. context_items inchanges
def test_context_items_unchanged():
    v2 = _v2(context_items=["item A", "item B"])
    result = enrich_context_packet_v2_with_tree_signal(v2, _packet())
    assert result.context_items == ["item A", "item B"]


# 10. patterns_detected non injectes dans context_items
def test_patterns_not_injected_into_context_items():
    result = enrich_context_packet_v2_with_tree_signal(_v2(), _packet())
    for item in result.context_items:
        assert "LANGUAGE_PATTERN_DETECTED" not in item
        assert "PATTERN" not in item


# 11. active_domains non injectes dans context_items
def test_active_domains_not_injected_into_context_items():
    result = enrich_context_packet_v2_with_tree_signal(_v2(), _packet())
    assert result.context_items == ["item existant"]


# 12. memory_relevance non mappe vers memory_status
def test_memory_relevance_not_mapped_to_memory_status():
    result = enrich_context_packet_v2_with_tree_signal(_v2(), _packet())
    assert result.memory_status == "CANDIDATE_ONLY"
    assert "0.5" not in result.memory_status


# 13. memory_relevance non mappe vers risk_flags
def test_memory_relevance_not_mapped_to_risk_flags():
    result = enrich_context_packet_v2_with_tree_signal(_v2(), _packet())
    for flag in result.risk_flags:
        assert "MEMORY_RELEVANCE" not in flag
        assert "0.5" not in flag


# 14. world_relevance non mappe vers risk_flags
def test_world_relevance_not_mapped_to_risk_flags():
    result = enrich_context_packet_v2_with_tree_signal(_v2(), _packet())
    for flag in result.risk_flags:
        assert "WORLD_RELEVANCE" not in flag


# 15. domain_sigma_envelope non injecte
def test_domain_sigma_envelope_not_injected():
    result = enrich_context_packet_v2_with_tree_signal(_v2(), _packet())
    all_content = str(result.context_items) + str(result.source_refs)
    assert "domain_sigma" not in all_content


# 16. memory_status inchange
def test_memory_status_unchanged():
    result = enrich_context_packet_v2_with_tree_signal(_v2(), _packet())
    assert result.memory_status == "CANDIDATE_ONLY"


# 17. risk_flags inchanges
def test_risk_flags_unchanged():
    result = enrich_context_packet_v2_with_tree_signal(_v2(), _packet())
    assert result.risk_flags == ["RISK_LOW"]


# 18. unknowns inchanges
def test_unknowns_unchanged():
    result = enrich_context_packet_v2_with_tree_signal(_v2(), _packet())
    assert result.unknowns == ["u1"]


# 19. contradictions inchangees
def test_contradictions_unchanged():
    result = enrich_context_packet_v2_with_tree_signal(_v2(), _packet())
    assert result.contradictions == ["c1"]


# 20. query/language inchanges
def test_query_language_unchanged():
    result = enrich_context_packet_v2_with_tree_signal(_v2(), _packet())
    assert result.query == "test W5 tree signal"
    assert result.language == "fr"


# 21a. fail-closed: readonly=False
def test_fail_closed_readonly():
    with pytest.raises(AssertionError, match="READONLY_VIOLATED"):
        enrich_context_packet_v2_with_tree_signal(_v2(), _packet(readonly=False))


# 21b. fail-closed: advisory_only=False
def test_fail_closed_advisory_only():
    with pytest.raises(AssertionError, match="ADVISORY_ONLY_VIOLATED"):
        enrich_context_packet_v2_with_tree_signal(_v2(), _packet(advisory_only=False))


# 21c. fail-closed: emits_act=True
def test_fail_closed_emits_act():
    with pytest.raises(AssertionError, match="EMITS_ACT_VIOLATED"):
        enrich_context_packet_v2_with_tree_signal(_v2(), _packet(emits_act=True))


# 21d. fail-closed: memory_write=True
def test_fail_closed_memory_write():
    with pytest.raises(AssertionError, match="MEMORY_WRITE_VIOLATED"):
        enrich_context_packet_v2_with_tree_signal(_v2(), _packet(memory_write=True))


# 21e. fail-closed: kernel_mutation=True
def test_fail_closed_kernel_mutation():
    with pytest.raises(AssertionError, match="KERNEL_MUTATION_VIOLATED"):
        enrich_context_packet_v2_with_tree_signal(_v2(), _packet(kernel_mutation=True))


# 21f. fail-closed: x108_mutation=True
def test_fail_closed_x108_mutation():
    with pytest.raises(AssertionError, match="X108_MUTATION_VIOLATED"):
        enrich_context_packet_v2_with_tree_signal(_v2(), _packet(x108_mutation=True))


# 22. mauvais type fail-closed
def test_fail_closed_bad_type():
    with pytest.raises(TypeError, match="TREE_SIGNAL_PACKET_TYPE_REQUIRED"):
        enrich_context_packet_v2_with_tree_signal(_v2(), "not a packet")


# 23. IDs negatifs rejetes
def test_fail_closed_negative_dominant_id():
    with pytest.raises(ValueError, match="DOMINANT_IDS_NEGATIVE"):
        enrich_context_packet_v2_with_tree_signal(_v2(), _packet(dominant_ids=[-1]))


# 24. aucun AgentResult / AgentLayer dans le module
def test_no_agent_symbols_in_module():
    import periphery.context.tree_signal_cognitive_bridge as mod
    assert "AgentResult" not in mod.__dict__
    assert "AgentLayer" not in mod.__dict__


# 25. aucun Sigma DomainAggregate / AgentVote
def test_no_sigma_execution_symbols():
    import periphery.context.tree_signal_cognitive_bridge as mod
    assert "DomainAggregate" not in mod.__dict__
    assert "AgentVote" not in mod.__dict__


# 26. aucun symbole execution plane
def test_no_execution_plane_symbols():
    import periphery.context.tree_signal_cognitive_bridge as mod
    assert "BrodyRuntimeResult" not in mod.__dict__
    assert "CanonicalDecisionEnvelope" not in mod.__dict__
    assert "MissionSequencer" not in mod.__dict__


# 27. E2E: ContextPacketV2 -> enrich -> admit -> DecisionTicketDryRun
def test_e2e_enrich_then_admit():
    v2 = _v2()
    enriched = enrich_context_packet_v2_with_tree_signal(v2, _packet(signal_id="sig-w5-e2e"))
    assert 1 in enriched.dominant_trees
    assert 7 in enriched.dominant_trees
    ticket = admit_cognitive_context(enriched, "sig-w5-e2e")
    assert isinstance(ticket, DecisionTicketDryRun)
    assert ticket.decision in ("ALLOW_CONTEXT_ONLY", "HOLD", "BLOCK")
    ticket.validate_invariants()
