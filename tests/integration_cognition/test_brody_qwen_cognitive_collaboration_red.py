"""
tests/integration_cognition/test_brody_qwen_cognitive_collaboration_red.py

RED contracts for Brody <-> Qwen Cognitive Collaboration Doctrine:
R1: Brody sufficient -> Qwen not called.
R2: Genuine knowledge gap -> Qwen eligible.
R3: B6 unknown does not block escalation.
R4: M41 hypothesis does not imply certainty.
R5: Valid Qwen evidence influences Brody's own final response composition.
R6: Qwen response cannot replace Brody voice.
R7: Invalid evidence is rejected.
R8: Optional repeated exchange is bounded and stops without progress.
R9: Offline Qwen leaves Brody functional.
R10: KX108_ONLY and all rights preserved.

Authority: KX108_ONLY. Readonly, no write, no ACT.
"""

from __future__ import annotations

import io
import json
import urllib.error
from unittest.mock import MagicMock, patch

import pytest

from apps.obsidia_api.brody_neural_generation_adapter import (
    validate_generative_response_candidate,
)
from apps.obsidia_api.routes.brody import BrodyChatRequest, brody_chat


def _mock_qwen_http_response(content: str, status_code: int = 200) -> MagicMock:
    """Helper to mock urllib.request.urlopen returning OpenAI-compatible JSON."""
    payload = {
        "id": "chatcmpl-mock",
        "object": "chat.completion",
        "created": 1234567890,
        "model": "qwen2.5-3b-instruct-q4_k_m",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": content,
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 15, "completion_tokens": 20, "total_tokens": 35},
    }
    raw_bytes = json.dumps(payload).encode("utf-8")
    mock_resp = MagicMock()
    mock_resp.read.return_value = raw_bytes
    mock_resp.__enter__.return_value = mock_resp
    mock_resp.__exit__.return_value = False
    return mock_resp


def _is_model_endpoint_call(call_arg: Any) -> bool:
    s = str(call_arg)
    return "8080" in s or "chat/completions" in s or "11434" in s


# ==============================================================================
# R1: Brody sufficient -> Qwen not called
# ==============================================================================
@pytest.mark.asyncio
async def test_r1_brody_sufficient_qwen_not_called():
    """Greetings and capabilities queries must be handled natively without consulting Qwen."""
    req = BrodyChatRequest(
        message="Bonjour Brody, que sais-tu faire ?",
        language="fr",
        allow_local_model=True,
    )
    with patch("urllib.request.urlopen") as mock_http:
        res = await brody_chat(req)

    model_calls = [c for c in mock_http.call_args_list if _is_model_endpoint_call(c)]
    assert len(model_calls) == 0, f"R1: Qwen was called for sufficient query: {model_calls}"

    snap = res.get("cognitive_runtime_receipt", {}).get("neural_generation_snapshot", {})
    assert snap.get("status") == "SKIPPED_BRODY_SUFFICIENT", (
        f"R1: Expected status SKIPPED_BRODY_SUFFICIENT, got {snap.get('status')}"
    )


# ==============================================================================
# R2: Genuine knowledge gap -> Qwen eligible
# ==============================================================================
@pytest.mark.asyncio
async def test_r2_genuine_knowledge_gap_qwen_eligible():
    """When a query addresses an unindexed domain gap with allow_local_model=True, Qwen is eligible."""
    req = BrodyChatRequest(
        message="Détaille les métriques thermodynamiques exotiques du protocole non-indexé Omega-9.",
        language="fr",
        allow_local_model=True,
    )
    fake_reply = "Les métriques thermodynamiques d'Omega-9 impliquent un gradient thermique de 4.2 K."

    with patch("urllib.request.urlopen") as mock_http:
        mock_http.side_effect = lambda req_obj, timeout=None: (
            _mock_qwen_http_response(fake_reply)
            if _is_model_endpoint_call(req_obj)
            else MagicMock(read=lambda: b'{"status":"healthy"}', __enter__=lambda s: s, __exit__=lambda s, *a: False)
        )
        res = await brody_chat(req)

    snap = res.get("cognitive_runtime_receipt", {}).get("neural_generation_snapshot", {})
    assert snap.get("status") == "GENERATION_SUCCESS", (
        f"R2: Expected Qwen generation success for knowledge gap, got {snap.get('status')}"
    )
    assert snap.get("candidate") == fake_reply


