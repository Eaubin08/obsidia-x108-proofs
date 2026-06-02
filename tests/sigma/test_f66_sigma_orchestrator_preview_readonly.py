from __future__ import annotations

from copy import deepcopy

import pytest

from sigma.orchestrator_preview import (
    COMPONENT,
    DECISION_AUTHORITY,
    PALIER,
    build_sigma_orchestrator_preview,
    validate_sigma_orchestrator_preview,
)


FALSE_FLAGS = (
    "allowed_to_decide",
    "emits_act",
    "emits_verdict",
    "kernel_mutation",
    "x108_mutation",
    "neo4j_write",
    "graphiti_write",
    "memory_write",
    "brody_decision",
)

REQUIRED_LAYERS = (
    "registry",
    "dispatcher",
    "packets",
    "connectors",
    "bus_bridge",
)


def test_f66_import_surface():
    assert PALIER == "F66"
    assert COMPONENT == "SIGMA_ORCHESTRATOR_PREVIEW_READONLY"
    assert DECISION_AUTHORITY == "KX108_ONLY"


def test_f66_build_returns_dict():
    preview = build_sigma_orchestrator_preview()
    assert isinstance(preview, dict)


def test_f66_identity_fields():
    preview = build_sigma_orchestrator_preview()
    assert preview["palier"] == "F66"
    assert preview["component"] == "SIGMA_ORCHESTRATOR_PREVIEW_READONLY"
    assert preview["decision_authority"] == "KX108_ONLY"
    assert preview["status"] == "READY"


def test_f66_readonly_advisory_boundary():
    preview = build_sigma_orchestrator_preview()
    assert preview["readonly"] is True
    assert preview["advisory_only"] is True


@pytest.mark.parametrize("flag", FALSE_FLAGS)
def test_f66_all_sovereignty_flags_false(flag):
    preview = build_sigma_orchestrator_preview()
    assert preview[flag] is False


def test_f66_no_route_no_main_no_network_no_file_write():
    preview = build_sigma_orchestrator_preview()
    assert preview["routes_created"] is False
    assert preview["main_modified"] is False
    assert preview["network_call"] is False
    assert preview["file_write"] is False


def test_f66_layers_present():
    preview = build_sigma_orchestrator_preview()
    assert isinstance(preview["layers"], dict)
    for layer in REQUIRED_LAYERS:
        assert layer in preview["layers"]


def test_f66_layer_summaries_are_readonly_metadata():
    preview = build_sigma_orchestrator_preview()
    for layer in REQUIRED_LAYERS:
        summary = preview["layers"][layer]
        assert isinstance(summary, dict)
        assert "module" in summary
        assert "available" in summary
        assert "error" in summary
        assert "public_symbol_count" in summary
        assert "public_symbols_preview" in summary


def test_f66_validate_default_preview_passes():
    result = validate_sigma_orchestrator_preview()
    assert result["status"] == "PASS"
    assert result["violations"] == []


def test_f66_validate_explicit_valid_preview_passes():
    preview = build_sigma_orchestrator_preview()
    result = validate_sigma_orchestrator_preview(preview)
    assert result["status"] == "PASS"
    assert result["violations"] == []


def _mutated_preview(key, value):
    preview = deepcopy(build_sigma_orchestrator_preview())
    preview[key] = value
    return preview


@pytest.mark.parametrize(
    "key,value,expected_violation",
    [
        ("decision_authority", "BRODY", "decision_authority_mismatch"),
        ("readonly", False, "readonly_not_true"),
        ("advisory_only", False, "advisory_only_not_true"),
        ("allowed_to_decide", True, "allowed_to_decide_not_false"),
        ("emits_act", True, "emits_act_not_false"),
        ("emits_verdict", True, "emits_verdict_not_false"),
        ("kernel_mutation", True, "kernel_mutation_not_false"),
        ("x108_mutation", True, "x108_mutation_not_false"),
        ("neo4j_write", True, "neo4j_write_not_false"),
        ("graphiti_write", True, "graphiti_write_not_false"),
        ("memory_write", True, "memory_write_not_false"),
        ("brody_decision", True, "brody_decision_not_false"),
        ("routes_created", True, "routes_created_not_false"),
        ("main_modified", True, "main_modified_not_false"),
        ("network_call", True, "network_call_not_false"),
        ("file_write", True, "file_write_not_false"),
    ],
)
def test_f66_validate_detects_boundary_violations(key, value, expected_violation):
    preview = _mutated_preview(key, value)
    result = validate_sigma_orchestrator_preview(preview)
    assert result["status"] == "FAIL"
    assert expected_violation in result["violations"]


def test_f66_validate_detects_missing_layers_dict():
    preview = deepcopy(build_sigma_orchestrator_preview())
    preview["layers"] = None
    result = validate_sigma_orchestrator_preview(preview)
    assert result["status"] == "FAIL"
    assert "layers_not_dict" in result["violations"]


@pytest.mark.parametrize("layer", REQUIRED_LAYERS)
def test_f66_validate_detects_missing_individual_layer(layer):
    preview = deepcopy(build_sigma_orchestrator_preview())
    del preview["layers"][layer]
    result = validate_sigma_orchestrator_preview(preview)
    assert result["status"] == "FAIL"
    assert f"missing_layer_{layer}" in result["violations"]


def test_f66_does_not_import_brody_orchestrators():
    preview = build_sigma_orchestrator_preview()
    modules = {
        summary["module"]
        for summary in preview["layers"].values()
        if isinstance(summary, dict)
    }
    assert "apps.obsidia_api.brody_full_runtime_orchestrator" not in modules
    assert "apps.obsidia_api.brody_automation_orchestrator" not in modules


def test_f66_forbidden_execution_tokens_not_used_as_fields():
    preview = build_sigma_orchestrator_preview()
    forbidden_field_names = {"act", "verdict", "decision", "allow", "hold", "block", "decide"}
    assert forbidden_field_names.isdisjoint(set(preview.keys()))


def test_f66_validation_result_is_not_a_decision_verdict():
    result = validate_sigma_orchestrator_preview()
    assert "decision" not in result
    assert "verdict" not in result
    assert "action" not in result
    assert "act" not in result
