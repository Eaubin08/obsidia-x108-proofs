from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest


ROOT = Path(
    __file__
).resolve().parents[2]


def _write_fake_router(
    root: Path,
) -> Path:
    pkg = root / "app" / "router"
    pkg.mkdir(
        parents=True,
        exist_ok=True,
    )

    (root / "app" / "__init__.py").write_text(
        "",
        encoding="utf-8",
    )

    (pkg / "__init__.py").write_text(
        "",
        encoding="utf-8",
    )

    decision = r'''
def decide(raw, memory_index=None):
    if "REMOTE_ESCALATE" in raw:
        return {
            "route": "fireworks",
            "level": 3,
            "reason": "REMOTE_REASONING_REQUIRED",
            "ir": {
                "intent_type": "analysis",
                "target_layer": "reasoning",
                "action": "analyze",
                "risk": "low",
            },
            "gate": {
                "verdict": "ALLOW",
            },
        }

    if "BRODY_LOCAL" in raw:
        return {
            "route": "brody",
            "level": 1,
            "reason": "LOCAL_BRODY_SUFFICIENT",
            "ir": {
                "intent_type": "question",
                "target_layer": "reasoning",
                "action": "answer",
                "risk": "low",
            },
            "gate": {
                "verdict": "ALLOW",
            },
        }

    if "CODE_LOCAL" in raw:
        return {
            "route": "obsidure_route_only",
            "level": 1,
            "reason": "LOCAL_OBSIDURE_ROUTE",
            "ir": {
                "intent_type": "code_request",
                "target_layer": "tooling",
                "action": "propose",
                "risk": "low",
            },
            "gate": {
                "verdict": "ALLOW",
            },
        }

    return {
        "route": "no_model_needed",
        "level": 0,
        "reason": "LOCAL_STRUCTURE_SUFFICIENT",
        "ir": {
            "intent_type": "question",
            "target_layer": "local",
            "action": "inspect",
            "risk": "low",
        },
        "gate": {
            "verdict": "ALLOW",
        },
    }
'''

    (pkg / "decision.py").write_text(
        decision,
        encoding="utf-8",
    )

    return root



@pytest.fixture(autouse=True)
def _stub_native_brody_runtime(
    monkeypatch,
):
    import scripts.obsidia_cognitive_ingress_v0 as ingress

    def fake_run_full_brody_runtime(
        *,
        message,
        session_id="local",
        language="fr",
        allow_provider=False,
        allow_memory_candidate=False,
        allow_manual_apply=False,
        x108_root=None,
    ):
        assert allow_provider is False
        assert allow_memory_candidate is False
        assert allow_manual_apply is False

        return {
            "action_id": "brody_test_runtime",
            "language": language,
            "timestamp": "2026-09-22T00:00:00+00:00",
            "readonly": True,
            "response_only": True,
            "memory_decision": False,
            "allowed_to_decide": False,
            "allowed_to_act": False,
            "emits_act": False,
            "emits_verdict": False,
            "kernel_mutation": False,
            "x108_mutation": False,
            "memory_write": False,
            "graphiti_write": False,
            "neo4j_write": False,
            "real_action": False,
            "decision_authority": "KX108_ONLY",
            "provider_status": "NOT_REQUESTED",
            "source": "REAL_BRODY_LOCAL_ENGINE_ONLY",
            "response": "Local Brody readonly candidate.",
            "response_md": "Local Brody readonly candidate.",
        }

    monkeypatch.setattr(
        ingress,
        "run_full_brody_runtime",
        fake_run_full_brody_runtime,
    )


def _clean_import_cache():
    import sys

    for name in list(sys.modules):
        if (
            name == "app"
            or name.startswith("app.")
        ):
            del sys.modules[name]


