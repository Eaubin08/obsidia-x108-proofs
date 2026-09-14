"""test_obsidia_terminal_routing_v1 — TERMINAL_ROUTING_FIXES_V1.

Scope : Phase A1 — policy word-boundary fix (A2), terminal_self route (A3),
capabilities/diagnostic corpus (A4), coder routing (A4), unknown fallback (A8).
Aucun subprocess. Aucune mutation. Aucun appel reseau.
"""

from __future__ import annotations

import py_compile
import sys
import json
import importlib
from types import SimpleNamespace
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CLI_DIR = _REPO_ROOT / "scripts"
sys.path.insert(0, str(_CLI_DIR))

import obsidia_cli as cli  # noqa: E402

_REG = cli.load_registry(cli.REGISTRY_PATH)


def _a(q: str) -> dict:
    return cli.answer_router(q, _REG)


# ---------------------------------------------------------------------------
# Compilation
# ---------------------------------------------------------------------------
def test_py_compile() -> None:
    py_compile.compile(str(_CLI_DIR / "obsidia_cli.py"), doraise=True)


# ---------------------------------------------------------------------------
# A2 — policy_check word-boundary : faux positifs corriges
# ---------------------------------------------------------------------------
def test_policy_no_false_positive_actuelle() -> None:
    """'actuelle' ne doit pas declencher deny 'act'."""
    r = _a("quelle est la configuration actuelle")
    assert r["output"] != "POLICY_DENY", (
        f"Faux positif 'act' sur 'actuelle' — output={r['output']}")


def test_policy_no_false_positive_action() -> None:
    r = _a("quelle action prendre pour sigma")
    assert r["output"] != "POLICY_DENY", (
        f"Faux positif 'act' sur 'action' — output={r['output']}")


def test_policy_no_false_positive_impact() -> None:
    r = _a("quel est l impact de cette modification")
    assert r["output"] != "POLICY_DENY"


def test_policy_real_deny_commit() -> None:
    """'commit' doit toujours etre refuse."""
    r = _a("commit ces fichiers")
    assert r["output"] == "POLICY_DENY"


def test_policy_real_deny_push() -> None:
    r = _a("push vers main")
    assert r["output"] == "POLICY_DENY"


def test_policy_real_deny_deploy() -> None:
    r = _a("deploie la version 2")
    assert r["output"] == "POLICY_DENY"


# ---------------------------------------------------------------------------
# A3 — terminal_self route
# ---------------------------------------------------------------------------
def test_self_route_qui_es_tu() -> None:
    """'qui es tu' doit router vers terminal_self et retourner GUIDE."""
    r = _a("qui es tu")
    assert r["detected_layer"] == "terminal_self", f"layer={r['detected_layer']}"
    assert r["output"] == "GUIDE"


def test_self_route_que_peux_tu_faire() -> None:
    r = _a("que peux tu faire")
    assert r["detected_layer"] == "terminal_self"
    assert r["output"] == "GUIDE"


def test_self_route_quelles_sont_tes_capacites() -> None:
    r = _a("quelles sont tes capacites")
    assert r["detected_layer"] == "terminal_self"
    assert r["output"] == "GUIDE"


# ---------------------------------------------------------------------------
# A4 — corpus terminal_self : contenu de la reponse
# ---------------------------------------------------------------------------
def test_self_answer_contains_non_souverain() -> None:
    """La reponse doit mentionner que le terminal est non souverain."""
    r = _a("qui es tu")
    assert r["output"] == "GUIDE"
    low = r["reponse"].lower()
    assert "non souverain" in low or "kx108" in low or "readonly" in low, (
        f"Reponse terminal_self manque identite : {r['reponse'][:200]}")


def test_self_answer_contains_decision_authority() -> None:
    r = _a("que fais tu")
    low = r["reponse"].lower()
    assert "kx108" in low or "x108" in low or "autorite" in low


def test_capabilities_answer_lists_layers() -> None:
    """La reponse capabilities doit lister les couches connues."""
    r = _a("quelles sont tes capacites")
    low = r["reponse"].lower()
    assert "brody" in low or "sigma" in low or "obsidure" in low, (
        f"Reponse capabilities ne liste pas les couches : {r['reponse'][:200]}")


# ---------------------------------------------------------------------------
# A4 — obsidure / coder routing
# ---------------------------------------------------------------------------
def test_coder_routes_obsidure_or_guide() -> None:
    """'peux tu coder' doit router vers obsidure (COMMANDS ou GUIDE), jamais EXECUTE."""
    r = _a("peux tu coder un patch pour sigma")
    assert r["output"] in ("COMMANDS", "GUIDE"), (
        f"Unexpected output for 'peux tu coder' : {r['output']}")
    assert r["output"] != "POLICY_DENY"


# ---------------------------------------------------------------------------
# A8 — build_unknown_answer : contenu ameliore
# ---------------------------------------------------------------------------
def test_unknown_answer_lists_layers() -> None:
    """Un STOP_UNKNOWN doit lister les couches disponibles."""
    r = _a("plop incomprehensible zzz")
    if r["output"] == "STOP_UNKNOWN":
        low = r["reponse"].lower()
        assert "brody" in low or "sigma" in low or "couche" in low, (
            f"STOP_UNKNOWN ne liste pas les couches : {r['reponse'][:300]}")


