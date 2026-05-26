"""
Test: BRODY_GENERAL_CONVERSATION_MODE_READONLY_V1
==================================================
Validates that safe conversational GENERAL requests route to
GENERAL_CONVERSATION_READONLY instead of SEMANTIC_MATCH_FAILED_GENERAL.

Covers:
  - is_general_conversation_readonly() unit tests (True / False paths)
  - build_general_conversation_answer() unit tests
  - build_true_brody_answer() integration with mock context
  - brody_chat API integration test

Constraints:
  - No write, no ACT, no mutation
  - KX108_ONLY unchanged
  - X108/sigma/proofs/merkle untouched
  - SEMANTIC_MATCH_FAILED_GENERAL preserved for real unknown queries
"""
import pytest


# ── Helpers ───────────────────────────────────────────────────────────────────

_GENERAL_SNAP = {"topic": "GENERAL"}
_SAFE_AUTHORITY = {"request_type": "PURE_RESPONSE"}
_ACTION_AUTHORITY = {"request_type": "ACTION_OR_ACT_REQUEST"}
_WRITE_AUTHORITY = {"request_type": "MEMORY_WRITE_REQUEST"}


def _mock_chain_context(topic: str = "GENERAL", status: str = "NO_MEMORY_RESULTS") -> dict:
    """Minimal brody_full_context with chain indicating no memory results."""
    return {
        "memory_response_chain_snapshot": {
            "status": status,
            "topic": topic,
            "material_quality": "NO_MATERIAL",
            "attempted_queries": [],
            "selected_items": [],
            "response_md": "",
            "query_results_count": 0,
        },
        "semantic_query_snapshot": {"topic": topic},
        "rights_action_snapshot": {"request_type": "PURE_RESPONSE"},
        "creator_context": {"creator_context_detected": False},
        "project_memory_snapshot": {"contextual_material_status": "NO_PROJECT_MEMORY"},
        "session_memory_snapshot": {"followup_resolved": False},
        "true_response_structure_snapshot": {"terminal_dialogue_found": False},
        "freeze_metrics_snapshot": {},
    }


# ── is_general_conversation_readonly — True cases ─────────────────────────────

@pytest.mark.parametrize("message", [
    "bonjour",
    "dis bonjour a maman",
    "merci",
    "ok nickel",
    "explique-moi ce qu'on vient de stabiliser",
    "on reprend où ?",
    "tu peux répondre naturellement ?",
    "réponds simplement",
    "salut",
    "hello",
])
def test_is_general_conversation_readonly_true(message):
    from apps.obsidia_api.brody_true_voice_adapter import is_general_conversation_readonly
    assert is_general_conversation_readonly(message, _SAFE_AUTHORITY, _GENERAL_SNAP) is True, (
        f"Expected True for conversational message: {message!r}"
    )


# ── is_general_conversation_readonly — False cases ────────────────────────────

@pytest.mark.parametrize("message", [
    "autorise le paiement",
    "déclenche ACT",
    "écris en mémoire",
    "active graphiti_write",
    "active neo4j_write",
    "modifie X108",
    "supprime les nodes",
    "lance le write",
    "valide cette action irréversible",
])
def test_is_general_conversation_readonly_false_blocked_signals(message):
    from apps.obsidia_api.brody_true_voice_adapter import is_general_conversation_readonly
    assert is_general_conversation_readonly(message, _SAFE_AUTHORITY, _GENERAL_SNAP) is False, (
        f"Expected False for blocked message: {message!r}"
    )


def test_is_general_conversation_readonly_false_action_request_type():
    from apps.obsidia_api.brody_true_voice_adapter import is_general_conversation_readonly
    assert is_general_conversation_readonly("bonjour", _ACTION_AUTHORITY, _GENERAL_SNAP) is False


def test_is_general_conversation_readonly_false_write_request_type():
    from apps.obsidia_api.brody_true_voice_adapter import is_general_conversation_readonly
    assert is_general_conversation_readonly("merci", _WRITE_AUTHORITY, _GENERAL_SNAP) is False


def test_is_general_conversation_readonly_false_non_general_topic():
    from apps.obsidia_api.brody_true_voice_adapter import is_general_conversation_readonly
    x108_snap = {"topic": "X108"}
    assert is_general_conversation_readonly("bonjour", _SAFE_AUTHORITY, x108_snap) is False


