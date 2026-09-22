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
        == "LLM_PROVIDER_GATE"
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