def test_unknown_answer_contains_examples() -> None:
    """Un STOP_UNKNOWN doit proposer des exemples de formulations."""
    r = _a("aaabbbccc xyz inconnu")
    if r["output"] == "STOP_UNKNOWN":
        low = r["reponse"].lower()
        assert ("exemple" in low or "->" in low or "→" in low or
                "formulation" in low or "precise" in low), (
            f"STOP_UNKNOWN sans exemples : {r['reponse'][:300]}")


# ---------------------------------------------------------------------------
# Gardes statiques : non-souverain inchange
# ---------------------------------------------------------------------------
def test_static_no_subprocess() -> None:
    src = (_CLI_DIR / "obsidia_cli.py").read_text(encoding="utf-8")
    assert "import subprocess" not in src
    assert "os.system" not in src
    assert "shell=True" not in src


def test_static_decision_authority_unchanged() -> None:
    """KX108_ONLY doit rester la seule autorite dans le code."""
    src = (_CLI_DIR / "obsidia_cli.py").read_text(encoding="utf-8")
    assert "KX108_ONLY" in src
    assert "decision_authority" in src


def test_static_terminal_self_in_plan_organes() -> None:
    """terminal_self doit etre dans PLAN_ORGANES."""
    assert "terminal_self" in cli.PLAN_ORGANES


def test_static_terminal_self_in_plan_tooling() -> None:
    """terminal_self doit etre dans PLAN_TOOLING."""
    assert "terminal_self" in cli.PLAN_TOOLING


# ---------------------------------------------------------------------------
# F32-B - bounded mission CLI surface
# ---------------------------------------------------------------------------
def _mission_fake_stack(monkeypatch, projection, rehydrate=None, advance=None):
    calls = {"rehydrate": 0, "advance": 0, "advance_kwargs": None}

    def _project_mission(**kwargs):
        return dict(projection)

    def _rehydrate_bound_work_unit(**kwargs):
        calls["rehydrate"] += 1
        if rehydrate is not None:
            return rehydrate
        return {
            "status": "WORK_UNIT_REHYDRATED",
            "work_unit": object(),
        }

    def _advance_bounded_mission(**kwargs):
        calls["advance"] += 1
        calls["advance_kwargs"] = kwargs
        if advance is not None:
            return dict(advance)
        return {"status": "ADVANCED"}

    modules = {
        "obsidia_bounded_mission_v0": SimpleNamespace(
            STATUS_PROJECTION_OK="PROJECTION_OK",
            STATUS_WORK_UNIT_REHYDRATED="WORK_UNIT_REHYDRATED",
            _BOUNDED_MISSION_DIR=Path("MISSIONS"),
            _BOUNDED_MISSION_HOLD_DIR=Path("HOLDS"),
            _BOUNDED_MISSION_DECISION_DIR=Path("DECISIONS"),
            project_mission=_project_mission,
            rehydrate_bound_work_unit=_rehydrate_bound_work_unit,
        ),
        "obsidia_mission_sequencer_v0": SimpleNamespace(
            AUTHORITY_MODE_BOUNDED_MISSION_AUTHORITY="BOUNDED_MISSION_AUTHORITY",
            advance_bounded_mission=_advance_bounded_mission,
        ),
        "obsidia_branching_ledger": SimpleNamespace(LEDGER_DIR=Path("LEDGER")),
        "obsidia_batch_selector": SimpleNamespace(SELECTOR_DIR=Path("SELECTOR")),
        "obsidia_batch_execution": SimpleNamespace(EXECUTION_DIR=Path("EXECUTION")),
        "obsidia_pre_execution_context": SimpleNamespace(PRE_EXECUTION_CONTEXT_DIR=Path("PEC")),
        "obsidia_kx108_decision_store": SimpleNamespace(KX108_DECISION_DIR=Path("KX")),
        "obsidia_test_contract": SimpleNamespace(TEST_CONTRACT_RESULT_DIR=Path("TCR")),
        "obsidia_sealed_evidence_v0": SimpleNamespace(
            SEALED_APPLY_RECEIPT_DIR=Path("SAR"),
            SEALED_ROLLBACK_EVIDENCE_DIR=Path("SRE"),
        ),
        "obsidia_governed_rollback_v0": SimpleNamespace(ROLLBACK_RESULT_DIR=Path("RBK")),
        "obsidia_mission_local_snapshot_v0": SimpleNamespace(
            _BOUNDED_MISSION_SNAPSHOT_DIR=Path("SNAP"),
        ),
    }

    real_import = importlib.import_module

    def _fake_import(name, package=None):
        if name in modules:
            return modules[name]
        return real_import(name, package)

    monkeypatch.setattr(importlib, "import_module", _fake_import)
    return calls


