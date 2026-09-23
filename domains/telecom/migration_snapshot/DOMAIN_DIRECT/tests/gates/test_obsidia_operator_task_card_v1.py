"""Tests for OBSIDIA_TERMINAL_OPERATOR_TASK_CARD_V1_SAFE."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "scripts" / "obsidia_cli.py"


def load_cli():
    spec = importlib.util.spec_from_file_location("obsidia_cli_operator_task_card_v1", CLI)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_operator_task_card_lean_domain_and_dry_run():
    cli = load_cli()
    out = cli.format_obsidure_operator_task_card_v1(
        "crée un nouveau théorème Lean périphérique Obsidia sans toucher le kernel"
    )
    assert "OBSIDIA OPERATOR TASK CARD" in out
    assert "OBSIDIA_TERMINAL_OPERATOR_TASK_CARD_V1_SAFE" in out
    assert "MODE: COMMANDS_ONLY" in out
    assert "domain=LEAN" in out
    assert "scripts/obsidure_cli.py" in out
    assert "--domain LEAN" in out
    assert "--dry-run" in out
    assert "kernel_mutation=False" in out
    assert "x108_mutation=False" in out


def test_operator_task_card_wiring_scope():
    cli = load_cli()
    out = cli.format_obsidure_operator_task_card_v1(
        "branche une couche readonly entre Brody et Obsidure"
    )
    assert "READONLY_WIRING_PREP" in out
    assert "scripts/obsidia_cli.py" in out
    assert "scripts/obsidia_registry.yaml" in out
    assert "no automatic apply" in out
    assert "no automatic commit" in out
    assert "no automatic push" in out


def test_operator_block_has_no_process_or_git_execution_calls():
    src = CLI.read_text(encoding="utf-8")
    block = src.split("OBSIDIA_TERMINAL_OPERATOR_TASK_CARD_V1_SAFE", 1)[1]
    block = block.split("def main(argv: list[str]) -> int:", 1)[0]
    forbidden = [
        "import subprocess",
        "subprocess.",
        "os.system",
        "Start-Process",
        "check_call",
        "check_output",
    ]
    for token in forbidden:
        assert token not in block, token


def test_operator_task_card_enriched_objective_and_skills():
    cli = load_cli()
    out = cli.format_obsidure_operator_task_card_v1(
        "crée un nouveau théorème Lean périphérique Obsidia sans toucher le kernel"
    )
    assert "Objectif : LEAN_SANDBOX" in out
    assert "OBJECTIVE ENRICHI POUR OBSIDURE" in out
    assert ".claude/skills/proof-sentinel/SKILL.md" in out
    assert "docs/protocols/OBSIDURE_APPLY_PROTOCOL.md" in out
    assert "HUMAN_APPROVED_WRITE" in out
