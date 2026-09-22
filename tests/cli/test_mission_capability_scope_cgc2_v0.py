"""
tests/cli/test_mission_capability_scope_cgc2_v0.py
=================================================
CG-C2 — HumanCapabilityGrant + MissionCapabilityScope + LeaseIssuanceDecision :
chaîne d'autorité humaine à 4 niveaux, ENTIÈREMENT INERTE.

  LEASE ≤ REQUESTED ≤ MISSION_CAPABILITY_SCOPE ≤ HUMAN_CAPABILITY_GRANT_SCOPE
  (chemins / opérations additionnellement bornés par la HMA Stage 4 vérifiée)

Source d'autorité :
  HumanMissionAuthorization (HMA Stage 4, racine humaine)  +
  HumanCapabilityGrant (issued_by=HUMAN, hash-lié aux champs de capacité exacts).
Une chaîne opaque NE satisfait PAS l'exigence d'octroi humain.
Aucun accès outil, aucun enforcement. Stores tmp ; router externe simulé.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_SCRIPTS = _REPO_ROOT / "scripts"
for _p in (str(_SCRIPTS), str(_REPO_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import obsidia_test_contract as TC                    # noqa: E402
import obsidia_isolated_work_unit_v0 as WU            # noqa: E402
import obsidia_bounded_mission_v0 as M               # noqa: E402
import obsidia_mission_authority_v0 as MA            # noqa: E402
import obsidia_gateway_route_decision_v0 as RD       # noqa: E402
import obsidia_cognitive_capability_lease_v0 as L    # noqa: E402
import obsidia_mission_capability_scope_v0 as MCS    # noqa: E402

_TARGET = "periphery/xdomain/cgc2_target_v0.txt"
_S1 = "periphery/xdomain/cgc2_src_1.txt"
_S2 = "periphery/xdomain/cgc2_src_2.txt"
_S3 = "periphery/xdomain/cgc2_src_3.txt"


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _git(repo: Path, *a: str) -> str:
    r = subprocess.run(["git", *a], cwd=str(repo), capture_output=True, text=True)
    assert r.returncode == 0, f"git {a}: {r.stderr}"
    return r.stdout.strip()


def _contract(cid: str) -> dict:
    return TC.build_test_contract(cid, "cand", "batch", _TARGET, [
        TC.build_check("post", TC.CHECK_TYPE_TARGET_SHA256, target_path=_TARGET,
                       expected_target_sha256=_sha(b"x"), required=True),
        TC.build_check("scope", TC.CHECK_TYPE_DIFF_SCOPE,
                       expected_diff_paths=[_TARGET], required=True),
    ])


# ── Router simulé -> classe de route déterministe ──────────────────────

def _drop_fake_router():
    for m in ("app", "app.router", "app.router.decision"):
        sys.modules.pop(m, None)


def _fake_router(monkeypatch, tmp_path, route, intent, gate="ALLOW"):
    root = tmp_path / "fake_router"
    (root / "app" / "router").mkdir(parents=True, exist_ok=True)
    (root / "app" / "__init__.py").write_text("", encoding="utf-8")
    (root / "app" / "router" / "__init__.py").write_text("", encoding="utf-8")
    dec = {"route": route, "level": 1, "reason": "fake",
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


@pytest.fixture(autouse=True)
def _isolate(monkeypatch, tmp_path):
    monkeypatch.setenv("OBSIDIA_CGB_STORE_DIR", str(tmp_path / "cgb_store"))
    monkeypatch.setenv("OBSIDIA_ROUTER_ROOT", str(tmp_path / "no_router"))
    _drop_fake_router()
    yield
    _drop_fake_router()


@pytest.fixture
def env(tmp_path):
    main = tmp_path / "main"
    (main / "periphery" / "xdomain").mkdir(parents=True)
    for f in (_TARGET, _S1, _S2, _S3):
        (main / f).write_bytes(f.encode())
    _git(main, "init", "-q")
    _git(main, "config", "user.email", "t@example.com")
    _git(main, "config", "user.name", "t")
    _git(main, "config", "commit.gpgsign", "false")
    _git(main, "add", ".")
    _git(main, "commit", "-q", "-m", "seed")
    base = _git(main, "rev-parse", "HEAD")
    stores = tmp_path / "missions"
    wt = (tmp_path / "wt").resolve()
    cr = WU.create_isolated_work_unit(repo_root=main, base_sha=base, branch_name="cgc2br",
                                      worktree_path=wt, work_unit_id="wu-cgc2-0001")
    assert cr["status"] == WU.WORK_UNIT_CREATED, cr
    return {"root": tmp_path, "main": main, "base": base, "stores": stores,
            "wu": cr["work_unit"], "wt": wt}


def _abc(env):
    return [
        {"ordinal": 0, "target_path": _TARGET, "source_git_commit": env["base"],
         "source_historical_path": _S1, "test_contract": _contract("c-A"),
         "dependency_ordinals": []},
        {"ordinal": 1, "target_path": _TARGET, "source_git_commit": env["base"],
         "source_historical_path": _S2, "test_contract": _contract("c-B"),
         "dependency_ordinals": [0]},
        {"ordinal": 2, "target_path": _TARGET, "source_git_commit": env["base"],
         "source_historical_path": _S3, "test_contract": _contract("c-C"),
         "dependency_ordinals": [1]},
    ]


def _hma(env, *, allowed=(_TARGET,), tag="a"):
    g = M.create_bounded_mission(
        objective=f"cgc2-{tag}", repository_identity="repo://cgc2",
        canonical_base_sha=env["base"], branch_name="cgc2br",
        worktree_path=str(env["wt"]), main_worktree_path=str(env["main"].resolve()),
        scope={"allowed_operation_shapes": ["UPDATE_TARGET_FROM_SOURCE"],
               "allowed_target_paths": list(allowed),
               "max_actions": 3, "max_retries_per_action": 0},
        human_mandate_reference=f"human-mandate-cgc2-{tag}",
        mission_store_dir=env["stores"])
    mid = g["mission_id"]
    M.bind_work_unit(mission_id=mid, work_unit=env["wu"], mission_store_dir=env["stores"])
    r = M.bind_mission_plan(mission_id=mid, actions=_abc(env), mission_store_dir=env["stores"])
    assert r["status"] == M.STATUS_PLAN_BOUND, r
    plan_id = r["plan_id"]
    b = MA.bind_human_mission_authorization(
        mission_id=mid, plan_id=plan_id,
        human_authorization_reference=f"human-auth-ref-cgc2-{tag}",
        mission_store_dir=env["stores"])
    assert b["status"] == MA.HMA_BOUND, b
    hma = MA.load_human_mission_authorization(mid, b["human_mission_authorization_id"], env["stores"])
    genesis = M.load_mission_genesis(mid, env["stores"])
    plan = M.load_mission_plan(mid, plan_id, env["stores"])

    def _verifier(x, _g=genesis, _p=plan):
        return MA.verify_human_mission_authorization(x, genesis=_g, plan=_p, revocations=[])

    return {"mid": mid, "plan_id": plan_id, "hma": hma, "genesis": genesis,
            "plan": plan, "verifier": _verifier}


def _cgb(monkeypatch, tmp_path, lease_class, tag="m"):
    rr, intent = _ROUTE_FOR[lease_class]
    _fake_router(monkeypatch, tmp_path, rr, intent)
    sub = RD.submit_mission(requested_outcome=f"mission {tag}")
    cap = RD.request_capability(mission_submission_id=sub["mission_submission_id"],
                                requested_capability=f"cap {tag}", reason="gap")
    ms = RD.load_mission_submission(sub["mission_submission_id"])
    cr = RD.load_capability_request(cap["capability_request_id"])
    return ms, cr, cap["route_decision"]


def _eng_scope(paths=(_TARGET,), tools=("Edit",), providers=("obsidure",)):
    return {"allowed_providers": list(providers), "allowed_tools": list(tools),
            "allowed_paths": list(paths), "allowed_operations": ["UPDATE_TARGET_FROM_SOURCE"],
            "read_scope": "BOUNDED_PATHS", "write_scope": "BOUNDED_PATHS",
            "test_scope": "BOUNDED", "git_scope": "READ_ONLY",
            "max_mutation_category": "UPDATE_TARGET_FROM_SOURCE"}


# Vérificateur d'autorisation humaine INJECTÉ (simule la frontière hôte :
# confirmation terminale / reçu signé / EAH d'une HumanApproval canonique).
_HUMAN_OK = lambda payload: (True, None)
_HUMAN_NO = lambda payload: (False, "human_declined")


def _hcga(h, ms, *, tag="a", classes=None, scope=None, verifier=_HUMAN_OK,
          decision_ref=None):
    out = MCS.prepare_human_capability_grant_authorization(
        hma=h["hma"], hma_verifier=h["verifier"],
        mission_submission_id=ms["mission_submission_id"],
        allowed_lease_classes=classes or [L.ENGINEERING_LEASE],
        capability_scope=scope or _eng_scope(paths=(_TARGET,), tools=("Edit", "Write")),
        human_decision_ref=decision_ref or f"human-decision-{tag}",
        human_authorization_verifier=verifier)
    assert out["status"] == MCS.STATUS_HCGA_ACTIVE, out
    return out["record"]


def _grant(h, ms, *, tag="a", classes=None, scope=None, hcga=None):
    classes = classes or [L.ENGINEERING_LEASE]
    scope = scope or _eng_scope(paths=(_TARGET,), tools=("Edit", "Write"))
    auth = hcga if hcga is not None else _hcga(h, ms, tag=tag, classes=classes, scope=scope)
    out = MCS.prepare_human_capability_grant(
        hma=h["hma"], hma_verifier=h["verifier"],
        human_capability_grant_authorization=auth,
        mission_submission_id=ms["mission_submission_id"],
        allowed_lease_classes=classes, capability_scope=scope)
    assert out["status"] == MCS.STATUS_HCG_ACTIVE, out
    return out["record"]


def _mk_mcs(env, monkeypatch, tmp_path, *, tag="a", mission_scope=None, lease_classes=None,
            grant_scope=None, grant_classes=None):
    h = _hma(env, tag=tag)
    ms, cr, rd = _cgb(monkeypatch, tmp_path, L.ENGINEERING_LEASE, tag=tag)
    grant = _grant(h, ms, tag=tag, classes=grant_classes or [L.ENGINEERING_LEASE],
                   scope=grant_scope or _eng_scope(paths=(_TARGET,), tools=("Edit", "Write")))
    out = MCS.prepare_mission_capability_scope(
        hma=h["hma"], hma_verifier=h["verifier"], human_capability_grant=grant,
        mission_submission_id=ms["mission_submission_id"],
        allowed_lease_classes=lease_classes or [L.ENGINEERING_LEASE],
        capability_scope=mission_scope or _eng_scope(paths=(_TARGET,), tools=("Edit", "Write")))
    assert out["status"] == MCS.STATUS_MCS_ACTIVE_INERT, out
    return h, ms, cr, rd, grant, out["record"]


# ══════════════════════════════════════════════════════════════════════════
#  Bornes d'inertie
# ══════════════════════════════════════════════════════════════════════════

def test_inertness_constants():
    assert MCS.MISSION_CAPABILITY_SCOPE_RUNTIME == "IMPLEMENTED_INERT_V0"
    assert MCS.LEASE_ISSUANCE_DECISION_RUNTIME == "IMPLEMENTED_INERT_V0"
    assert MCS.MISSION_CAPABILITY_SCOPE_BINDING == "ACTIVE"
    assert MCS.HUMAN_CAPABILITY_GRANT_VERIFICATION == "ACTIVE"
    assert MCS.HUMAN_CAPABILITY_GRANT_AUTHORIZATION_VERIFICATION == "ACTIVE"
    # frontière de confiance externe — formulation véridique (pas de surclamation)
    assert MCS.HUMAN_CAPABILITY_GRANT_ORIGIN_SELF_ASSERTED is False
    assert MCS.HUMAN_AUTHORIZATION_VERIFIER_REQUIRED is True
    assert MCS.HUMAN_AUTHORIZATION_VERIFIER_IMPLEMENTATION_WIRED is False
    assert MCS.HUMAN_ORIGIN_PROOF_MODEL == "EXTERNAL_TRUST_BOUNDARY"
    assert MCS.TRUSTED_HUMAN_AUTHORIZATION_HOST_BINDING == "NOT_YET_ENFORCED"
    assert MCS.CLAUDE_CANNOT_BYPASS_HOST_TRUST_BOUNDARY == "NOT_YET_PROVEN"
    assert MCS.HUMAN_COGNITIVE_CAPABILITY_GRANT_BINDING == "VERIFIED_CONDITIONAL_ON_EXTERNAL_HUMAN_VERIFIER"
    assert MCS.PRECONDITION_CGE_1_TRUSTED_HUMAN_AUTHORIZATION_HOST_BINDING == "OPEN"
    assert MCS.CG_D_SHADOW_MAY_PROCEED_WITH_EXTERNAL_TRUST_BOUNDARY_UNWIRED is True
    assert MCS.CG_E_ACTIVE_ENFORCEMENT_REQUIRES_TRUSTED_HUMAN_AUTHORIZATION_HOST_BINDING is True
    assert not hasattr(MCS, "CLAUDE_CAN_CREATE_HUMAN_CAPABILITY_GRANT")  # surclamation retirée
    assert MCS.MISSION_CAPABILITY_SCOPE_IS_EXECUTION_AUTHORITY is False
    assert MCS.MISSION_CAPABILITY_SCOPE_IS_KX_AUTHORITY is False
    assert MCS.LEASE_ISSUANCE_DECISION_IS_EXECUTION_AUTHORITY is False
    assert MCS.LEASE_ISSUANCE_DECISION_IS_KX_AUTHORITY is False
    assert MCS.LEASE_GRANTS_TOOL_ACCESS is False
    assert MCS.LEASE_ENFORCEMENT_ACTIVE is False
    assert MCS.HARD_TOOL_GATE_ACTIVE is False
    assert MCS.PRE_TOOL_LEASE_LOOKUP_ACTIVE is False
    assert MCS.CLAUDE_ROLE_TRANSPORT_ONLY_TECHNICALLY_ENFORCED is False
    assert MCS.DEFAULT_MISSION_CAPABILITY_SCOPE == "EMPTY_NOT_ALL"
    assert MCS.MULTI_OPERATION_GENERALIZATION == "NOT_YET_PROVEN"


# ══════════════════════════════════════════════════════════════════════════
#  HumanCapabilityGrantAuthorization — preuve d'origine humaine (§9)
# ══════════════════════════════════════════════════════════════════════════

def _candidate_material_hash(h, ms, *, classes, scope):
    return MCS._candidate_material_hash(MCS._candidate_material(
        hma=h["hma"], mission_submission_id=ms["mission_submission_id"],
        allowed_lease_classes=classes, capability_scope=scope))


def test_grant_needs_verified_human_authorization(env, monkeypatch, tmp_path):
    """§9 : issued_by="HUMAN" par défaut SANS autorisation vérifiée -> FAIL_CLOSED."""
    h = _hma(env)
    ms, _, _ = _cgb(monkeypatch, tmp_path, L.ENGINEERING_LEASE)
    out = MCS.prepare_human_capability_grant_authorization(
        hma=h["hma"], hma_verifier=h["verifier"],
        mission_submission_id=ms["mission_submission_id"],
        allowed_lease_classes=[L.ENGINEERING_LEASE],
        capability_scope=_eng_scope(paths=(_TARGET,)),
        human_decision_ref="hd", human_authorization_verifier=None)
    assert out["status"] == MCS.STATUS_HCGA_REJECTED
    assert "HUMAN_AUTHORIZATION_VERIFIER_REQUIRED" in out["reason"]


def test_grant_human_authorization_declined(env, monkeypatch, tmp_path):
    """§9 : autorisation humaine explicitement refusée -> FAIL_CLOSED."""
    h = _hma(env)
    ms, _, _ = _cgb(monkeypatch, tmp_path, L.ENGINEERING_LEASE)
    out = MCS.prepare_human_capability_grant_authorization(
        hma=h["hma"], hma_verifier=h["verifier"],
        mission_submission_id=ms["mission_submission_id"],
        allowed_lease_classes=[L.ENGINEERING_LEASE],
        capability_scope=_eng_scope(paths=(_TARGET,)),
        human_decision_ref="hd", human_authorization_verifier=_HUMAN_NO)
    assert out["status"] == MCS.STATUS_HCGA_REJECTED
    assert out["reason"].startswith("HCGA_HUMAN_AUTHORIZATION_UNVERIFIED")


def test_grant_arbitrary_string_authorization_rejected(env, monkeypatch, tmp_path):
    """§9 : une chaîne d'autorisation seule ne peut pas créer un grant."""
    h = _hma(env)
    ms, _, _ = _cgb(monkeypatch, tmp_path, L.ENGINEERING_LEASE)
    out = MCS.prepare_human_capability_grant(
        hma=h["hma"], hma_verifier=h["verifier"],
        human_capability_grant_authorization="i-am-human-trust-me",
        mission_submission_id=ms["mission_submission_id"],
        allowed_lease_classes=[L.ENGINEERING_LEASE], capability_scope=_eng_scope(paths=(_TARGET,)))
    assert out["status"] == MCS.STATUS_HCG_REJECTED
    assert out["reason"].startswith("HCG_HUMAN_AUTHORIZATION_UNVERIFIED")