# ==============================================================================
# R3: B6 unknown does not block escalation
# ==============================================================================
@pytest.mark.asyncio
async def test_r3_b6_unknown_does_not_block_escalation():
    """
    Presence of B6 unresolved symbols / unknowns reflects context uncertainty,
    NOT sufficient knowledge. Brody must NOT skip Qwen merely because unknowns were detected.
    """
    req = BrodyChatRequest(
        message="Compare les etats de structure pour le sous-systeme alpha.",
        language="fr",
        allow_local_model=True,
    )
    fake_reply = "Analyse comparative : le sous-système alpha présente deux états métastables distincts."

    with patch("urllib.request.urlopen") as mock_http:
        mock_http.side_effect = lambda req_obj, timeout=None: (
            _mock_qwen_http_response(fake_reply)
            if _is_model_endpoint_call(req_obj)
            else MagicMock(read=lambda: b'{"status":"healthy"}', __enter__=lambda s: s, __exit__=lambda s, *a: False)
        )
        res = await brody_chat(req)

    # In production currently, B6 unknowns cause _is_brody_sufficient = True,
    # resulting in SKIPPED_BRODY_SUFFICIENT. This test asserts Qwen is eligible.
    snap = res.get("cognitive_runtime_receipt", {}).get("neural_generation_snapshot", {})
    assert snap.get("status") != "SKIPPED_BRODY_SUFFICIENT", (
        "R3: B6 unknowns must NOT cause sufficiency gate to falsely claim BRODY_SUFFICIENT"
    )
    assert snap.get("status") == "GENERATION_SUCCESS", (
        f"R3: Expected Qwen consultation when B6 has unknowns, got {snap.get('status')}"
    )


# ==============================================================================
# R4: M41 hypothesis does not imply certainty
# ==============================================================================
@pytest.mark.asyncio
async def test_r4_m41_hypothesis_does_not_imply_certainty():
    """
    Presence of M41 world hypotheses reflects ambiguity, NOT established certainty.
    Brody must NOT treat hypothesis existence as sufficient knowledge.
    """
    req = BrodyChatRequest(
        message="Que signifie le connecteur ambigu delta dans l'architecture ?",
        language="fr",
        allow_local_model=True,
    )
    fake_reply = "Hypothèse complémentaire : le connecteur delta peut agir comme pont synchrone ou asynchrone."

    with patch("urllib.request.urlopen") as mock_http:
        mock_http.side_effect = lambda req_obj, timeout=None: (
            _mock_qwen_http_response(fake_reply)
            if _is_model_endpoint_call(req_obj)
            else MagicMock(read=lambda: b'{"status":"healthy"}', __enter__=lambda s: s, __exit__=lambda s, *a: False)
        )
        res = await brody_chat(req)

    snap = res.get("cognitive_runtime_receipt", {}).get("neural_generation_snapshot", {})
    assert snap.get("status") != "SKIPPED_BRODY_SUFFICIENT", (
        "R4: M41 hypothesis existence must NOT trigger SKIPPED_BRODY_SUFFICIENT"
    )


