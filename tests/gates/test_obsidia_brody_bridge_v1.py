
from __future__ import annotations

import importlib.util
import json
import urllib.error
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CLI_PATH = ROOT / "scripts" / "obsidia_cli.py"


def load_cli():
    spec = importlib.util.spec_from_file_location("obsidia_cli_brody_bridge_test", CLI_PATH)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def registry():
    return {
        "layers": {
            "brody": {
                "mode": "commands",
                "commands": [],
                "triggers": ["brody", "contexte", "synthese"],
            }
        },
        "policy": {},
        "health_endpoints": {
            "api_health": "http://127.0.0.1:8000/api/health",
        },
        "receipt_path": ".local_obsidia/receipts/obsidia_terminal_receipts.jsonl",
    }


def test_brody_bridge_detects_explicit_queries():
    mod = load_cli()
    for raw in ["brody", "brody explique le contexte", "explique moi obsidia"]:
        assert mod.detect_brody_bridge_query(raw, mod.normalize(raw)) is True


def test_brody_payload_is_readonly_advisory():
    mod = load_cli()
    payload = mod.build_brody_bridge_payload("brody explique", registry())
    assert payload["message"] == "brody explique"
    assert payload["language"] == "fr"
    assert payload["session_id"] == "obsidia-terminal"
    assert payload["allow_provider"] is False
    assert payload["allow_memory_candidate"] is False
    assert payload["allow_manual_apply"] is False
    assert payload["compact"] is True
    assert payload["debug"] is False


def test_brody_extract_answer_priority():
    mod = load_cli()
    answer, source = mod.extract_brody_bridge_answer({
        "response": "r",
        "response_md": "md",
        "final_answer": "final",
    })
    assert answer == "final"
    assert source == "final_answer"


def test_brody_bridge_api_up(monkeypatch):
    mod = load_cli()

    class DummyResponse:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return json.dumps({
                "final_answer": "Réponse Brody live",
                "decision_authority": "KX108_ONLY",
            }).encode("utf-8")

    def fake_urlopen(req, timeout=0):
        assert req.get_method() == "POST"
        assert "/api/brody/chat" in req.full_url
        return DummyResponse()

    monkeypatch.setattr(mod.urllib.request, "urlopen", fake_urlopen)

    response = mod.build_brody_bridge_response("brody explique le contexte", registry())
    assert response["detected_layer"] == "brody"
    assert response["mode_reponse"] == "ANSWER_BRODY"
    assert response["etat_technique"]["brody_status"] == "UP"
    assert response["etat_technique"]["answer_source"] == "final_answer"
    assert response["proof_panel"]["decision_authority"] == "KX108_ONLY"
    assert response["proof_panel"]["brody_decides"] is False
    assert "Réponse Brody live" in response["reponse"]


def test_brody_bridge_api_down_fallback(monkeypatch):
    mod = load_cli()

    def fake_urlopen(req, timeout=0):
        raise urllib.error.URLError("down")

    monkeypatch.setattr(mod.urllib.request, "urlopen", fake_urlopen)

    response = mod.build_brody_bridge_response("brody explique le contexte", registry())
    assert response["detected_layer"] == "brody"
    assert response["mode_reponse"] == "ANSWER_LOCAL"
    assert response["output"] == "GUIDE"
    assert response["etat_technique"]["brody_status"] == "DOWN"
    assert response["etat_technique"]["fallback"] is True
    assert response["etat_technique"]["mutation"] == "none"
    assert response["etat_technique"]["subprocess"] == "none"
    assert response["proof_panel"]["emits_act"] is False


def test_answer_router_uses_brody_bridge(monkeypatch):
    mod = load_cli()

    def fake_urlopen(req, timeout=0):
        raise urllib.error.URLError("down")

    monkeypatch.setattr(mod.urllib.request, "urlopen", fake_urlopen)

    response = mod.answer_router("brody explique le contexte", registry())
    assert response["detected_layer"] == "brody"
    assert response["etat_technique"]["brody_bridge"] == "used"
    assert response["output"] == "GUIDE"


def test_brody_bridge_has_separated_surfaces(monkeypatch):
    mod = load_cli()

    def fake_urlopen(req, timeout=0):
        raise urllib.error.URLError("down")

    monkeypatch.setattr(mod.urllib.request, "urlopen", fake_urlopen)

    response = mod.build_brody_bridge_response("brody explique", registry())
    assert "main_answer" in response
    assert "etat_technique" in response
    assert "outils_panel" in response
    assert "proof_panel" in response
    assert response["outils_panel"]["decision"] == "forbidden"
    assert response["outils_panel"]["memory_write"] == "forbidden"


def test_brody_bridge_segment_has_no_subprocess():
    src = CLI_PATH.read_text(encoding="utf-8")
    segment = src.split("OBSIDIA_TERMINAL_BRODY_BRIDGE_V1", 1)[1]
    segment = segment.split("FIN TERMINAL BRODY BRIDGE V1", 1)[0]
    assert "import subprocess" not in segment
    assert "subprocess.run" not in segment
    assert "os.system" not in segment
