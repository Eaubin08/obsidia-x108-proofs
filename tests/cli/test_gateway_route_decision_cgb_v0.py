"""
tests/cli/test_gateway_route_decision_cgb_v0.py
============================================
CG-B — RouteDecision + RouteReceipt canoniques NON SOUVERAINS + API minimale
mission/status/receipt/HOLD/capability-request, runtime INERTE.

Le routeur externe (`app.router.decision.decide`) est simulé par un module
jetable écrit dans un tmp_path et pointé via `OBSIDIA_ROUTER_ROOT`. Aucune
permission Claude, aucun hook, aucun bail runtime.
"""
from __future__ import annotations

import json
import sys
import textwrap
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_SCRIPTS = _REPO_ROOT / "scripts"
for _p in (str(_SCRIPTS), str(_REPO_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import obsidia_gateway_route_decision_v0 as RD   # noqa: E402


def _drop_fake_router_modules():
    for m in ("app", "app.router", "app.router.decision"):
        sys.modules.pop(m, None)


@pytest.fixture(autouse=True)
def _isolate(monkeypatch, tmp_path):
    """Chaque test : router pointé sur un tmp vide (ROUTER_UNAVAILABLE) par
    défaut ; store CG-B redirigé vers tmp (jamais audit/) ; modules fake
    router purgés."""
    monkeypatch.setenv("OBSIDIA_ROUTER_ROOT", str(tmp_path / "no_router"))
    monkeypatch.setenv("OBSIDIA_CGB_STORE_DIR", str(tmp_path / "cgb_default_store"))
    _drop_fake_router_modules()
    # purge d'éventuels vrais chemins router du sys.path
    for p in list(sys.path):
        if p.endswith("obsidia-router"):
            sys.path.remove(p)
    yield
    _drop_fake_router_modules()


def _install_fake_router(root: Path, decide_body: str):
    (root / "app" / "router").mkdir(parents=True, exist_ok=True)
    (root / "app" / "__init__.py").write_text("", encoding="utf-8")
    (root / "app" / "router" / "__init__.py").write_text("", encoding="utf-8")
    (root / "app" / "router" / "decision.py").write_text(
        textwrap.dedent(decide_body), encoding="utf-8")


def _router_returns(monkeypatch, tmp_path, decision):
    root = tmp_path / "fake_router"
    payload = json.dumps(decision)
    _install_fake_router(root, "import json\n"
                         f"_D = json.loads({payload!r})\n"
                         "def decide(prompt, memory_index=None):\n"
                         "    return _D if not isinstance(_D, dict) else dict(_D)\n")
    monkeypatch.setenv("OBSIDIA_ROUTER_ROOT", str(root))
    _drop_fake_router_modules()


def _router_raises(monkeypatch, tmp_path):
    root = tmp_path / "fake_router_exc"
    _install_fake_router(root, """
        def decide(prompt, memory_index=None):
            raise RuntimeError("router boom")
    """)
    monkeypatch.setenv("OBSIDIA_ROUTER_ROOT", str(root))
    _drop_fake_router_modules()


def _store(tmp_path):
    return tmp_path / "cgb_store"


# ══════════════════════════════════════════════════════════════════════════
#  Frontière router — fail-closed
# ══════════════════════════════════════════════════════════════════════════

def test_router_unavailable_structured_hold_no_llm():
    d = RD.build_route_decision("explique le theoreme 17")
    assert d["router_status"] == RD.ROUTER_UNAVAILABLE
    assert d["fail_closed_hold"] is True
    assert d["route_class"] == RD.ROUTE_HUMAN_AUTHORITY
    assert d["human_authority_required"] is True
    assert d["route_class"] not in (RD.ROUTE_LLM_LANGUAGE, RD.ROUTE_LLM_REASONING,
                                    RD.ROUTE_LLM_ENGINEERING)
    ok, why = RD.verify_route_decision(d)
    assert ok, why


def test_router_exception_structured_hold(monkeypatch, tmp_path):
    _router_raises(monkeypatch, tmp_path)
    d = RD.build_route_decision("statut kernel")
    assert d["router_status"] == RD.ROUTER_EXCEPTION
    assert d["fail_closed_hold"] is True
    assert d["route_class"] == RD.ROUTE_HUMAN_AUTHORITY


@pytest.mark.parametrize("bad", [
    {"route": 123, "ir": {}, "gate": {}},
    {"route": "", "ir": {}, "gate": {}},
    {"ir": {}, "gate": {}},
    {"route": "brody", "ir": "nope", "gate": {}},
    {"route": "brody", "ir": {}, "gate": "nope"},
    "not-a-dict",
    [1, 2, 3],
])
def test_router_malformed_decision_structured_hold(monkeypatch, tmp_path, bad):
    _router_returns(monkeypatch, tmp_path, bad)
    d = RD.build_route_decision("x")
    assert d["router_status"] == RD.MALFORMED_ROUTER_DECISION
    assert d["fail_closed_hold"] is True
    assert d["route_class"] == RD.ROUTE_HUMAN_AUTHORITY


def test_no_fail_open_flags():
    assert RD.CG_B_ROUTER_COLOCATION_DEFERRED is True
    for st in (RD.ROUTER_UNAVAILABLE, RD.ROUTER_EXCEPTION, RD.MALFORMED_ROUTER_DECISION):
        assert st in RD._ROUTER_HOLD_STATUSES


# ══════════════════════════════════════════════════════════════════════════
#  Router disponible — normalisation en classes canoniques
# ══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("router_route,intent,gate,expected", [
    ("no_model_needed", "status", "ALLOW", RD.ROUTE_STACK_NATIVE),
    ("memory_hit", "question", "ALLOW", RD.ROUTE_STACK_NATIVE),
    ("semantic_memory_hit", "question", "ALLOW", RD.ROUTE_STACK_NATIVE),
    ("lean_route_only", "proof", "ALLOW", RD.ROUTE_STACK_NATIVE),
    ("brody", "explain", "ALLOW", RD.ROUTE_LLM_LANGUAGE),
    ("brody", "design", "ALLOW", RD.ROUTE_LLM_REASONING),
    ("obsidure_route_only", "code_request", "ALLOW", RD.ROUTE_LLM_ENGINEERING),
    ("fireworks", "code_request", "ALLOW", RD.ROUTE_LLM_ENGINEERING),
    ("fireworks", "explain", "ALLOW", RD.ROUTE_LLM_LANGUAGE),
    ("fireworks", "design", "ALLOW", RD.ROUTE_LLM_REASONING),
    ("fireworks", "wat", "ALLOW", RD.ROUTE_UNKNOWN),
    ("denied", "world_action", "DENY", RD.ROUTE_HUMAN_AUTHORITY),
    ("hold_commands_only", "world_action", "HOLD", RD.ROUTE_HUMAN_AUTHORITY),
    ("clarification_needed", "unknown", "CLARIFY", RD.ROUTE_HUMAN_AUTHORITY),
    ("domain_bridge", "bank", "ALLOW", RD.ROUTE_HUMAN_AUTHORITY),
])
def test_route_class_mapping(monkeypatch, tmp_path, router_route, intent, gate, expected):
    _router_returns(monkeypatch, tmp_path, {
        "route": router_route, "level": 1, "reason": "fake",
        "ir": {"intent_type": intent, "target_layer": "x", "action": "y", "risk": "low"},
        "gate": {"verdict": gate, "reason": "fake"},
    })
    d = RD.build_route_decision("some request")
    assert d["router_status"] == RD.ROUTER_OK
    assert d["route_class"] == expected
    if expected == RD.ROUTE_UNKNOWN:
        assert d["unknown"] is True