def test_grant_authorization_for_another_candidate_hash_rejected(env, monkeypatch, tmp_path):
    """§9 : autorisation pour un AUTRE matériel candidat -> FAIL_CLOSED."""
    h = _hma(env)
    ms, _, _ = _cgb(monkeypatch, tmp_path, L.ENGINEERING_LEASE)
    # autorisation émise pour une portée Edit-seule
    hcga = _hcga(h, ms, scope=_eng_scope(paths=(_TARGET,), tools=("Edit",)))
    # mais on demande un grant Edit+Write
    out = MCS.prepare_human_capability_grant(
        hma=h["hma"], hma_verifier=h["verifier"], human_capability_grant_authorization=hcga,
        mission_submission_id=ms["mission_submission_id"],
        allowed_lease_classes=[L.ENGINEERING_LEASE],
        capability_scope=_eng_scope(paths=(_TARGET,), tools=("Edit", "Write")))
    assert out["status"] == MCS.STATUS_HCG_REJECTED
    assert out["reason"].startswith("HCG_HUMAN_AUTHORIZATION_UNVERIFIED")


def test_grant_authorization_for_another_mission_rejected(env, monkeypatch, tmp_path):
    """§9 : autorisation d'une autre mission -> FAIL_CLOSED."""
    h_a = _hma(env, tag="A")
    ms_a, _, _ = _cgb(monkeypatch, tmp_path, L.ENGINEERING_LEASE, tag="A")
    h_b = _hma(env, tag="B")
    ms_b, _, _ = _cgb(monkeypatch, tmp_path, L.ENGINEERING_LEASE, tag="B")
    hcga_b = _hcga(h_b, ms_b, tag="B")
    out = MCS.prepare_human_capability_grant(
        hma=h_a["hma"], hma_verifier=h_a["verifier"], human_capability_grant_authorization=hcga_b,
        mission_submission_id=ms_a["mission_submission_id"],
        allowed_lease_classes=[L.ENGINEERING_LEASE], capability_scope=_eng_scope(paths=(_TARGET,)))
    assert out["status"] == MCS.STATUS_HCG_REJECTED


