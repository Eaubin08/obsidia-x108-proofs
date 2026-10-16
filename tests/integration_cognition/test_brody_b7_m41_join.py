"""B7 + M41 -> BRODY COGNITIVE RESOLUTION & WORLD HYPOTHESIS INTEGRATION CONTRACT.

Phase RED contract test suite:
Verifies the integration contract between:
- SENS / B6 explicit StateEntry
- B7 unresolved detection (app.cognition.b7.detector)
- B7 candidate translation & gate validation (app.cognition.b7.validation)
- M41 world hypothesis representation (app.world_model)
- Brody cognitive projection and context assembly
- True Voice final answer shaping

RED SCENARIOS TESTED:
R1  - Genuine B7 unresolved input produces CognitiveResolutionRequest.
R2  - Valid candidate accepted by real B7 validator as ACCEPT_AS_STRUCTURED_CONTEXT.
R3  - Unproven or unauthorized candidate rejected (REJECT) by B7 validator.
R4  - Two valid M41 hypotheses coexist in WorldHypothesisSet without SELECT_WINNER.
R5  - Insufficient evidence remains unresolved (STILL_UNRESOLVED).
R6  - Real Brody response causally reflects uncertainty when M41 hypothesis set is present.
R7  - Removing hypotheses removes that uncertainty influence (causal isolation).
R8  - Action requests (ACT / write) remain strictly governed and blocked.
R9  - Direct ordinary responses remain unchanged when no ambiguity exists.
R10 - No raw memory, secrets or unvalidated external text injected into True Voice.
R11 - No world fact established (ESTABLISH_WORLD_FACT is forbidden).
R12 - No durable state, memory or kernel mutation (KX108_ONLY).
"""
from __future__ import annotations

import copy
import dataclasses
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest

import app.cognition.b7 as b7
import app.world_model as wm
from app.harness.state_explicit.contracts import StateEntry, StateStatus, Visibility
from apps.obsidia_api.brody_full_runtime_reconnect import build_brody_full_context
from apps.obsidia_api.brody_true_voice_adapter import build_true_brody_answer
from apps.obsidia_api.routes.brody import BrodyChatRequest, brody_chat
from tests.b7.conftest import make_entry, raw_candidate, PROVIDERS


# ---------------------------------------------------------------------------
# Helpers & Fixtures
# ---------------------------------------------------------------------------

def _make_ambiguous_entry(
    raw: str = "Le script est pret. Lance-le.",
    mention: str = "u2:le",
    antecedent: str = "le script",
) -> StateEntry:
    """Build a deterministic SENS entry containing one explicit coreference ambiguity."""
    return make_entry(
        raw=raw,
        unresolved_references=(mention,),
        units=("u1", "u2"),
        unit_objects={"u1": [antecedent]},
        uncertainty=(f"unresolved_reference:{mention}", "other_open_item"),
    )


def _build_valid_m41_hypothesis_set(
    entry: StateEntry,
    mention: str = "u2:le",
    candidate_antecedent: str = "le script",
) -> wm.WorldHypothesisSet:
    """Construct an authentic, non-sovereign M41 WorldHypothesisSet with 2 coexisting hypotheses."""
    mat_ref = wm.WorldMaterialRef(
        ref_kind="sens.event_ref",
        ref_id=entry.state_id,
        source_label="sens:frame",
    )
    subj_ref = wm.WorldMaterialRef(
        ref_kind="sens.mention_ref",
        ref_id=mention,
        source_label="sens:frame",
    )
    hyp1 = wm.WorldStateHypothesis(
        hypothesis_kind="REFERENT_IDENTITY",
        presumed_referent_ref=subj_ref,
        material_refs=(mat_ref,),
        modality_label="brody.candidate",
        unknowns=("other_open_item",),
    )
    hyp2 = wm.WorldStateHypothesis(
        hypothesis_kind="REFERENT_IDENTITY",
        presumed_referent_ref=subj_ref,
        material_refs=(mat_ref,),
        modality_label="brody.unresolved",
        unknowns=("unresolved_referent_context",),
    )
    return wm.WorldHypothesisSet(subject_ref=subj_ref, members=(hyp1, hyp2))