def test_local_first_route_skips_llm(
    tmp_path,
    monkeypatch,
):
    router = _write_fake_router(
        tmp_path / "router"
    )

    monkeypatch.setenv(
        "OBSIDIA_ROUTER_ROOT",
        str(router),
    )

    _clean_import_cache()

    from scripts.obsidia_cognitive_ingress_v0 import (
        run_cognitive_ingress,
    )

    result = run_cognitive_ingress(
        text=(
            "bonjour donne le statut local"
        ),
        session_id="test-local",
    )

    assert (
        result["route_decision"][
            "router_route"
        ]
        == "no_model_needed"
    )

    assert (
        result["llm_activation"][
            "required"
        ]
        is False
    )

    assert (
        result["llm_activation"][
            "activated"
        ]
        is False
    )

    assert (
        result["llm_activation"][
            "tokens_spent"
        ]
        == 0
    )

    assert (
        result["llm_activation"][
            "model_call_used"
        ]
        is False
    )

    assert (
        result["next_stage"]
        == "LOCAL_STACK_RESULT"
    )

    assert (
        result["decision_authority"]
        == "KX108_ONLY"
    )

    assert (
        result["authority"]
        == "NONE"
    )

    assert (
        result["real_execution"]
        is False
    )

    join = result[
        "cognitive_join"
    ]

    assert (
        join.get("status")
        == "READY_SHADOW_READONLY"
    )

    components = join.get(
        "components"
    )

    assert isinstance(
        components,
        dict,
    )

    assert (
        "CONTEXT_PACKET_V2"
        in components
    )

    assert (
        "W1_RUNTIME_JOIN"
        in components
    )

    assert (
        "W2_X108_ADMISSION"
        in components
    )

    assert (
        result[
            "decision_ticket_dry_run"
        ]
        is not None
    )


def test_explicit_remote_route_marks_llm_required_but_does_not_call(
    tmp_path,
    monkeypatch,
):
    router = _write_fake_router(
        tmp_path / "router"
    )

    monkeypatch.setenv(
        "OBSIDIA_ROUTER_ROOT",
        str(router),
    )

    _clean_import_cache()

    from scripts.obsidia_cognitive_ingress_v0 import (
        run_cognitive_ingress,
    )

    result = run_cognitive_ingress(
        text=(
            "bonjour REMOTE_ESCALATE "
            "analyse ce problème complexe"
        ),
        session_id="test-remote",
    )

    activation = result[
        "llm_activation"
    ]

    assert activation[
        "required"
    ] is True

    assert activation[
        "activated"
    ] is False

    assert activation[
        "model_call_used"
    ] is False

    assert activation[
        "tokens_spent"
    ] == 0

    assert activation[
        "reason"
    ] == (
        "EXPLICIT_REMOTE_ROUTE_SELECTED"
    )

    assert (
        result["next_stage"]
        == "LOCAL_MODEL_GATE"
    )

    receipt = result[
        "route_receipt"
    ]

    assert (
        receipt[
            "model_call_used"
        ]
        is False
    )

    assert (
        receipt[
            "model_call_avoided"
        ]
        is False
    )

    assert (
        receipt[
            "result_status"
        ]
        == "LLM_REQUIRED_NOT_CALLED"
    )


def test_obsidure_route_remains_local_no_remote_llm(
    tmp_path,
    monkeypatch,
):
    router = _write_fake_router(
        tmp_path / "router"
    )

    monkeypatch.setenv(
        "OBSIDIA_ROUTER_ROOT",
        str(router),
    )

    _clean_import_cache()

    from scripts.obsidia_cognitive_ingress_v0 import (
        run_cognitive_ingress,
    )

    result = run_cognitive_ingress(
        text=(
            "bonjour CODE_LOCAL "
            "prépare un correctif borné"
        ),
        session_id="test-code-local",
    )

    assert (
        result["route_decision"][
            "router_route"
        ]
        == "obsidure_route_only"
    )

    assert (
        result["llm_activation"][
            "required"
        ]
        is False
    )

    assert (
        result["llm_activation"][
            "model_call_used"
        ]
        is False
    )


def test_missing_router_fails_closed_without_llm(
    tmp_path,
    monkeypatch,
):
    missing = (
        tmp_path
        / "router-does-not-exist"
    )

    monkeypatch.setenv(
        "OBSIDIA_ROUTER_ROOT",
        str(missing),
    )

    _clean_import_cache()

    from scripts.obsidia_cognitive_ingress_v0 import (
        run_cognitive_ingress,
    )

    result = run_cognitive_ingress(
        text=(
            "bonjour analyse ceci"
        ),
        session_id="test-fail-closed",
    )

    route = result[
        "route_decision"
    ]

    assert (
        route[
            "fail_closed_hold"
        ]
        is True
    )

    assert (
        route[
            "human_authority_required"
        ]
        is True
    )

    assert (
        result["llm_activation"][
            "required"
        ]
        is False
    )

    assert (
        result["llm_activation"][
            "model_call_used"
        ]
        is False
    )