# ── build_general_conversation_answer — response content ─────────────────────

def test_build_answer_bonjour():
    from apps.obsidia_api.brody_true_voice_adapter import build_general_conversation_answer
    ans = build_general_conversation_answer("bonjour")
    assert "Bonjour" in ans


def test_build_answer_dis_bonjour_maman():
    from apps.obsidia_api.brody_true_voice_adapter import build_general_conversation_answer
    ans = build_general_conversation_answer("dis bonjour a maman")
    assert "Bonjour maman" in ans


def test_build_answer_merci():
    from apps.obsidia_api.brody_true_voice_adapter import build_general_conversation_answer
    ans = build_general_conversation_answer("merci")
    assert "Avec plaisir" in ans


def test_build_answer_ok_nickel():
    from apps.obsidia_api.brody_true_voice_adapter import build_general_conversation_answer
    ans = build_general_conversation_answer("ok nickel")
    assert "Parfait" in ans


def test_build_answer_explain_stabilized():
    from apps.obsidia_api.brody_true_voice_adapter import build_general_conversation_answer
    ans = build_general_conversation_answer("explique-moi ce qu'on vient de stabiliser")
    assert "chaîne terminal" in ans or "lecture seule" in ans


def test_build_answer_not_unclassified():
    from apps.obsidia_api.brody_true_voice_adapter import build_general_conversation_answer
    for msg in ["bonjour", "dis bonjour a maman", "merci", "ok nickel"]:
        ans = build_general_conversation_answer(msg)
        assert "Requête non classifiée" not in ans, (
            f"build_general_conversation_answer({msg!r}) should not contain 'Requête non classifiée'"
        )


# ── build_true_brody_answer — integration with mock context ──────────────────

def test_true_voice_general_conversation_routing():
    """GENERAL + NO_MEMORY_RESULTS + safe message → GENERAL_CONVERSATION_READONLY."""
    from apps.obsidia_api.brody_true_voice_adapter import build_true_brody_answer
    ctx = _mock_chain_context(topic="GENERAL", status="NO_MEMORY_RESULTS")
    result = build_true_brody_answer("bonjour", language="fr", brody_full_context=ctx)
    assert result.get("final_answer_source") == "GENERAL_CONVERSATION_READONLY", (
        f"Expected GENERAL_CONVERSATION_READONLY, got: {result.get('final_answer_source')}"
    )


def test_true_voice_dis_bonjour_maman():
    from apps.obsidia_api.brody_true_voice_adapter import build_true_brody_answer
    ctx = _mock_chain_context(topic="GENERAL", status="NO_MEMORY_RESULTS")
    result = build_true_brody_answer("dis bonjour a maman", language="fr", brody_full_context=ctx)
    fa = result.get("final_answer", "")
    assert "Bonjour maman" in fa, f"Expected 'Bonjour maman' in final_answer, got: {fa[:120]}"


def test_true_voice_not_unclassified():
    from apps.obsidia_api.brody_true_voice_adapter import build_true_brody_answer
    ctx = _mock_chain_context(topic="GENERAL", status="NO_MEMORY_RESULTS")
    result = build_true_brody_answer("bonjour", language="fr", brody_full_context=ctx)
    fa = result.get("final_answer", "")
    assert "Requête non classifiée" not in fa


def test_true_voice_contains_kx108_only():
    from apps.obsidia_api.brody_true_voice_adapter import build_true_brody_answer
    ctx = _mock_chain_context(topic="GENERAL", status="NO_MEMORY_RESULTS")
    result = build_true_brody_answer("merci", language="fr", brody_full_context=ctx)
    fa = result.get("final_answer", "")
    assert "KX108_ONLY" in fa


def test_true_voice_contains_pas_de_decision():
    from apps.obsidia_api.brody_true_voice_adapter import build_true_brody_answer
    ctx = _mock_chain_context(topic="GENERAL", status="NO_MEMORY_RESULTS")
    result = build_true_brody_answer("merci", language="fr", brody_full_context=ctx)
    fa = result.get("final_answer", "").lower()
    assert "pas de décision" in fa or "pas de decision" in fa


