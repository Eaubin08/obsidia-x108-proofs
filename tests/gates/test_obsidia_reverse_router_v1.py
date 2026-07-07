
from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CLI_PATH = ROOT / "scripts" / "obsidia_cli.py"


def load_cli():
    spec = importlib.util.spec_from_file_location("obsidia_cli_reverse_test", CLI_PATH)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def registry():
    return {
        "layers": {},
        "policy": {},
        "receipt_path": ".local_obsidia/receipts/obsidia_terminal_receipts.jsonl",
    }


def test_reverse_trigger_words():
    mod = load_cli()
    for raw in ["suite", "continue", "reprendre", "reprendre le plan", "next", "on continue"]:
        assert mod.detect_reverse_router_query(raw, mod.normalize(raw)) is True


def test_reverse_router_direct_response_no_context_safe():
    mod = load_cli()
    response = mod.build_reverse_router_response("suite", registry())
    assert response["detected_layer"] == "reverse"
    assert response["mode_reponse"] == "ANSWER_LOCAL"
    assert response["output"] == "GUIDE"
    assert response["etat_technique"]["mutation"] == "none"
    assert response["etat_technique"]["subprocess"] == "none"
    assert response["proof_panel"]["decision_authority"] == "KX108_ONLY"


def test_answer_router_uses_reverse_before_unknown():
    mod = load_cli()
    response = mod.answer_router("suite", registry())
    assert response["detected_layer"] == "reverse"
    assert response["output"] == "GUIDE"
    assert response.get("output") != "STOP_UNKNOWN"
    assert "Suites possibles" in response["reponse"]


def test_continue_and_reprendre_do_not_fall_unknown():
    mod = load_cli()
    for raw in ["continue", "reprendre le plan", "next"]:
        response = mod.answer_router(raw, registry())
        assert response["detected_layer"] == "reverse"
        assert response["etat_technique"]["reverse_status"] in {
            "NO_CONTEXT",
            "CONTEXT_PARTIAL",
            "CONTEXT_FOUND",
        }


def test_reverse_surfaces_are_separated():
    mod = load_cli()
    response = mod.build_reverse_router_response("suite", registry())
    assert "main_answer" in response
    assert "etat_technique" in response
    assert "outils_panel" in response
    assert "proof_panel" in response
    assert response["outils_panel"]["reverse_router"] == "used"
    assert response["outils_panel"]["network"] == "none"


def test_reverse_does_not_emit_executable_mutation_action():
    mod = load_cli()
    response = mod.build_reverse_router_response("suite", registry())
    rendered = json.dumps(response, ensure_ascii=False).lower()
    forbidden_executable_fragments = [
        "git commit",
        "git push",
        "deploy",
        "apply gated",
        "--apply",
        "--deploy",
    ]
    for fragment in forbidden_executable_fragments:
        assert fragment not in rendered


def test_reverse_code_has_no_subprocess_import():
    src = CLI_PATH.read_text(encoding="utf-8")
    segment = src.split("OBSIDIA_TERMINAL_REVERSE_ROUTER_V1", 1)[1]
    segment = segment.split("FIN TERMINAL REVERSE ROUTER V1", 1)[0]
    assert "import subprocess" not in segment
    assert "subprocess.run" not in segment
    assert "os.system" not in segment

def test_reverse_does_not_steal_nl_plan_questions():
    mod = load_cli()
    for raw in [
        "c'est quoi la suite",
        "prepare la suite sans modifier",
        "qu'est-ce que je dois faire maintenant",
        "prochaine etape",
    ]:
        assert mod.detect_reverse_router_query(raw, mod.normalize(raw)) is False