def test_source_contains_no_model_execution_primitive():
    source = (
        ROOT
        / "scripts"
        / "obsidia_cognitive_ingress_v0.py"
    ).read_text(
        encoding="utf-8",
    )

    forbidden = (
        "call_claude(",
        "subprocess.run(",
        "llama-server",
        "openai.",
        "anthropic.",
        "fireworks.ai",
    )

    for token in forbidden:
        assert token not in source


def test_native_brody_runs_before_model_gate(
    tmp_path,
    monkeypatch,
):
    router = _write_fake_router(
        tmp_path / "router"
    )

    monkeypatch.setenv(
        "OBSIDIA_ROUTER_ROOT",
        str(router),
    )

    _clean_import_cache()

    from scripts.obsidia_cognitive_ingress_v0 import (
        run_cognitive_ingress,
    )

    result = run_cognitive_ingress(
        text=(
            "BRODY_LOCAL explain "
            "this structured request"
        ),
        session_id="test-native-brody",
    )

    brody = result["brody_stage"]

    assert brody["attempted"] is True
    assert brody["candidate_available"] is True
    assert brody["boundary_ok"] is True
    assert brody["provider_status"] == "NOT_REQUESTED"

    assert result["llm_activation"]["required"] is False
    assert result["llm_activation"]["activated"] is False
    assert result["llm_activation"]["tokens_spent"] == 0

    assert result["next_stage"] == "LOCAL_STACK_RESULT"

    components = (
        result["cognitive_join"].get("components")
        or {}
    )

    assert (
        components.get("W3_BRODY")
        == "READY:REAL_RUNTIME_ADAPTER"
    )


def test_remote_route_runs_brody_before_local_model_gate(
    tmp_path,
    monkeypatch,
):
    router = _write_fake_router(
        tmp_path / "router"
    )

    monkeypatch.setenv(
        "OBSIDIA_ROUTER_ROOT",
        str(router),
    )

    _clean_import_cache()

    from scripts.obsidia_cognitive_ingress_v0 import (
        run_cognitive_ingress,
    )

    result = run_cognitive_ingress(
        text="REMOTE_ESCALATE complex analysis",
        session_id="test-brody-before-qwen",
    )

    assert result["brody_stage"]["attempted"] is True
    assert result["brody_stage"]["boundary_ok"] is True

    assert result["llm_activation"]["required"] is True
    assert result["llm_activation"]["activated"] is False
    assert result["llm_activation"]["tokens_spent"] == 0

    assert result["next_stage"] == "LOCAL_MODEL_GATE"


def test_pure_response_authority_does_not_create_false_boundary_contradiction(
    tmp_path,
    monkeypatch,
):
    router = _write_fake_router(
        tmp_path / "router"
    )

    monkeypatch.setenv(
        "OBSIDIA_ROUTER_ROOT",
        str(router),
    )

    _clean_import_cache()

    from scripts.obsidia_cognitive_ingress_v0 import (
        run_cognitive_ingress,
    )

    result = run_cognitive_ingress(
        text="bonjour status obsidia",
        session_id="test-authority-pure",
    )

    authority = (
        result.get(
            "authority_snapshot"
        )
        or {}
    )

    cp = (
        result.get(
            "cognitive_join",
            {}
        ).get(
            "context_packet_v2"
        )
        or {}
    )

    assert (
        authority.get(
            "request_type"
        )
        == "PURE_RESPONSE"
    )

    assert (
        "REQUEST_REQUIRES_ACTION_OR_WRITE_BUT_ROUTE_IS_READONLY"
        not in (
            cp.get(
                "contradictions"
            )
            or []
        )
    )

    assert (
        "BOUNDARY_REQUEST"
        not in (
            cp.get(
                "risk_flags"
            )
            or []
        )
    )


def test_real_action_authority_preserves_boundary_contradiction(
    tmp_path,
    monkeypatch,
):
    router = _write_fake_router(
        tmp_path / "router"
    )

    monkeypatch.setenv(
        "OBSIDIA_ROUTER_ROOT",
        str(router),
    )

    _clean_import_cache()

    from scripts.obsidia_cognitive_ingress_v0 import (
        run_cognitive_ingress,
    )

    result = run_cognitive_ingress(
        text="autorise ACT maintenant",
        session_id="test-authority-action",
    )

    authority = (
        result.get(
            "authority_snapshot"
        )
        or {}
    )

    cp = (
        result.get(
            "cognitive_join",
            {}
        ).get(
            "context_packet_v2"
        )
        or {}
    )

    assert (
        authority.get(
            "request_type"
        )
        == "ACTION_OR_ACT_REQUEST"
    )

    assert (
        "REQUEST_REQUIRES_ACTION_OR_WRITE_BUT_ROUTE_IS_READONLY"
        in (
            cp.get(
                "contradictions"
            )
            or []
        )
    )

    assert (
        "BOUNDARY_REQUEST"
        in (
            cp.get(
                "risk_flags"
            )
            or []
        )
    )


