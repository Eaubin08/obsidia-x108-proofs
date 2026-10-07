import hashlib
import json

import pytest

from apps.obsidia_api import brody_real_response_pipeline as pipeline
from periphery.cognition.semantic_roles_v0 import (
    SemanticResolutionStatusV0,
    SemanticRoleBindingV0,
    SemanticRoleCandidateV0,
    SemanticRoleKindV0,
    build_semantic_role_projection_v0,
)


def _resolved(role, value):
    return SemanticRoleBindingV0(
        role=role,
        status=SemanticResolutionStatusV0.RESOLVED,
        candidates=(SemanticRoleCandidateV0(value=value),),
    )


def _projection():
    return build_semantic_role_projection_v0(
        raw_utterance="Explique ce que tu sais en mémoire sur Obsidia, et détaille.",
        bindings=(
            _resolved(SemanticRoleKindV0.FOCUS, "MEMORY"),
            _resolved(SemanticRoleKindV0.SCOPE, "OBSIDIA"),
            _resolved(SemanticRoleKindV0.OPERATION, "EXPLAIN"),
            _resolved(SemanticRoleKindV0.QUALIFIER, "DETAILED"),
            SemanticRoleBindingV0(
                role=SemanticRoleKindV0.SOURCE_OR_INSTRUMENT,
                status=SemanticResolutionStatusV0.UNKNOWN,
            ),
        ),
        source_refs=("live-finding:jarjar-memory-focus",),
    )


class _Terminal:
    @staticmethod
    def extract_memory_query(message):
        return message

    @staticmethod
    def is_action_risk(message):
        return False

    @staticmethod
    def build_response(**kwargs):
        return {"response_md": "Réponse Brody déterministe."}


def _patch_stable_brody(monkeypatch):
    monkeypatch.setattr(pipeline, "_TERMINAL", _Terminal())
    monkeypatch.setattr(pipeline, "_LOCAL_ENGINE", object())
    monkeypatch.setattr(pipeline, "_HYDRATION", object())
    monkeypatch.setattr(
        pipeline,
        "build_brody_pre_reasoning_snapshot",
        lambda **kwargs: {
            "reasoning_directive": {
                "resolution_required": False,
                "resolution_targets": [],
            },
            "pre_reasoning_calibration": {},
        },
    )
    monkeypatch.setattr(
        pipeline,
        "calibrate_pre_response",
        lambda **kwargs: {
            "response_readiness": "READY",
            "calibration_required": False,
            "calibration_flags": [],
        },
    )
    monkeypatch.setattr(
        pipeline,
        "calibrate_pre_action",
        lambda **kwargs: {
            "action_candidate_readiness": "NO_ACTION_CANDIDATE_REQUESTED",
            "candidate_projection_ready": False,
            "intent": "pure_response",
            "risk_flags": [],
        },
    )
    monkeypatch.setattr(
        pipeline,
        "build_final_sense_halo",
        lambda **kwargs: {
            "integration_trace": {},
            "intent": "pure_response",
            "readonly": True,
        },
    )


def test_r6_b_attaches_semantic_role_context_with_hash(monkeypatch):
    _patch_stable_brody(monkeypatch)
    projection = _projection()

    result = pipeline.run_brody_real_response_pipeline(
        message="Explique ce que tu sais en mémoire sur Obsidia, et détaille.",
        semantic_role_projection=projection,
    )

    ctx = result["semantic_role_context"]
    assert ctx["roles"]["FOCUS"]["resolved_value"] == "MEMORY"
    assert ctx["roles"]["SCOPE"]["resolved_value"] == "OBSIDIA"
    assert ctx["roles"]["OPERATION"]["resolved_value"] == "EXPLAIN"
    assert ctx["roles"]["SOURCE_OR_INSTRUMENT"]["status"] == "UNKNOWN"

    expected_hash = hashlib.sha256(
        json.dumps(
            ctx,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()

    assert result["semantic_role_projection_sha256"] == expected_hash
    assert result["context_packet"]["semantic_role_projection_sha256"] == expected_hash
    assert result["context_packet"]["semantic_role_projection"] == ctx

    assert ctx["readonly"] is True
    assert ctx["non_sovereign"] is True
    assert ctx["decision_authority"] == "KX108_ONLY"
    assert ctx["allowed_to_decide"] is False
    assert ctx["allowed_to_act"] is False
    assert ctx["memory_write"] is False
    assert ctx["kernel_mutation"] is False


def test_r6_b_context_does_not_change_brody_response_or_route(monkeypatch):
    _patch_stable_brody(monkeypatch)

    baseline = pipeline.run_brody_real_response_pipeline(
        message="Explique ce que tu sais en mémoire sur Obsidia, et détaille.",
    )
    enriched = pipeline.run_brody_real_response_pipeline(
        message="Explique ce que tu sais en mémoire sur Obsidia, et détaille.",
        semantic_role_projection=_projection(),
    )

    for key in (
        "response_md",
        "response_source",
        "source",
        "action_risk",
        "engine_status",
        "decision_authority",
        "allowed_to_decide",
        "allowed_to_act",
        "emits_act",
        "emits_verdict",
        "memory_write",
        "kernel_mutation",
    ):
        assert enriched[key] == baseline[key]

    assert baseline["semantic_role_context"] is None
    assert baseline["semantic_role_projection_sha256"] is None
    assert enriched["semantic_role_context"] is not None


def test_r6_b_rejects_non_contract_semantic_context(monkeypatch):
    _patch_stable_brody(monkeypatch)

    with pytest.raises(TypeError):
        pipeline.run_brody_real_response_pipeline(
            message="Explique Obsidia.",
            semantic_role_projection={"FOCUS": "OBSIDIA"},
        )
