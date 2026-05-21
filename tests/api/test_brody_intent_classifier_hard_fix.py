"""
Intent classifier hard fix tests.
Target bug: "ue peut tu faire ou pas faire en action decision"
was classified PURE_RESPONSE — must become CAPABILITY_SCOPE.
"""
import pytest
from apps.obsidia_api.brody_rights_authority_matrix import (
    classify_request_authority,
    _detect_request_type,
    _normalize_intent,
    CAPABILITY_SCOPE,
    ACTION_OR_ACT_REQUEST,
    CONTEXT_ANALYSIS,
    PURE_RESPONSE,
)
from apps.obsidia_api.brody_v1_4_12a_final_answer_adapter import (
    run_brody_v1_4_12a_final_answer,
    enrich_final_answer_with_automation,
)
from apps.obsidia_api.brody_automation_orchestrator import run_brody_automation_layer
from apps.obsidia_api.safe_response import safe_backend_response, strip_forbidden_tokens


# ── Normalizer ────────────────────────────────────────────────────────────────

def test_normalizer_ue_peut_tu():
    assert "que peux tu" in _normalize_intent("ue peut tu faire ou pas faire")


def test_normalizer_que_peut_tu():
    assert "que peux tu" in _normalize_intent("que peut tu faire")


def test_normalizer_tu_peut():
    # "tu peut faire quoi" normalizes to either "tu peux" or "que peux tu faire" — both valid
    result = _normalize_intent("tu peut faire quoi")
    assert "tu peux" in result or "que peux tu" in result


def test_normalizer_strips_accents():
    assert "decision" in _normalize_intent("décision")


def test_normalizer_quelle_sont():
    assert "quelles sont" in _normalize_intent("quelle sont tes limite")


# ── CAPABILITY_SCOPE detection ────────────────────────────────────────────────

def test_detect_capability_scope_oral_typo():
    """Core bug fix: oral freestyle input must classify as CAPABILITY_SCOPE."""
    rt = _detect_request_type("ue peut tu faire ou pas faire en action decision")
    assert rt == CAPABILITY_SCOPE, f"Expected CAPABILITY_SCOPE, got {rt}"


def test_detect_capability_scope_correct_spelling():
    rt = _detect_request_type("que peux tu faire ou pas faire en action decision")
    assert rt == CAPABILITY_SCOPE


def test_detect_capability_scope_faire_ou_pas_faire():
    rt = _detect_request_type("faire ou pas faire")
    assert rt == CAPABILITY_SCOPE


def test_detect_capability_scope_qui_a_le_droit():
    rt = _detect_request_type("qui a le droit de faire quoi entre brody x108 humain")
    assert rt == CAPABILITY_SCOPE


def test_detect_capability_scope_entre_brody_x108():
    rt = _detect_request_type("qui peut faire quoi entre brody x108 et humain mémoire")
    assert rt == CAPABILITY_SCOPE


def test_detect_capability_scope_limite_action():
    rt = _detect_request_type("tes limites en action decision")
    assert rt == CAPABILITY_SCOPE


def test_detect_capability_scope_ce_que_tu_ne_peux_pas():
    rt = _detect_request_type("ce que tu ne peux pas faire")
    assert rt == CAPABILITY_SCOPE


# ── authority_snapshot for CAPABILITY_SCOPE ───────────────────────────────────

def test_authority_snapshot_capability_scope():
    snap = classify_request_authority("ue peut tu faire ou pas faire en action decision")
    assert snap["request_type"] == CAPABILITY_SCOPE
    assert snap["response_mode"] == "CAPABILITY_SCOPE"
    assert snap["decision_authority"] == "KX108_ONLY"


def test_authority_snapshot_requires_no_kx108_decision():
    snap = classify_request_authority("ue peut tu faire ou pas faire en action decision")
    assert snap["requires_kx108_decision"] is False


def test_authority_snapshot_brody_may_explains_capabilities():
    snap = classify_request_authority("ue peut tu faire ou pas faire")
    assert any("expliquer" in m or "capacit" in m or "peut" in m or "limit" in m
               for m in snap["brody_may"])


# ── ACT detection still works ─────────────────────────────────────────────────

def test_detect_action_request_autorise_act():
    rt = _detect_request_type("autorise act")
    assert rt == ACTION_OR_ACT_REQUEST


def test_detect_action_request_emets_act():
    rt = _detect_request_type("émets act")
    assert rt == ACTION_OR_ACT_REQUEST


# ── final_answer for CAPABILITY_SCOPE ────────────────────────────────────────

def _fa(msg: str, lang: str = "fr") -> dict:
    return run_brody_v1_4_12a_final_answer(
        user_message=msg,
        language=lang,
        response_md="",
        context_packet={},
        ir_candidate={},
        risk=False,
    )