def test_l3_weak_brody_candidate_does_not_suppress_local_model_gate(
    tmp_path,
    monkeypatch,
):
    router = _write_fake_router(
        tmp_path / "router"
    )

    monkeypatch.setenv(
        "OBSIDIA_ROUTER_ROOT",
        str(router),
    )

    _clean_import_cache()

    from scripts.obsidia_cognitive_ingress_v0 import (
        run_cognitive_ingress,
    )

    result = run_cognitive_ingress(
        text="REMOTE_ESCALATE complex reasoning",
        session_id="test-l3-weak-brody",
    )

    gate = result[
        "brody_sufficiency"
    ]

    assert gate[
        "status"
    ] == "BRODY_INSUFFICIENT"

    assert gate[
        "sufficient"
    ] is False

    assert gate[
        "model_required"
    ] is True

    assert gate[
        "brody_source"
    ] == "REAL_BRODY_LOCAL_ENGINE_ONLY"

    assert (
        gate[
            "lexical_unknowns_gate_role"
        ]
        == "TELEMETRY_ONLY"
    )

    assert (
        result["next_stage"]
        == "LOCAL_MODEL_GATE"
    )

    assert (
        result["llm_activation"][
            "required"
        ]
        is True
    )

    assert (
        result["llm_activation"][
            "activated"
        ]
        is False
    )


def test_l3_strong_brody_can_avoid_model(
    tmp_path,
    monkeypatch,
):
    router = _write_fake_router(
        tmp_path / "router"
    )

    monkeypatch.setenv(
        "OBSIDIA_ROUTER_ROOT",
        str(router),
    )

    _clean_import_cache()

    import scripts.obsidia_cognitive_ingress_v0 as ingress

    def strong_brody(
        *,
        message,
        session_id="local",
        language="fr",
        allow_provider=False,
        allow_memory_candidate=False,
        allow_manual_apply=False,
        x108_root=None,
    ):
        return {
            "action_id": "strong_brody_test",
            "language": language,
            "timestamp": "2026-09-22T00:00:00+00:00",
            "readonly": True,
            "response_only": True,
            "memory_decision": False,
            "allowed_to_decide": False,
            "allowed_to_act": False,
            "emits_act": False,
            "emits_verdict": False,
            "kernel_mutation": False,
            "x108_mutation": False,
            "memory_write": False,
            "graphiti_write": False,
            "neo4j_write": False,
            "real_action": False,
            "decision_authority": "KX108_ONLY",
            "provider_status": "NOT_REQUESTED",
            "source": "REAL_BRODY_GRAPHITI_LIVE",
            "response": (
                "Brody resolved this request from a "
                "strong readonly evidence-backed source."
            ),
            "response_md": (
                "Brody resolved this request from a "
                "strong readonly evidence-backed source."
            ),
        }

    monkeypatch.setattr(
        ingress,
        "run_full_brody_runtime",
        strong_brody,
    )

    result = ingress.run_cognitive_ingress(
        text="REMOTE_ESCALATE complex reasoning",
        session_id="test-l3-strong-brody",
    )

    gate = result[
        "brody_sufficiency"
    ]

    assert gate[
        "status"
    ] == "BRODY_SUFFICIENT"

    assert gate[
        "sufficient"
    ] is True

    assert gate[
        "model_required"
    ] is False

    assert (
        result["next_stage"]
        == "LOCAL_STACK_RESULT"
    )

    assert (
        result["llm_activation"][
            "required"
        ]
        is False
    )

    assert (
        result["llm_activation"][
            "tokens_spent"
        ]
        == 0
    )