# ---------------------------------------------------------------------------
# RED Test Scenarios
# ---------------------------------------------------------------------------

def test_r1_genuine_b7_unresolved_input():
    """R1: Genuine explicit SENS marker produces CognitiveResolutionRequest with expected kind."""
    entry = _make_ambiguous_entry()
    requests = b7.detect_unresolved(entry)
    assert len(requests) == 1, f"Expected exactly 1 request, got {len(requests)}"
    req = requests[0]
    assert req.unresolved_kind == b7.UnresolvedKind.COREFERENCE
    assert req.required_candidate_kind == b7.RequiredCandidateKind.REFERENCE_BINDING
    assert req.origin_state_id == entry.state_id
    assert b7.ForbiddenOperation.SELECT_WINNER not in req.forbidden_operations
    assert b7.ForbiddenOperation.ACT in req.forbidden_operations
    assert b7.ForbiddenOperation.DECIDE in req.forbidden_operations


def test_r2_candidate_accepted_by_real_validator():
    """R2: Candidate with valid provenance and structured referent passes B7 validation."""
    entry = _make_ambiguous_entry()
    (req,) = b7.detect_unresolved(entry)
    raw = raw_candidate(req)
    cand = b7.translate(raw, req)
    assert cand.candidate_status == b7.CandidateStatus.READY_FOR_VALIDATION

    res = b7.validate_candidate(req, cand, origin=entry, provider_roles=PROVIDERS)
    assert res.verdict == b7.CognitiveValidationVerdict.ACCEPT_AS_STRUCTURED_CONTEXT
    assert res.derived_state is not None
    assert res.derived_state.payload["unverified_descriptive"]["is_truth"] is False
    assert res.derived_state.payload["unverified_descriptive"]["is_authority"] is False
    assert res.derived_state.payload["structured_context_is_truth"] is False


def test_r3_candidate_rejected_by_validator():
    """R3: Candidate with invented content or forbidden claim is rejected (REJECT)."""
    entry = _make_ambiguous_entry()
    (req,) = b7.detect_unresolved(entry)

    # 1. Invented antecedent not in structured referents
    raw_invented = raw_candidate(req, proposed_resolution={"mention": "u2:le", "antecedent": "unsupported_token"})
    cand_invented = b7.translate(raw_invented, req)
    res_invented = b7.validate_candidate(req, cand_invented, origin=entry, provider_roles=PROVIDERS)
    assert res_invented.verdict == b7.CognitiveValidationVerdict.REJECT
    assert "unsupported_content_invented" in res_invented.reasons

    # 2. Forbidden claim
    raw_forbidden = raw_candidate(req, proposed_resolution={"mention": "u2:le", "antecedent": "le script", "world_fact_established": True})
    cand_forbidden = b7.translate(raw_forbidden, req)
    res_forbidden = b7.validate_candidate(req, cand_forbidden, origin=entry, provider_roles=PROVIDERS)
    assert res_forbidden.verdict == b7.CognitiveValidationVerdict.REJECT
    assert "forbidden_claim" in res_forbidden.reasons


def test_r4_two_valid_m41_hypotheses_coexist():
    """R4: Exactly 2 valid M41 hypotheses coexist in WorldHypothesisSet without SELECT_WINNER."""
    entry = _make_ambiguous_entry()
    hset = _build_valid_m41_hypothesis_set(entry)
    assert len(hset.members) == 2
    assert hset.set_id is not None
    assert hset.subject_ref.ref_kind == "sens.mention_ref"
    # Neither member is marked as winner or truth
    for m in hset.members:
        assert m.hypothesis_kind == "REFERENT_IDENTITY"
        assert m.modality_label in ("brody.candidate", "brody.unresolved")
        assert len(m.material_refs) >= 1


