"""
W4 — Tests: enrich_context_packet_v2_with_memory composable bridge.
"""
from __future__ import annotations

import dataclasses
import hashlib
import pytest

from periphery.memory.memory_candidate import MemoryCandidate, build_memory_candidate_v2
from periphery.memory.memory_source_types import MemorySourceType
from periphery.context.context_packet_builder_v2 import ContextPacketV2, build_context_packet_v2
from periphery.context.memory_cognitive_bridge import (
    extract_memory_context_items,
    enrich_context_packet_v2_with_memory,
)
from periphery.context.cognitive_x108_admission import admit_cognitive_context
from runtime_wiring.packet_types import DecisionTicketDryRun


def _sha16(ref: str) -> str:
    return hashlib.sha256(ref.encode()).hexdigest()[:16]


def _base_v2(
    query: str = "test W4 query",
    language: str = "fr",
    dominant_trees=None,
    context_items=None,
    source_refs=None,
    risk_flags=None,
    unknowns=None,
    contradictions=None,
    memory_status: str = "CANDIDATE_ONLY",
) -> ContextPacketV2:
    return build_context_packet_v2(
        query=query,
        language=language,
        dominant_trees=[1, 7, 13] if dominant_trees is None else dominant_trees,
        context_items=["item existant"] if context_items is None else context_items,
        source_refs=["ref://existing/1"] if source_refs is None else source_refs,
        risk_flags=["RISK_LOW"] if risk_flags is None else risk_flags,
        unknowns=["u1"] if unknowns is None else unknowns,
        contradictions=["c1"] if contradictions is None else contradictions,
        memory_status=memory_status,
    )

def _cand(
    source_id: str = "mem-src-w4",
    content: str = "resume memoire candidat W4",
    risk_flags=None,
) -> MemoryCandidate:
    c = build_memory_candidate_v2(
        source_id=source_id,
        source_type=MemorySourceType.OPERATOR_SESSION,
        content=content,
    )
    if risk_flags is None:
        return c
    return dataclasses.replace(c, risk_flags=risk_flags)


# 1. content_summary ajouté à context_items
def test_content_summary_added():
    c = _cand()
    enriched = enrich_context_packet_v2_with_memory(_base_v2(), c)
    assert c.content_summary in enriched.context_items

# 2. context_items existants préservés
def test_existing_context_items_preserved():
    v2 = _base_v2(context_items=["item A", "item B"])
    enriched = enrich_context_packet_v2_with_memory(v2, _cand())
    assert "item A" in enriched.context_items
    assert "item B" in enriched.context_items

# 3. content_summary dédupliqué
def test_content_summary_deduplicated():
    summary = "resume unique W4"
    c = _cand(content=summary)
    v2 = _base_v2(context_items=[summary])
    enriched = enrich_context_packet_v2_with_memory(v2, c)
    assert enriched.context_items.count(summary) == 1

# 4. source_id ajouté à source_refs
def test_source_id_added_to_source_refs():
    c = _cand(source_id="mem-new-42")
    enriched = enrich_context_packet_v2_with_memory(_base_v2(), c)
    assert "mem-new-42" in enriched.source_refs

# 5. source_refs existants préservés
def test_existing_source_refs_preserved():
    v2 = _base_v2(source_refs=["ref://pre/existing"])
    enriched = enrich_context_packet_v2_with_memory(v2, _cand(source_id="mem-new-99"))
    assert "ref://pre/existing" in enriched.source_refs

# 6. source_refs dédupliqués
def test_source_refs_deduplicated():
    sid = "mem-shared-id"
    v2 = _base_v2(source_refs=[sid])
    enriched = enrich_context_packet_v2_with_memory(v2, _cand(source_id=sid))
    assert enriched.source_refs.count(sid) == 1

# 7. source_hashes parallèle exact avec source_refs
def test_source_hashes_parallel_exact():
    c = _cand(source_id="mem-hash-par")
    enriched = enrich_context_packet_v2_with_memory(_base_v2(source_refs=[]), c)
    assert len(enriched.source_hashes) == len(enriched.source_refs)
    for ref, h in zip(enriched.source_refs, enriched.source_hashes):
        assert h == _sha16(ref)

# 8. hash = sha256(source_id)[:16] — convention canonique
def test_hash_is_sha256_of_source_id():
    sid = "mem-canonical-hash-check"
    v2_clean = build_context_packet_v2(query="test W4 query", language="fr", source_refs=[])
    enriched = enrich_context_packet_v2_with_memory(v2_clean, _cand(source_id=sid))
    assert _sha16(sid) in enriched.source_hashes

# 9. content_hash ne remplace pas le hash du source_ref
def test_content_hash_not_used_as_source_hash():
    c = _cand(source_id="mem-src-check", content="contenu test")
    v2_clean = build_context_packet_v2(query="test W4 query", language="fr", source_refs=[])
    enriched = enrich_context_packet_v2_with_memory(v2_clean, c)
    assert c.content_hash not in enriched.source_hashes
    assert _sha16("mem-src-check") in enriched.source_hashes

# 10. risk_flags ajoutés
def test_risk_flags_added():
    c = _cand(risk_flags=["RISK_MEMORY", "RISK_CANDIDATE"])
    enriched = enrich_context_packet_v2_with_memory(_base_v2(risk_flags=[]), c)
    assert "RISK_MEMORY" in enriched.risk_flags
    assert "RISK_CANDIDATE" in enriched.risk_flags