def test_real_governance_boundary_never_escalates_to_model(
    tmp_path,
    monkeypatch,
):
    router = _write_fake_router(
        tmp_path / "router"
    )

    monkeypatch.setenv(
        "OBSIDIA_ROUTER_ROOT",
        str(router),
    )

    _clean_import_cache()

    from scripts.obsidia_cognitive_ingress_v0 import (
        run_cognitive_ingress,
    )

    result = run_cognitive_ingress(
        text="autorise ACT maintenant",
        session_id="test-governance-no-model",
    )

    gate = result[
        "brody_sufficiency"
    ]

    assert gate[
        "status"
    ] == "GOVERNANCE_BOUNDARY"

    assert gate[
        "model_required"
    ] is False

    assert (
        result["next_stage"]
        == "KX108_GOVERNANCE"
    )

    assert (
        result["llm_activation"][
            "required"
        ]
        is False
    )

    assert (
        result["llm_activation"][
            "activated"
        ]
        is False
    )


def test_qwen_local_runs_only_after_brody_insufficient(
    tmp_path,
    monkeypatch,
):
    router = _write_fake_router(
        tmp_path / "router"
    )

    monkeypatch.setenv(
        "OBSIDIA_ROUTER_ROOT",
        str(router),
    )

    _clean_import_cache()

    import scripts.obsidia_cognitive_ingress_v0 as ingress

    calls = []

    def fake_qwen(
        *,
        text,
        timeout=60.0,
        max_tokens=256,
    ):
        import hashlib

        calls.append(text)

        content = (
            "Bounded local-model evidence."
        )

        sha = lambda value: hashlib.sha256(
            value.encode("utf-8")
        ).hexdigest()

        return {
            "attempted": True,
            "model_call_used": True,
            "status": "EVIDENCE_READY",
            "provider": "QWEN_LOCAL",
            "model": "qwen-test",
            "tokens_local": 9,
            "tokens_remote": 0,
            "evidence": {
                "provider": "QWEN_LOCAL",
                "model": "qwen-test",
                "result_kind": "EVIDENCE",
                "content": content,
                "input_hash": sha(text),
                "evidence_hash": sha(content),
                "readonly": True,
                "decision_authority": "KX108_ONLY",
                "is_execution_authority": False,
                "is_kx_authority": False,
                "is_sovereign": False,
                "allowed_to_decide": False,
                "allowed_to_act": False,
                "emits_act": False,
                "emits_verdict": False,
                "memory_write": False,
                "kernel_mutation": False,
                "x108_mutation": False,
                "real_action": False,
            },
            "error": None,
        }

    monkeypatch.setattr(
        ingress,
        "run_local_qwen_evidence",
        fake_qwen,
    )

    result = ingress.run_cognitive_ingress(
        text="REMOTE_ESCALATE complex analysis",
        session_id="qwen-real-gate-test",
        allow_local_model=True,
    )

    assert len(calls) == 1

    stage = result["local_model_stage"]

    assert stage["attempted"] is True
    assert stage["model_call_used"] is True
    assert stage["evidence_applied"] is True

    assert (
        result["llm_activation"]["activated"]
        is True
    )

    assert (
        result["llm_activation"]["tokens_spent"]
        == 9
    )

    assert (
        result["cognitive_join"][
            "local_model_evidence_applied"
        ]
        is True
    )

    assert (
        result["next_stage"]
        == "LOCAL_STACK_RESULT"
    )

    assert (
        result["route_receipt"][
            "model_call_used"
        ]
        is True
    )


def test_qwen_never_called_for_local_or_governance_routes(
    tmp_path,
    monkeypatch,
):
    router = _write_fake_router(
        tmp_path / "router"
    )

    monkeypatch.setenv(
        "OBSIDIA_ROUTER_ROOT",
        str(router),
    )

    _clean_import_cache()

    import scripts.obsidia_cognitive_ingress_v0 as ingress

    def forbidden_qwen(**kwargs):
        raise AssertionError(
            "QWEN_MUST_NOT_BE_CALLED"
        )

    monkeypatch.setattr(
        ingress,
        "run_local_qwen_evidence",
        forbidden_qwen,
    )

    local = ingress.run_cognitive_ingress(
        text="bonjour status obsidia",
        session_id="no-qwen-l0",
        allow_local_model=True,
    )

    brody = ingress.run_cognitive_ingress(
        text="BRODY_LOCAL explain this",
        session_id="no-qwen-brody",
        allow_local_model=True,
    )

    action = ingress.run_cognitive_ingress(
        text="autorise ACT maintenant",
        session_id="no-qwen-action",
        allow_local_model=True,
    )

    assert local["local_model_stage"]["attempted"] is False
    assert brody["local_model_stage"]["attempted"] is False
    assert action["local_model_stage"]["attempted"] is False