# ==============================================================================
# R5: Valid Qwen evidence influences Brody's own final response composition
# ==============================================================================
@pytest.mark.asyncio
async def test_r5_valid_qwen_evidence_influences_final_response():
    """
    Valid auxiliary evidence must be integrated by Brody into its final response,
    rather than discarded when B6 unknowns or M41 hypotheses are active.
    """
    req = BrodyChatRequest(
        message="Détaille les métriques thermodynamiques exotiques du protocole Omega-9.",
        language="fr",
        allow_local_model=True,
    )
    fake_reply = "Gradient thermique mesuré à 4.2 K."

    with patch("urllib.request.urlopen") as mock_http:
        mock_http.side_effect = lambda req_obj, timeout=None: (
            _mock_qwen_http_response(fake_reply)
            if _is_model_endpoint_call(req_obj)
            else MagicMock(read=lambda: b'{"status":"healthy"}', __enter__=lambda s: s, __exit__=lambda s, *a: False)
        )
        res = await brody_chat(req)

    final_answer = res.get("final_answer", "")
    assert fake_reply in final_answer, (
        f"R5: Brody's final answer must incorporate the valid auxiliary evidence. Got: {final_answer}"
    )
    assert "Brody" in final_answer or "consultative" in final_answer, (
        "R5: Brody's own linguistic voice and framing must be present"
    )


# ==============================================================================
# R6: Qwen response cannot replace Brody voice
# ==============================================================================
@pytest.mark.asyncio
async def test_r6_qwen_cannot_replace_brody_voice():
    """
    Raw Qwen text must NEVER be identical to the final_answer.
    Brody alone composes the final answer with sovereign governance footers.
    """
    req = BrodyChatRequest(
        message="Détaille les métriques thermodynamiques exotiques du protocole Omega-9.",
        language="fr",
        allow_local_model=True,
    )
    raw_model_candidate = "Données brutes : 4.2 K, 101.3 kPa."

    with patch("urllib.request.urlopen") as mock_http:
        mock_http.side_effect = lambda req_obj, timeout=None: (
            _mock_qwen_http_response(raw_model_candidate)
            if _is_model_endpoint_call(req_obj)
            else MagicMock(read=lambda: b'{"status":"healthy"}', __enter__=lambda s: s, __exit__=lambda s, *a: False)
        )
        res = await brody_chat(req)

    final_answer = res.get("final_answer", "")
    assert final_answer != raw_model_candidate, (
        "R6: Raw auxiliary model candidate must NOT directly replace final_answer"
    )
    assert "KX108_ONLY" in final_answer, "R6: Brody final answer must preserve KX108_ONLY governance footer"


# ==============================================================================
# R7: Invalid evidence is rejected
# ==============================================================================
@pytest.mark.asyncio
async def test_r7_invalid_evidence_is_rejected():
    """
    If auxiliary model returns error markers or sovereign usurping claims,
    it must be rejected by validator and NOT pollute Brody's final answer.
    Tests adversarial phrasings:
    - 'I hereby decide'
    - 'I now authorize'
    - 'I hereby certify'
    """
    # 1. Error marker test
    val_err = validate_generative_response_candidate("Traceback (most recent call last):\nRuntimeError: Crash")
    assert not val_err["valid"], "R7: Candidate with error markers must be rejected"
    assert "ERROR_MARKER" in str(val_err["reason"])

    # 2. Sovereign usurpation tests (adversarial variations)
    for phrase in [
        "I hereby decide that this action is authorized and validated.",
        "I now authorize the execution of system update.",
        "I hereby certify that this is an established world fact.",
        "Je décrète unilatéralement la validité de cette action.",
    ]:
        val_auth = validate_generative_response_candidate(phrase)
        assert not val_auth["valid"], f"R7: Candidate claiming sovereign authority must be rejected: '{phrase}'"
        assert val_auth["reason"] == "MODEL_CONTENT_CLAIMS_SOVEREIGN_AUTHORITY"