def test_grant_authorization_narrower_scope_rejected(env, monkeypatch, tmp_path):
    """§9 : autorisation pour une portée plus étroite que le grant demandé -> FAIL_CLOSED
    (hash candidat différent)."""
    h = _hma(env)
    ms, _, _ = _cgb(monkeypatch, tmp_path, L.ENGINEERING_LEASE)
    hcga = _hcga(h, ms, classes=[L.ENGINEERING_LEASE], scope=_eng_scope(paths=(_TARGET,), tools=("Edit",)))
    out = MCS.prepare_human_capability_grant(
        hma=h["hma"], hma_verifier=h["verifier"], human_capability_grant_authorization=hcga,
        mission_submission_id=ms["mission_submission_id"],
        allowed_lease_classes=[L.ENGINEERING_LEASE, L.LANGUAGE_LEASE],
        capability_scope=_eng_scope(paths=(_TARGET,), tools=("Edit",)))
    assert out["status"] == MCS.STATUS_HCG_REJECTED


def test_grant_authorization_tampered_rejected(env, monkeypatch, tmp_path):
    h = _hma(env)
    ms, _, _ = _cgb(monkeypatch, tmp_path, L.ENGINEERING_LEASE)
    hcga = _hcga(h, ms)
    bad = dict(hcga); bad["candidate_material_hash"] = "z" * 64
    assert MCS.verify_human_capability_grant_authorization(bad)[0] is False
    bad2 = dict(hcga); bad2["approved_by"] = "CLAUDE"
    assert MCS.verify_human_capability_grant_authorization(bad2)[0] is False
    out = MCS.prepare_human_capability_grant(
        hma=h["hma"], hma_verifier=h["verifier"], human_capability_grant_authorization=bad,
        mission_submission_id=ms["mission_submission_id"],
        allowed_lease_classes=[L.ENGINEERING_LEASE], capability_scope=_eng_scope(paths=(_TARGET,), tools=("Edit", "Write")))
    assert out["status"] == MCS.STATUS_HCG_REJECTED


def test_grant_authorization_replayed_against_different_grant_material(env, monkeypatch, tmp_path):
    """§9 : autorisation valide rejouée contre un autre matériel de grant -> FAIL_CLOSED."""
    h = _hma(env)
    ms, _, _ = _cgb(monkeypatch, tmp_path, L.ENGINEERING_LEASE)
    hcga = _hcga(h, ms, classes=[L.ENGINEERING_LEASE], scope=_eng_scope(paths=(_TARGET,), tools=("Edit",)))
    ok = MCS.prepare_human_capability_grant(
        hma=h["hma"], hma_verifier=h["verifier"], human_capability_grant_authorization=hcga,
        mission_submission_id=ms["mission_submission_id"],
        allowed_lease_classes=[L.ENGINEERING_LEASE], capability_scope=_eng_scope(paths=(_TARGET,), tools=("Edit",)))
    assert ok["status"] == MCS.STATUS_HCG_ACTIVE
    replay = MCS.prepare_human_capability_grant(
        hma=h["hma"], hma_verifier=h["verifier"], human_capability_grant_authorization=hcga,
        mission_submission_id=ms["mission_submission_id"],
        allowed_lease_classes=[L.LANGUAGE_LEASE], capability_scope=_eng_scope(paths=(_TARGET,), tools=("Edit",),
                                                                             providers=("brody",)))
    assert replay["status"] == MCS.STATUS_HCG_REJECTED