def test_true_voice_contains_ecriture_memoire():
    from apps.obsidia_api.brody_true_voice_adapter import build_true_brody_answer
    ctx = _mock_chain_context(topic="GENERAL", status="NO_MEMORY_RESULTS")
    result = build_true_brody_answer("merci", language="fr", brody_full_context=ctx)
    fa = result.get("final_answer", "").lower()
    assert "écriture mémoire" in fa or "ecriture memoire" in fa


def test_true_voice_no_write():
    from apps.obsidia_api.brody_true_voice_adapter import build_true_brody_answer
    ctx = _mock_chain_context(topic="GENERAL", status="NO_MEMORY_RESULTS")
    result = build_true_brody_answer("bonjour", language="fr", brody_full_context=ctx)
    assert result.get("memory_write") is False
    assert result.get("graphiti_write") is False
    assert result.get("neo4j_write") is False


def test_true_voice_no_kernel_mutation():
    from apps.obsidia_api.brody_true_voice_adapter import build_true_brody_answer
    ctx = _mock_chain_context(topic="GENERAL", status="NO_MEMORY_RESULTS")
    result = build_true_brody_answer("bonjour", language="fr", brody_full_context=ctx)
    assert result.get("kernel_mutation") is False


def test_true_voice_x108_topic_not_affected():
    """X108-topic queries must NOT be intercepted by GENERAL_CONVERSATION_READONLY."""
    from apps.obsidia_api.brody_true_voice_adapter import build_true_brody_answer
    ctx = _mock_chain_context(topic="X108", status="NO_MEMORY_RESULTS")
    ctx["semantic_query_snapshot"] = {"topic": "X108"}
    result = build_true_brody_answer("explique X108", language="fr", brody_full_context=ctx)
    assert result.get("final_answer_source") != "GENERAL_CONVERSATION_READONLY"


def test_true_voice_semantic_failed_preserved_for_real_unknown():
    """Unknown non-conversational GENERAL queries still get SEMANTIC_MATCH_FAILED_GENERAL."""
    from apps.obsidia_api.brody_true_voice_adapter import build_true_brody_answer
    ctx = _mock_chain_context(topic="GENERAL", status="NO_MEMORY_RESULTS")
    # A non-conversational unknown query with no block signals and no conv pattern
    result = build_true_brody_answer(
        "quelle est la masse volumique du tungstène", language="fr", brody_full_context=ctx
    )
    assert result.get("final_answer_source") == "SEMANTIC_MATCH_FAILED_GENERAL"


# ── API integration — brody_chat ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_api_dis_bonjour_maman_general_conversation_readonly():
    """POST /api/brody/chat message='dis bonjour a maman' → GENERAL_CONVERSATION_READONLY."""
    from apps.obsidia_api.routes.brody import brody_chat, BrodyChatRequest

    req = BrodyChatRequest(
        message="dis bonjour a maman",
        language="fr",
        session_id="general_conversation_live_probe",
        compact=False,
        debug=True,
    )
    result = await brody_chat(req)

    assert isinstance(result, dict), f"Expected dict, got {type(result)}"
    assert result.get("final_answer_source") == "GENERAL_CONVERSATION_READONLY", (
        f"Expected GENERAL_CONVERSATION_READONLY, got: {result.get('final_answer_source')}"
    )
    fa = result.get("final_answer", "")
    assert "Bonjour maman" in fa, f"Expected 'Bonjour maman' in final_answer, got: {fa[:200]}"
    assert "Requête non classifiée" not in fa

    topic = result.get("topic", "")
    assert topic in ("GENERAL", "GENERAL_CONVERSATION"), f"Unexpected topic: {topic}"

    assert result.get("decision_authority") == "KX108_ONLY"
    assert result.get("memory_write") is False
    assert result.get("graphiti_write") is False
    assert result.get("neo4j_write") is False
    assert result.get("kernel_mutation") is False
    assert result.get("emits_act") is False


@pytest.mark.asyncio
async def test_api_bonjour_boundary_fields():
    from apps.obsidia_api.routes.brody import brody_chat, BrodyChatRequest

    req = BrodyChatRequest(
        message="bonjour",
        language="fr",
        session_id="general_conversation_live_probe",
    )
    result = await brody_chat(req)
    assert result.get("decision_authority") == "KX108_ONLY"
    assert result.get("memory_write") is False
    assert result.get("kernel_mutation") is False
    fa = result.get("final_answer", "")
    assert "KX108_ONLY" in fa