def test_engineering_is_never_the_default(monkeypatch, tmp_path):
    # route d'escalade + intent ambigu -> UNKNOWN, jamais ENGINEERING
    _router_returns(monkeypatch, tmp_path, {
        "route": "fireworks", "level": 3, "reason": "escalation",
        "ir": {"intent_type": "vague", "target_layer": None, "action": None, "risk": None},
        "gate": {"verdict": "ALLOW"}})
    d = RD.build_route_decision("do something clever")
    assert d["route_class"] == RD.ROUTE_UNKNOWN
    assert d["route_class"] != RD.ROUTE_LLM_ENGINEERING


def test_claude_candidate_only_when_router_selected(monkeypatch, tmp_path):
    # LLM reasoning explicite -> provider claude candidat DANS le receipt
    _router_returns(monkeypatch, tmp_path, {
        "route": "fireworks", "level": 3, "reason": "novel",
        "ir": {"intent_type": "design"}, "gate": {"verdict": "ALLOW"}})
    d = RD.build_route_decision("nouvelle architecture X")
    assert d["route_class"] == RD.ROUTE_LLM_REASONING
    # aucune auto-résolution d'ingénierie
    assert d["route_class"] != RD.ROUTE_LLM_ENGINEERING


def test_human_authority_route_no_engineering_autoresolution(monkeypatch, tmp_path):
    _router_returns(monkeypatch, tmp_path, {
        "route": "denied", "reason": "protected zone",
        "ir": {"intent_type": "code_request"},   # même un intent code -> DENY domine
        "gate": {"verdict": "DENY"}})
    d = RD.build_route_decision("patch proofs/lean/Foo.lean")
    assert d["route_class"] == RD.ROUTE_HUMAN_AUTHORITY
    assert d["route_class"] != RD.ROUTE_LLM_ENGINEERING


