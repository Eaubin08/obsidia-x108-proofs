"""B7/M41 -> BRODY TRUE VOICE ALTERNATIVES DISCRIMINANT RED CONTRACT TEST.

Contract: BRODY_M41_TRUE_VOICE_ALTERNATIVES_CONTRACT_V1
Scope: French coreference with 2 noun phrases producing a WorldHypothesisSet.
Verification:
1. Real execution path invokes B7 validate_candidate and wm.WorldHypothesisSet.
2. (DISCRIMINANT RED) final_answer explicitly exposes the actual competing alternatives without selecting a winner.
3. Causal isolation: when the ambiguity is absent, the alternatives formulation disappears.
4. Falsified or incomplete snapshot (< 2 hypotheses) fails closed (no alternatives assertion).
5. ACTION_BOUNDARY retains absolute priority over any M41 hypothesis context.
"""
from __future__ import annotations

import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import app.cognition.b7 as b7
import app.world_model as wm
from apps.obsidia_api.routes.brody import BrodyChatRequest, brody_chat
from apps.obsidia_api.brody_true_voice_adapter import build_true_brody_answer
from apps.obsidia_api.brody_full_runtime_reconnect import build_brody_full_context


@pytest.mark.asyncio
async def test_1_real_path_invokes_b7_and_builds_m41_from_candidates(monkeypatch: pytest.MonkeyPatch):
    """Test 1: The real request path executes genuine B7 translation/validation and builds M41 hypotheses."""
    call_counts = {"validate_candidate": 0, "world_hypothesis_set": 0}

    orig_validate = b7.validate_candidate
    def spy_validate(*args, **kwargs):
        call_counts["validate_candidate"] += 1
        return orig_validate(*args, **kwargs)
    monkeypatch.setattr(b7, "validate_candidate", spy_validate)

    orig_hset = wm.WorldHypothesisSet
    def spy_hset(*args, **kwargs):
        call_counts["world_hypothesis_set"] += 1
        return orig_hset(*args, **kwargs)
    monkeypatch.setattr(wm, "WorldHypothesisSet", spy_hset)

    message = "Le document et le fichier sont disponibles, comment peut-on le verifier ?"
    req = BrodyChatRequest(
        message=message,
        language="fr",
        session_id="test_b7_m41_real_path",
        compact=False,
        debug=True,
    )
    res = await brody_chat(req)

    # 1. B7 validation was executed for the 2 candidate referents
    assert call_counts["validate_candidate"] >= 2, (
        f"Expected at least 2 validate_candidate executions, got {call_counts['validate_candidate']}"
    )

    # 2. M41 WorldHypothesisSet was constructed
    assert call_counts["world_hypothesis_set"] >= 1, (
        f"Expected at least 1 WorldHypothesisSet construction, got {call_counts['world_hypothesis_set']}"
    )

    # 3. Receipt carries valid world_hypothesis_snapshot
    cog_receipt = res.get("cognitive_runtime_receipt", {})
    wh_snap = cog_receipt.get("world_hypothesis_snapshot")
    assert wh_snap is not None, "world_hypothesis_snapshot must be present in cognitive_runtime_receipt"
    assert wh_snap.get("status") == "HYPOTHESIS_SET_ATTACHED"
    assert wh_snap.get("hypotheses_count") == 2
    assert wh_snap.get("decision_authority") == "KX108_ONLY"

    # 4. Snapshot members contain the candidate referent texts
    members = wh_snap.get("members", [])
    assert len(members) == 2
    member_unknowns = {u for m in members for u in m.get("unknowns", [])}
    assert "le document" in member_unknowns
    assert "le fichier" in member_unknowns


@pytest.mark.asyncio
async def test_2_final_answer_exposes_real_alternatives_without_winner():
    """Test 2 (DISCRIMINANT RED): final_answer must explicitly expose the actual competing alternatives.

    CURRENT RUNTIME BEHAVIOR:
      Emits generic advisory text without naming the candidate alternatives:
      'Analyse cognitive Brody : une ambiguïté a été détectée dans l'énoncé. Plusieurs hypothèses coexistent...'
    CONTRACT REQUIREMENT (RED UNTIL GREEN):
      Must articulate the coexisting alternatives (naming 'document' and 'fichier')
      consultatively, stating that the context cannot unilaterally decide between them.
    """
    message = "Le document et le fichier sont disponibles, comment peut-on le verifier ?"
    req = BrodyChatRequest(
        message=message,
        language="fr",
        session_id="test_b7_m41_alternatives_red",
        compact=False,
        debug=True,
    )
    res = await brody_chat(req)

    final_ans = str(res.get("final_answer") or res.get("response") or "")
    final_ans_lower = final_ans.lower()

    # Generic advisory checks (already present)
    assert "kx108_only" in final_ans_lower

    # DISCRIMINANT RED ASSERTIONS:
    # 1. The actual competing alternatives must be formulated in final_answer
    assert "document" in final_ans_lower, (
        f"RED: final_answer does not articulate alternative 'document': {final_ans!r}"
    )
    assert "fichier" in final_ans_lower, (
        f"RED: final_answer does not articulate alternative 'fichier': {final_ans!r}"
    )

    # 2. Must explicitly state that the context cannot decide / choose between alternatives
    assert (
        "ne permet pas de trancher" in final_ans_lower
        or "sans trancher" in final_ans_lower
        or "sans selection" in final_ans_lower
        or "sans sélection" in final_ans_lower
    ), (
        f"RED: final_answer does not explicitly state that context cannot decide between alternatives: {final_ans!r}"
    )