def _projection(**overrides):
    base = {
        "status": "PROJECTION_OK",
        "mission_id": "msn-test",
        "current_state": "ACTION_EXECUTED_KEPT",
        "revision": 7,
        "mission_tip_sha": "a" * 40,
        "active_plan_id": "mpl-active",
        "plan_completed": False,
        "active_hold_id": None,
        "mission_authority_mode": "BOUNDED_MISSION_AUTHORITY_PREPARED",
        "active_hma_id": "hma-test",
        "actions_completed": 1,
        "actions_failed": 0,
        "unknowns": [],
        "extra_inspect_field": "preserved",
    }
    base.update(overrides)
    return base


def test_mission_status_is_readonly_projection(monkeypatch) -> None:
    calls = _mission_fake_stack(monkeypatch, _projection())
    out = json.loads(cli._dispatch_mission("status msn-test"))

    assert out["status"] == "PROJECTION_OK"
    assert out["active_plan_id"] == "mpl-active"
    assert out["decision_authority"] == "KX108_ONLY"
    assert out["terminal_authority"] == "NONE"
    assert calls["rehydrate"] == 0
    assert calls["advance"] == 0


def test_mission_inspect_returns_full_projection_readonly(monkeypatch) -> None:
    calls = _mission_fake_stack(monkeypatch, _projection())
    out = json.loads(cli._dispatch_mission("inspect msn-test"))

    assert out["extra_inspect_field"] == "preserved"
    assert out["active_plan_id"] == "mpl-active"
    assert calls["rehydrate"] == 0
    assert calls["advance"] == 0


def test_mission_resume_uses_active_plan_and_advances_exactly_once(monkeypatch) -> None:
    wu = object()
    calls = _mission_fake_stack(
        monkeypatch,
        _projection(active_plan_id="mpl-derived"),
        rehydrate={"status": "WORK_UNIT_REHYDRATED", "work_unit": wu},
        advance={"status": "ACTION_PREPARED"},
    )

    out = json.loads(cli._dispatch_mission("resume msn-test"))
    kw = calls["advance_kwargs"]

    assert calls["rehydrate"] == 1
    assert calls["advance"] == 1
    assert kw["mission_id"] == "msn-test"
    assert kw["plan_id"] == "mpl-derived"
    assert kw["work_unit"] is wu
    assert kw["authority_mode"] == "BOUNDED_MISSION_AUTHORITY"
    assert kw["human_authorized_execution_authority_hash"] is None
    assert kw["human_authorization_reference"] is None
    assert kw["human_mission_decision_id"] is None
    assert out["per_action_human_eah_supplied"] is False
    assert out["decision_authority"] == "KX108_ONLY"
    assert out["terminal_authority"] == "NONE"


def test_mission_resume_uses_canonical_owner_store_paths(monkeypatch) -> None:
    calls = _mission_fake_stack(monkeypatch, _projection())
    cli._dispatch_mission("resume msn-test")
    kw = calls["advance_kwargs"]

    assert kw["ledger_dir"] == Path("LEDGER")
    assert kw["selector_dir"] == Path("SELECTOR")
    assert kw["execution_dir"] == Path("EXECUTION")
    assert kw["pre_execution_context_dir"] == Path("PEC")
    assert kw["kx108_pre_decision_dir"] == Path("KX")
    assert kw["kx108_post_decision_dir"] == Path("KX")
    assert kw["test_contract_results_dir"] == Path("TCR")
    assert kw["sealed_receipt_dir"] == Path("SAR")
    assert kw["sealed_rollback_evidence_dir"] == Path("SRE")
    assert kw["rollback_result_dir"] == Path("RBK")
    assert kw["mission_store_dir"] == Path("MISSIONS")
    assert kw["hold_store_dir"] == Path("HOLDS")
    assert kw["decision_store_dir"] == Path("DECISIONS")
    assert kw["snapshot_store_dir"] == Path("SNAP")


def test_mission_resume_without_active_plan_fails_before_rehydrate(monkeypatch) -> None:
    calls = _mission_fake_stack(monkeypatch, _projection(active_plan_id=None))
    out = json.loads(cli._dispatch_mission("resume msn-test"))

    assert out["status"] == "MISSION_RESUME_REJECTED"
    assert out["reason"] == "NO_ACTIVE_PLAN"
    assert calls["rehydrate"] == 0
    assert calls["advance"] == 0


def test_mission_resume_rehydrate_failure_never_advances(monkeypatch) -> None:
    calls = _mission_fake_stack(
        monkeypatch,
        _projection(),
        rehydrate={"status": "WORK_UNIT_REHYDRATE_REJECTED", "reason": "HEAD_DRIFT"},
    )
    out = json.loads(cli._dispatch_mission("resume msn-test"))

    assert out["status"] == "MISSION_RESUME_REJECTED"
    assert "WORK_UNIT_REHYDRATE_FAILED" in out["reason"]
    assert calls["rehydrate"] == 1
    assert calls["advance"] == 0


def test_static_mission_routes_shell_and_one_shot() -> None:
    src = (_CLI_DIR / "obsidia_cli.py").read_text(encoding="utf-8")
    assert src.count('if cmd0 == "mission":') == 2
    assert src.count("print(_dispatch_mission(_obj_mission))") == 2
    assert "def _dispatch_mission(rest: str) -> str:" in src
    assert "def _dispatch_build(rest: str) -> str:" in src