# ══════════════════════════════════════════════════════════════════════════
#  RouteReceipt — déterministe / hash-valide / non-autorité
# ══════════════════════════════════════════════════════════════════════════

def test_route_receipt_deterministic_and_hash_valid(monkeypatch, tmp_path):
    _router_returns(monkeypatch, tmp_path, {
        "route": "memory_hit", "reason": "hit", "ir": {"intent_type": "question"},
        "gate": {"verdict": "ALLOW"}})
    d = RD.build_route_decision("q")
    r1 = RD.build_route_receipt(d, requested_outcome="q", selected_route=d["route_class"],
                               reason=d["reason"], persist=False)
    r2 = RD.build_route_receipt(d, requested_outcome="q", selected_route=d["route_class"],
                               reason=d["reason"], persist=False)
    assert r1["receipt_hash"] == r2["receipt_hash"]
    assert r1["route_receipt_id"] == r2["route_receipt_id"]
    ok, why = RD.verify_route_receipt(r1)
    assert ok, why
    assert r1["is_authority"] is False and r1["can_authorize_execution"] is False
    assert r1["lease_id"] is None
    # tamper -> invalide
    bad = dict(r1); bad["selected_route"] = "ROUTE_LLM_ENGINEERING"
    ok2, _ = RD.verify_route_receipt(bad)
    assert ok2 is False


def test_route_receipt_retrieval(tmp_path):
    sd = _store(tmp_path)
    d = RD.build_route_decision("q")   # router unavailable -> HOLD decision, ok pour un receipt
    rec = RD.build_route_receipt(d, requested_outcome="q", selected_route=d["route_class"],
                                reason=d["reason"], store_dir=sd)
    got = RD.get_receipt(rec["route_receipt_id"], store_dir=sd)
    assert got is not None and got["receipt_hash"] == rec["receipt_hash"]
    assert RD.get_receipt("rcpt-" + "0" * 32, store_dir=sd) is None
    assert RD.get_receipt("not-an-id", store_dir=sd) is None


# ══════════════════════════════════════════════════════════════════════════
#  API minimale — inerte
# ══════════════════════════════════════════════════════════════════════════

def test_submit_mission_routes_but_never_executes(monkeypatch, tmp_path):
    _router_returns(monkeypatch, tmp_path, {
        "route": "no_model_needed", "reason": "local", "ir": {"intent_type": "status"},
        "gate": {"verdict": "ALLOW"}})
    sd = _store(tmp_path)
    r = RD.submit_mission(requested_outcome="statut", store_dir=sd)
    assert r["status"] == RD.STATUS_SUBMITTED_ROUTED_INERT
    assert r["execution_started"] is False and r["cg_b_inert"] is True
    assert r["route_decision"]["route_class"] == RD.ROUTE_STACK_NATIVE
    st = RD.get_status(r["mission_submission_id"], store_dir=sd)
    assert st["status"] == RD.STATUS_SUBMITTED_ROUTED_INERT
    assert st["execution_started"] is False


def test_submit_mission_human_authority_awaits_human(tmp_path):
    sd = _store(tmp_path)   # router unavailable -> ROUTE_HUMAN_AUTHORITY
    r = RD.submit_mission(requested_outcome="fais un truc", store_dir=sd)
    assert r["status"] == RD.STATUS_AWAITING_HUMAN
    assert r["execution_started"] is False
    st = RD.get_status(r["mission_submission_id"], store_dir=sd)
    assert st["status"] == RD.STATUS_AWAITING_HUMAN
    assert st["fail_closed_hold"] is True


def test_submit_mission_rejects_empty():
    assert RD.submit_mission(requested_outcome="  ")["status"] == RD.STATUS_API_REJECTED


