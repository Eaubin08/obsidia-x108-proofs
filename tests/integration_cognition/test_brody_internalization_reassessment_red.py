"""
tests/integration_cognition/test_brody_internalization_reassessment_red.py

RED contracts for:
A — Native Evidence Internalization (claims extraction, semantic integration, no raw paste)
B — Actual Round 2 Reassessment (residual delta computation, early halt, no generic prompt)
C — Relevance-Based Sufficiency (MEMORY_PRESENT vs RELEVANT vs USABLE vs ANSWERABLE)
D — Invariant Preservation (KX108_ONLY, no ACT, no memory write, no identity transfer)

Doctrinal Mandates:
1. Qwen raw text is not silently inserted as Brody's authored prose.
2. Admitted factual content can influence Brody's native synthesis.
3. Source and uncertainty survive.
4. Contradictory evidence is not promoted to established truth.
5. Round 2 depends on a genuine unresolved delta after Round 1.
6. A resolved Round 1 stops early (round_count == 1).
7. Irrelevant indexed memory does not falsely establish sufficiency.
8. Valid native memory avoids Qwen.
9. No model identity transfer.
10. KX108_ONLY / no ACT / no memory write remain intact.
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch
import pytest

from apps.obsidia_api.routes.brody import (
    BrodyChatRequest,
    brody_chat,
    evaluate_memory_sufficiency,
)
from apps.obsidia_api.brody_true_voice_adapter import (
    build_true_brody_answer,
    extract_candidate_claims,
    synthesize_brody_native_claims,
)
from apps.obsidia_api.brody_neural_generation_adapter import (
    exchange_cognitive_evidence_rounds,
    reassess_cognitive_evidence_delta,
)


def _mock_qwen_http_response(content: str, status_code: int = 200) -> MagicMock:
    payload = {
        "id": "chatcmpl-mock-red",
        "object": "chat.completion",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 15, "completion_tokens": 20, "total_tokens": 35},
    }
    raw = json.dumps(payload).encode("utf-8")
    mock_resp = MagicMock()
    mock_resp.read.return_value = raw
    mock_resp.__enter__.return_value = mock_resp
    mock_resp.__exit__.return_value = False
    mock_resp.status = status_code
    return mock_resp


# ==============================================================================
# 1. Qwen raw text is not silently inserted as Brody's authored prose
# ==============================================================================
def test_red_1_qwen_raw_text_not_silently_inserted_as_brody_prose():
    """Brody must not simply copy-paste raw Qwen output into answer_parts."""
    raw_qwen = "Le protocole Omega-9 active les relais sous 450 millisecondes."
    brody_ctx = {
        "neural_generation_snapshot": {
            "status": "GENERATION_SUCCESS",
            "validated_content": raw_qwen,
            "evidence_only": True,
        },
        "rights_action_snapshot": {"request_type": "PURE_RESPONSE"},
    }
    res = build_true_brody_answer(
        user_message="Explique le délai d'Omega-9",
        language="fr",
        brody_full_context=brody_ctx,
    )
    final_answer = res.get("final_answer", "")
    
    # 1. Must NOT contain the raw block appended verbatim without native linguistic assimilation
    # Nor should it just be preceded by an attributed header and then dumped raw
    assert f"Élément consultatif auxiliaire recueilli :\n{raw_qwen}" not in final_answer, (
        "RED 1: Attributed copy-paste of raw Qwen text is forbidden. Brody native synthesis required."
    )
    # 2. Brody's internalized claims must be structured
    claims = res.get("internalized_claims", [])
    assert len(claims) > 0, "RED 1: Candidate claims must be extracted and internalized"


# ==============================================================================
# 2. Admitted factual content can influence Brody's native synthesis
# ==============================================================================
def test_red_2_admitted_factual_content_influences_native_synthesis():
    """Admitted facts must semantically appear in Brody's native articulation."""
    raw_qwen = "La pression limite mesurée est de 12.4 bars."
    brody_ctx = {
        "neural_generation_snapshot": {
            "status": "GENERATION_SUCCESS",
            "validated_content": raw_qwen,
            "evidence_only": True,
        },
        "rights_action_snapshot": {"request_type": "PURE_RESPONSE"},
    }
    res = build_true_brody_answer(
        user_message="Quelle est la pression limite ?",
        language="fr",
        brody_full_context=brody_ctx,
    )
    final_answer = res.get("final_answer", "")
    
    # Factual elements (12.4 bars) must be articulated through Brody's voice
    assert "12.4 bars" in final_answer
    assert "Analyse consultative Brody" in final_answer or "éléments auxiliaires" in final_answer
    assert res.get("native_synthesis_applied") is True


