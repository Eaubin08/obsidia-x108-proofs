from __future__ import annotations

import importlib.util
import json
import urllib.error
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CLI_PATH = ROOT / "scripts" / "obsidia_cli.py"


def load_cli():
    spec = importlib.util.spec_from_file_location("obsidia_cli_dynamic_panels_test", CLI_PATH)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def registry():
    return {
        "layers": {
            "brody": {"mode": "commands", "commands": [], "triggers": ["brody"]},
            "obsidure": {"mode": "commands", "commands": [], "triggers": ["obsidure", "patch", "code"]},
        },
        "policy": {
            "deny_keywords": ["commit", "push", "apply", "deploy", "delete"],
            "deny_message": "DENY TEST",
        },
        "health_endpoints": {
            "api_health": "http://127.0.0.1:8000/api/health",
        },
        "receipt_path": ".local_obsidia/receipts/obsidia_terminal_receipts.jsonl",
    }


def make_obsidure_repo(tmp_path: Path) -> Path:
    root = tmp_path
    proposals = root / "_PATCH_PROPOSALS"
    proposals.mkdir()
    p = proposals / "p-new"
    p.mkdir()
    (p / "proposal.json").write_text(json.dumps({
        "created_at": "2026-07-01T02:00:00+00:00",
        "status": "AWAITING_HUMAN_APPROVED_WRITE",
        "files": ["scripts/obsidia_cli.py"],
    }), encoding="utf-8")
    (p / "RECEIPT.md").write_text("# Receipt\nOK\n", encoding="utf-8")
    return root


def test_choose_dynamic_tab_by_layer():
    mod = load_cli()
    assert mod.choose_dynamic_right_tab_v1({"detected_layer": "brody"}) == "STATUS"
    assert mod.choose_dynamic_right_tab_v1({"detected_layer": "obsidure"}) == "TOOLS"
    assert mod.choose_dynamic_right_tab_v1({"detected_layer": "reverse"}) == "PLAN"
    assert mod.choose_dynamic_right_tab_v1({"detected_layer": "policy", "output": "POLICY_DENY"}) == "TOOLS"
    assert mod.choose_dynamic_right_tab_v1({"detected_layer": "terminal"}) == "STATUS"
    assert mod.choose_dynamic_right_tab_v1({"detected_layer": "obsidienne"}) == "PROOF"


def test_attach_dynamic_panels_metadata():
    mod = load_cli()
    response = mod.attach_dynamic_panels_v1({
        "detected_layer": "brody",
        "etat_technique": {},
    })
    assert response["dynamic_right_tab"] == "STATUS"
    assert response["dynamic_panels"]["version"] == "DYNAMIC_PANELS_AFTER_CORE_V1"
    assert response["dynamic_panels"]["available"] == ["PLAN", "STATUS", "TOOLS", "PROOF"]
    assert response["dynamic_panels"]["subprocess"] == "none"
    assert response["dynamic_panels"]["decision_authority"] == "KX108_ONLY"
    assert response["etat_technique"]["dynamic_right_tab"] == "STATUS"


def test_brody_answer_gets_status_tab(monkeypatch):
    mod = load_cli()

    def fake_urlopen(req, timeout=0):
        raise urllib.error.URLError("down")

    monkeypatch.setattr(mod.urllib.request, "urlopen", fake_urlopen)
    response = mod.answer_router("brody explique le contexte", registry())
    assert response["detected_layer"] == "brody"
    assert response["dynamic_right_tab"] == "STATUS"
    assert response["dynamic_panels"]["version"] == "DYNAMIC_PANELS_AFTER_CORE_V1"


def test_obsidure_answer_gets_tools_tab(monkeypatch, tmp_path):
    mod = load_cli()
    monkeypatch.setattr(mod, "REPO_ROOT", make_obsidure_repo(tmp_path))
    response = mod.answer_router("obsidure status", registry())
    assert response["detected_layer"] == "obsidure"
    assert response["dynamic_right_tab"] == "TOOLS"
    assert response["outils_panel"]["apply"] == "forbidden"


def test_reverse_answer_gets_plan_tab():
    mod = load_cli()
    response = mod.answer_router("suite", registry())
    assert response["detected_layer"] == "reverse"
    assert response["dynamic_right_tab"] == "PLAN"


def test_policy_deny_gets_tools_tab():
    mod = load_cli()
    response = mod.answer_router("commit le kernel", registry())
    assert response["output"] == "POLICY_DENY"
    assert response["dynamic_right_tab"] == "TOOLS"
    assert response["dynamic_panels"]["mutation"] == "none"


def test_ir_answer_gets_status_tab():
    mod = load_cli()
    response = mod.answer_router("traduit ma demande en langage uni", registry())
    assert response["detected_layer"] == "terminal"
    assert response["dynamic_right_tab"] == "STATUS"


def test_extract_plan_panel_honors_dynamic_tabs(monkeypatch, tmp_path):
    mod = load_cli()
    monkeypatch.setattr(mod, "REPO_ROOT", make_obsidure_repo(tmp_path))
    response = mod.answer_router("obsidure status", registry())
    lines = mod.extract_plan_panel(response, response["dynamic_right_tab"])
    assert lines[0] == "=== TOOLS ==="
    rendered = "\n".join(lines)
    assert "apply" in rendered.lower()


def test_dynamic_panels_segment_has_no_subprocess():
    src = CLI_PATH.read_text(encoding="utf-8")
    segment = src.split("OBSIDIA_TERMINAL_DYNAMIC_PANELS_AFTER_CORE_V1", 1)[1]
    segment = segment.split("FIN DYNAMIC PANELS AFTER CORE V1", 1)[0]
    assert "import subprocess" not in segment
    assert "subprocess.run" not in segment
    assert "os.system" not in segment
