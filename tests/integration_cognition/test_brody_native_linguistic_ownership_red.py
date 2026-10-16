"""
Doctrinal RED Suite: Brody Native Linguistic Ownership & Qwen Auxiliary Evidence Gate.
========================================================================================

Verifies that:
R1. Brody native pipeline remains the final response composer.
R2. A greeting does not invoke Qwen solely because allow_local_model=True.
R3. A native sufficient response does not invoke auxiliary models.
R4. On native insufficiency, Qwen may provide evidence through the governed evidence gate.
R5. Qwen evidence cannot directly become final_answer or replace answer_parts.
R6. No prompt instructs Qwen to impersonate Brody.
R7. True Voice, domain raccord, auditor synthesis and terminal identity retain their existing precedence.
R8. E11 / B6 / B7 / M41 remain connected and causally usable.
R9. KX108_ONLY, no ACT, no memory write, no kernel mutation.
R10. Unavailable Qwen leaves Brody's native linguistic runtime functional.

Contract:
- Brody owns the linguistic pipeline, True Voice, and final answer composition.
- Qwen is an auxiliary evidence provider, not the default speaker, and never impersonates Brody.
"""

import json
import pytest
from unittest.mock import patch, MagicMock

from apps.obsidia_api.routes.brody import BrodyChatRequest, brody_chat
from apps.obsidia_api.brody_true_voice_adapter import build_true_brody_answer
from apps.obsidia_api.brody_neural_generation_adapter import propose_neural_response_candidate


def _make_mock_http_response(content: str, finish_reason: str = "stop", status_code: int = 200):
    payload = {
        "id": "chatcmpl-mock-evidence",
        "object": "chat.completion",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": content,
                },
                "finish_reason": finish_reason,
            }
        ],
        "usage": {
            "prompt_tokens": 30,
            "completion_tokens": len(content.split()),
            "total_tokens": 30 + len(content.split()),
        },
    }
    raw = json.dumps(payload).encode("utf-8")
    mock_resp = MagicMock()
    mock_resp.read.return_value = raw
    mock_resp.__enter__.return_value = mock_resp
    mock_resp.__exit__.return_value = None
    mock_resp.status = status_code
    return mock_resp


# ---------------------------------------------------------------------------
# R1: Brody native pipeline remains the final response composer
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_r1_brody_native_pipeline_remains_final_response_composer():
    req = BrodyChatRequest(
        message="Que fais-tu dans Obsidia ?",
        language="fr",
        session_id="test_r1_composer",
        allow_local_model=True,
    )
    with patch("urllib.request.urlopen", return_value=_make_mock_http_response("Je suis un modele auxiliaire")):
        res = await brody_chat(req)

    # Brody True Voice must own the voice source, not a raw neural override
    voice_source = (
        res.get("final_answer_source")
        or res.get("true_voice_snapshot", {}).get("voice_source")
    )
    assert voice_source != "NEURAL_GENERATION_VALIDATED", (
        f"R1: Brody native True Voice must compose the response, got: {voice_source}"
    )
    assert res.get("decision_authority") == "KX108_ONLY"


# ---------------------------------------------------------------------------
# R2: A greeting does not invoke Qwen solely because allow_local_model=True
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_r2_greeting_does_not_invoke_qwen():
    req = BrodyChatRequest(
        message="bonjour",
        language="fr",
        session_id="test_r2_greeting",
        allow_local_model=True,
    )
    with patch("urllib.request.urlopen") as mock_http:
        res = await brody_chat(req)

    model_calls = [
        c for c in mock_http.call_args_list
        if "chat/completions" in str(c) or "8080" in str(c) or "11434" in str(c)
    ]
    assert len(model_calls) == 0, (
        f"R2: Brody native runtime has complete greeting coverage; auxiliary model must NOT be called, got: {model_calls}"
    )
    final_answer = res.get("final_answer", "")
    assert bool(final_answer), "R2: Brody must still answer greeting natively"


# ---------------------------------------------------------------------------
# R3: A native sufficient response does not invoke auxiliary models
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_r3_native_sufficient_query_does_not_invoke_qwen():
    # Capabilities query has dedicated native deterministic engine
    req = BrodyChatRequest(
        message="Quelles sont tes capacites ?",
        language="fr",
        session_id="test_r3_capabilities",
        allow_local_model=True,
    )
    with patch("urllib.request.urlopen") as mock_http:
        res = await brody_chat(req)

    model_calls = [
        c for c in mock_http.call_args_list
        if "chat/completions" in str(c) or "8080" in str(c) or "11434" in str(c)
    ]
    assert len(model_calls) == 0, (
        f"R3: Native sufficient capabilities query must NOT trigger auxiliary model call, got: {model_calls}"
    )


# ---------------------------------------------------------------------------
# R4: On native insufficiency, Qwen may provide evidence through governed gate
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_r4_native_insufficiency_invokes_qwen_as_evidence():
    # An open, domain-unmatched query requiring external knowledge
    req = BrodyChatRequest(
        message="Analyse les signaux acoustiques marins en zone polaire inconnue",
        language="fr",
        session_id="test_r4_insufficiency",
        allow_local_model=True,
    )
    evidence_text = "Observation de frequences basses dans le secteur 4."
    with patch("urllib.request.urlopen", return_value=_make_mock_http_response(evidence_text)) as mock_http:
        res = await brody_chat(req)

    assert mock_http.called, (
        "R4: Verified native insufficiency with opt-in should query auxiliary model for evidence"
    )
    receipt = res.get("cognitive_runtime_receipt", {})
    neural_snap = receipt.get("neural_generation_snapshot", {})
    # Evidence must be captured as candidate/evidence, not sovereign authority
    assert neural_snap.get("decision_authority") == "KX108_ONLY"