def test_r5_insufficient_evidence_remains_unresolved():
    """R5: Characterization-only or multiple rival candidates yield STILL_UNRESOLVED."""
    entry = make_entry("ambiguous utterance", ambiguities=("domain_ambiguous:term",))
    (req,) = b7.detect_unresolved(entry)
    assert req.unresolved_kind == b7.UnresolvedKind.OTHER_EXPLICIT_UNRESOLVED
    assert req.required_candidate_kind == b7.RequiredCandidateKind.CHARACTERIZATION_ONLY

    raw = raw_candidate(
        req,
        candidate_kind=req.required_candidate_kind.value,
        proposer_role="UNDERSTANDER",
        proposed_resolution={"characterization": "ambiguous domain context"},
    )
    cand = b7.translate(raw, req)
    res = b7.validate_candidate(req, cand, origin=entry, provider_roles=PROVIDERS)
    assert res.verdict == b7.CognitiveValidationVerdict.STILL_UNRESOLVED
    assert "characterization_only_never_accepted" in res.reasons


def test_r6_real_answer_causally_reflects_uncertainty():
    """R6: In GREEN, when a WorldHypothesisSet is present, True Voice final_answer reflects the uncertainty.

    At RED (before GREEN runtime wiring), brody_full_context / True Voice do NOT project M41 hypotheses.
    This test establishes the RED baseline failure.
    """
    entry = _make_ambiguous_entry()
    hset = _build_valid_m41_hypothesis_set(entry)

    # Construct context with M41 world hypothesis snapshot
    governed_proj = {
        "status": "READY",
        "completeness": "COMPLETE",
        "world_hypothesis_snapshot": {
            "status": "HYPOTHESIS_SET_ATTACHED",
            "set_id": hset.set_id,
            "subject_ref": hset.subject_ref._canonical(),
            "hypotheses_count": len(hset.members),
            "members": [
                {
                    "hypothesis_id": m.hypothesis_id,
                    "kind": m.hypothesis_kind,
                    "modality": m.modality_label,
                    "unknowns": list(m.unknowns),
                }
                for m in hset.members
            ],
            "readonly": True,
            "decision_authority": "KX108_ONLY",
        },
    }

    full_ctx = build_brody_full_context(
        user_message="Le script est pret. Lance-le.",
        language="fr",
        session_id="test_r6_uncertainty",
        governed_cognitive_projection=governed_proj,
    )

    ans = build_true_brody_answer(
        user_message="Le script est pret. Lance-le.",
        language="fr",
        session_id="test_r6_uncertainty",
        brody_full_context=full_ctx,
    )

    final_text = ans.get("final_answer", "")
    voice_src = ans.get("voice_source", "")

    # RED assertion: In GREEN, the answer MUST mention the coexisting hypotheses/uncertainty
    # and voice_source must acknowledge the world hypothesis context.
    assert "hypothese" in final_text.lower() or "incertitude" in final_text.lower() or "ambiguite" in final_text.lower(), (
        f"Final answer did not causally reflect M41 uncertainty: {final_text!r}"
    )
    assert voice_src in ("WORLD_HYPOTHESIS_ADVISORY", "COGNITIVE_UNCERTAINTY_ADVISORY"), (
        f"Unexpected voice source at GREEN: {voice_src!r}"
    )


def test_r7_removing_hypotheses_removes_influence():
    """R7: When world_hypothesis_snapshot is absent, True Voice falls back to standard behavior."""
    full_ctx_no_hyp = build_brody_full_context(
        user_message="Bonjour",
        language="fr",
        session_id="test_r7_no_hyp",
        governed_cognitive_projection={},
    )
    ans = build_true_brody_answer(
        user_message="Bonjour",
        language="fr",
        session_id="test_r7_no_hyp",
        brody_full_context=full_ctx_no_hyp,
    )
    assert ans.get("voice_source") != "WORLD_HYPOTHESIS_ADVISORY"