def test_request_capability_is_inert(tmp_path):
    sd = _store(tmp_path)
    r = RD.submit_mission(requested_outcome="mission", store_dir=sd)
    cap = RD.request_capability(
        mission_submission_id=r["mission_submission_id"],
        requested_capability="Write scripts/new_thing.py",
        reason="capability gap", store_dir=sd)
    assert cap["status"] == RD.STATUS_CAPABILITY_REQUEST_RECORDED_INERT
    assert cap["granted"] is False
    assert cap["grants_tool_access"] is False
    assert cap["lease_runtime_implemented"] is False
    assert cap["cognitive_capability_lease_active"] is False
    assert cap["engineering_lease_active"] is False
    assert cap["cg_b_inert"] is True
    assert RD.CAPABILITY_REQUEST_CAN_GRANT_TOOL_ACCESS is False
    assert RD.LEASE_RUNTIME_IMPLEMENTED is False
    # l'artefact persisté porte les mêmes invariants
    art = json.loads((sd / "capability_requests" / f"{cap['capability_request_id']}.json").read_text(encoding="utf-8"))
    assert art["granted"] is False and art["grants_tool_access"] is False
    assert art["claude_self_authorizes_engineering"] is False


def test_respond_to_hold_is_inert(tmp_path):
    sd = _store(tmp_path)
    r = RD.submit_mission(requested_outcome="mission", store_dir=sd)
    hr = RD.respond_to_hold(mission_submission_id=r["mission_submission_id"],
                            human_decision_ref="hdr-42", resolution="go", store_dir=sd)
    assert hr["status"] == RD.STATUS_HOLD_RESPONSE_RECORDED_INERT
    assert hr["grants_capability"] is False and hr["starts_execution"] is False
    assert RD.respond_to_hold(mission_submission_id=r["mission_submission_id"],
                              human_decision_ref="  ", resolution="go",
                              store_dir=sd)["status"] == RD.STATUS_API_REJECTED


def test_api_unknown_ids_rejected(tmp_path):
    sd = _store(tmp_path)
    assert RD.get_status("gsub-" + "0" * 32, store_dir=sd)["status"] == RD.STATUS_API_REJECTED
    assert RD.request_capability(mission_submission_id="gsub-" + "0" * 32,
                                 requested_capability="x", reason="y",
                                 store_dir=sd)["status"] == RD.STATUS_API_REJECTED


# ══════════════════════════════════════════════════════════════════════════
#  Gateway handle() — DENY/HOLD/no_model_needed => 0 appel LLM
# ══════════════════════════════════════════════════════════════════════════

def _gw():
    import importlib
    import obsidia_gateway as GW
    return importlib.reload(GW)


def test_gateway_handle_router_unavailable_hold_zero_llm():
    GW = _gw()
    c = {"llm_calls_avoided": 0, "llm_calls": 0}
    ans = GW.handle("explique tout", {}, c)
    assert "HOLD" in ans and "ROUTER_UNAVAILABLE" in ans
    assert c["llm_calls"] == 0
    assert c["last_route"].startswith("router_hold:")


@pytest.mark.parametrize("router_route,gate,intent", [
    ("denied", "DENY", "world_action"),
    ("hold_commands_only", "HOLD", "world_action"),
    ("clarification_needed", "CLARIFY", "unknown"),
    ("no_model_needed", "ALLOW", "status"),
])
def test_gateway_handle_deny_hold_clarify_nomodel_zero_llm(monkeypatch, tmp_path,
                                                          router_route, gate, intent):
    _router_returns(monkeypatch, tmp_path, {
        "route": router_route, "level": 0, "reason": "fake",
        "ir": {"intent_type": intent, "target_layer": "x"},
        "gate": {"verdict": gate, "reason": "fake"},
        "memory_entry": "x", "topic": "t"})
    GW = _gw()
    c = {"llm_calls_avoided": 0, "llm_calls": 0}
    GW.handle("une requete", {}, c)
    assert c["llm_calls"] == 0, f"{router_route} ne doit lancer aucun LLM"


# ══════════════════════════════════════════════════════════════════════════
#  Statique — pas de changement de permission Claude / hook / bail
# ══════════════════════════════════════════════════════════════════════════

def test_no_claude_permission_or_hook_change():
    r = __import__("subprocess").run(
        ["git", "status", "--porcelain", ".claude/"],
        cwd=str(_REPO_ROOT), capture_output=True, text=True)
    assert r.stdout.strip() == "", f".claude/ modifié: {r.stdout}"


def test_stage4_authority_and_lean_untouched():
    r = __import__("subprocess").run(
        ["git", "status", "--porcelain", "proofs/lean/",
         "scripts/obsidia_mission_sequencer_v0.py",
         "scripts/obsidia_mission_authority_v0.py",
         "scripts/obsidia_governed_apply_v0.py"],
        cwd=str(_REPO_ROOT), capture_output=True, text=True)
    assert r.stdout.strip() == "", f"fichiers gelés modifiés: {r.stdout}"