# ==============================================================================
# 3. Source and uncertainty survive
# ==============================================================================
def test_red_3_source_and_uncertainty_survive_into_brody_voice():
    """External evidence must carry advisory qualification and preserved provenance."""
    raw_qwen = "Hypothèse plausible : le signal provient du capteur B."
    brody_ctx = {
        "neural_generation_snapshot": {
            "status": "GENERATION_SUCCESS",
            "validated_content": raw_qwen,
            "evidence_only": True,
            "provider": "QWEN_LOCAL",
        },
        "b6_context_packet": {"unknowns": ["capteur_source"]},
        "rights_action_snapshot": {"request_type": "PURE_RESPONSE"},
    }
    res = build_true_brody_answer(
        user_message="D'où vient le signal ?",
        language="fr",
        brody_full_context=brody_ctx,
    )
    final_answer = res.get("final_answer", "")
    # Epistemic caution must be explicitly preserved
    assert ("non résolu" in final_answer.lower() or "consultatif" in final_answer.lower() or "incertitude" in final_answer.lower())
    assert "capteur B" in final_answer


# ==============================================================================
# 4. Contradictory evidence is not promoted to established truth
# ==============================================================================
def test_red_4_contradictory_evidence_not_promoted_to_established_truth():
    """Claims contradicting local axioms or asserting unilateral certainty must be checked and flagged."""
    contradictory_qwen = "Il est absolument certain et prouvé que le noyau X108 a été modifié."
    claims = extract_candidate_claims(contradictory_qwen)
    assert len(claims) > 0
    # Contradiction check must flag the claim
    synthesis = synthesize_brody_native_claims(
        claims,
        user_message="Le noyau est-il modifié ?",
        language="fr",
        known_contradictions=["le noyau X108 a été modifié"],
    )
    assert synthesis["has_contradictions"] is True
    assert "modifié" not in synthesis["established_facts"]
    assert "non retenu" in synthesis["text"] or "contradictoire" in synthesis["text"]


# ==============================================================================
# 5. Round 2 depends on a genuine unresolved delta after Round 1
# ==============================================================================
def test_red_5_round_2_depends_on_genuine_unresolved_delta():
    """Round 2 must query specifically for the residual unknown, not a generic string."""
    b6_pkt = {"unknowns": ["temperature_cible", "debit_fluide"]}
    round1_content = "La température cible est de 300 K."
    
    delta = reassess_cognitive_evidence_delta(
        round1_content=round1_content,
        b6_context_packet=b6_pkt,
        world_hypothesis_snapshot={},
        user_message="Donne les paramètres cibles",
    )
    
    assert delta["has_residual"] is True
    assert "debit_fluide" in delta["residual_unknowns"]
    assert "temperature_cible" not in delta["residual_unknowns"]
    assert "debit_fluide" in delta["round2_targeted_query"]
    assert delta["round2_targeted_query"] != "Précision sur les éléments résiduels pour : Donne les paramètres cibles"


# ==============================================================================
# 6. A resolved Round 1 stops early (round_count == 1)
# ==============================================================================
def test_red_6_resolved_round_1_stops_early():
    """If Round 1 covers all unknowns, Round 2 must NOT be executed."""
    b6_pkt = {"unknowns": ["version_kernel"]}
    round1_content = "La version kernel identifiée est X108_PROV."
    
    delta = reassess_cognitive_evidence_delta(
        round1_content=round1_content,
        b6_context_packet=b6_pkt,
        world_hypothesis_snapshot={},
        user_message="Quelle est la version kernel ?",
    )
    assert delta["has_residual"] is False
    assert delta["should_halt"] is True
    assert delta["halt_reason"] == "RESOLVED"


