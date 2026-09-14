"""
tests/cli/test_cognitive_capability_lease_cgc_v0.py
================================================
CG-C — CognitiveCapabilityLease + EngineeringLease : représentation runtime
canonique ENTIÈREMENT INERTE (aucun accès outil, aucun enforcement, aucune
autorité). Router externe simulé ; store redirigé vers tmp.
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

import obsidia_gateway_route_decision_v0 as RD    # noqa: E402
import obsidia_cognitive_capability_lease_v0 as L  # noqa: E402


def _drop_fake_router():
    for m in ("app", "app.router", "app.router.decision"):
        sys.modules.pop(m, None)


@pytest.fixture(autouse=True)
def _isolate(monkeypatch, tmp_path):
    monkeypatch.setenv("OBSIDIA_CGB_STORE_DIR", str(tmp_path / "store"))
    monkeypatch.setenv("OBSIDIA_ROUTER_ROOT", str(tmp_path / "no_router"))
    _drop_fake_router()
    for p in list(sys.path):
        if p.endswith("obsidia-router"):
            sys.path.remove(p)
    yield
    _drop_fake_router()


def _fake_router(monkeypatch, tmp_path, router_route, intent, gate="ALLOW"):
    root = tmp_path / "fake_router"
    (root / "app" / "router").mkdir(parents=True, exist_ok=True)
    (root / "app" / "__init__.py").write_text("", encoding="utf-8")
    (root / "app" / "router" / "__init__.py").write_text("", encoding="utf-8")
    dec = {"route": router_route, "level": 1, "reason": "fake",
           "ir": {"intent_type": intent, "target_layer": "x", "action": "y", "risk": "low"},
           "gate": {"verdict": gate, "reason": "fake"}}
    (root / "app" / "router" / "decision.py").write_text(
        "import json\n_D = json.loads(%r)\n"
        "def decide(prompt, memory_index=None):\n    return dict(_D)\n" % json.dumps(dec),
        encoding="utf-8")
    monkeypatch.setenv("OBSIDIA_ROUTER_ROOT", str(root))
    _drop_fake_router()


_ROUTE_FOR = {
    L.LANGUAGE_LEASE: ("brody", "explain"),
    L.REASONING_LEASE: ("brody", "design"),
    L.ENGINEERING_LEASE: ("obsidure_route_only", "code_request"),
}


def _material(monkeypatch, tmp_path, lease_class, tag="m"):
    rr, intent = _ROUTE_FOR[lease_class]
    _fake_router(monkeypatch, tmp_path, rr, intent)
    sub = RD.submit_mission(requested_outcome=f"mission {tag}")
    cap = RD.request_capability(mission_submission_id=sub["mission_submission_id"],
                                requested_capability=f"cap {tag}", reason="gap")
    ms = RD.load_mission_submission(sub["mission_submission_id"])
    cr = RD.load_capability_request(cap["capability_request_id"])
    return ms, cr, cap["route_decision"]


def _eng_scope(paths=("scripts/x.py",), tools=("Edit",)):
    return {"allowed_providers": ["obsidure"], "allowed_tools": list(tools),
            "allowed_paths": list(paths), "allowed_operations": ["UPDATE_TARGET_FROM_SOURCE"],
            "read_scope": "BOUNDED_PATHS", "write_scope": "BOUNDED_PATHS",
            "test_scope": "BOUNDED", "git_scope": "READ_ONLY",
            "max_mutation_category": "UPDATE_TARGET_FROM_SOURCE"}


# ══════════════════════════════════════════════════════════════════════════
#  Bornes d'inertie
# ══════════════════════════════════════════════════════════════════════════

def test_inertness_flags():
    assert L.LEASE_RECORD_RUNTIME_IMPLEMENTED is True
    assert L.LEASE_ENFORCEMENT_ACTIVE is False
    assert L.LEASE_GRANTS_TOOL_ACCESS is False
    assert L.HARD_TOOL_GATE_ACTIVE is False
    assert L.PRE_TOOL_LEASE_LOOKUP_ACTIVE is False
    assert L.COGNITIVE_CAPABILITY_LEASE_ACTIVE is False
    assert L.ENGINEERING_LEASE_ACTIVE is False
    assert L.CLAUDE_SELF_AUTHORIZES_ENGINEERING is False
    assert L.PROVIDER_SELF_ISSUES_LEASE is False
    assert L.LEASE_CLASS_IMPLICIT_GLOBAL_RIGHTS is False
    assert L.MISSION_CAPABILITY_SCOPE_BINDING == "NOT_YET_ACTIVE"
    assert L.LEASE_CAN_AUTHORIZE_TOOL_ACCESS_WHILE_MISSION_SCOPE_UNBOUND is False
    assert L.MAX_GOVERNED_MUTATION_OPERATION_V0 == "UPDATE_TARGET_FROM_SOURCE"


# ══════════════════════════════════════════════════════════════════════════
#  Construction + hash déterministe + 3 classes
# ══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("lease_class", [L.LANGUAGE_LEASE, L.REASONING_LEASE, L.ENGINEERING_LEASE])
def test_build_all_classes_deterministic(monkeypatch, tmp_path, lease_class):
    ms, cr, rd = _material(monkeypatch, tmp_path, lease_class)
    scope = _eng_scope() if lease_class == L.ENGINEERING_LEASE else \
        {"allowed_providers": ["brody"]}
    out1 = L.prepare_cognitive_capability_lease(
        lease_class=lease_class, capability_request=cr, route_decision=rd,
        mission_submission=ms, lease_scope=scope, requested_capability_scope=scope)
    out2 = L.prepare_cognitive_capability_lease(
        lease_class=lease_class, capability_request=cr, route_decision=rd,
        mission_submission=ms, lease_scope=scope, requested_capability_scope=scope)
    assert out1["status"] == L.STATUS_LEASE_BUILT_INERT, out1
    lease = out1["lease"]
    assert lease["lease_id"] == out2["lease"]["lease_id"]
    assert lease["lease_record_hash"] == out2["lease"]["lease_record_hash"]
    assert lease["lease_id"].startswith("cclease-")
    assert lease["is_execution_authority"] is False and lease["is_kx_authority"] is False
    assert lease["is_sovereign"] is False and lease["grants_tool_access"] is False
    assert lease["issued_by"] == L.ISSUER_GATEWAY_CAPABILITY_DECISION
    assert lease["route_class"] == L._CLASS_TO_ROUTE[lease_class]
    assert lease["mission_genesis_record_hash"] == "NOT_BOUND"
    ok, why = L.verify_capability_lease(lease)
    assert ok, why


# ══════════════════════════════════════════════════════════════════════════
#  Issuer
# ══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("bad", ["CLAUDE", "BRODY", "OBSIDURE", "SELF", ""])
def test_issuer_claude_and_providers_rejected(monkeypatch, tmp_path, bad):
    ms, cr, rd = _material(monkeypatch, tmp_path, L.REASONING_LEASE)
    out = L.prepare_cognitive_capability_lease(
        lease_class=L.REASONING_LEASE, capability_request=cr, route_decision=rd,
        mission_submission=ms, lease_scope={"allowed_providers": ["brody"]},
        requested_capability_scope={"allowed_providers": ["brody"]}, issued_by=bad)
    assert out["status"] == L.STATUS_LEASE_REJECTED
    assert out["reason"].startswith("ISSUER_NOT_AUTHORIZED")


# ══════════════════════════════════════════════════════════════════════════
#  Route ↔ classe
# ══════════════════════════════════════════════════════════════════════════

def test_route_class_mismatch_rejected(monkeypatch, tmp_path):
    ms, cr, rd = _material(monkeypatch, tmp_path, L.LANGUAGE_LEASE)   # rd = ROUTE_LLM_LANGUAGE
    out = L.prepare_cognitive_capability_lease(
        lease_class=L.ENGINEERING_LEASE, capability_request=cr, route_decision=rd,
        mission_submission=ms, lease_scope=_eng_scope(), requested_capability_scope=_eng_scope())
    assert out["status"] == L.STATUS_LEASE_REJECTED
    assert "ROUTE_CLASS_INCOMPATIBLE" in out["reason"]


def test_human_authority_route_no_lease(monkeypatch, tmp_path):
    _fake_router(monkeypatch, tmp_path, "denied", "code_request", gate="DENY")
    sub = RD.submit_mission(requested_outcome="x")
    cap = RD.request_capability(mission_submission_id=sub["mission_submission_id"],
                                requested_capability="c", reason="r")
    ms = RD.load_mission_submission(sub["mission_submission_id"])
    cr = RD.load_capability_request(cap["capability_request_id"])
    out = L.prepare_cognitive_capability_lease(
        lease_class=L.ENGINEERING_LEASE, capability_request=cr, route_decision=cap["route_decision"],
        mission_submission=ms, lease_scope=_eng_scope(), requested_capability_scope=_eng_scope())
    assert out["status"] == L.STATUS_LEASE_REJECTED
    assert "NO_LEASE_FOR_HOLD_OR_DENY" in out["reason"] or "NO_LEASE_FOR_ROUTE" in out["reason"]


def test_unknown_route_no_engineering_lease(monkeypatch, tmp_path):
    _fake_router(monkeypatch, tmp_path, "fireworks", "vague")   # -> ROUTE_UNKNOWN
    sub = RD.submit_mission(requested_outcome="x")
    cap = RD.request_capability(mission_submission_id=sub["mission_submission_id"],
                                requested_capability="c", reason="r")
    ms = RD.load_mission_submission(sub["mission_submission_id"])
    cr = RD.load_capability_request(cap["capability_request_id"])
    out = L.prepare_cognitive_capability_lease(
        lease_class=L.ENGINEERING_LEASE, capability_request=cr, route_decision=cap["route_decision"],
        mission_submission=ms, lease_scope=_eng_scope(), requested_capability_scope=_eng_scope())
    assert out["status"] == L.STATUS_LEASE_REJECTED
    assert "NO_LEASE_FOR_ROUTE" in out["reason"]


def test_router_fail_closed_hold_no_lease():
    # router indisponible -> rd fail_closed_hold=True, route_class=ROUTE_HUMAN_AUTHORITY
    rd = RD.build_route_decision("x")
    assert rd["fail_closed_hold"] is True
    fake_cr = {"domain_tag": "OBSIDIA_CGB_CAPABILITY_REQUEST_V0", "granted": False,
               "capability_request_id": "gcap-" + "0" * 32, "mission_submission_id": "gsub-" + "0" * 32,
               "route_decision": rd, "requested_capability": "x", "reason": "y"}
    fake_ms = {"domain_tag": "OBSIDIA_CGB_MISSION_SUBMISSION_V0",
               "mission_submission_id": "gsub-" + "0" * 32, "envelope_refs": {}}
    out = L.prepare_cognitive_capability_lease(
        lease_class=L.ENGINEERING_LEASE, capability_request=fake_cr, route_decision=rd,
        mission_submission=fake_ms, lease_scope=_eng_scope(), requested_capability_scope=_eng_scope())
    assert out["status"] == L.STATUS_LEASE_REJECTED
    assert "NO_LEASE_FOR_HOLD_OR_DENY_OR_FAILCLOSED" in out["reason"]


# ══════════════════════════════════════════════════════════════════════════
#  Binding mission / request
# ══════════════════════════════════════════════════════════════════════════

def test_capability_request_route_decision_mismatch(monkeypatch, tmp_path):
    ms, cr, rd = _material(monkeypatch, tmp_path, L.REASONING_LEASE)
    other_rd = RD.build_route_decision("totally other")   # router unavailable -> different id
    out = L.prepare_cognitive_capability_lease(
        lease_class=L.REASONING_LEASE, capability_request=cr, route_decision=other_rd,
        mission_submission=ms, lease_scope={"allowed_providers": ["brody"]},
        requested_capability_scope={"allowed_providers": ["brody"]})
    assert out["status"] == L.STATUS_LEASE_REJECTED


def test_cross_mission_capability_request(monkeypatch, tmp_path):
    ms_a, cr_a, rd_a = _material(monkeypatch, tmp_path, L.REASONING_LEASE, tag="A")
    ms_b, _, _ = _material(monkeypatch, tmp_path, L.REASONING_LEASE, tag="B")
    out = L.prepare_cognitive_capability_lease(
        lease_class=L.REASONING_LEASE, capability_request=cr_a, route_decision=rd_a,
        mission_submission=ms_b, lease_scope={"allowed_providers": ["brody"]},
        requested_capability_scope={"allowed_providers": ["brody"]})
    assert out["status"] == L.STATUS_LEASE_REJECTED
    assert "CAPABILITY_REQUEST_MISSION_MISMATCH" in out["reason"] or "MISSION" in out["reason"]


# ══════════════════════════════════════════════════════════════════════════
#  Portée : jamais d'élargissement, jamais ALL
# ══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("bad_scope", [
    {"allowed_paths": ["**"]},
    {"allowed_paths": ["*"]},
    {"allowed_tools": ["ALL"]},
    {"allowed_providers": ["ALL"]},
    {"allowed_providers": ["unknown_model"]},
    {"git_scope": "ALL"},
    {"allowed_operations": ["CREATE"]},
    {"allowed_operations": ["DELETE"]},
    {"write_scope": "BOUNDED_PATHS"},   # sans allowed_paths -> incomplet
    {"max_mutation_category": "UPDATE_TARGET_FROM_SOURCE"},  # sans write_scope
    {"unknown_field": 1},
])
def test_unbounded_or_invalid_scope_fail_closed(bad_scope):
    s, why = L.normalize_scope(bad_scope)
    assert s is None, f"portée non bornée acceptée: {bad_scope}"


def test_lease_scope_expansion_over_request_rejected(monkeypatch, tmp_path):
    ms, cr, rd = _material(monkeypatch, tmp_path, L.ENGINEERING_LEASE)
    requested = _eng_scope(paths=("scripts/a.py",), tools=("Edit",))
    wider = _eng_scope(paths=("scripts/a.py", "scripts/b.py"), tools=("Edit", "Write"))
    out = L.prepare_cognitive_capability_lease(
        lease_class=L.ENGINEERING_LEASE, capability_request=cr, route_decision=rd,
        mission_submission=ms, lease_scope=wider, requested_capability_scope=requested)
    assert out["status"] == L.STATUS_LEASE_REJECTED
    assert "LEASE_SCOPE_EXPANSION_OVER_REQUEST" in out["reason"]


def test_lease_may_narrow_request(monkeypatch, tmp_path):
    ms, cr, rd = _material(monkeypatch, tmp_path, L.ENGINEERING_LEASE)
    requested = _eng_scope(paths=("scripts/a.py", "scripts/b.py"), tools=("Edit", "Write"))
    narrower = _eng_scope(paths=("scripts/a.py",), tools=("Edit",))
    out = L.prepare_cognitive_capability_lease(
        lease_class=L.ENGINEERING_LEASE, capability_request=cr, route_decision=rd,
        mission_submission=ms, lease_scope=narrower, requested_capability_scope=requested)
    assert out["status"] == L.STATUS_LEASE_BUILT_INERT
    assert out["lease"]["grants_tool_access"] is False


def test_engineering_lease_without_scope_is_incomplete_inert(monkeypatch, tmp_path):
    ms, cr, rd = _material(monkeypatch, tmp_path, L.ENGINEERING_LEASE)
    out = L.prepare_cognitive_capability_lease(
        lease_class=L.ENGINEERING_LEASE, capability_request=cr, route_decision=rd,
        mission_submission=ms)   # aucune portée -> empty_scope, jamais élargie
    assert out["status"] == L.STATUS_LEASE_BUILT_INERT
    assert out["lease"]["capability_scope"] == L.empty_scope()
    assert out["lease"]["grants_tool_access"] is False


# ══════════════════════════════════════════════════════════════════════════
#  Write-once + restart
# ══════════════════════════════════════════════════════════════════════════

def test_write_once_idempotent_and_divergent_fail_closed(monkeypatch, tmp_path):
    ms, cr, rd = _material(monkeypatch, tmp_path, L.REASONING_LEASE)
    lease = L.build_cognitive_capability_lease(
        lease_class=L.REASONING_LEASE, capability_request=cr, route_decision=rd,
        mission_submission=ms, lease_scope={"allowed_providers": ["brody"]},
        requested_capability_scope={"allowed_providers": ["brody"]})
    sd = tmp_path / "lstore"
    assert L.persist_capability_lease(lease, store_dir=sd)["status"] == "STORED"
    assert L.persist_capability_lease(lease, store_dir=sd)["status"] == "IDEMPOTENT_ALREADY_EXISTS"
    tampered = dict(lease); tampered["reason"] = "changed"
    # même lease_id (on force), octets divergents
    p = sd / "capability_leases" / f"{lease['lease_id']}.json"
    p.write_text(json.dumps({**lease, "reason": "hand-edited"}, indent=2, sort_keys=True) + "\n",
                 encoding="utf-8")
    r = L.persist_capability_lease(lease, store_dir=sd)
    assert r["status"] == "LEASE_IMMUTABILITY_VIOLATION"
    assert r["divergent_lease_rewrite"] == "FAIL_CLOSED"


def test_restart_reload_no_in_memory_dependency(monkeypatch, tmp_path):
    ms, cr, rd = _material(monkeypatch, tmp_path, L.LANGUAGE_LEASE)
    lease = L.build_cognitive_capability_lease(
        lease_class=L.LANGUAGE_LEASE, capability_request=cr, route_decision=rd,
        mission_submission=ms, lease_scope={"allowed_providers": ["brody"]},
        requested_capability_scope={"allowed_providers": ["brody"]})
    sd = tmp_path / "lstore"
    L.persist_capability_lease(lease, store_dir=sd)
    lid = lease["lease_id"]
    del lease
    reloaded = L.load_capability_lease(lid, store_dir=sd)
    assert reloaded is not None and reloaded["lease_id"] == lid
    ok, why = L.verify_capability_lease(reloaded)
    assert ok, why
    assert L.load_capability_lease("cclease-" + "0" * 32, store_dir=sd) is None


# ══════════════════════════════════════════════════════════════════════════
#  Falsification (rejeu §25)
# ══════════════════════════════════════════════════════════════════════════

def _built(monkeypatch, tmp_path, cls, scope=None):
    ms, cr, rd = _material(monkeypatch, tmp_path, cls)
    scope = scope or ({"allowed_providers": ["brody"]} if cls != L.ENGINEERING_LEASE else _eng_scope())
    lease = L.build_cognitive_capability_lease(
        lease_class=cls, capability_request=cr, route_decision=rd, mission_submission=ms,
        lease_scope=scope, requested_capability_scope=scope)
    return ms, cr, rd, lease


@pytest.mark.parametrize("mut", [
    ("lease_class", L.ENGINEERING_LEASE),
    ("issued_by", "CLAUDE"),
    ("route_class", "ROUTE_LLM_ENGINEERING"),
    ("mission_submission_id", "gsub-" + "9" * 32),
    ("capability_request_id", "gcap-" + "9" * 32),
    ("route_decision_ref", "rdec-" + "9" * 32),
    ("is_execution_authority", True),
    ("grants_tool_access", True),
    ("termination_condition", "BOGUS"),
])
def test_tampered_lease_fail_closed(monkeypatch, tmp_path, mut):
    _, _, _, lease = _built(monkeypatch, tmp_path, L.REASONING_LEASE)
    bad = dict(lease); bad[mut[0]] = mut[1]
    ok, why = L.verify_capability_lease(bad)
    assert ok is False, f"falsification acceptée: {mut}"


def test_scope_field_added_after_hash_fail_closed(monkeypatch, tmp_path):
    _, _, _, lease = _built(monkeypatch, tmp_path, L.ENGINEERING_LEASE,
                            scope=_eng_scope(paths=("scripts/a.py",)))
    bad = json.loads(json.dumps(lease))
    bad["capability_scope"]["allowed_paths"].append("scripts/secret.py")
    ok, _ = L.verify_capability_lease(bad)
    assert ok is False
    bad2 = json.loads(json.dumps(lease))
    bad2["capability_scope"]["allowed_tools"].append("Bash")
    assert L.verify_capability_lease(bad2)[0] is False
    bad3 = json.loads(json.dumps(lease))
    bad3["capability_scope"]["allowed_operations"].append("DELETE")
    assert L.verify_capability_lease(bad3)[0] is False


# ══════════════════════════════════════════════════════════════════════════
#  Vérificateur contextuel — verdicts structurés
# ══════════════════════════════════════════════════════════════════════════

def test_context_valid_inert_when_scope_unbound(monkeypatch, tmp_path):
    ms, cr, rd, lease = _built(monkeypatch, tmp_path, L.REASONING_LEASE)
    v = L.verify_capability_lease_context(
        lease=lease, mission_submission=ms, capability_request=cr, route_decision=rd,
        revocations=[], mission_status="OPEN")
    assert v["verdict"] == L.V_MISSION_SCOPE_UNBOUND   # §16 : pas d'artefact de portée mission
    assert v["grants_tool_access"] is False and v["enforcement_active"] is False


def test_context_valid_inert_with_mission_scope(monkeypatch, tmp_path):
    ms, cr, rd, lease = _built(monkeypatch, tmp_path, L.ENGINEERING_LEASE,
                              scope=_eng_scope(paths=("scripts/a.py",)))
    mission_scope = _eng_scope(paths=("scripts/a.py", "scripts/b.py"), tools=("Edit", "Write"))
    v = L.verify_capability_lease_context(
        lease=lease, mission_submission=ms, capability_request=cr, route_decision=rd,
        revocations=[], mission_status="OPEN", authorized_capability_scope=mission_scope)
    assert v["verdict"] == L.V_VALID_INERT
    assert v["grants_tool_access"] is False


def test_context_scope_expansion_vs_mission(monkeypatch, tmp_path):
    ms, cr, rd, lease = _built(monkeypatch, tmp_path, L.ENGINEERING_LEASE,
                              scope=_eng_scope(paths=("scripts/a.py", "scripts/b.py")))
    tight = _eng_scope(paths=("scripts/a.py",))
    v = L.verify_capability_lease_context(
        lease=lease, mission_submission=ms, capability_request=cr, route_decision=rd,
        authorized_capability_scope=tight, mission_status="OPEN")
    assert v["verdict"] == L.V_SCOPE_EXPANSION


@pytest.mark.parametrize("status,expected", [("CLOSED", "MISSION_CLOSED"), ("HOLD", "MISSION_HOLD")])
def test_context_mission_closed_or_hold(monkeypatch, tmp_path, status, expected):
    ms, cr, rd, lease = _built(monkeypatch, tmp_path, L.REASONING_LEASE)
    v = L.verify_capability_lease_context(
        lease=lease, mission_submission=ms, capability_request=cr, route_decision=rd,
        mission_status=status, authorized_capability_scope={"allowed_providers": ["brody"]})
    assert v["verdict"] == expected


def test_context_cross_mission_and_request_and_route(monkeypatch, tmp_path):
    ms_a, cr_a, rd_a, lease = _built(monkeypatch, tmp_path, L.REASONING_LEASE)
    ms_b, cr_b, rd_b = _material(monkeypatch, tmp_path, L.REASONING_LEASE, tag="B")
    assert L.verify_capability_lease_context(
        lease=lease, mission_submission=ms_b, capability_request=cr_a,
        route_decision=rd_a)["verdict"] == L.V_MISSION_MISMATCH
    assert L.verify_capability_lease_context(
        lease=lease, mission_submission=ms_a, capability_request=cr_b,
        route_decision=rd_a)["verdict"] == L.V_REQUEST_MISMATCH
    assert L.verify_capability_lease_context(
        lease=lease, mission_submission=ms_a, capability_request=cr_a,
        route_decision=rd_b)["verdict"] == L.V_ROUTE_MISMATCH


def test_context_tampered_lease_verdict(monkeypatch, tmp_path):
    ms, cr, rd, lease = _built(monkeypatch, tmp_path, L.REASONING_LEASE)
    bad = dict(lease); bad["reason"] = "x"
    v = L.verify_capability_lease_context(lease=bad, mission_submission=ms,
                                         capability_request=cr, route_decision=rd)
    assert v["verdict"] == L.V_STRUCTURAL_INVALID


# ══════════════════════════════════════════════════════════════════════════
#  Révocation
# ══════════════════════════════════════════════════════════════════════════

def test_revocation_build_record_reload_and_context(monkeypatch, tmp_path):
    ms, cr, rd, lease = _built(monkeypatch, tmp_path, L.ENGINEERING_LEASE,
                              scope=_eng_scope(paths=("scripts/a.py",)))
    sd = tmp_path / "lstore"
    L.persist_capability_lease(lease, store_dir=sd)
    rev = L.build_lease_revocation(lease=lease, reason="operator stop")["revocation"]
    assert rev["revocation_id"].startswith("cclrev-")
    assert L.record_lease_revocation(rev, store_dir=sd)["status"] == "REVOCATION_RECORDED"
    assert L.record_lease_revocation(rev, store_dir=sd)["status"] == "IDEMPOTENT_ALREADY_EXISTS"
    revs = L.load_lease_revocations(lease["lease_id"], store_dir=sd)
    assert len(revs) == 1
    v = L.verify_capability_lease_context(
        lease=lease, mission_submission=ms, capability_request=cr, route_decision=rd,
        revocations=revs, mission_status="OPEN",
        authorized_capability_scope=_eng_scope(paths=("scripts/a.py",)))
    assert v["verdict"] == L.V_REVOKED
    assert v["grants_tool_access"] is False


def test_revocation_issuer_claude_rejected(monkeypatch, tmp_path):
    _, _, _, lease = _built(monkeypatch, tmp_path, L.REASONING_LEASE)
    out = L.build_lease_revocation(lease=lease, reason="x", issued_by="CLAUDE")
    assert out["status"] == L.STATUS_LEASE_REJECTED
    assert out["reason"].startswith("ISSUER_NOT_AUTHORIZED")


def test_revocation_tamper_and_cross_lease(monkeypatch, tmp_path):
    _, _, _, lease_a = _built(monkeypatch, tmp_path, L.REASONING_LEASE)
    _, _, _, lease_b = _built(monkeypatch, tmp_path, L.LANGUAGE_LEASE)
    rev_a = L.build_lease_revocation(lease=lease_a, reason="stop")["revocation"]
    bad = dict(rev_a); bad["reason"] = "changed"
    assert L.verify_lease_revocation(bad)[0] is False           # tamper
    assert L.verify_lease_revocation(rev_a, lease_b)[0] is False  # cross-lease substitution


def test_revocation_divergent_duplicate_fail_closed(monkeypatch, tmp_path):
    _, _, _, lease = _built(monkeypatch, tmp_path, L.REASONING_LEASE)
    sd = tmp_path / "lstore"
    rev = L.build_lease_revocation(lease=lease, reason="stop")["revocation"]
    L.record_lease_revocation(rev, store_dir=sd)
    p = sd / "capability_leases" / "revocations" / f"{rev['revocation_id']}.json"
    p.write_text(json.dumps({**rev, "reason": "hand"}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    assert L.record_lease_revocation(rev, store_dir=sd)["status"] == "REVOCATION_IMMUTABILITY_VIOLATION"


# ══════════════════════════════════════════════════════════════════════════
#  Providers n'auto-appellent rien / statique
# ══════════════════════════════════════════════════════════════════════════

def test_module_has_no_provider_autocall_or_hook():
    src = (_SCRIPTS / "obsidia_cognitive_capability_lease_v0.py").read_text(encoding="utf-8")
    for banned in ("subprocess", "urllib", "requests", "PreToolUse", "settings.local",
                   ".claude/", "run_obsidure", "agent_obsidure", "call_brody", "claude -p",
                   "atomic_replace_with_bytes", "run_and_persist_kx108"):
        assert banned not in src, banned
    assert L.LANGUAGE_LEASE_AUTO_CALLS_PROVIDER is False
    assert L.REASONING_LEASE_AUTO_CALLS_PROVIDER is False
    assert L.ENGINEERING_LEASE_AUTO_CALLS_PROVIDER is False


def test_gateway_handle_does_not_touch_lease(monkeypatch, tmp_path):
    import importlib
    import obsidia_gateway as GW
    GW = importlib.reload(GW)
    src = Path(GW.__file__).read_text(encoding="utf-8")
    assert "obsidia_cognitive_capability_lease" not in src
    guard = (_REPO_ROOT / ".claude" / "hooks" / "obsidia_pretooluse_guard.py").read_text(encoding="utf-8")
    assert "cognitive_capability_lease" not in guard


# ══════════════════════════════════════════════════════════════════════════
#  Gel : CG-B, .claude/, Stage 4, Lean
# ══════════════════════════════════════════════════════════════════════════

def test_cg_b_receipt_still_requires_null_lease_id():
    rd = RD.build_route_decision("x")
    rec = RD.build_route_receipt(rd, requested_outcome="x", selected_route=rd["route_class"],
                                reason=rd["reason"], persist=False)
    assert rec["lease_id"] is None
    bad = dict(rec); bad["lease_id"] = "cclease-" + "0" * 32
    assert RD.verify_route_receipt(bad)[0] is False


def test_frozen_paths_clean():
    r = __import__("subprocess").run(
        ["git", "status", "--porcelain", ".claude/", "proofs/lean/", "CLAUDE.md",
         "scripts/obsidia_mission_sequencer_v0.py", "scripts/obsidia_mission_authority_v0.py",
         "scripts/obsidia_governed_apply_v0.py"],
        cwd=str(_REPO_ROOT), capture_output=True, text=True)
    assert r.stdout.strip() == "", f"gelé modifié: {r.stdout}"
