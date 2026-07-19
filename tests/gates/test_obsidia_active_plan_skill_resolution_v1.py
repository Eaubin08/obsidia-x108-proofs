
from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CLI_PATH = REPO_ROOT / "scripts" / "obsidia_cli.py"


def load_cli():
    spec = importlib.util.spec_from_file_location("obsidia_cli_active_plan_skill_resolution_test", CLI_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_active_plan_contains_readonly_skill_resolution():
    cli = load_cli()
    registry = cli.load_registry(cli.REGISTRY_PATH)

    plan = cli.build_active_plan("branche obsidure au terminal sans action automatique", registry)

    assert "input_skill_resolution" in plan
    resolved = plan["input_skill_resolution"]
    assert resolved["version"] == "OBSIDIA_TERMINAL_INPUT_SKILL_RESOLVER_V1_READONLY"
    assert resolved["mode"] == "READONLY_BACKGROUND_SUPPORT_NO_AUTHORITY"
    assert resolved["decision_authority"] == "KX108_ONLY"
    assert resolved["emits_act"] is False
    assert resolved["kernel_mutation"] is False
    assert resolved["memory_write"] is False
    assert resolved["resolved_route"] == "READONLY_WIRING"
    assert ".claude/skills/terminal-builder/SKILL.md" in resolved["selected_skills"]


def test_plan_route_and_tools_views_display_skill_resolution():
    cli = load_cli()
    registry = cli.load_registry(cli.REGISTRY_PATH)
    plan = cli.build_active_plan("branche obsidure au terminal sans action automatique", registry)

    plan_text = cli.format_active_plan(plan)
    route_text = cli.format_route_view(plan)
    tools_text = cli.format_tools_view(plan)

    for text in (plan_text, route_text):
        assert "INPUT_SKILL_RESOLUTION:" in text
        assert "OBSIDIA_TERMINAL_INPUT_SKILL_RESOLVER_V1_READONLY" in text
        assert "READONLY_BACKGROUND_SUPPORT_NO_AUTHORITY" in text
        assert "input_skill_resolver=readonly_advisory" in text
        assert "authority=NONE_SKILLS_ARE_ADVISORY_ONLY" in text
        assert "subprocess=forbidden" in text
        assert "act_emission=forbidden" in text

    assert "SKILLS CONSULTATIFS READONLY:" in tools_text
    assert "PROTOCOLES CONSULTATIFS READONLY:" in tools_text
    assert ".claude/skills/terminal-builder/SKILL.md" in tools_text


def test_handle_plan_command_receipt_contains_skill_resolution():
    cli = load_cli()
    registry = cli.load_registry(cli.REGISTRY_PATH)

    text, receipt, plan = cli.handle_plan_command(
        "plan",
        "branche obsidure au terminal sans action automatique",
        registry,
    )

    assert receipt is not None
    assert plan is not None
    assert "input_skill_resolution" in receipt
    assert receipt["input_skill_resolution"]["mode"] == "READONLY_BACKGROUND_SUPPORT_NO_AUTHORITY"
    assert "INPUT_SKILL_RESOLUTION:" in text


def test_policy_denied_plan_keeps_skills_advisory_only():
    cli = load_cli()
    registry = cli.load_registry(cli.REGISTRY_PATH)

    plan = cli.build_active_plan("commit et push le patch obsidure", registry)
    text = cli.format_active_plan(plan)

    assert plan["output_predicted"] == "POLICY_DENY"
    assert plan["input_skill_resolution"]["emits_act"] is False
    assert plan["input_skill_resolution"]["kernel_mutation"] is False
    assert plan["input_skill_resolution"]["memory_write"] is False
    assert "authority=NONE_SKILLS_ARE_ADVISORY_ONLY" in text
    assert "commit=forbidden" in text
    assert "push=forbidden" in text
    assert "act_emission=forbidden" in text