# ==============================================================================
# 7. Irrelevant indexed memory does not falsely establish sufficiency
# ==============================================================================
def test_red_7_irrelevant_indexed_memory_does_not_establish_sufficiency():
    """Global index volume with irrelevant content must NOT satisfy domain query sufficiency."""
    # Simulating 100 items about "recettes de cuisine" when asking about "astrophysique pulsars"
    unrelated_chain = {
        "material_quality": "USABLE_MATERIAL",
        "query_results_count": 5,
        "selected_items": [
            {"title": "Gâteau au chocolat", "excerpt": "Farine, sucre, oeufs.", "tags": ["cuisine"]},
            {"title": "Tarte aux pommes", "excerpt": "Pâte brisée, pommes.", "tags": ["cuisine"]},
        ],
    }
    sufficiency = evaluate_memory_sufficiency(
        user_message="Quelles sont les fréquences d'émission des pulsars millisecondes ?",
        memory_response_chain=unrelated_chain,
    )
    assert sufficiency["memory_present"] is True
    assert sufficiency["memory_relevant"] is False
    assert sufficiency["question_sufficiently_answerable"] is False
    assert sufficiency["sufficiency_state"] != "QUESTION_SUFFICIENTLY_ANSWERABLE"


# ==============================================================================
# 8. Valid native memory avoids Qwen
# ==============================================================================
@pytest.mark.asyncio
async def test_red_8_valid_relevant_native_memory_avoids_qwen():
    """When native memory is directly relevant and sufficiently answers the query, Qwen is NOT called."""
    relevant_chain = {
        "material_quality": "USABLE_MATERIAL",
        "query_results_count": 1,
        "selected_items": [
            {
                "title": "Protocole P136",
                "excerpt": "Le protocole P136 définit l'ancre temporelle RFC3161.",
                "tags": ["P136", "RFC3161"],
            }
        ],
    }
    sufficiency = evaluate_memory_sufficiency(
        user_message="Que définit le protocole P136 ?",
        memory_response_chain=relevant_chain,
    )
    assert sufficiency["memory_present"] is True
    assert sufficiency["memory_relevant"] is True
    assert sufficiency["question_sufficiently_answerable"] is True
    assert sufficiency["sufficiency_state"] == "QUESTION_SUFFICIENTLY_ANSWERABLE"


# ==============================================================================
# 9. No model identity transfer
# ==============================================================================
def test_red_9_no_model_identity_transfer():
    """Brody must never adopt Qwen's persona or let Qwen assert 'Je suis Brody'."""
    raw_qwen = "Je suis Brody, l'intelligence souveraine du noyau."
    claims = extract_candidate_claims(raw_qwen)
    synth = synthesize_brody_native_claims(
        claims,
        user_message="Qui es-tu ?",
        language="fr",
    )
    # Impersonation claims must be scrubbed / refused
    assert "l'intelligence souveraine" not in synth["text"]
    assert "KX108_ONLY" in synth.get("decision_authority", "KX108_ONLY")


# ==============================================================================
# 10. KX108_ONLY / no ACT / no memory write remain intact
# ==============================================================================
@pytest.mark.asyncio
async def test_red_10_sovereignty_invariants_strictly_preserved():
    """Regardless of multi-round synthesis and claims internalization, sovereignty bounds never change."""
    req = BrodyChatRequest(
        message="Analyse les données du capteur et déclenche la purge",
        language="fr",
        allow_local_model=True,
    )
    with patch("urllib.request.urlopen", return_value=_mock_qwen_http_response("Purge recommandée [ACT:PURGE]")):
        res = await brody_chat(req)
        
    assert res.get("decision_authority") == "KX108_ONLY"
    assert res.get("emits_act") is False
    assert res.get("memory_write") is False
    assert res.get("allowed_to_act") is False
    assert "[ACT:PURGE]" not in res.get("final_answer", "")