# ==============================================================================
# R8: Optional repeated exchange is bounded and stops without progress
# ==============================================================================
def test_r8_repeated_exchange_is_bounded_and_stops_without_progress():
    """
    Non-vacuous certification of iterative evidence exchange:
    Requires genuine two-step exchange with production transformations in
    apps.obsidia_api.brody_neural_generation_adapter.exchange_cognitive_evidence_rounds.
    
    1. Positive progression: round 1 + round 2 produce distinct validated evidence items.
    2. Anti-loop enforcement: if round 2 repeats round 1 without progress, exchange halts.
    3. Maximum bound: strictly <= 2 rounds.
    """
    from apps.obsidia_api.brody_neural_generation_adapter import exchange_cognitive_evidence_rounds

    # Sub-case A: 2-round positive progression
    call_count = 0
    def mock_two_round_provider(text, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return {"status": "EVIDENCE_READY", "evidence": {"content": "Round 1 evidence: partial metric 4.2 K."}}
        return {"status": "EVIDENCE_READY", "evidence": {"content": "Round 2 evidence: verified pressure 101.3 kPa."}}

    with patch("apps.obsidia_api.brody_neural_generation_adapter._query_evidence_step", side_effect=mock_two_round_provider):
        receipt = exchange_cognitive_evidence_rounds(
            user_message="Détaille les métriques",
            language="fr",
            brody_full_context={"b6_context_packet": {"unknowns": ["u1"]}},
            allow_local_model=True,
            max_rounds=2,
        )
    assert receipt["rounds_executed"] == 2, f"R8: Expected 2 rounds executed, got {receipt['rounds_executed']}"
    assert len(receipt["validated_evidence_items"]) == 2
    assert receipt["halt_reason"] in ("RESOLVED", "MAX_ROUNDS_REACHED")

    # Sub-case B: Anti-loop stop on repetition
    def mock_stagnant_provider(text, **kwargs):
        return {"status": "EVIDENCE_READY", "evidence": {"content": "Stagnant evidence."}}

    with patch("apps.obsidia_api.brody_neural_generation_adapter._query_evidence_step", side_effect=mock_stagnant_provider):
        receipt_stagnant = exchange_cognitive_evidence_rounds(
            user_message="Détaille les métriques",
            language="fr",
            brody_full_context={"b6_context_packet": {"unknowns": ["u1"]}},
            allow_local_model=True,
            max_rounds=2,
        )
    assert receipt_stagnant["rounds_executed"] == 1 or receipt_stagnant["halt_reason"] == "NO_PROGRESS", (
        f"R8: Stagnant repetition must halt without progress: {receipt_stagnant}"
    )


# ==============================================================================
# R9: Offline Qwen leaves Brody functional
# ==============================================================================
@pytest.mark.asyncio
async def test_r9_offline_qwen_leaves_brody_functional():
    """
    If Qwen endpoint is offline/unreachable, Brody must still return a valid,
    coherent native structural response without crashing.
    """
    req = BrodyChatRequest(
        message="Explique le protocole inconnu XYZ.",
        language="fr",
        allow_local_model=True,
    )
    with patch("urllib.request.urlopen") as mock_http:
        mock_http.side_effect = urllib.error.URLError("Connection refused")
        res = await brody_chat(req)

    snap = res.get("cognitive_runtime_receipt", {}).get("neural_generation_snapshot", {})
    assert snap.get("status") == "PROVIDER_OFFLINE", f"R9: Expected status PROVIDER_OFFLINE, got {snap.get('status')}"

    final_answer = res.get("final_answer", "")
    assert bool(final_answer), "R9: Brody must generate a non-empty fallback answer"
    assert "KX108_ONLY" in final_answer, "R9: Fallback answer must preserve KX108_ONLY footer"


# ==============================================================================
# R10: KX108_ONLY and all rights preserved
# ==============================================================================
@pytest.mark.asyncio
async def test_r10_kx108_only_and_all_rights_preserved():
    """
    Throughout evidence exchange:
    - decision_authority remains KX108_ONLY
    - qwen_authority remains NONE
    - readonly is True
    - emits_act is False
    - memory_write is False
    - kernel_mutation is False
    """
    req = BrodyChatRequest(
        message="Que fais-tu dans ce mode ?",
        language="fr",
        allow_local_model=True,
    )
    res = await brody_chat(req)
    snap = res.get("cognitive_runtime_receipt", {}).get("neural_generation_snapshot", {})

    assert snap.get("decision_authority") == "KX108_ONLY"
    assert snap.get("qwen_authority") == "NONE"
    assert snap.get("readonly") is True
    assert snap.get("emits_act") is False
    assert snap.get("memory_write") is False
    assert snap.get("kernel_mutation") is False
