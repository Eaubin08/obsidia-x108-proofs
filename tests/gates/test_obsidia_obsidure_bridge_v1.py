
from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CLI_PATH = ROOT / "scripts" / "obsidia_cli.py"


def load_cli():
    spec = importlib.util.spec_from_file_location("obsidia_cli_obsidure_bridge_test", CLI_PATH)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def registry():
    return {
        "layers": {
            "obsidure": {
                "mode": "commands",
                "commands": [],
                "triggers": ["obsidure", "patch", "code"],
            }
        },
        "policy": {},
        "receipt_path": ".local_obsidia/receipts/obsidia_terminal_receipts.jsonl",
    }


def make_repo(tmp_path: Path) -> Path:
    root = tmp_path
    proposals = root / "_PATCH_PROPOSALS"
    proposals.mkdir()

    p1 = proposals / "p-old"
    p1.mkdir()
    (p1 / "proposal.json").write_text(json.dumps({
        "created_at": "2026-07-01T01:00:00+00:00",
        "status": "AWAITING_HUMAN_APPROVED_WRITE",
        "objective": "old objective",
        "patches": [{"path": "scripts/a.py"}],
    }), encoding="utf-8")
    (p1 / "RECEIPT.md").write_text("# Old\nstatus old\n", encoding="utf-8")

    p2 = proposals / "p-new"
    p2.mkdir()
    (p2 / "proposal.json").write_text(json.dumps({
        "created_at": "2026-07-01T02:00:00+00:00",
        "status": "AWAITING_HUMAN_APPROVED_WRITE",
        "objective": "new objective",
        "files": ["scripts/obsidia_cli.py"],
    }), encoding="utf-8")
    (p2 / "RECEIPT.md").write_text("# New\nstatus new\nscope ok\n", encoding="utf-8")

    (root / "scripts" / "gates").mkdir(parents=True)
    return root


def test_obsidure_bridge_detects_queries():
    mod = load_cli()
    for raw in ["obsidure", "obsidure status", "obsidure latest", "obsidure gates", "peux tu coder"]:
        assert mod.detect_obsidure_bridge_query(raw, mod.normalize(raw)) is True


def test_collect_obsidure_state_reads_latest(monkeypatch, tmp_path):
    mod = load_cli()
    root = make_repo(tmp_path)
    monkeypatch.setattr(mod, "REPO_ROOT", root)

    state = mod.collect_obsidure_bridge_state_v1(limit=5)
    assert state["status"] == "OK"
    assert state["proposal_count"] == 2
    assert state["latest"]["id"] == "p-new"
    assert state["latest"]["status"] == "AWAITING_HUMAN_APPROVED_WRITE"
    assert state["latest"]["files"] == ["scripts/obsidia_cli.py"]


def test_obsidure_latest_response_has_surfaces(monkeypatch, tmp_path):
    mod = load_cli()
    root = make_repo(tmp_path)
    monkeypatch.setattr(mod, "REPO_ROOT", root)

    response = mod.build_obsidure_bridge_response("obsidure latest", registry())
    assert response["detected_layer"] == "obsidure"
    assert response["output"] == "GUIDE"
    assert response["mode_reponse"] == "ANSWER_LOCAL"
    assert response["etat_technique"]["proposal_count"] == 2
    assert response["etat_technique"]["latest_id"] == "p-new"
    assert response["proof_panel"]["decision_authority"] == "KX108_ONLY"
    assert "Receipt preview" in response["reponse"]


def test_obsidure_gates_are_commands_only(monkeypatch, tmp_path):
    mod = load_cli()
    root = make_repo(tmp_path)
    monkeypatch.setattr(mod, "REPO_ROOT", root)

    response = mod.build_obsidure_bridge_response("obsidure gates", registry())
    assert response["outils_panel"]["gates"] == "commands-only"
    assert response["outils_panel"]["apply"] == "forbidden"
    assert response["outils_panel"]["commit"] == "forbidden"
    assert response["outils_panel"]["push"] == "forbidden"
    assert "Gates commands-only" in response["reponse"]


def test_answer_router_uses_obsidure_bridge(monkeypatch, tmp_path):
    mod = load_cli()
    root = make_repo(tmp_path)
    monkeypatch.setattr(mod, "REPO_ROOT", root)

    response = mod.answer_router("obsidure status", registry())
    assert response["detected_layer"] == "obsidure"
    assert response["etat_technique"]["obsidure_bridge"] == "used"
    assert response["output"] == "GUIDE"


def test_obsidure_missing_dir_safe(monkeypatch, tmp_path):
    mod = load_cli()
    monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)

    response = mod.build_obsidure_bridge_response("obsidure status", registry())
    assert response["etat_technique"]["obsidure_status"] == "NO_PROPOSALS_DIR"
    assert response["etat_technique"]["proposal_count"] == 0
    assert response["proof_panel"]["mutation"] == "none"


def test_obsidure_bridge_does_not_emit_executable_apply_commit_push(monkeypatch, tmp_path):
    mod = load_cli()
    root = make_repo(tmp_path)
    monkeypatch.setattr(mod, "REPO_ROOT", root)

    response = mod.build_obsidure_bridge_response("peux tu coder", registry())
    rendered = json.dumps(response, ensure_ascii=False).lower()
    forbidden_executable = [
        "git commit",
        "git push",
        "scripts/apply_proposal.ps1",
        "--apply",
        "apply_proposal",
    ]
    for item in forbidden_executable:
        assert item not in rendered
    assert response["etat_technique"]["subprocess"] == "none"


def test_obsidure_bridge_segment_has_no_subprocess():
    src = CLI_PATH.read_text(encoding="utf-8")
    segment = src.split("OBSIDIA_TERMINAL_OBSIDURE_BRIDGE_V1", 1)[1]
    segment = segment.split("FIN TERMINAL OBSIDURE BRIDGE V1", 1)[0]
    assert "import subprocess" not in segment
    assert "subprocess.run" not in segment
    assert "os.system" not in segment

def test_mutation_words_remain_policy_deny_after_obsidure_bridge():
    mod = load_cli()
    for raw in ["commit le kernel", "apply le patch", "push la branche"]:
        response = mod.answer_router(raw, registry())
        assert response["output"] == "POLICY_DENY"
        assert response["mode_reponse"] == "POLICY_DENY"
        assert response["etat_technique"]["mutation"] == "forbidden"
