"""
tests/integration_cognition/test_brody_semantic_adversarial_red.py

Adversarial RED Suite reproducing the 5 verified counter-audit findings:
A — Raw claim verbatim reuse inside template wrapping.
B — Negative / unresolved statements ("reste inconnue") falsely resolving B6 unknowns.
C — Topic-relevant memory lacking the answer falsely declaring QUESTION_SUFFICIENTLY_ANSWERABLE.
D — Conflicting property values (10 bars vs 15 bars) admitted without contradiction detection.
E — Non-deterministic claim identifiers across separate Python executions.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from unittest.mock import patch, MagicMock
import pytest

from apps.obsidia_api.routes.brody import (
    BrodyChatRequest,
    brody_chat,
    evaluate_memory_sufficiency,
)
from apps.obsidia_api.brody_neural_generation_adapter import (
    reassess_cognitive_evidence_delta,
)
from apps.obsidia_api.brody_true_voice_adapter import (
    build_true_brody_answer,
    extract_candidate_claims,
    synthesize_brody_native_claims,
)


def _mock_qwen_http_response(content: str) -> MagicMock:
    payload = {
        "id": "chatcmpl-mock-adv",
        "object": "chat.completion",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 10, "completion_tokens": 15, "total_tokens": 25},
    }
    raw = json.dumps(payload).encode("utf-8")
    mock_resp = MagicMock()
    mock_resp.read.return_value = raw
    mock_resp.__enter__.return_value = mock_resp
    mock_resp.__exit__.return_value = False
    mock_resp.status = 200
    return mock_resp


# ==============================================================================
# A: Raw Qwen claim clause must not be reused verbatim inside template wrapping
# ==============================================================================
def test_adv_a_raw_claim_not_reused_verbatim_in_brody_answer():
    """
    Brody must not simply copy-paste raw Qwen claim clauses into answer_parts
    under a fixed consultative prefix. Native semantic reconstruction required.
    """
    raw_clause = "Le capteur B manifeste une oscillation transitoire induite par la valve secondaire."
    brody_ctx = {
        "neural_generation_snapshot": {
            "status": "GENERATION_SUCCESS",
            "validated_content": f"Voici l'analyse : {raw_clause}",
            "evidence_only": True,
            "provider": "QWEN_LOCAL",
        },
        "rights_action_snapshot": {"request_type": "PURE_RESPONSE"},
    }
    res = build_true_brody_answer(
        user_message="Pourquoi le capteur B oscille-t-il ?",
        language="fr",
        brody_full_context=brody_ctx,
    )
    final_answer = res.get("final_answer", "")
    
    # Assert raw clause is not verbatim pasted
    assert raw_clause not in final_answer, (
        f"ADV-A: Raw auxiliary clause was pasted verbatim into final answer: {final_answer}"
    )
    # Contract updated on the Claude branch (provenance honesty closure): the answer is a
    # deterministic pattern rewrite of the auxiliary clause, not a proven semantic
    # reconstruction. The level must say so, and the per-statement record must agree.
    # NOTE: conflicts with the AGY branch contract (REAL_SEMANTIC_RECONSTRUCTION); to reconcile.
    assert res.get("native_linguistic_level") == "TEMPLATE_REWRITE"
    records = res.get("formulation_records") or []
    assert records and all(r["provenance"] == "TEMPLATE_REWRITE" for r in records)
    assert all(r["text_identity"] == "REWORDED" and r["origin"] == "AUXILIARY_MODEL" for r in records)
    assert res.get("auxiliary_wording_dependency") is True


# ==============================================================================
# B: Negative/unresolved statements must NOT falsely resolve B6 unknowns
# ==============================================================================
def test_adv_b_unresolved_statement_does_not_falsely_resolve_unknown():
    """
    'La température cible reste inconnue' mentions 'température' and 'cible',
    but expresses negative epistemic polarity. It must NOT resolve temperature_cible.
    """
    b6_pkt = {"unknowns": ["temperature_cible"]}
    round1_content = "La température cible reste inconnue et non mesurable."
    
    delta = reassess_cognitive_evidence_delta(
        round1_content=round1_content,
        b6_context_packet=b6_pkt,
        world_hypothesis_snapshot={},
        user_message="Donne la température cible",
    )
    
    assert delta["has_residual"] is True, "ADV-B: Negative polarity must keep has_residual=True"
    assert "temperature_cible" in delta["residual_unknowns"], "ADV-B: Unknown must remain in residual_unknowns"
    assert delta["should_halt"] is False, "ADV-B: Must not halt early on negative assertion"
    assert delta["halt_reason"] != "RESOLVED", "ADV-B: Unknown must not be marked RESOLVED"


# ==============================================================================
# C: Topic-relevant memory lacking the answer must NOT declare QUESTION_ANSWERABLE
# ==============================================================================
def test_adv_c_topic_relevant_memory_lacking_answer_not_sufficient():
    """
    When asking 'Quelle est la pression limite de X ?', memory stating only
    'X utilise une pression régulée' is TOPIC_RELEVANT, but the answer is NOT established.
    """
    chain = {
        "material_quality": "USABLE_MATERIAL",
        "query_results_count": 1,
        "selected_items": [
            {
                "title": "Système X",
                "excerpt": "X utilise une pression régulée. La documentation de sécurité existe.",
                "tags": ["système_x", "pression"],
            }
        ],
    }
    suff = evaluate_memory_sufficiency(
        user_message="Quelle est la pression limite de X ?",
        memory_response_chain=chain,
    )
    
    assert suff["memory_present"] is True
    assert suff["memory_relevant"] is True
    # Crucial: Question is NOT sufficiently answerable because 'limite' is unanswered
    assert suff["question_sufficiently_answerable"] is False, (
        f"ADV-C: False sufficiency! One topic keyword must not imply question is answerable. Result: {suff}"
    )
    assert suff["sufficiency_state"] in ("MEMORY_RELEVANT", "EVIDENCE_USABLE")
    assert suff["sufficiency_state"] != "QUESTION_SUFFICIENTLY_ANSWERABLE"


# ==============================================================================
# D: Conflicting property values must trigger contradiction detection
# ==============================================================================
def test_adv_d_conflicting_property_values_trigger_contradiction():
    """
    Two claims asserting incompatible values for the same subject property
    (10 bars vs 15 bars) must be flagged as a contradiction, not silently admitted.
    """
    text1 = "La pression limite de X est de 10 bars."
    text2 = "La pression limite de X est de 15 bars."
    
    claims1 = extract_candidate_claims(text1)
    claims2 = extract_candidate_claims(text2)
    all_claims = claims1 + claims2
    
    synth = synthesize_brody_native_claims(
        all_claims,
        user_message="Quelle est la pression limite de X ?",
        language="fr",
    )
    
    assert synth["has_contradictions"] is True, "ADV-D: Incompatible values for same property must trigger contradiction"
    assert "10 bars" in synth["text"] and "15 bars" in synth["text"]
    assert "contradictoire" in synth["text"].lower() or "conflit" in synth["text"].lower()


# ==============================================================================
# E: Claim identifiers must be deterministic and replay-stable across processes
# ==============================================================================
def test_adv_e_claim_ids_stable_across_python_processes():
    """
    claim_id must use cryptographic / deterministic hashing (e.g. sha256),
    NOT Python's randomized builtin hash().
    """
    stmt = "Le gradient thermique de la sonde Omega-9 est stable."
    
    # Run two separate Python processes computing the claim_id
    code = (
        "from apps.obsidia_api.brody_true_voice_adapter import extract_candidate_claims; "
        f"claims = extract_candidate_claims({repr(stmt)}); "
        "print(claims[0]['claim_id'])"
    )
    res1 = subprocess.check_output([sys.executable, "-c", code], text=True).strip()
    res2 = subprocess.check_output([sys.executable, "-c", code], text=True).strip()
    
    assert res1 == res2, f"ADV-E: claim_id is not replay-stable across processes: {res1} != {res2}"
