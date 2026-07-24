
from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CLI_PATH = REPO_ROOT / "scripts" / "obsidia_cli.py"


def load_cli():
    spec = importlib.util.spec_from_file_location("obsidia_cli_gate_planner_test", CLI_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_gate_planner_exists_and_is_advisory_only():
    cli = load_cli()
    assert hasattr(cli, "build_gate_plan_v1")
    plan = cli.build_gate_plan_v1(
        route="OBSIDURE",
        kind="PROPOSAL_PREP",
        domain="AUTO",
        selected_skills=[],
        selected_protocols=[],
        detected_layer="obsidure",
        output_predicted="COMMANDS",
    )
    assert plan["version"] == "OBSIDIA_TERMINAL_GATE_PLANNER_V1"
    assert plan["mode"] == "COMMANDS_ONLY_NO_EXECUTION"
    assert plan["authority"] == "NONE_GATE_PLANNER_IS_ADVISORY_ONLY"
    assert plan["decision_authority"] == "KX108_ONLY"
    assert plan["emits_act"] is False
    assert plan["emits_verdict"] is False
    assert plan["kernel_mutation"] is False
    assert plan["memory_write"] is False
    assert plan["auto_execution"] is False


def test_lean_route_proposes_lake_build_without_execution():
    cli = load_cli()
    plan = cli.build_gate_plan_v1(
        route="LEAN_SANDBOX_OBSIDURE",
        kind="LEAN_SANDBOX_PREP",
        domain="LEAN",
        selected_skills=[".claude/skills/proof-sentinel/SKILL.md"],
        selected_protocols=["docs/protocols/OBSIDURE_APPLY_PROTOCOL.md"],
        detected_layer="obsidure",
        output_predicted="COMMANDS",
    )
    assert plan["gate_family"] == "LEAN_PROOF"
    joined = " ".join(plan["required_checks"] + plan["recommended_commands"])
    assert "lake build" in joined
    assert "lean_manifest_guard" in joined or "obsidia_lean_manifest_guard" in joined
    assert plan["auto_execution"] is False


def test_obsidure_route_proposes_dry_run_and_forbids_apply_commit_push():
    cli = load_cli()
    plan = cli.build_gate_plan_v1(
        route="OBSIDURE",
        kind="PROPOSAL_PREP",
        domain="AUTO",
        selected_skills=[],
        selected_protocols=["docs/protocols/OBSIDURE_APPLY_PROTOCOL.md"],
        detected_layer="obsidure",
        output_predicted="COMMANDS",
    )
    assert plan["gate_family"] == "OBSIDURE_PROPOSAL"
    assert "--dry-run" in " ".join(plan["recommended_commands"]).lower()
    forbidden = " ".join(plan["forbidden_actions"]).lower()
    assert "apply" in forbidden
    assert "commit" in forbidden
    assert "push" in forbidden


def test_terminal_route_proposes_py_compile_pytest_and_forbidden_patterns():
    cli = load_cli()
    plan = cli.build_gate_plan_v1(
        route="READONLY_WIRING",
        kind="READONLY_WIRING_PREP",
        domain="AUTO",
        selected_skills=[".claude/skills/terminal-builder/SKILL.md"],
        selected_protocols=[],
        detected_layer="terminal",
        output_predicted="COMMANDS",
    )
    assert plan["gate_family"] == "TERMINAL_CLI"
    joined = " ".join(plan["required_checks"] + plan["recommended_commands"]).lower()
    assert "py_compile" in joined
    assert "pytest" in joined
    assert "forbidden" in joined


def test_brody_memory_route_is_readonly_non_sovereign():
    cli = load_cli()
    plan = cli.build_gate_plan_v1(
        route="MEMORY_SRL_SUPPORT",
        kind="READONLY_WIRING_PREP",
        domain="SRL",
        selected_skills=[],
        selected_protocols=[],
        detected_layer="brody",
        output_predicted="GUIDE",
    )
    assert plan["gate_family"] == "MEMORY_BRODY"
    assert plan["mode"] == "READONLY_CHECKS"
    joined = " ".join(plan["required_checks"] + plan["forbidden_actions"]).lower()
    assert "memory_write" in joined or "memory write" in joined
    assert "sovereign" in joined or "souverain" in joined or "décide" in joined or "décision" in joined


def test_sigma_domain_route_is_advisory_only_and_no_act():
    cli = load_cli()
    plan = cli.build_gate_plan_v1(
        route="BANK_DOMAIN_SUPPORT",
        kind="DOMAIN_SUPPORT",
        domain="BANK",
        selected_skills=[],
        selected_protocols=[],
        detected_layer="sigma",
        output_predicted="EXECUTE",
    )
    assert plan["gate_family"] == "SIGMA_OIE_DOMAINS"
    assert plan["mode"] == "READONLY_CHECKS"
    joined = " ".join(plan["required_checks"] + plan["forbidden_actions"]).upper()
    assert "ALLOW" in joined
    assert "BLOCK" in joined
    assert "HOLD" in joined
    assert "ACT" in joined


def test_policy_deny_family_forbids_mutations():
    cli = load_cli()
    plan = cli.build_gate_plan_v1(
        route="OBSIDURE",
        kind="PROPOSAL_PREP",
        domain="AUTO",
        selected_skills=[],
        selected_protocols=[],
        detected_layer="obsidure",
        output_predicted="POLICY_DENY",
    )
    assert plan["gate_family"] == "POLICY_DENIED"
    assert plan["mode"] == "POLICY_ONLY"
    forbidden = " ".join(plan["forbidden_actions"]).lower()
    assert "apply" in forbidden
    assert "commit" in forbidden
    assert "push" in forbidden


def test_skill_resolver_includes_gate_plan():
    cli = load_cli()
    resolved = cli.resolve_terminal_input_with_skills_v1("crée un théorème lean")
    assert "gate_plan" in resolved
    assert resolved["gate_plan"]["version"] == "OBSIDIA_TERMINAL_GATE_PLANNER_V1"
    assert resolved["gate_plan"]["authority"] == "NONE_GATE_PLANNER_IS_ADVISORY_ONLY"


def test_active_plan_contains_gate_plan_and_displays_it():
    cli = load_cli()
    registry = cli.load_registry(cli.REGISTRY_PATH)
    plan = cli.build_active_plan("obsidure prépare un patch lean", registry)
    assert "gate_plan" in plan
    assert plan["gate_plan"]["version"] == "OBSIDIA_TERMINAL_GATE_PLANNER_V1"

    text = cli.format_active_plan(plan)
    assert "GATE_PLAN:" in text
    assert "OBSIDIA_TERMINAL_GATE_PLANNER_V1" in text
    assert "NONE_GATE_PLANNER_IS_ADVISORY_ONLY" in text


def test_route_and_tools_views_display_gate_plan():
    cli = load_cli()
    registry = cli.load_registry(cli.REGISTRY_PATH)
    plan = cli.build_active_plan("branche obsidure au terminal sans action automatique", registry)

    route_text = cli.format_route_view(plan)
    tools_text = cli.format_tools_view(plan)

    assert "GATE_PLAN:" in route_text
    assert "NONE_GATE_PLANNER_IS_ADVISORY_ONLY" in route_text
    assert "GATE_PLAN:" in tools_text
    assert "required_checks" in tools_text
    assert "recommended_commands" in tools_text


def test_runtime_normal_in_contains_gate_plan_and_surface_displays_gates_panel():
    cli = load_cli()
    registry = cli.load_registry(cli.REGISTRY_PATH)
    response = cli.answer_router("branche obsidure au terminal sans action automatique", registry)
    assert "gate_plan" in response
    assert response["gate_plan"]["version"] == "OBSIDIA_TERMINAL_GATE_PLANNER_V1"
    assert response["gate_plan"]["auto_execution"] is False

    text = cli.format_surface_response(response)
    assert "GATES_PANEL:" in text
    assert "GATE_PLAN:" in text
    assert "NONE_GATE_PLANNER_IS_ADVISORY_ONLY" in text


def test_operator_task_card_contains_gate_plan():
    cli = load_cli()
    card = cli.build_obsidure_operator_task_card_v1("prépare un patch lean")
    assert "gate_plan" in card
    assert card["gate_plan"]["version"] == "OBSIDIA_TERMINAL_GATE_PLANNER_V1"
    assert card["gate_plan"]["auto_execution"] is False

    text = cli.format_obsidure_operator_task_card_v1(card)
    assert "GATE_PLAN:" in text
    assert "NONE_GATE_PLANNER_IS_ADVISORY_ONLY" in text


def test_handle_plan_command_gates_with_arg_returns_gate_plan():
    cli = load_cli()
    registry = cli.load_registry(cli.REGISTRY_PATH)
    text, receipt, plan = cli.handle_plan_command(
        "gates",
        "obsidure prépare un patch lean",
        registry,
    )
    assert receipt is not None
    assert plan is not None
    assert "gate_plan" in receipt
    assert "OBSIDIA_GATE_PLAN:" in text
    assert "OBSIDIA_TERMINAL_GATE_PLANNER_V1" in text


def test_extract_gates_panel_returns_lines():
    cli = load_cli()
    registry = cli.load_registry(cli.REGISTRY_PATH)
    response = cli.answer_router("obsidure prépare un patch lean", registry)
    lines = cli.extract_gates_panel(response)
    assert isinstance(lines, list)
    assert any("GATE_PLAN" in line for line in lines)
    assert any("OBSIDIA_TERMINAL_GATE_PLANNER_V1" in line for line in lines)


def test_policy_denied_active_plan_keeps_gate_planner_advisory():
    cli = load_cli()
    registry = cli.load_registry(cli.REGISTRY_PATH)
    plan = cli.build_active_plan("commit et push le patch obsidure", registry)
    assert plan["output_predicted"] == "POLICY_DENY"
    assert plan["gate_plan"]["gate_family"] == "POLICY_DENIED"
    assert plan["gate_plan"]["auto_execution"] is False

    text = cli.format_active_plan(plan)
    assert "POLICY_DENY" in text
    assert "commit" in text.lower()
    assert "push" in text.lower()
    assert "NONE_GATE_PLANNER_IS_ADVISORY_ONLY" in text