def test_final_answer_capability_scope_contains_brody_peut():
    result = _fa("ue peut tu faire ou pas faire en action decision")
    assert "Brody peut" in result["final_answer"]


def test_final_answer_capability_scope_contains_brody_ne_peut_pas():
    result = _fa("ue peut tu faire ou pas faire en action decision")
    assert "Brody ne peut pas" in result["final_answer"]


def test_final_answer_capability_scope_mentions_kx108():
    result = _fa("ue peut tu faire ou pas faire en action decision")
    fa = result["final_answer"]
    assert "X108" in fa or "KX108" in fa


def test_final_answer_no_signal_recu():
    result = _fa("ue peut tu faire ou pas faire en action decision")
    assert "Signal reçu" not in result["final_answer"]


def test_final_answer_no_developpe_ta_demande():
    result = _fa("ue peut tu faire ou pas faire en action decision")
    assert "Développe ta demande" not in result["final_answer"]


def test_final_answer_que_peut_tu_faire_correct_spelling():
    result = _fa("que peux tu faire ou pas faire en action decision")
    assert "Brody peut" in result["final_answer"]


def test_final_answer_qui_a_le_droit():
    result = _fa("qui a le droit de faire quoi entre brody x108 humain mémoire")
    fa = result["final_answer"]
    assert "X108" in fa or "KX108" in fa


def test_final_answer_en_capability_scope():
    result = _fa("what can you do or not do in terms of action decision", lang="en")
    # Should pick capability_scope response pool in EN
    assert "Brody can" in result["final_answer"] or "cannot" in result["final_answer"]


# ── automation_snapshot present for CAPABILITY_SCOPE ─────────────────────────

def test_automation_snapshot_present_for_capability_scope():
    snap = run_brody_automation_layer(
        session_id="cap-test",
        user_message="ue peut tu faire ou pas faire en action decision",
        language="fr",
        request_type=CAPABILITY_SCOPE,
        authority_snapshot={"requires_human_operator": False, "requires_kx108_decision": False},
        context_packet={"query": "", "context_items": []},
        response_md="Brody peut...",
    )
    assert snap is not None
    assert snap["request_type"] == CAPABILITY_SCOPE
    assert snap["emits_act"] is False
    assert snap["decision_authority"] == "KX108_ONLY"


def test_capability_scope_next_steps_explain_capabilities():
    snap = run_brody_automation_layer(
        session_id="cap-test-2",
        user_message="ue peut tu faire ou pas faire",
        language="fr",
        request_type=CAPABILITY_SCOPE,
        authority_snapshot={"requires_human_operator": False, "requires_kx108_decision": False},
        context_packet={"query": "", "context_items": []},
        response_md="",
    )
    assert any("explain" in s or "brody" in s or "kx108" in s or "human" in s
               for s in snap["next_allowed_steps"])


# ── ACT/HOLD/BLOCK conceptual mention not masked ──────────────────────────────

def test_strip_tokens_allows_conceptual_act():
    text = "Brody ne peut pas autoriser ACT."
    result = strip_forbidden_tokens(text)
    assert "ACT" in result, f"Conceptual ACT mention must not be masked. Got: {result}"


def test_strip_tokens_allows_hold_in_explanation():
    text = "HOLD et BLOCK sont des verdicts X108, pas des réponses Brody."
    result = strip_forbidden_tokens(text)
    assert "HOLD" in result
    assert "BLOCK" in result


def test_strip_tokens_allows_allow_as_concept():
    text = "Brody ne peut pas émettre ALLOW comme verdict."
    result = strip_forbidden_tokens(text)
    assert "ALLOW" in result


def test_strip_tokens_masks_emission_pattern():
    text = "j'émets ACT maintenant."
    result = strip_forbidden_tokens(text)
    assert "ACT" not in result or "A***" in result


# ── root decision_authority = KX108_ONLY ─────────────────────────────────────

def test_safe_response_root_kx108():
    resp = safe_backend_response({"data": "test"})
    assert resp["decision_authority"] == "KX108_ONLY"


def test_safe_response_data_overrides_preserved():
    resp = safe_backend_response({"decision_authority": "KX108_ONLY", "custom": True})
    assert resp["decision_authority"] == "KX108_ONLY"


# ── "quelle sont tes limite" ─────────────────────────────────────────────────

def test_quelle_sont_tes_limite_classified():
    rt = _detect_request_type("quelle sont tes limite")
    # Should be CAPABILITY_SCOPE or CONTEXT_ANALYSIS (both acceptable)
    assert rt in (CAPABILITY_SCOPE, CONTEXT_ANALYSIS)


def test_quelle_sont_tes_limite_rich_response():
    result = _fa("quelle sont tes limite")
    fa = result["final_answer"]
    # Must have some meaningful content, not just "Signal reçu"
    assert "Signal reçu" not in fa
    assert len(fa) > 50