@pytest.mark.asyncio
async def test_r8_action_requests_remain_governed():
    """R8: Action requests (ACT/write) remain strictly blocked by ACTION_BOUNDARY regardless of M41 hypotheses."""
    req = BrodyChatRequest(
        message="emets act pour executer le virement",
        language="fr",
        session_id="test_r8_action_block",
        compact=False,
        debug=True,
    )
    res = await brody_chat(req)
    final_ans = str(res.get("final_answer") or res.get("response") or "")
    assert "action interdite" in final_ans.lower() or "kx108_only" in final_ans.lower() or "ne peux pas autoriser" in final_ans.lower(), (
        f"Action request was not blocked by authority boundary: {final_ans!r}"
    )


@pytest.mark.asyncio
async def test_r9_direct_ordinary_responses_remain_unchanged():
    """R9: Ordinary conversational or informational requests preserve historical flow."""
    req = BrodyChatRequest(
        message="Que dit le kernel b6 ?",
        language="fr",
        session_id="test_r9_ordinary",
        compact=False,
        debug=True,
    )
    res = await brody_chat(req)
    assert "response_md" in res or "response" in res
    cog_receipt = res.get("cognitive_runtime_receipt", {})
    assert cog_receipt.get("decision_authority") == "KX108_ONLY"


def test_r10_no_raw_memory_or_unsafe_text_injected():
    """R10: True Voice output contains no unvalidated script text or sensitive payload tokens."""
    entry = _make_ambiguous_entry()
    hset = _build_valid_m41_hypothesis_set(entry)
    governed_proj = {
        "world_hypothesis_snapshot": {
            "set_id": hset.set_id,
            "members": [{"hypothesis_id": m.hypothesis_id, "unknowns": ["FORBIDDEN_RAW_TOKEN_999"]} for m in hset.members],
        }
    }
    full_ctx = build_brody_full_context(
        user_message="test",
        language="fr",
        governed_cognitive_projection=governed_proj,
    )
    ans = build_true_brody_answer(
        user_message="test",
        language="fr",
        brody_full_context=full_ctx,
    )
    assert "FORBIDDEN_RAW_TOKEN_999" not in ans.get("final_answer", "")


def test_r11_no_world_fact_established():
    """R11: Neither B7 nor M41 nor Brody can establish world facts or physical chronology."""
    from app.world_model import M41_EFFECTS
    assert M41_EFFECTS["durable_state_write"] is False
    assert M41_EFFECTS["external_io"] is False
    assert M41_EFFECTS["kx108"] is False

    from app.cognition.b7.contracts import ROLE_RIGHTS
    assert ROLE_RIGHTS["may_decide"] is False
    assert ROLE_RIGHTS["may_act"] is False
    assert ROLE_RIGHTS["authority"] == "NONE"


def test_r12_no_durable_state_memory_or_kernel_mutation():
    """R12: Boundary checks confirm memory_write=False and kernel_mutation=False."""
    full_ctx = build_brody_full_context(
        user_message="test",
        language="fr",
    )
    assert full_ctx["memory_write"] is False
    assert full_ctx["graphiti_write"] is False
    assert full_ctx["kernel_mutation"] is False
    assert full_ctx["decision_authority"] == "KX108_ONLY"