def test_grant_valid_exact_human_authorization_pass(env, monkeypatch, tmp_path):
    h = _hma(env)
    ms, _, _ = _cgb(monkeypatch, tmp_path, L.ENGINEERING_LEASE)
    a = _grant(h, ms)
    b = _grant(h, ms)
    assert a["human_capability_grant_id"] == b["human_capability_grant_id"]
    assert a["grant_record_hash"] == b["grant_record_hash"]
    assert a["human_capability_grant_id"].startswith("hcg-")
    assert a["issued_by"] == "HUMAN"
    assert a["human_capability_grant_authorization_id"].startswith("hcga-")
    assert a["candidate_material_hash"] == _candidate_material_hash(
        h, ms, classes=[L.ENGINEERING_LEASE], scope=_eng_scope(paths=(_TARGET,), tools=("Edit", "Write")))
    for bit in ("is_execution_authority", "is_kx_authority", "is_sovereign", "grants_tool_access"):
        assert a[bit] is False
    assert MCS.verify_human_capability_grant(a) == (True, None)
    assert MCS.verify_human_capability_grant(a, hma=h["hma"], hma_verifier=h["verifier"]) == (True, None)
    hcga = _hcga(h, ms)
    assert MCS.verify_human_capability_grant(a, human_capability_grant_authorization=hcga) == (True, None)


def test_grant_no_issued_by_parameter(env, monkeypatch, tmp_path):
    h = _hma(env)
    ms, _, _ = _cgb(monkeypatch, tmp_path, L.ENGINEERING_LEASE)
    with pytest.raises(TypeError):
        MCS.prepare_human_capability_grant(
            hma=h["hma"], hma_verifier=h["verifier"],
            human_capability_grant_authorization=_hcga(h, ms),
            mission_submission_id=ms["mission_submission_id"],
            allowed_lease_classes=[L.ENGINEERING_LEASE],
            capability_scope=_eng_scope(paths=(_TARGET,), tools=("Edit", "Write")),
            issued_by="HUMAN")  # paramètre supprimé


def test_grant_scope_fail_closed_via_authorization(env, monkeypatch, tmp_path):
    h = _hma(env)
    ms, _, _ = _cgb(monkeypatch, tmp_path, L.ENGINEERING_LEASE)
    for bad in ({"allowed_paths": ["**"]}, {"allowed_tools": ["ALL"]},
                {"allowed_providers": ["nope"]}, {"allowed_operations": ["CREATE"]}):
        out = MCS.prepare_human_capability_grant_authorization(
            hma=h["hma"], hma_verifier=h["verifier"],
            mission_submission_id=ms["mission_submission_id"],
            allowed_lease_classes=[L.ENGINEERING_LEASE], capability_scope=bad,
            human_decision_ref="hd", human_authorization_verifier=_HUMAN_OK)
        assert out["status"] == MCS.STATUS_HCGA_REJECTED


def test_grant_tamper_fail_closed(env, monkeypatch, tmp_path):
    h = _hma(env)
    ms, _, _ = _cgb(monkeypatch, tmp_path, L.ENGINEERING_LEASE)
    g = _grant(h, ms)
    for f, v in [("issued_by", "CLAUDE"), ("human_authorization_reference", "forged"),
                 ("candidate_material_hash", "x" * 64),
                 ("human_capability_grant_authorization_hash", "y" * 64),
                 ("grant_record_hash", "z" * 64), ("is_execution_authority", True),
                 ("status", "BOGUS")]:
        bad = dict(g); bad[f] = v
        assert MCS.verify_human_capability_grant(bad)[0] is False
    bad_scope = json.loads(json.dumps(g))
    bad_scope["capability_scope"]["allowed_tools"].append("Bash")
    assert MCS.verify_human_capability_grant(bad_scope)[0] is False


