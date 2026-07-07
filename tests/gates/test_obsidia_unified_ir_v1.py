"""test_obsidia_unified_ir_v1 — OS Langage Uni / UnifiedInputIR V1.

Scope:
- Pure local IR.
- No subprocess.
- No mutation.
- Does not replace X108.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLI_PATH = ROOT / "scripts" / "obsidia_cli.py"

spec = importlib.util.spec_from_file_location("obsidia_cli", CLI_PATH)
cli = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(cli)


def _ir(text: str) -> dict:
    return cli.normalize_unified_input(text, {})


def test_01_unified_ir_functions_exist() -> None:
    assert hasattr(cli, "normalize_unified_input")
    assert hasattr(cli, "format_unified_ir")
    assert hasattr(cli, "detect_unified_ir_query")
    assert hasattr(cli, "build_unified_ir_response")


def test_02_explique_obsidia_routes_to_brody_question() -> None:
    ir = _ir("explique moi Obsidia")
    assert ir["intent_type"] == "question"
    assert ir["action_type"] == "answer"
    assert ir["needs"]["brody"] is True
    assert ir["risk_level"] == "low"


def test_03_code_request_routes_to_obsidure() -> None:
    ir = _ir("peux tu coder une correction")
    assert ir["intent_type"] == "code_request"
    assert ir["target_layer"] == "obsidure"
    assert ir["action_type"] == "commands"
    assert ir["needs"]["obsidure"] is True
    assert ir["needs"]["x108_gate"] is True


def test_04_suite_routes_to_reverse_plan() -> None:
    ir = _ir("suite")
    assert ir["intent_type"] == "plan"
    assert ir["target_layer"] == "reverse"
    assert ir["needs"]["reverse"] is True


def test_05_reverse_request_routes_to_reverse() -> None:
    ir = _ir("reverse ce que je veux faire")
    assert ir["target_layer"] == "reverse"
    assert ir["needs"]["reverse"] is True


def test_06_langage_uni_request_detected() -> None:
    raw = "traduit ma demande en langage uni"
    assert cli.detect_unified_ir_query(raw, cli.normalize(raw)) is True
    resp = cli.build_unified_ir_response(raw, {})
    assert "UnifiedInputIR" in resp["reponse"]
    assert resp["etat_technique"]["target_layer"] == "terminal"


def test_07_sigma_routes_to_audit_proof() -> None:
    ir = _ir("sigma coherence")
    assert ir["intent_type"] == "audit"
    assert ir["target_layer"] == "sigma"
    assert ir["needs"]["proof"] is True


def test_08_lean_routes_to_proof() -> None:
    ir = _ir("preuves lean")
    assert ir["target_layer"] == "lean"
    assert ir["needs"]["proof"] is True


def test_09_domains_routes_to_domains() -> None:
    ir = _ir("domains bank trading gps")
    assert ir["target_layer"] == "domains"


def test_10_stack_active_routes_to_live_status() -> None:
    ir = _ir("tout est actif ?")
    assert ir["intent_type"] == "status"
    assert ir["target_layer"] == "live"
    assert ir["action_type"] == "status"


def test_11_deny_words_raise_high_risk() -> None:
    ir = _ir("commit le patch")
    assert ir["action_type"] == "deny"
    assert ir["risk_level"] == "high"
    assert "no_auto_commit" in ir["constraints"]


def test_12_unknown_has_missing_context() -> None:
    ir = _ir("blabla incomplet")
    assert ir["intent_type"] == "unknown"
    assert ir["needs"]["reverse"] is True
    assert ir["missing"]


def test_13_format_unified_ir_is_human_readable() -> None:
    txt = cli.format_unified_ir(_ir("peux tu coder une correction"))
    assert "intent_type" in txt
    assert "target_layer" in txt
    assert "needs" in txt


def test_14_answer_router_exposes_ir_on_explicit_request() -> None:
    resp = cli.answer_router("traduit ma demande en langage uni", {})
    assert resp["mode_reponse"] == "ANSWER_LOCAL"
    assert resp["detected_layer"] == "terminal"
    assert "UnifiedInputIR" in resp["reponse"]
    assert "etat_technique" in resp
    assert "outils_panel" in resp


def test_15_main_answer_has_no_surface_filter_tokens() -> None:
    resp = cli.answer_router("traduit ma demande en langage uni", {})
    lines = cli.extract_main_answer_panel(resp)
    combined = "\n".join(lines)
    for forbidden in cli._SURFACE_FILTER_TOKENS:
        assert forbidden not in combined


def test_16_no_subprocess_import_added() -> None:
    src = CLI_PATH.read_text(encoding="utf-8")
    # Le lot IR ne doit pas ajouter d'import subprocess.
    assert "import subprocess" not in src
