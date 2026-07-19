
from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CLI_PATH = REPO_ROOT / "scripts" / "obsidia_cli.py"


def load_cli():
    spec = importlib.util.spec_from_file_location("obsidia_cli_input_skill_resolver_test", CLI_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_input_skill_resolver_inventory_reads_existing_profiles():
    cli = load_cli()
    inventory = cli._skill_resolver_inventory_v1()
    paths = {item["path"] for item in inventory}

    assert ".claude/skills/agent-router-obsidia/SKILL.md" in paths
    assert ".claude/skills/proof-sentinel/SKILL.md" in paths
    assert "docs/protocols/OBSIDURE_APPLY_PROTOCOL.md" in paths
    assert "docs/protocols/OBSIDIA_OPERATOR_DOCTRINE.md" in paths


def test_input_skill_resolver_resolves_lean_without_authority():
    cli = load_cli()
    resolved = cli.resolve_terminal_input_with_skills_v1(
        "crée un théorème Lean périphérique avec Obsidure sans toucher au kernel"
    )

    assert resolved["version"] == "OBSIDIA_TERMINAL_INPUT_SKILL_RESOLVER_V1_READONLY"
    assert resolved["mode"] == "READONLY_BACKGROUND_SUPPORT_NO_AUTHORITY"
    assert resolved["decision_authority"] == "KX108_ONLY"
    assert resolved["emits_act"] is False
    assert resolved["kernel_mutation"] is False
    assert resolved["memory_write"] is False
    assert resolved["resolved_route"] == "LEAN_SANDBOX_OBSIDURE"
    assert ".claude/skills/proof-sentinel/SKILL.md" in resolved["selected_skills"]
    assert "docs/protocols/KERNEL_BOUNDARY_CHECK_PROTOCOL.md" in resolved["selected_protocols"]


def test_operator_task_card_uses_input_resolution_by_skills():
    cli = load_cli()
    card = cli.build_obsidure_operator_task_card_v1(
        "branche les skills au terminal sans action automatique"
    )

    assert "input_resolution" in card
    assert card["input_resolution"]["mode"] == "READONLY_BACKGROUND_SUPPORT_NO_AUTHORITY"
    assert card["input_resolution"]["emits_act"] is False
    assert card["input_resolution"]["kernel_mutation"] is False
    assert ".claude/skills/terminal-builder/SKILL.md" in card["skill_hints"]


def test_resolve_command_text_is_advisory_only():
    cli = load_cli()
    text = cli.format_terminal_input_resolution_v1(
        "branche les skills au terminal sans action automatique"
    )

    assert "OBSIDIA_TERMINAL_INPUT_SKILL_RESOLVER_V1_READONLY" in text
    assert "READONLY_BACKGROUND_SUPPORT_NO_AUTHORITY" in text
    assert "SKILLS CONSULTES EN READONLY" in text
    assert "no background execution" in text
    assert "no subprocess" in text
    assert "no apply" in text
    assert "no commit" in text
    assert "no push" in text


def test_operator_output_mentions_input_resolution_by_skills():
    cli = load_cli()
    text = cli.format_obsidure_operator_task_card_v1(
        "branche les skills au terminal sans action automatique"
    )

    assert "INPUT_RESOLUTION_BY_SKILLS:" in text
    assert "OBSIDIA_TERMINAL_INPUT_SKILL_RESOLVER_V1_READONLY" in text
    assert "authority=NONE_SKILLS_ARE_ADVISORY_ONLY" in text