def test_qwen_failure_never_falls_back_remote(
    tmp_path,
    monkeypatch,
):
    router = _write_fake_router(
        tmp_path / "router"
    )

    monkeypatch.setenv(
        "OBSIDIA_ROUTER_ROOT",
        str(router),
    )

    _clean_import_cache()

    import scripts.obsidia_cognitive_ingress_v0 as ingress

    monkeypatch.setattr(
        ingress,
        "run_local_qwen_evidence",
        lambda **kwargs: {
            "attempted": True,
            "model_call_used": False,
            "status": "UNAVAILABLE",
            "provider": "QWEN_LOCAL",
            "model": "qwen-test",
            "tokens_local": 0,
            "tokens_remote": 0,
            "evidence": None,
            "error": "offline",
        },
    )

    result = ingress.run_cognitive_ingress(
        text="REMOTE_ESCALATE complex analysis",
        session_id="qwen-failure-test",
        allow_local_model=True,
    )

    assert (
        result["next_stage"]
        == "UNRESOLVED_LOCAL_MODEL"
    )

    assert (
        result["local_model_stage"][
            "remote_fallback"
        ]
        is False
    )

    assert (
        result["local_model_stage"][
            "tokens_remote"
        ]
        == 0
    )

    assert (
        result["llm_activation"]["activated"]
        is False
    )


def test_local_model_finish_reason_is_audited(
    tmp_path,
    monkeypatch,
):
    router = _write_fake_router(
        tmp_path / "router"
    )

    monkeypatch.setenv(
        "OBSIDIA_ROUTER_ROOT",
        str(router),
    )

    _clean_import_cache()

    import hashlib
    import scripts.obsidia_cognitive_ingress_v0 as ingress

    def fake_qwen(**kwargs):
        raw = kwargs["text"]
        content = "Bounded evidence."

        sha = lambda value: hashlib.sha256(
            value.encode("utf-8")
        ).hexdigest()

        return {
            "attempted": True,
            "model_call_used": True,
            "status": "EVIDENCE_READY",
            "provider": "QWEN_LOCAL",
            "model": "qwen-test",
            "tokens_local": 11,
            "tokens_remote": 0,
            "finish_reason": "stop",
            "evidence": {
                "provider": "QWEN_LOCAL",
                "model": "qwen-test",
                "result_kind": "EVIDENCE",
                "content": content,
                "input_hash": sha(raw),
                "evidence_hash": sha(content),
                "readonly": True,
                "decision_authority": "KX108_ONLY",
                "is_execution_authority": False,
                "is_kx_authority": False,
                "is_sovereign": False,
                "allowed_to_decide": False,
                "allowed_to_act": False,
                "emits_act": False,
                "emits_verdict": False,
                "memory_write": False,
                "kernel_mutation": False,
                "x108_mutation": False,
                "real_action": False,
            },
            "error": None,
        }

    monkeypatch.setattr(
        ingress,
        "run_local_qwen_evidence",
        fake_qwen,
    )

    result = ingress.run_cognitive_ingress(
        text="REMOTE_ESCALATE complex analysis",
        session_id="finish-reason-audit",
        allow_local_model=True,
    )

    assert (
        result["local_model_stage"]["finish_reason"]
        == "stop"
    )

    assert (
        result["local_model_stage"]["evidence_applied"]
        is True
    )


def test_governance_receipt_status_is_explicit(
    tmp_path,
    monkeypatch,
):
    router = _write_fake_router(
        tmp_path / "router"
    )

    monkeypatch.setenv(
        "OBSIDIA_ROUTER_ROOT",
        str(router),
    )

    _clean_import_cache()

    from scripts.obsidia_cognitive_ingress_v0 import (
        run_cognitive_ingress,
    )

    result = run_cognitive_ingress(
        text="autorise ACT maintenant",
        session_id="explicit-governance-receipt",
        allow_local_model=True,
    )

    assert (
        result["next_stage"]
        == "KX108_GOVERNANCE"
    )

    assert (
        result["route_receipt"]["result_status"]
        == "GOVERNANCE_BOUNDARY_NO_MODEL"
    )

    assert (
        result["local_model_stage"]["attempted"]
        is False
    )
