
from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CLI_PATH = REPO_ROOT / "scripts" / "obsidia_cli.py"


def load_cli():
    spec = importlib.util.spec_from_file_location("obsidia_cli_runtime_input_resolver_test", CLI_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_answer_router_attaches_input_skill_resolution_to_free_in():
    cli = load_cli()
    registry = cli.load_registry(cli.REGISTRY_PATH)

    response = cli.answer_router("branche les skills au terminal sans action automatique", registry)

    assert "input_skill_resolution" in response
    resolved = response["input_skill_resolution"]
    assert resolved["version"] == "OBSIDIA_TERMINAL_INPUT_SKILL_RESOLVER_V1_READONLY"
    assert resolved["mode"] == "READONLY_BACKGROUND_SUPPORT_NO_AUTHORITY"
    assert resolved["decision_authority"] == "KX108_ONLY"
    assert resolved["emits_act"] is False
    assert resolved["kernel_mutation"] is False
    assert resolved["memory_write"] is False
    assert resolved["resolved_route"] == "READONLY_WIRING"
    assert ".claude/skills/terminal-builder/SKILL.md" in resolved["selected_skills"]


def test_runtime_resolution_is_visible_in_status_and_tools_panels():
    cli = load_cli()
    registry = cli.load_registry(cli.REGISTRY_PATH)

    response = cli.answer_router("branche les skills au terminal sans action automatique", registry)

    etat = response["etat_technique"]
    outils = response["outils_panel"]

    assert etat["skill_resolver"] == "OBSIDIA_TERMINAL_INPUT_SKILL_RESOLVER_V1_READONLY"
    assert etat["skill_resolver_mode"] == "READONLY_BACKGROUND_SUPPORT_NO_AUTHORITY"
    assert etat["skill_resolver_authority"] == "NONE"
    assert etat["skill_resolver_exec"] == "forbidden"

    assert outils["input_skill_resolver"] == "readonly_advisory"
    assert "terminal-builder" in outils["skills_readonly"]
    assert outils["skill_policy"] == "advisory_only_no_subprocess_no_apply_no_act"


def test_surface_response_shows_runtime_skill_resolution():
    cli = load_cli()
    registry = cli.load_registry(cli.REGISTRY_PATH)

    response = cli.answer_router("branche les skills au terminal sans action automatique", registry)
    text = cli.format_surface_response(response)

    assert "skill_resolver" in text
    assert "OBSIDIA_TERMINAL_INPUT_SKILL_RESOLVER_V1_READONLY" in text
    assert "READONLY_BACKGROUND_SUPPORT_NO_AUTHORITY" in text
    assert "readonly_advisory" in text


def test_policy_denied_input_still_gets_advisory_skill_resolution_without_act():
    cli = load_cli()
    registry = cli.load_registry(cli.REGISTRY_PATH)

    response = cli.answer_router("commit et push le patch obsidure", registry)

    assert response["output"] == "POLICY_DENY"
    assert "input_skill_resolution" in response
    resolved = response["input_skill_resolution"]
    assert resolved["emits_act"] is False
    assert resolved["kernel_mutation"] is False
    assert resolved["memory_write"] is False
    assert response["etat_technique"]["skill_resolver_authority"] == "NONE"