# 11. risk_flags existants préservés
def test_existing_risk_flags_preserved():
    v2 = _base_v2(risk_flags=["RISK_EXISTING"])
    c = _cand(risk_flags=["RISK_NEW"])
    enriched = enrich_context_packet_v2_with_memory(v2, c)
    assert "RISK_EXISTING" in enriched.risk_flags
    assert "RISK_NEW" in enriched.risk_flags

# 12. risk_flags dédupliqués
def test_risk_flags_deduplicated():
    v2 = _base_v2(risk_flags=["RISK_SHARED"])
    c = _cand(risk_flags=["RISK_SHARED", "RISK_NEW"])
    enriched = enrich_context_packet_v2_with_memory(v2, c)
    assert enriched.risk_flags.count("RISK_SHARED") == 1

# 13. dominant_trees inchangés
def test_dominant_trees_unchanged():
    v2 = _base_v2(dominant_trees=[5, 11, 23])
    enriched = enrich_context_packet_v2_with_memory(v2, _cand())
    assert enriched.dominant_trees == [5, 11, 23]

# 14. memory_status inchangé
def test_memory_status_unchanged():
    v2 = _base_v2(memory_status="READ_ONLY")
    enriched = enrich_context_packet_v2_with_memory(v2, _cand())
    assert enriched.memory_status == "READ_ONLY"

# 15. unknowns inchangés
def test_unknowns_unchanged():
    v2 = _base_v2(unknowns=["unknown_alpha"])
    enriched = enrich_context_packet_v2_with_memory(v2, _cand())
    assert enriched.unknowns == ["unknown_alpha"]

# 16. contradictions inchangées
def test_contradictions_unchanged():
    v2 = _base_v2(contradictions=["contr_x vs contr_y"])
    enriched = enrich_context_packet_v2_with_memory(v2, _cand())
    assert enriched.contradictions == ["contr_x vs contr_y"]

# 17. query inchangée
def test_query_unchanged():
    v2 = _base_v2(query="query originale inchangee")
    enriched = enrich_context_packet_v2_with_memory(v2, _cand())
    assert enriched.query == "query originale inchangee"

# 18. language inchangée
def test_language_unchanged():
    v2 = _base_v2(language="fr")
    enriched = enrich_context_packet_v2_with_memory(v2, _cand())
    assert enriched.language == "fr"

# 19. invariants ContextPacketV2 inchangés
def test_v2_invariants_unchanged():
    enriched = enrich_context_packet_v2_with_memory(_base_v2(), _cand())
    assert enriched.readonly is True
    assert enriched.context_signal_only is True
    assert enriched.decision_authority == "KX108_ONLY"
    assert enriched.allowed_to_decide is False
    assert enriched.allowed_to_act is False
    assert enriched.kernel_mutation is False
    assert enriched.memory_write is False

# 20. memory_write_allowed=True -> fail closed
def test_memory_write_allowed_true_fails():
    bad = dataclasses.replace(_cand(), memory_write_allowed=True)
    with pytest.raises(AssertionError, match="MEMORY_WRITE_ALLOWED_VIOLATED"):
        enrich_context_packet_v2_with_memory(_base_v2(), bad)

# 21. auto_promotion_allowed=True -> fail closed
def test_auto_promotion_allowed_true_fails():
    bad = dataclasses.replace(_cand(), auto_promotion_allowed=True)
    with pytest.raises(AssertionError, match="AUTO_PROMOTION_ALLOWED_VIOLATED"):
        enrich_context_packet_v2_with_memory(_base_v2(), bad)

# 22. mauvais type -> fail closed
def test_bad_type_enrich_fails():
    with pytest.raises(TypeError, match="MEMORY_CANDIDATE_TYPE_REQUIRED"):
        enrich_context_packet_v2_with_memory(_base_v2(), "not a MemoryCandidate")

def test_bad_type_extract_fails():
    with pytest.raises(TypeError, match="MEMORY_CANDIDATE_TYPE_REQUIRED"):
        extract_memory_context_items("not a MemoryCandidate")

# 23. aucun Graphiti importé
def test_no_graphiti_imported():
    import periphery.context.memory_cognitive_bridge as mod
    assert "GraphitiContextResult" not in mod.__dict__
    assert "GraphitiContextPacket" not in mod.__dict__
    assert "query_graphiti_readonly" not in mod.__dict__

# 24. aucun provider/execution importé
def test_no_provider_execution_imported():
    import periphery.context.memory_cognitive_bridge as mod
    assert "BrodyRuntimeEngine" not in mod.__dict__
    assert "BrodyRuntimeResult" not in mod.__dict__
    assert "CanonicalExecutionEnvelope" not in mod.__dict__

# 25. aucun AgentResult / AgentLayer
def test_no_agent_symbols_imported():
    import periphery.context.memory_cognitive_bridge as mod
    assert "AgentResult" not in mod.__dict__
    assert "AgentLayer" not in mod.__dict__

# 26. E2E : V2 enrichi Memory -> W2 -> DecisionTicketDryRun valide
def test_e2e_enriched_memory_to_admit_cognitive_context():
    v2 = _base_v2()
    c = _cand()
    enriched = enrich_context_packet_v2_with_memory(v2, c)
    result = admit_cognitive_context(enriched, "sig-w4-e2e")
    assert isinstance(result, DecisionTicketDryRun)
    assert result.decision in {"BLOCK", "HOLD", "ALLOW_CONTEXT_ONLY"}
    assert result.emits_act is False
    assert result.decision_authority == "KX108_ONLY"
    result.validate_invariants()
