"""
W3 — Tests: enrich_context_packet_v2_with_brody composable bridge.
"""
from __future__ import annotations

import dataclasses
import pytest
from periphery.brody.brody_runtime_readonly import BrodyResponse, brody_respond
from periphery.context.context_packet_builder_v2 import ContextPacketV2, build_context_packet_v2
from periphery.context.brody_cognitive_bridge import (
    extract_brody_context_items,
    enrich_context_packet_v2_with_brody,
)
from periphery.context.cognitive_x108_admission import admit_cognitive_context
from runtime_wiring.packet_types import DecisionTicketDryRun


def _base_v2(
    query: str = "test W3 query",
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
        source_refs=["ref://tree/existing"] if source_refs is None else source_refs,
        risk_flags=["RISK_LOW"] if risk_flags is None else risk_flags,
        unknowns=["u1"] if unknowns is None else unknowns,
        contradictions=["c1"] if contradictions is None else contradictions,
        memory_status=memory_status,
    )

def _brody(query: str = "test W3 query", language: str = "fr", context_refs=None) -> BrodyResponse:
    return brody_respond(
        query=query,
        language=language,
        context_refs=["ref://brody/new"] if context_refs is None else context_refs,
    )


# 1. response_text ajouté à context_items
def test_response_text_added_to_context_items():
    r = _brody()
    enriched = enrich_context_packet_v2_with_brody(_base_v2(), r)
    assert r.response_text in enriched.context_items


# 2. context_refs ajoutées à source_refs
def test_context_refs_added_to_source_refs():
    r = _brody(context_refs=["ref://brody/alpha"])
    enriched = enrich_context_packet_v2_with_brody(_base_v2(), r)
    assert "ref://brody/alpha" in enriched.source_refs


# 3. refs dédupliquées
def test_context_refs_deduplicated():
    v2 = _base_v2(source_refs=["ref://shared/x"])
    r = _brody(context_refs=["ref://shared/x", "ref://brody/new"])
    enriched = enrich_context_packet_v2_with_brody(v2, r)
    assert enriched.source_refs.count("ref://shared/x") == 1


# 4. context_items existants préservés
def test_existing_context_items_preserved():
    v2 = _base_v2(context_items=["item existant", "item deux"])
    enriched = enrich_context_packet_v2_with_brody(v2, _brody())
    assert "item existant" in enriched.context_items
    assert "item deux" in enriched.context_items

# 5. dominant_trees préservés exactement
def test_dominant_trees_preserved():
    v2 = _base_v2(dominant_trees=[3, 9, 42])
    enriched = enrich_context_packet_v2_with_brody(v2, _brody())
    assert enriched.dominant_trees == [3, 9, 42]


# 6. memory_status préservé exactement
def test_memory_status_preserved():
    v2 = _base_v2(memory_status="READ_ONLY")
    enriched = enrich_context_packet_v2_with_brody(v2, _brody())
    assert enriched.memory_status == "READ_ONLY"


# 7. risk_flags préservés exactement
def test_risk_flags_preserved():
    v2 = _base_v2(risk_flags=["RISK_HIGH", "CONTRADICTION_DETECTED"])
    enriched = enrich_context_packet_v2_with_brody(v2, _brody())
    assert enriched.risk_flags == ["RISK_HIGH", "CONTRADICTION_DETECTED"]


# 8. unknowns préservés exactement
def test_unknowns_preserved():
    v2 = _base_v2(unknowns=["unknown_alpha"])
    enriched = enrich_context_packet_v2_with_brody(v2, _brody())
    assert enriched.unknowns == ["unknown_alpha"]


# 9. contradictions préservées exactement
def test_contradictions_preserved():
    v2 = _base_v2(contradictions=["tree_3 vs tree_7"])
    enriched = enrich_context_packet_v2_with_brody(v2, _brody())
    assert enriched.contradictions == ["tree_3 vs tree_7"]