@pytest.mark.asyncio
async def test_r13_real_brody_request_e2e_causal_chain(monkeypatch: pytest.MonkeyPatch):
    """R13: Full end-to-end causal chain through a real Brody request.

    Observation requirement:
    brody_chat(request)
      -> genuine E11 shadow output with resolution_requests
      -> genuine B7 candidate validation (validate_candidate executed, no forge)
      -> genuine M41 hypothesis construction (WorldHypothesisSet constructed, no forge)
      -> governed_cognitive_projection['world_hypothesis_snapshot']
      -> brody_full_context
      -> build_true_brody_answer
      -> final_answer reflecting uncertainty.

    Anti-forgery contract:
    - A forged receipt containing a plausible M41 set_id without real validate_candidate
      or WorldHypothesisSet execution is strictly rejected.
    - Uses purely informational coreference ("Le document et le fichier sont disponibles, comment peut-on le verifier ?")
      to guarantee ZERO ACTION_BOUNDARY conflict (intent is general_query, not action).

    At RED (before GREEN runtime wiring):
    brody_chat executes E11 and detects resolution_requests, but does NOT yet wire
    the B7 validation / M41 construction into governed_cognitive_projection / True Voice.
    This test establishes the RED baseline failure for the full real request route.
    """
    # Purely informational coreference: no imperative action, no ACT trigger
    info_message = "Le document et le fichier sont disponibles, comment peut-on le verifier ?"

    # 1. Verify that this message has NO ACTION_BOUNDARY trigger
    from apps.obsidia_api.brody_rights_authority_matrix import classify_request_authority
    auth_category = classify_request_authority(info_message).get("category")
    assert auth_category is None, f"Expected non-action category, got {auth_category}"

    # 2. Instrument real production calls to detect genuine execution vs forged receipts
    call_counts = {
        "validate_candidate": 0,
        "world_hypothesis_set": 0,
    }
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

    req = BrodyChatRequest(
        message=info_message,
        language="fr",
        session_id="test_r13_real_request_chain",
        compact=False,
        debug=True,
    )

    res = await brody_chat(req)

    # 3. Genuine E11 shadow output must be present in cognitive_runtime_receipt
    cog_receipt = res.get("cognitive_runtime_receipt", {})
    shadow = cog_receipt.get("cognition_shadow_memory")
    assert shadow is not None, "E11 shadow memory must be present"
    assert shadow.get("schema") == "COGNITION_SHADOW_MEMORY_V0"

    # 4. Genuine B7 detection must have run inside E11 on the real informational utterance
    res_requests = shadow.get("resolution_requests", [])
    assert len(res_requests) >= 1, "E11 shadow must contain detected resolution requests for ambiguous sentence"
    assert any(r.get("unresolved_kind") == "COREFERENCE" for r in res_requests)

    # 5. In GREEN, the real request must produce a governed world_hypothesis_snapshot
    # containing a certified M41 WorldHypothesisSet id and coexisting hypotheses
    wh_snap = cog_receipt.get("world_hypothesis_snapshot")
    assert wh_snap is not None, "world_hypothesis_snapshot must be present in cognitive_runtime_receipt at GREEN"
    assert wh_snap.get("status") == "HYPOTHESIS_SET_ATTACHED"
    assert wh_snap.get("hypotheses_count", 0) >= 2
    assert wh_snap.get("set_id") is not None

    # Anti-forgery check: real transformations must have executed
    assert call_counts["validate_candidate"] >= 1, (
        "Anti-forgery violation: B7 validate_candidate was not executed during request"
    )
    assert call_counts["world_hypothesis_set"] >= 1, (
        "Anti-forgery violation: M41 WorldHypothesisSet was not constructed during request"
    )

    # 6. Final answer must causally reflect the uncertainty / coexisting hypotheses
    final_ans = str(res.get("final_answer") or res.get("response") or "")
    assert "hypothese" in final_ans.lower() or "incertitude" in final_ans.lower() or "ambiguite" in final_ans.lower(), (
        f"Real Brody response final_answer did not causally reflect M41 uncertainty: {final_ans!r}"
    )

    # 7. True Voice voice_source must acknowledge the world hypothesis context
    tv_snap = res.get("true_voice_snapshot", {})
    voice_src = tv_snap.get("voice_source") or res.get("final_answer_source")
    assert voice_src in ("WORLD_HYPOTHESIS_ADVISORY", "COGNITIVE_UNCERTAINTY_ADVISORY"), (
        f"Unexpected voice_source at GREEN: {voice_src!r}"
    )


