from __future__ import annotations

from apps.obsidia_api.brody_pre_reasoning_adapter import (
    build_brody_pre_reasoning_snapshot,
)

import apps.obsidia_api.brody_full_runtime_orchestrator as full_runtime
import apps.obsidia_api.brody_real_response_pipeline as real_pipeline


def _pre(message: str) -> dict:
    return build_brody_pre_reasoning_snapshot(
        user_message=message,
        language="fr",
        intent="pure_response",
        authority_snapshot={
            "request_type": "PURE_RESPONSE",
        },
    )


def _directive(result: dict) -> dict:
    value = result.get(
        "reasoning_directive",
        {},
    )

    return (
        value
        if isinstance(value, dict)
        else {}
    )


def _qualification(result: dict) -> dict:
    value = result.get(
        "unknown_qualification",
        {},
    )

    return (
        value
        if isinstance(value, dict)
        else {}
    )


def test_bonjour_is_surface_language_not_epistemic_unknown():
    result = _pre("bonjour")

    directive = _directive(result)
    qualification = _qualification(result)

    assert (
        "bonjour"
        not in qualification.get(
            "unresolved_unknowns",
            [],
        )
    )

    assert (
        directive.get(
            "resolution_required"
        )
        is False
    )


def test_generic_context_is_not_epistemic_unknown():
    result = _pre(
        "explique le contexte"
    )

    directive = _directive(result)
    qualification = _qualification(result)

    assert (
        "contexte"
        not in qualification.get(
            "unresolved_unknowns",
            [],
        )
    )

    assert (
        directive.get(
            "resolution_required"
        )
        is False
    )


def test_florvaxium_remains_genuinely_unresolved():
    result = _pre(
        "explique le florvaxium"
    )

    directive = _directive(result)
    qualification = _qualification(result)

    assert (
        qualification.get(
            "unresolved_unknowns"
        )
        == [
            "florvaxium",
        ]
    )

    assert (
        directive.get(
            "resolution_required"
        )
        is True
    )


def _isolate_full_runtime(monkeypatch):
    monkeypatch.setattr(
        full_runtime,
        "_load_all",
        lambda: None,
    )

    for name in (
        "_TERMINAL",
        "_LOCAL",
        "_HYDRATION",
        "_CONTEXT",
        "_SESSION_LEDGER",
        "_PRESAVE",
        "_SCHEDULER",
        "_TRIAGE",
        "_AUTO_TRIAGE",
        "_CANDIDATE_EXPORT",
        "_IMPORT_DRY_RUN",
        "_REVIEW_GATE",
        "_GUARDED_APPLY",
    ):
        monkeypatch.setattr(
            full_runtime,
            name,
            None,
            raising=False,
        )

    monkeypatch.setattr(
        full_runtime,
        "_probe_graphiti",
        lambda: {
            "status": (
                "GRAPHITI_OFFLINE_TEST"
            ),
            "blocker": "TEST_ONLY",
            "port_7688_open": False,
        },
    )


def test_full_runtime_preserves_pre_reasoning_snapshot(
    monkeypatch,
):
    _isolate_full_runtime(
        monkeypatch
    )

    result = (
        full_runtime.run_full_brody_runtime(
            message=(
                "explique le florvaxium"
            ),
            session_id=(
                "semantic-4f-test"
            ),
            language="fr",
            allow_provider=False,
            allow_memory_candidate=False,
            allow_manual_apply=False,
        )
    )

    pre = result.get(
        "pre_reasoning_snapshot"
    )

    assert isinstance(
        pre,
        dict,
    )

    qualification = pre.get(
        "unknown_qualification",
        {},
    )

    assert (
        qualification.get(
            "unresolved_unknowns"
        )
        == [
            "florvaxium",
        ]
    )


def test_real_response_pipeline_already_preserves_snapshot(
    monkeypatch,
):
    monkeypatch.setattr(
        real_pipeline,
        "_load",
        lambda: None,
    )

    monkeypatch.setattr(
        real_pipeline,
        "_TERMINAL",
        None,
        raising=False,
    )

    monkeypatch.setattr(
        real_pipeline,
        "_LOCAL_ENGINE",
        None,
        raising=False,
    )

    monkeypatch.setattr(
        real_pipeline,
        "_HYDRATION",
        None,
        raising=False,
    )

    result = (
        real_pipeline.run_brody_real_response_pipeline(
            message=(
                "explique le florvaxium"
            ),
            language="fr",
            session_id=(
                "semantic-4f-real"
            ),
        )
    )

    pre = result.get(
        "pre_reasoning_snapshot"
    )

    assert isinstance(
        pre,
        dict,
    )

    assert (
        pre.get(
            "reasoning_directive",
            {},
        ).get(
            "resolution_required"
        )
        is True
    )