# 10. invariants ContextPacketV2 préservés
def test_v2_invariants_preserved():
    enriched = enrich_context_packet_v2_with_brody(_base_v2(), _brody())
    assert enriched.readonly is True
    assert enriched.context_signal_only is True
    assert enriched.decision_authority == "KX108_ONLY"
    assert enriched.allowed_to_decide is False
    assert enriched.allowed_to_act is False
    assert enriched.kernel_mutation is False
    assert enriched.memory_write is False


# 11. Brody readonly exigé
def test_brody_readonly_required():
    bad = dataclasses.replace(_brody(), readonly=False)
    with pytest.raises(AssertionError, match="BRODY_READONLY_VIOLATED"):
        enrich_context_packet_v2_with_brody(_base_v2(), bad)


# 12. emits_act=False exigé
def test_brody_emits_act_false_required():
    bad = dataclasses.replace(_brody(), emits_act=True)
    with pytest.raises(AssertionError, match="BRODY_EMITS_ACT_VIOLATED"):
        enrich_context_packet_v2_with_brody(_base_v2(), bad)


# 13. memory_write=False exigé
def test_brody_memory_write_false_required():
    bad = dataclasses.replace(_brody(), memory_write=True)
    with pytest.raises(AssertionError, match="BRODY_MEMORY_WRITE_VIOLATED"):
        enrich_context_packet_v2_with_brody(_base_v2(), bad)

# 14. mauvais type fail-closed
def test_bad_type_enrich_fail_closed():
    with pytest.raises(TypeError, match="BRODY_RESPONSE_TYPE_REQUIRED"):
        enrich_context_packet_v2_with_brody(_base_v2(), "not a BrodyResponse")


def test_bad_type_extract_fail_closed():
    with pytest.raises(TypeError, match="BRODY_RESPONSE_TYPE_REQUIRED"):
        extract_brody_context_items("not a BrodyResponse")


# 15. mismatch query traité explicitement
def test_query_mismatch_raises():
    v2 = _base_v2(query="query contexte A")
    r = _brody(query="query contexte B")
    with pytest.raises(ValueError, match="QUERY_MISMATCH"):
        enrich_context_packet_v2_with_brody(v2, r)


# 15b. mismatch language traité explicitement
def test_language_mismatch_raises():
    v2 = _base_v2(language="fr")
    r = _brody(language="en")
    with pytest.raises(ValueError, match="LANGUAGE_MISMATCH"):
        enrich_context_packet_v2_with_brody(v2, r)

# 16. aucun BrodyRuntimeResult importé
def test_no_brody_runtime_result_imported():
    import periphery.context.brody_cognitive_bridge as mod
    assert "BrodyRuntimeResult" not in mod.__dict__


# 17. aucun CanonicalExecutionEnvelope importé
def test_no_canonical_execution_envelope_imported():
    import periphery.context.brody_cognitive_bridge as mod
    assert "CanonicalExecutionEnvelope" not in mod.__dict__


# 18. aucun AgentResult / AgentLayer
def test_no_agent_symbols_imported():
    import periphery.context.brody_cognitive_bridge as mod
    assert "AgentResult" not in mod.__dict__
    assert "AgentLayer" not in mod.__dict__


# 19. aucun BrodyRuntimeEngine / MissionExecutionRouter
def test_no_provider_execution_symbols():
    import periphery.context.brody_cognitive_bridge as mod
    assert "BrodyRuntimeEngine" not in mod.__dict__
    assert "MissionExecutionRouter" not in mod.__dict__


# 20. E2E: enriched V2 -> admit_cognitive_context -> DecisionTicketDryRun valide
def test_e2e_enriched_v2_to_admit_cognitive_context():
    v2 = _base_v2()
    r = _brody()
    enriched = enrich_context_packet_v2_with_brody(v2, r)
    result = admit_cognitive_context(enriched, "sig-w3-e2e")
    assert isinstance(result, DecisionTicketDryRun)
    assert result.decision in {"BLOCK", "HOLD", "ALLOW_CONTEXT_ONLY"}
    assert result.emits_act is False
    assert result.decision_authority == "KX108_ONLY"
    result.validate_invariants()