@pytest.mark.asyncio
async def test_3_causal_isolation_disappearance_without_snapshot_or_resolved():
    """Test 3: When the ambiguity is absent, the alternatives formulation disappears (causal isolation)."""
    # Query with no coreference ambiguity
    unambiguous_msg = "Bonjour, donne-moi le statut du systeme."
    req = BrodyChatRequest(
        message=unambiguous_msg,
        language="fr",
        session_id="test_b7_m41_unambiguous",
        compact=False,
        debug=True,
    )
    res = await brody_chat(req)
    final_ans = str(res.get("final_answer") or res.get("response") or "")

    # In the absence of an M41 hypothesis set, world_hypothesis_snapshot is None
    wh_snap = res.get("cognitive_runtime_receipt", {}).get("world_hypothesis_snapshot")
    assert wh_snap is None, "Unambiguous query must not attach world_hypothesis_snapshot"

    tv_snap = res.get("true_voice_snapshot", {})
    voice_src = tv_snap.get("voice_source") or res.get("final_answer_source")
    assert voice_src != "WORLD_HYPOTHESIS_ADVISORY", (
        f"Expected non-hypothesis voice source for unambiguous query, got: {voice_src!r}"
    )
    assert "plusieurs hypothèses coexistent" not in final_ans.lower()


def test_4_falsified_or_incomplete_snapshot_fails_closed():
    """Test 4: A falsified or incomplete snapshot (< 2 hypotheses) fails closed and does not claim alternatives."""
    # 1. Snapshot with only 1 hypothesis
    incomplete_snapshot = {
        "status": "HYPOTHESIS_SET_ATTACHED",
        "set_id": "fake_single_set",
        "hypotheses_count": 1,
        "members": [{"hypothesis_id": "hyp1", "unknowns": ["seul_candidat"]}],
        "readonly": True,
        "decision_authority": "KX108_ONLY",
    }
    ctx_incomplete = build_brody_full_context(
        user_message="Test message",
        language="fr",
        session_id="test_incomplete_snap",
        governed_cognitive_projection={"world_hypothesis_snapshot": incomplete_snapshot},
    )
    ans_incomplete = build_true_brody_answer(
        user_message="Test message",
        language="fr",
        session_id="test_incomplete_snap",
        brody_full_context=ctx_incomplete,
    )
    assert ans_incomplete.get("voice_source") != "WORLD_HYPOTHESIS_ADVISORY", (
        "Incomplete snapshot (< 2 members) must not trigger WORLD_HYPOTHESIS_ADVISORY"
    )

    # 2. Corrupted status
    corrupted_snapshot = {
        "status": "INVALID_STATUS",
        "set_id": "fake_corrupt_set",
        "hypotheses_count": 2,
        "members": [{"hypothesis_id": "h1", "unknowns": ["a"]}, {"hypothesis_id": "h2", "unknowns": ["b"]}],
        "readonly": True,
        "decision_authority": "KX108_ONLY",
    }
    ctx_corrupt = build_brody_full_context(
        user_message="Test message",
        language="fr",
        session_id="test_corrupt_snap",
        governed_cognitive_projection={"world_hypothesis_snapshot": corrupted_snapshot},
    )
    ans_corrupt = build_true_brody_answer(
        user_message="Test message",
        language="fr",
        session_id="test_corrupt_snap",
        brody_full_context=ctx_corrupt,
    )
    assert ans_corrupt.get("voice_source") != "WORLD_HYPOTHESIS_ADVISORY", (
        "Corrupted snapshot status must not trigger WORLD_HYPOTHESIS_ADVISORY"
    )


@pytest.mark.asyncio
async def test_5_action_boundary_blocks_priority_over_m41_hypotheses():
    """Test 5: ACTION_BOUNDARY retains absolute priority over any M41 hypothesis context."""
    # 1. End-to-end via brody_chat: action request with ambiguity
    action_message = "Le document et le fichier sont prets. Emets act pour executer le virement."
    req = BrodyChatRequest(
        message=action_message,
        language="fr",
        session_id="test_action_boundary_priority",
        compact=False,
        debug=True,
    )
    res = await brody_chat(req)
    final_ans = str(res.get("final_answer") or res.get("response") or "").lower()

    # Must be blocked by ACTION_BOUNDARY
    assert (
        "refus structurel" in final_ans
        or "action interdite" in final_ans
        or "kx108_only" in final_ans
        or "ne peux pas autoriser" in final_ans
    ), f"Action request was not blocked by ACTION_BOUNDARY: {final_ans!r}"

    # 2. Directly on True Voice adapter: action_boundary_already prevents WORLD_HYPOTHESIS_ADVISORY
    wh_snap = {
        "status": "HYPOTHESIS_SET_ATTACHED",
        "hypotheses_count": 2,
        "members": [{"hypothesis_id": "h1", "unknowns": ["le doc"]}, {"hypothesis_id": "h2", "unknowns": ["le zip"]}],
        "readonly": True,
        "decision_authority": "KX108_ONLY",
    }
    ctx = build_brody_full_context(
        user_message=action_message,
        language="fr",
        session_id="test_action_direct",
        authority_snapshot={"request_type": "ACTION_OR_ACT_REQUEST"},
        governed_cognitive_projection={"world_hypothesis_snapshot": wh_snap},
    )
    ans = build_true_brody_answer(
        user_message=action_message,
        language="fr",
        session_id="test_action_direct",
        brody_full_context=ctx,
    )
    assert ans.get("voice_source") == "ACTION_BOUNDARY", (
        f"Expected voice_source ACTION_BOUNDARY, got: {ans.get('voice_source')!r}"
    )
