
from __future__ import annotations

import importlib.util
import json
import urllib.error
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CLI_PATH = ROOT / "scripts" / "obsidia_cli.py"


def load_cli():
    spec = importlib.util.spec_from_file_location("obsidia_cli_surface_composer_test", CLI_PATH)
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


def assert_core_surfaces(response: dict):
    assert response["surface_composer"] == "CORE_SURFACE_COMPOSER_V1"
    assert "main_answer" in response
    assert "etat_technique" in response
    assert "outils_panel" in response
    assert "proof_panel" in response
    assert response["etat_technique"]["surface_composer"] == "CORE_SURFACE_COMPOSER_V1"
    assert response["etat_technique"]["decision_authority"] == "KX108_ONLY"
    assert response["etat_technique"]["mutation"] in ("none", "forbidden")
    assert response["etat_technique"]["subprocess"] == "none"
    assert response["proof_panel"]["decision_authority"] == "KX108_ONLY"
    assert response["proof_panel"]["authority"] == "NONE"


def test_composer_fills_missing_surfaces():
    mod = load_cli()
    response = mod.compose_core_surfaces_v1({
        "reponse": "hello",
        "detected_layer": "terminal",
        "mode_reponse": "ANSWER_LOCAL",
        "output": "GUIDE",
    }, "hello", registry())
    assert_core_surfaces(response)
    assert response["main_answer"]["direct"] == "hello"


def test_unified_ir_is_composed():
    mod = load_cli()
    response = mod.answer_router("traduit ma demande en langage uni", registry())
    assert response["detected_layer"] == "terminal"
    assert_core_surfaces(response)


def test_reverse_router_is_composed():
    mod = load_cli()
    response = mod.answer_router("suite", registry())
    assert response["detected_layer"] == "reverse"
    assert_core_surfaces(response)


def test_brody_bridge_is_composed(monkeypatch):
    mod = load_cli()

    def fake_urlopen(req, timeout=0):
        raise urllib.error.URLError("down")

    monkeypatch.setattr(mod.urllib.request, "urlopen", fake_urlopen)
    response = mod.answer_router("brody explique le contexte", registry())
    assert response["detected_layer"] == "brody"
    assert_core_surfaces(response)
    assert response["proof_panel"]["brody_decides"] is False


def test_obsidure_bridge_is_composed(monkeypatch, tmp_path):
    mod = load_cli()
    monkeypatch.setattr(mod, "REPO_ROOT", make_obsidure_repo(tmp_path))
    response = mod.answer_router("obsidure status", registry())
    assert response["detected_layer"] == "obsidure"
    assert_core_surfaces(response)
    assert response["outils_panel"]["apply"] == "forbidden"
    assert response["outils_panel"]["commit"] == "forbidden"
    assert response["outils_panel"]["push"] == "forbidden"


def test_policy_deny_is_composed():
    mod = load_cli()
    response = mod.answer_router("commit le kernel", registry())
    assert response["output"] == "POLICY_DENY"
    assert response["plan_status"] == "DENIED"
    assert_core_surfaces(response)
    assert response["etat_technique"]["mutation"] == "forbidden"


def test_composer_segment_has_no_subprocess():
    src = CLI_PATH.read_text(encoding="utf-8")
    segment = src.split("OBSIDIA_TERMINAL_CORE_SURFACE_COMPOSER_V1", 1)[1]
    segment = segment.split("FIN CORE SURFACE COMPOSER V1", 1)[0]
    assert "import subprocess" not in segment
    assert "subprocess.run" not in segment
    assert "os.system" not in segment

def test_local_read_secret_density_guard_blocks_dense_file(monkeypatch, tmp_path):
    mod = load_cli()
    root = tmp_path
    docs = root / "docs"
    docs.mkdir()
    dense = docs / "dense.md"
    dense.write_text("\n".join("password = X" for _ in range(20)), encoding="utf-8")
    monkeypatch.setattr(mod, "REPO_ROOT", root)

    result = mod.classify_local_read_intent("lis docs/dense.md", "lis docs/dense.md")
    assert result["mode"] == "ANSWER_POLICY_DENY"
    assert result["reason"] == "SECRET_DENSITY_GUARD"
    assert result["output"] == "POLICY_DENY"