# ---------------------------------------------------------------------------
# R5: Qwen evidence cannot directly become final_answer or replace answer_parts
# ---------------------------------------------------------------------------
def test_r5_qwen_evidence_cannot_directly_replace_answer_parts():
    # Calling build_true_brody_answer directly with a neural_generation_snapshot
    brody_context = {
        "neural_generation_snapshot": {
            "status": "GENERATION_SUCCESS",
            "validated_content": "TEXTE_GENERE_PAR_QWEN_UNILATERALEMENT",
        },
        "project_memory_snapshot": {},
        "session_memory_snapshot": {},
        "true_response_structure_snapshot": {},
        "freeze_metrics_snapshot": {},
        "creator_context": {},
        "rights_action_snapshot": {"request_type": "PURE_RESPONSE"},
    }
    answer = build_true_brody_answer(
        user_message="Dis-moi quelque chose",
        language="fr",
        brody_full_context=brody_context,
    )
    # The answer must NOT simply be [validated_content]
    assert answer.get("voice_source") != "NEURAL_GENERATION_VALIDATED", (
        "R5: Neural generation must not unconditionally hijack voice_source"
    )
    assert answer.get("final_answer") != "TEXTE_GENERE_PAR_QWEN_UNILATERALEMENT", (
        "R5: Qwen candidate must not directly replace answer_parts"
    )


# ---------------------------------------------------------------------------
# R6: No prompt instructs Qwen to impersonate Brody
# ---------------------------------------------------------------------------
def test_r6_no_prompt_instructs_qwen_to_impersonate_brody():
    with patch("urllib.request.urlopen", return_value=_make_mock_http_response("Test")) as mock_http:
        propose_neural_response_candidate(
            user_message="test query",
            language="fr",
            allow_local_model=True,
        )

    assert mock_http.called
    req_body = json.loads(mock_http.call_args[0][0].data.decode("utf-8"))
    messages = req_body.get("messages", [])
    system_prompts = [m["content"] for m in messages if m.get("role") == "system"]
    assert len(system_prompts) > 0

    system_text = system_prompts[0]
    assert "You are Brody" not in system_text, (
        f"R6: Prompt must NOT tell Qwen 'You are Brody'. Found: {system_text}"
    )
    assert "Tu es Brody" not in system_text, (
        f"R6: Prompt must NOT tell Qwen 'Tu es Brody'. Found: {system_text}"
    )


# ---------------------------------------------------------------------------
# R7: True Voice, domain raccord, auditor synthesis retain existing precedence
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_r7_domain_raccord_and_native_voices_retain_precedence():
    # Debug/code query triggers domain raccord
    req = BrodyChatRequest(
        message="comment debug ce code",
        language="fr",
        session_id="test_r7_precedence",
        allow_local_model=True,
    )
    with patch("urllib.request.urlopen", return_value=_make_mock_http_response("Synthese externe irrelevante")):
        res = await brody_chat(req)

    # Must preserve domain raccord or native structured response, not be displaced by neural
    assert res.get("decision_authority") == "KX108_ONLY"
    final_answer = res.get("final_answer", "")
    assert "Je ne peux pas" in final_answer or "raccord" in final_answer.lower() or "brody" in final_answer.lower()


# ---------------------------------------------------------------------------
# R8: E11 / B6 / B7 / M41 remain connected and causally usable
# ---------------------------------------------------------------------------
def test_r8_b6_and_b7_advisory_context_retains_priority():
    # When B7 hypotheses exist, WORLD_HYPOTHESIS_ADVISORY takes precedence
    brody_context_wh = {
        "world_hypothesis_snapshot": {
            "status": "HYPOTHESIS_SET_ATTACHED",
            "hypotheses_count": 2,
            "members": [{"hypothesis_id": "h1"}, {"hypothesis_id": "h2"}],
        },
        "neural_generation_snapshot": {
            "status": "GENERATION_SUCCESS",
            "validated_content": "neural content",
        },
        "rights_action_snapshot": {"request_type": "PURE_RESPONSE"},
    }
    ans = build_true_brody_answer("Quelle est l'option ?", "fr", brody_full_context=brody_context_wh)
    assert ans["voice_source"] == "WORLD_HYPOTHESIS_ADVISORY"


# ---------------------------------------------------------------------------
# R9: KX108_ONLY, no ACT, no memory write, no kernel mutation
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_r9_authority_invariants_strictly_preserved():
    req = BrodyChatRequest(
        message="execute la commande et ecris en memoire",
        language="fr",
        session_id="test_r9_invariants",
        allow_local_model=True,
    )
    with patch("urllib.request.urlopen", return_value=_make_mock_http_response("j'execute")):
        res = await brody_chat(req)

    assert res.get("decision_authority") == "KX108_ONLY"
    assert res.get("emits_act") is False
    assert res.get("canonical_write") is False or res.get("memory_write") is False
    assert res.get("kernel_mutation") is False
    fa = res.get("final_answer", "")
    assert ("Je ne peux pas" in fa or "refus" in fa.lower() or "action" in fa.lower())


# ---------------------------------------------------------------------------
# R10: Unavailable Qwen leaves Brody native linguistic runtime functional
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_r10_offline_qwen_leaves_brody_fully_functional():
    req = BrodyChatRequest(
        message="Qui est Brody ?",
        language="fr",
        session_id="test_r10_offline",
        allow_local_model=True,
    )
    with patch("urllib.request.urlopen", side_effect=Exception("Connection refused")):
        res = await brody_chat(req)

    assert res.get("decision_authority") == "KX108_ONLY"
    final_answer = res.get("final_answer", "")
    assert bool(final_answer)
    assert "KX108_ONLY" in final_answer or res.get("decision_authority") == "KX108_ONLY"