def test_grant_write_once_and_reload(env, monkeypatch, tmp_path):
    h = _hma(env)
    ms, _, _ = _cgb(monkeypatch, tmp_path, L.ENGINEERING_LEASE)
    hcga = _hcga(h, ms)
    g = _grant(h, ms, hcga=hcga)
    sd = tmp_path / "cgb_store"
    assert MCS.persist_human_capability_grant_authorization(hcga, store_dir=sd)["status"] == "STORED"
    assert MCS.persist_human_capability_grant(g, store_dir=sd)["status"] == "STORED"
    assert MCS.persist_human_capability_grant(g, store_dir=sd)["status"] == "IDEMPOTENT_ALREADY_EXISTS"
    p = sd / "human_capability_grants" / f"{g['human_capability_grant_id']}.json"
    p.write_text(json.dumps({**g, "status": "hand"}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    assert MCS.persist_human_capability_grant(g, store_dir=sd)["status"] == "HCG_IMMUTABILITY_VIOLATION"
    p.write_text(json.dumps(g, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    assert MCS.load_human_capability_grant(g["human_capability_grant_id"], store_dir=sd) == g
    assert MCS.load_human_capability_grant_authorization(
        hcga["human_capability_grant_authorization_id"], store_dir=sd) == hcga


# ══════════════════════════════════════════════════════════════════════════
#  MissionCapabilityScope liée à l'octroi humain
# ══════════════════════════════════════════════════════════════════════════

def test_mcs_binds_verified_grant(env, monkeypatch, tmp_path):
    _, _, _, _, grant, mcs = _mk_mcs(env, monkeypatch, tmp_path)
    assert mcs["human_capability_grant_id"] == grant["human_capability_grant_id"]
    assert mcs["human_capability_grant_hash"] == grant["grant_record_hash"]
    assert "human_capability_grant_reference" not in mcs
    assert MCS.verify_mission_capability_scope(mcs) == (True, None)


def test_mcs_missing_grant_rejected(env, monkeypatch, tmp_path):
    h = _hma(env)
    ms, _, _ = _cgb(monkeypatch, tmp_path, L.ENGINEERING_LEASE)
    out = MCS.prepare_mission_capability_scope(
        hma=h["hma"], hma_verifier=h["verifier"], human_capability_grant=None,
        mission_submission_id=ms["mission_submission_id"],
        allowed_lease_classes=[L.ENGINEERING_LEASE], capability_scope=_eng_scope())
    assert out["status"] == MCS.STATUS_MCS_REJECTED
    assert out["reason"].startswith("HUMAN_CAPABILITY_GRANT_INVALID")


def test_mcs_scope_cannot_exceed_grant(env, monkeypatch, tmp_path):
    h = _hma(env)
    ms, _, _ = _cgb(monkeypatch, tmp_path, L.ENGINEERING_LEASE)
    grant = _grant(h, ms, scope=_eng_scope(paths=(_TARGET,), tools=("Edit",)))
    out = MCS.prepare_mission_capability_scope(
        hma=h["hma"], hma_verifier=h["verifier"], human_capability_grant=grant,
        mission_submission_id=ms["mission_submission_id"],
        allowed_lease_classes=[L.ENGINEERING_LEASE],
        capability_scope=_eng_scope(paths=(_TARGET,), tools=("Edit", "Write")))
    assert out["status"] == MCS.STATUS_MCS_REJECTED
    assert out["reason"].startswith("MCS_CAPABILITY_SCOPE_EXCEEDS_HUMAN_GRANT")


def test_mcs_lease_classes_cannot_exceed_grant(env, monkeypatch, tmp_path):
    h = _hma(env)
    ms, _, _ = _cgb(monkeypatch, tmp_path, L.ENGINEERING_LEASE)
    grant = _grant(h, ms, classes=[L.ENGINEERING_LEASE])
    out = MCS.prepare_mission_capability_scope(
        hma=h["hma"], hma_verifier=h["verifier"], human_capability_grant=grant,
        mission_submission_id=ms["mission_submission_id"],
        allowed_lease_classes=[L.ENGINEERING_LEASE, L.LANGUAGE_LEASE],
        capability_scope=_eng_scope(paths=(_TARGET,), tools=("Edit", "Write")))
    assert out["status"] == MCS.STATUS_MCS_REJECTED
    assert out["reason"].startswith("MCS_LEASE_CLASSES_EXCEED_HUMAN_GRANT")


def test_mcs_grant_mission_mismatch(env, monkeypatch, tmp_path):
    h_a = _hma(env, tag="A")
    ms_a, _, _ = _cgb(monkeypatch, tmp_path, L.ENGINEERING_LEASE, tag="A")
    ms_b, _, _ = _cgb(monkeypatch, tmp_path, L.ENGINEERING_LEASE, tag="B")
    grant_a = _grant(h_a, ms_a, tag="A")
    out = MCS.prepare_mission_capability_scope(
        hma=h_a["hma"], hma_verifier=h_a["verifier"], human_capability_grant=grant_a,
        mission_submission_id=ms_b["mission_submission_id"],
        allowed_lease_classes=[L.ENGINEERING_LEASE],
        capability_scope=_eng_scope(paths=(_TARGET,)))
    assert out["status"] == MCS.STATUS_MCS_REJECTED
    assert out["reason"] in ("GRANT_MISSION_SUBMISSION_MISMATCH",)


def test_mcs_grant_from_mission_a_used_for_mission_b(env, monkeypatch, tmp_path):
    h_a = _hma(env, tag="A")
    ms_a, _, _ = _cgb(monkeypatch, tmp_path, L.ENGINEERING_LEASE, tag="A")
    h_b = _hma(env, tag="B")
    ms_b, _, _ = _cgb(monkeypatch, tmp_path, L.ENGINEERING_LEASE, tag="B")
    grant_a = _grant(h_a, ms_a, tag="A")
    # grant_a est chaîné à HMA_A ; on essaie avec HMA_B
    out = MCS.prepare_mission_capability_scope(
        hma=h_b["hma"], hma_verifier=h_b["verifier"], human_capability_grant=grant_a,
        mission_submission_id=ms_a["mission_submission_id"],
        allowed_lease_classes=[L.ENGINEERING_LEASE],
        capability_scope=_eng_scope(paths=(_TARGET,)))
    assert out["status"] == MCS.STATUS_MCS_REJECTED
    assert out["reason"].startswith("HUMAN_CAPABILITY_GRANT_INVALID")


def test_mcs_altered_after_grant_fail_closed(env, monkeypatch, tmp_path):
    _, _, _, _, grant, mcs = _mk_mcs(env, monkeypatch, tmp_path)
    bad = json.loads(json.dumps(mcs))
    bad["capability_scope"]["allowed_tools"].append("Bash")
    assert MCS.verify_mission_capability_scope(bad)[0] is False
    bad2 = dict(mcs); bad2["human_capability_grant_hash"] = "z" * 64
    assert MCS.verify_mission_capability_scope(bad2)[0] is False


def test_mcs_default_scope_empty_not_all(env, monkeypatch, tmp_path):
    h = _hma(env)
    ms, _, _ = _cgb(monkeypatch, tmp_path, L.ENGINEERING_LEASE)
    grant = _grant(h, ms, classes=[L.LANGUAGE_LEASE], scope=_eng_scope(tools=("Edit",)))
    out = MCS.prepare_mission_capability_scope(
        hma=h["hma"], hma_verifier=h["verifier"], human_capability_grant=grant,
        mission_submission_id=ms["mission_submission_id"],
        allowed_lease_classes=[L.LANGUAGE_LEASE], capability_scope=None)
    assert out["record"]["capability_scope"] == L.empty_scope()


def test_mcs_write_once_and_reload(env, monkeypatch, tmp_path):
    _, _, _, _, _, mcs = _mk_mcs(env, monkeypatch, tmp_path)
    sd = tmp_path / "cgb_store"
    assert MCS.persist_mission_capability_scope(mcs, store_dir=sd)["status"] == "STORED"
    assert MCS.persist_mission_capability_scope(mcs, store_dir=sd)["status"] == "IDEMPOTENT_ALREADY_EXISTS"
    p = sd / "mission_capability_scopes" / f"{mcs['mission_capability_scope_id']}.json"
    p.write_text(json.dumps({**mcs, "status": "hand"}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    r = MCS.persist_mission_capability_scope(mcs, store_dir=sd)
    assert r["status"] == "MCS_IMMUTABILITY_VIOLATION"
    p.write_text(json.dumps(mcs, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    assert MCS.load_mission_capability_scope(mcs["mission_capability_scope_id"], store_dir=sd) == mcs


# ══════════════════════════════════════════════════════════════════════════
#  LeaseIssuanceDecision — exige la chaîne humaine complète
# ══════════════════════════════════════════════════════════════════════════

def _issue(env, monkeypatch, tmp_path, *, lease_scope=None, mission_scope=None,
           lease_class=L.ENGINEERING_LEASE, mission_status="ACTIVE", tag="a",
           lease_classes=None, grant_scope=None, grant_classes=None,
           human_capability_grant="__default__"):
    h, ms, cr, rd, grant, mcs = _mk_mcs(
        env, monkeypatch, tmp_path, tag=tag, mission_scope=mission_scope,
        lease_classes=lease_classes, grant_scope=grant_scope, grant_classes=grant_classes)
    g = grant if human_capability_grant == "__default__" else human_capability_grant
    dec = MCS.evaluate_lease_issuance(
        mission_submission=ms, capability_request=cr, route_decision=rd,
        mission_capability_scope=mcs, proposed_lease_class=lease_class,
        proposed_lease_scope=lease_scope or _eng_scope(paths=(_TARGET,)),
        mission_status=mission_status, human_capability_grant=g,
        mcs_hma=h["hma"], hma_verifier=h["verifier"])
    return h, ms, cr, rd, grant, mcs, dec


def test_issuance_eligible_with_full_chain(env, monkeypatch, tmp_path):
    *_, dec = _issue(env, monkeypatch, tmp_path)
    assert dec["outcome"] == MCS.LEASE_ELIGIBLE_INERT
    assert dec["lease_issuance_decision_id"].startswith("lidec-")
    assert dec["human_capability_grant_ref"].startswith("hcg-")
    assert dec["is_execution_authority"] is False and dec["is_kx_authority"] is False
    assert dec["grants_tool_access"] is False
    assert MCS.verify_lease_issuance_decision(dec) == (True, None)


def test_issuance_without_grant_not_eligible(env, monkeypatch, tmp_path):
    *_, dec = _issue(env, monkeypatch, tmp_path, human_capability_grant=None)
    assert dec["outcome"] == MCS.LEASE_HOLD_HUMAN_CAPABILITY_GRANT_MISSING


def test_issuance_with_string_grant_not_eligible(env, monkeypatch, tmp_path):
    *_, dec = _issue(env, monkeypatch, tmp_path, human_capability_grant="opaque")
    assert dec["outcome"] == MCS.LEASE_DENIED_AUTHORITY_GAP


def test_issuance_with_tampered_grant_not_eligible(env, monkeypatch, tmp_path):
    h, ms, cr, rd, grant, mcs = _mk_mcs(env, monkeypatch, tmp_path)
    bad = dict(grant); bad["human_authorization_reference"] = "changed"
    dec = MCS.evaluate_lease_issuance(
        mission_submission=ms, capability_request=cr, route_decision=rd,
        mission_capability_scope=mcs, proposed_lease_class=L.ENGINEERING_LEASE,
        proposed_lease_scope=_eng_scope(paths=(_TARGET,)), mission_status="ACTIVE",
        human_capability_grant=bad, mcs_hma=h["hma"], hma_verifier=h["verifier"])
    assert dec["outcome"] == MCS.LEASE_DENIED_AUTHORITY_GAP


def test_issuance_with_substituted_grant_not_eligible(env, monkeypatch, tmp_path):
    h, ms, cr, rd, grant, mcs = _mk_mcs(env, monkeypatch, tmp_path, tag="A")
    # un grant valide mais d'une AUTRE mission
    h2 = _hma(env, tag="B")
    ms2, _, _ = _cgb(monkeypatch, tmp_path, L.ENGINEERING_LEASE, tag="B")
    other = _grant(h2, ms2, tag="B")
    dec = MCS.evaluate_lease_issuance(
        mission_submission=ms, capability_request=cr, route_decision=rd,
        mission_capability_scope=mcs, proposed_lease_class=L.ENGINEERING_LEASE,
        proposed_lease_scope=_eng_scope(paths=(_TARGET,)), mission_status="ACTIVE",
        human_capability_grant=other, mcs_hma=h["hma"], hma_verifier=h["verifier"])
    assert dec["outcome"] == MCS.LEASE_DENIED_AUTHORITY_GAP


def test_issuance_denied_scope(env, monkeypatch, tmp_path):
    *_, dec = _issue(env, monkeypatch, tmp_path,
                     grant_scope=_eng_scope(paths=(_TARGET,), tools=("Edit",)),
                     mission_scope=_eng_scope(paths=(_TARGET,), tools=("Edit",)),
                     lease_scope=_eng_scope(paths=(_TARGET,), tools=("Edit", "Write")))
    assert dec["outcome"] == MCS.LEASE_DENIED_SCOPE


def test_issuance_denied_mission_state(env, monkeypatch, tmp_path):
    for st in ("HOLD", "CLOSED", "REVOKED"):
        *_, dec = _issue(env, monkeypatch, tmp_path, mission_status=st, tag=f"s{st}")
        assert dec["outcome"] == MCS.LEASE_DENIED_MISSION_STATE


def test_issuance_denied_issuer(env, monkeypatch, tmp_path):
    h, ms, cr, rd, grant, mcs = _mk_mcs(env, monkeypatch, tmp_path)
    dec = MCS.evaluate_lease_issuance(
        mission_submission=ms, capability_request=cr, route_decision=rd,
        mission_capability_scope=mcs, proposed_lease_class=L.ENGINEERING_LEASE,
        proposed_lease_scope=_eng_scope(paths=(_TARGET,)), mission_status="ACTIVE",
        human_capability_grant=grant, issued_by="CLAUDE")
    assert dec["outcome"] == MCS.LEASE_DENIED_ISSUER


def test_issuance_decision_tamper_fail_closed(env, monkeypatch, tmp_path):
    *_, dec = _issue(env, monkeypatch, tmp_path)
    for f, v in [("outcome", "LEASE_DENIED_SCOPE"), ("human_capability_grant_ref", "hcg-" + "9" * 32),
                 ("proposed_lease_class", "LANGUAGE_LEASE"), ("is_kx_authority", True)]:
        bad = dict(dec); bad[f] = v
        assert MCS.verify_lease_issuance_decision(bad)[0] is False



def test_issuance_decision_write_once_and_reload(env, monkeypatch, tmp_path):
    *_, dec = _issue(env, monkeypatch, tmp_path)
    sd = tmp_path / "cgb_store"
    assert MCS.persist_lease_issuance_decision(dec, store_dir=sd)["status"] == "STORED"
    assert MCS.persist_lease_issuance_decision(dec, store_dir=sd)["status"] == "IDEMPOTENT_ALREADY_EXISTS"

    p = sd / "lease_issuance_decisions" / f"{dec['lease_issuance_decision_id']}.json"
    p.write_text(
        json.dumps({**dec, "reason": "hand-edited"}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    r = MCS.persist_lease_issuance_decision(dec, store_dir=sd)
    assert r["status"] == "LIDEC_IMMUTABILITY_VIOLATION"
    assert r["divergent_lidec_rewrite"] == "FAIL_CLOSED"

    p.write_text(json.dumps(dec, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    assert MCS.load_lease_issuance_decision(
        dec["lease_issuance_decision_id"], store_dir=sd
    ) == dec

# ══════════════════════════════════════════════════════════════════════════
#  Bail v2 — chaîne à 4 niveaux
# ══════════════════════════════════════════════════════════════════════════

def _v2_lease(env, monkeypatch, tmp_path, *, lease_scope=None, req_scope=None,
              mission_scope=None, grant_scope=None, tag="a",
              lease_class=L.ENGINEERING_LEASE, lease_classes=None, grant_classes=None):
    h, ms, cr, rd, grant, mcs, dec = _issue(
        env, monkeypatch, tmp_path, tag=tag, mission_scope=mission_scope,
        grant_scope=grant_scope, lease_scope=lease_scope or _eng_scope(paths=(_TARGET,)),
        lease_class=lease_class, lease_classes=lease_classes, grant_classes=grant_classes)
    assert dec["outcome"] == MCS.LEASE_ELIGIBLE_INERT, dec
    out = L.prepare_cognitive_capability_lease(
        lease_class=lease_class, capability_request=cr, route_decision=rd,
        mission_submission=ms,
        lease_scope=lease_scope or _eng_scope(paths=(_TARGET,)),
        requested_capability_scope=req_scope or _eng_scope(paths=(_TARGET,), tools=("Edit", "Write")),
        mission_capability_scope=mcs, lease_issuance_decision=dec)
    return h, ms, cr, rd, grant, mcs, dec, out


def test_v2_lease_builds_and_context_valid_inert(env, monkeypatch, tmp_path):
    h, ms, cr, rd, grant, mcs, dec, out = _v2_lease(env, monkeypatch, tmp_path)
    assert out["status"] == L.STATUS_LEASE_BUILT_INERT, out
    lease = out["lease"]
    assert lease["schema_version"] == L.SCHEMA_VERSION_MISSION_BOUND
    assert lease["mission_capability_scope_binding"] == "ACTIVE"
    assert lease["grants_tool_access"] is False and lease["lease_enforcement_active"] is False
    v = L.verify_capability_lease_context(
        lease=lease, mission_submission=ms, capability_request=cr, route_decision=rd,
        revocations=[], mission_status="OPEN",
        mission_capability_scope=mcs, lease_issuance_decision=dec, human_capability_grant=grant)
    assert v["verdict"] == L.V_VALID_INERT
    assert v["grants_tool_access"] is False and v["enforcement_active"] is False
    assert v["human_capability_grant_binding"] == "VERIFIED_CONDITIONAL_ON_EXTERNAL_HUMAN_VERIFIER"
    assert v["human_origin_proof_model"] == "EXTERNAL_TRUST_BOUNDARY"


def test_v2_context_requires_human_grant(env, monkeypatch, tmp_path):
    h, ms, cr, rd, grant, mcs, dec, out = _v2_lease(env, monkeypatch, tmp_path)
    v = L.verify_capability_lease_context(
        lease=out["lease"], mission_submission=ms, capability_request=cr, route_decision=rd,
        mission_capability_scope=mcs, lease_issuance_decision=dec, mission_status="OPEN")
    assert v["verdict"] == L.V_HUMAN_GRANT_INVALID


def test_v2_context_human_grant_substitution_fail_closed(env, monkeypatch, tmp_path):
    h, ms, cr, rd, grant, mcs, dec, out = _v2_lease(env, monkeypatch, tmp_path, tag="A")
    h2 = _hma(env, tag="B")
    ms2, _, _ = _cgb(monkeypatch, tmp_path, L.ENGINEERING_LEASE, tag="B")
    other = _grant(h2, ms2, tag="B")
    v = L.verify_capability_lease_context(
        lease=out["lease"], mission_submission=ms, capability_request=cr, route_decision=rd,
        mission_capability_scope=mcs, lease_issuance_decision=dec,
        human_capability_grant=other, mission_status="OPEN")
    assert v["verdict"] in (L.V_HUMAN_GRANT_MISMATCH, L.V_HUMAN_GRANT_INVALID)


def test_v2_context_human_grant_hash_tamper_fail_closed(env, monkeypatch, tmp_path):
    h, ms, cr, rd, grant, mcs, dec, out = _v2_lease(env, monkeypatch, tmp_path)
    bad = json.loads(json.dumps(grant))
    bad["capability_scope"]["allowed_tools"].append("Bash")
    v = L.verify_capability_lease_context(
        lease=out["lease"], mission_submission=ms, capability_request=cr, route_decision=rd,
        mission_capability_scope=mcs, lease_issuance_decision=dec,
        human_capability_grant=bad, mission_status="OPEN")
    assert v["verdict"] == L.V_HUMAN_GRANT_INVALID


def test_v2_request_scope_exceeds_mission_fail_closed(env, monkeypatch, tmp_path):
    h, ms, cr, rd, grant, mcs, dec = _issue(
        env, monkeypatch, tmp_path,
        grant_scope=_eng_scope(paths=(_TARGET,), tools=("Edit",)),
        mission_scope=_eng_scope(paths=(_TARGET,), tools=("Edit",)),
        lease_scope=_eng_scope(paths=(_TARGET,), tools=("Edit",)))
    out = L.prepare_cognitive_capability_lease(
        lease_class=L.ENGINEERING_LEASE, capability_request=cr, route_decision=rd,
        mission_submission=ms, lease_scope=_eng_scope(paths=(_TARGET,), tools=("Edit",)),
        requested_capability_scope=_eng_scope(paths=(_TARGET,), tools=("Edit", "Write")),
        mission_capability_scope=mcs, lease_issuance_decision=dec)
    assert out["status"] == L.STATUS_LEASE_REJECTED
    assert "REQUEST_SCOPE_EXCEEDS_MISSION_SCOPE" in out["reason"]


def test_v2_lease_scope_tamper_detected_by_context(env, monkeypatch, tmp_path):
    h, ms, cr, rd, grant, mcs, dec, out = _v2_lease(
        env, monkeypatch, tmp_path,
        grant_scope=_eng_scope(paths=(_TARGET,), tools=("Edit",)),
        mission_scope=_eng_scope(paths=(_TARGET,), tools=("Edit",)),
        lease_scope=_eng_scope(paths=(_TARGET,), tools=("Edit",)),
        req_scope=_eng_scope(paths=(_TARGET,), tools=("Edit",)))
    lease = json.loads(json.dumps(out["lease"]))
    lease["capability_scope"]["allowed_tools"].append("Write")
    v = L.verify_capability_lease_context(
        lease=lease, mission_submission=ms, capability_request=cr, route_decision=rd,
        mission_capability_scope=mcs, lease_issuance_decision=dec,
        human_capability_grant=grant, mission_status="OPEN")
    assert v["verdict"] == L.V_STRUCTURAL_INVALID  # hash cassé


def test_v2_cross_mission_scope_replay(env, monkeypatch, tmp_path):
    h, ms, cr, rd, grant, mcs, dec, out = _v2_lease(env, monkeypatch, tmp_path, tag="A")
    _, _, _, _, _, mcs_b, _ = _issue(env, monkeypatch, tmp_path, tag="B")
    v = L.verify_capability_lease_context(
        lease=out["lease"], mission_submission=ms, capability_request=cr, route_decision=rd,
        mission_capability_scope=mcs_b, lease_issuance_decision=dec,
        human_capability_grant=grant, mission_status="OPEN")
    assert v["verdict"] in (L.V_MISSION_SCOPE_MISMATCH, L.V_MISSION_MISMATCH)


def test_v2_restart_reload_full_human_chain(env, monkeypatch, tmp_path):
    h, ms, cr, rd, grant, mcs, dec, out = _v2_lease(env, monkeypatch, tmp_path)
    lease = out["lease"]
    sd = tmp_path / "cgb_store"

    # Rebuild the exact HCGA material bound into this default V2 grant, then
    # prove the HCG really points to that canonical authorization by ID + hash.
    hcga = _hcga(h, ms)
    assert hcga["human_capability_grant_authorization_id"] == \
        grant["human_capability_grant_authorization_id"]
    assert hcga["authorization_record_hash"] == \
        grant["human_capability_grant_authorization_hash"]

    assert MCS.persist_human_capability_grant_authorization(
        hcga, store_dir=sd)["status"] == "STORED"
    assert MCS.persist_human_capability_grant(grant, store_dir=sd)["status"] == "STORED"
    assert MCS.persist_mission_capability_scope(mcs, store_dir=sd)["status"] == "STORED"
    assert MCS.persist_lease_issuance_decision(dec, store_dir=sd)["status"] == "STORED"
    assert L.persist_capability_lease(lease, store_dir=sd)["status"] == "STORED"

    aid = hcga["human_capability_grant_authorization_id"]
    gid = grant["human_capability_grant_id"]
    mid = mcs["mission_capability_scope_id"]
    did = dec["lease_issuance_decision_id"]
    lid = lease["lease_id"]

    del hcga, grant, mcs, dec, lease

    ra = MCS.load_human_capability_grant_authorization(aid, store_dir=sd)
    rg = MCS.load_human_capability_grant(gid, store_dir=sd)
    rm = MCS.load_mission_capability_scope(mid, store_dir=sd)
    rli = MCS.load_lease_issuance_decision(did, store_dir=sd)
    rl = L.load_capability_lease(lid, store_dir=sd)

    assert ra is not None and rg is not None and rm is not None
    assert rli is not None and rl is not None

    v = L.verify_capability_lease_context(
        lease=rl,
        mission_submission=ms,
        capability_request=cr,
        route_decision=rd,
        mission_capability_scope=rm,
        lease_issuance_decision=rli,
        human_capability_grant=rg,
        human_capability_grant_authorization=ra,
        mission_status="OPEN",
    )
    assert v["verdict"] == L.V_VALID_INERT
    assert v["grants_tool_access"] is False


def test_v2_mission_closed_and_hold(env, monkeypatch, tmp_path):
    h, ms, cr, rd, grant, mcs, dec, out = _v2_lease(env, monkeypatch, tmp_path)
    for st, expect in (("CLOSED", L.V_MISSION_CLOSED), ("HOLD", L.V_MISSION_HOLD)):
        v = L.verify_capability_lease_context(
            lease=out["lease"], mission_submission=ms, capability_request=cr, route_decision=rd,
            mission_capability_scope=mcs, lease_issuance_decision=dec,
            human_capability_grant=grant, mission_status=st)
        assert v["verdict"] == expect


# ══════════════════════════════════════════════════════════════════════════
#  Backward-compat / legacy v1 / statique
# ══════════════════════════════════════════════════════════════════════════

def test_legacy_v1_lease_stays_inert_not_enforceable(env, monkeypatch, tmp_path):
    _fake_router(monkeypatch, tmp_path, "obsidure_route_only", "code_request")
    sub = RD.submit_mission(requested_outcome="legacy")
    cap = RD.request_capability(mission_submission_id=sub["mission_submission_id"],
                                requested_capability="c", reason="r")
    ms = RD.load_mission_submission(sub["mission_submission_id"])
    cr = RD.load_capability_request(cap["capability_request_id"])
    v1 = L.build_cognitive_capability_lease(
        lease_class=L.ENGINEERING_LEASE, capability_request=cr,
        route_decision=cap["route_decision"], mission_submission=ms,
        lease_scope={"allowed_providers": ["obsidure"]},
        requested_capability_scope={"allowed_providers": ["obsidure"]})
    assert v1["schema_version"] == L.SCHEMA_VERSION
    assert v1["mission_capability_scope_binding"] == "NOT_YET_ACTIVE"
    v = L.verify_capability_lease_context(
        lease=v1, mission_submission=ms, capability_request=cr,
        route_decision=cap["route_decision"], mission_status="OPEN")
    assert v["verdict"] == L.V_MISSION_SCOPE_UNBOUND
    assert v["grants_tool_access"] is False
    assert v["legacy_lease"] == L.LEGACY_CGC_LEASE_WITHOUT_MISSION_SCOPE


def test_module_static_no_enforcement_no_hook():
    src = (_SCRIPTS / "obsidia_mission_capability_scope_v0.py").read_text(encoding="utf-8")
    for banned in ("subprocess", "urllib", "requests", "PreToolUse", "settings.local",
                   ".claude/", "run_obsidure", "atomic_replace_with_bytes",
                   "run_and_persist_kx108", "os.system",
                   "import obsidia_mission_authority_v0", "import obsidia_bounded_mission_v0",
                   "import obsidia_batch_execution"):
        assert banned not in src, banned


def test_trust_boundary_is_external_and_not_overclaimed():
    """§1/§3 : CG-C2 définit/vérifie le CONTRAT de la frontière de confiance ;
    il n'instancie PAS la racine externe et NE prétend PAS que Claude ne peut
    techniquement pas la contourner."""
    assert MCS.HUMAN_ORIGIN_PROOF_MODEL == "EXTERNAL_TRUST_BOUNDARY"
    assert MCS.HUMAN_AUTHORIZATION_VERIFIER_REQUIRED is True
    assert MCS.HUMAN_AUTHORIZATION_VERIFIER_IMPLEMENTATION_WIRED is False
    assert MCS.TRUSTED_HUMAN_AUTHORIZATION_HOST_BINDING == "NOT_YET_ENFORCED"
    assert MCS.CLAUDE_CANNOT_BYPASS_HOST_TRUST_BOUNDARY == "NOT_YET_PROVEN"
    assert MCS.HUMAN_COGNITIVE_CAPABILITY_GRANT_BINDING == \
        "VERIFIED_CONDITIONAL_ON_EXTERNAL_HUMAN_VERIFIER"
    # aucune constante ne prétend une restriction Claude déjà imposée
    for name in dir(MCS):
        assert name != "CLAUDE_CAN_CREATE_HUMAN_CAPABILITY_GRANT"


def test_issuance_route_and_request_mismatch(env, monkeypatch, tmp_path):
    """§6 : route mismatch + request mismatch au niveau de l'émission."""
    h, ms, cr, rd, grant, mcs = _mk_mcs(env, monkeypatch, tmp_path,
                                        lease_classes=[L.ENGINEERING_LEASE, L.LANGUAGE_LEASE],
                                        grant_classes=[L.ENGINEERING_LEASE, L.LANGUAGE_LEASE])
    # route est ENGINEERING mais on propose LANGUAGE
    dec = MCS.evaluate_lease_issuance(
        mission_submission=ms, capability_request=cr, route_decision=rd,
        mission_capability_scope=mcs, proposed_lease_class=L.LANGUAGE_LEASE,
        proposed_lease_scope=_eng_scope(paths=(_TARGET,)), mission_status="ACTIVE",
        human_capability_grant=grant, mcs_hma=h["hma"], hma_verifier=h["verifier"])
    assert dec["outcome"] == MCS.LEASE_DENIED_ROUTE
    # capability_request d'une autre mission
    _, _, cr_b, _, _, _ = _mk_mcs(env, monkeypatch, tmp_path, tag="B")
    dec2 = MCS.evaluate_lease_issuance(
        mission_submission=ms, capability_request=cr_b, route_decision=rd,
        mission_capability_scope=mcs, proposed_lease_class=L.ENGINEERING_LEASE,
        proposed_lease_scope=_eng_scope(paths=(_TARGET,)), mission_status="ACTIVE",
        human_capability_grant=grant, mcs_hma=h["hma"], hma_verifier=h["verifier"])
    assert dec2["outcome"] == MCS.LEASE_DENIED_REQUEST_MISMATCH


def test_v2_context_issuance_substitution_and_not_eligible(env, monkeypatch, tmp_path):
    """§6 : substitution / non-éligibilité de la LeaseIssuanceDecision en contexte."""
    h, ms, cr, rd, grant, mcs, dec, out = _v2_lease(env, monkeypatch, tmp_path)
    bad_dec = MCS.evaluate_lease_issuance(
        mission_submission=ms, capability_request=cr, route_decision=rd,
        mission_capability_scope=mcs, proposed_lease_class=L.ENGINEERING_LEASE,
        proposed_lease_scope=_eng_scope(paths=(_TARGET,)), mission_status="HOLD",
        human_capability_grant=grant)
    assert bad_dec["outcome"] == MCS.LEASE_DENIED_MISSION_STATE
    v = L.verify_capability_lease_context(
        lease=out["lease"], mission_submission=ms, capability_request=cr, route_decision=rd,
        mission_capability_scope=mcs, lease_issuance_decision=bad_dec,
        human_capability_grant=grant, mission_status="OPEN")
    assert v["verdict"] in (L.V_ISSUANCE_NOT_ELIGIBLE, L.V_ISSUANCE_MISMATCH)


def test_v2_lease_le_human_grant_positive(env, monkeypatch, tmp_path):
    """§10/§11 : LEASE ≤ HUMAN_GRANT vérifié (chaîne positive à 4 niveaux)."""
    h, ms, cr, rd, grant, mcs, dec, out = _v2_lease(
        env, monkeypatch, tmp_path,
        grant_scope=_eng_scope(paths=(_TARGET,), tools=("Edit", "Write")),
        mission_scope=_eng_scope(paths=(_TARGET,), tools=("Edit", "Write")),
        lease_scope=_eng_scope(paths=(_TARGET,), tools=("Edit",)),
        req_scope=_eng_scope(paths=(_TARGET,), tools=("Edit", "Write")))
    v = L.verify_capability_lease_context(
        lease=out["lease"], mission_submission=ms, capability_request=cr, route_decision=rd,
        mission_capability_scope=mcs, lease_issuance_decision=dec,
        human_capability_grant=grant, mission_status="OPEN")
    assert v["verdict"] == L.V_VALID_INERT
    # lease scope (Edit) ⊆ mcs (Edit+Write) ⊆ grant (Edit+Write) ⊆ HMA paths
    lsc = out["lease"]["capability_scope"]
    assert set(lsc["allowed_tools"]) <= set(grant["capability_scope"]["allowed_tools"])
    assert set(lsc["allowed_paths"]) <= set(h["hma"]["allowed_target_paths"])


def test_frozen_paths_clean():
    r = subprocess.run(
        ["git", "status", "--porcelain", ".claude/", "proofs/lean/", "CLAUDE.md",
         "scripts/obsidia_mission_sequencer_v0.py", "scripts/obsidia_mission_authority_v0.py",
         "scripts/obsidia_governed_apply_v0.py", "audit/merkle_seal.json"],
        cwd=str(_REPO_ROOT), capture_output=True, text=True)
    assert r.stdout.strip() == "", f"gelé modifié: {r.stdout}"


def test_cgb_route_receipt_still_requires_null_lease_id():
    rd = RD.build_route_decision("x")
    rec = RD.build_route_receipt(rd, requested_outcome="x", selected_route=rd["route_class"],
                                reason=rd["reason"], persist=False)
    assert rec["lease_id"] is None
    bad = dict(rec); bad["lease_id"] = "cclease-" + "0" * 32
    assert RD.verify_route_receipt(bad)[0] is False


def test_cgc_regression_still_green_import():
    # sanity : les 3 modules coexistent sans import Stage 4 dans CG-C2
    import importlib
    for m in ("obsidia_gateway_route_decision_v0", "obsidia_cognitive_capability_lease_v0",
              "obsidia_mission_capability_scope_v0"):
        importlib.import_module(m)
