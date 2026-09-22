"""
tests/cli/test_mission_authority_conformance_v0.py
=================================================
STAGE 4D — conformance sémantique modèle formel Lean (4A/4B) ↔ vérificateur
runtime Stage 4C.

ARCHITECTURE (§4) : UNE SEULE source de vérité par vecteur = une fonction
`mutate(ctx)` qui définit UN scénario sémantique canonique appliqué au
fixture RÉEL. Ce même scénario est ensuite :
  - évalué par le vérificateur runtime RÉEL committé
    (obsidia_mission_authority_v0.verify_derived_action_authority_witness),
  - projeté en `CanonicalVector` (mapping identités runtime→Nat explicite)
    et évalué par l'ORACLE Lean exécutable
    (Obsidia.MissionAuthority.ConformanceVectors.semanticVerdict), qui
    appelle `decide` sur les PRÉDICATS FORMELS COMMITTÉS 4A/4B.
Les deux verdicts sont NORMALISÉS puis comparés.

Aucune « réponse attendue » n'est saisie : chaque côté CALCULE son verdict.

SHA-256 n'est PAS modélisé côté Lean : la liaison EAH est sémantique
(égalité witnessEAH = envelopeEAH). Les vecteurs de conformance ne testent
que la sémantique d'autorité, pas l'implémentation cryptographique.
"""
from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_SCRIPTS = _REPO_ROOT / "scripts"
_LEAN_DIR = _REPO_ROOT / "proofs" / "lean"
_LEAN_OBSIDIA_BUILT = False

def _ensure_lean_obsidia_built() -> None:
    """Materialize declared Obsidia Lean library before generated oracle imports."""
    global _LEAN_OBSIDIA_BUILT
    if _LEAN_OBSIDIA_BUILT:
        return

    result = subprocess.run(
        ["lake", "build", "Obsidia"],
        cwd=str(_LEAN_DIR),
        capture_output=True,
        text=True,
        timeout=400,
    )
    assert result.returncode == 0, (
        "Lean Obsidia library prebuild failed:\n"
        + result.stdout
        + "\n"
        + result.stderr
    )
    _LEAN_OBSIDIA_BUILT = True

for _p in (str(_SCRIPTS), str(_REPO_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import obsidia_test_contract as TC                 # noqa: E402
import obsidia_isolated_work_unit_v0 as WU         # noqa: E402
import obsidia_bounded_mission_v0 as M             # noqa: E402
import obsidia_batch_execution as E                # noqa: E402
import obsidia_mission_authority_v0 as MA          # noqa: E402

_TARGET = "periphery/xdomain/conf_target_v0.txt"
_S1 = "periphery/xdomain/conf_src_1.txt"
_S2 = "periphery/xdomain/conf_src_2.txt"


# ── Registre d'identité EXPLICITE runtime(str) → Nat (§7) ─────────────────
class _Reg:
    def __init__(self):
        self._m: dict = {}
        self._n = 1

    def __call__(self, s) -> int:
        if s is None:
            return 0
        key = str(s)
        if key not in self._m:
            self._m[key] = self._n
            self._n += 1
        return self._m[key]


# ── Verdict normalisé partagé (§8) ───────────────────────────────────────
_ALLOWABLE = "ALLOWABLE"


def _norm(reason) -> str:
    if reason is None:
        return _ALLOWABLE
    r = reason
    table = [
        ("DAAW_SCOPE_AMPLIFICATION", "SCOPE_AMPLIFICATION"),
        ("HMA_INVALID:HMA_SCOPE_NOT_BOUNDED_BY_GENESIS", "SCOPE_AMPLIFICATION"),
        ("HMA_INVALID:HMA_MAX_ACTIONS_EXCEEDS_GENESIS", "SCOPE_AMPLIFICATION"),
        ("HMA_INVALID:HMA_MAX_RETRIES_EXCEEDS_GENESIS", "SCOPE_AMPLIFICATION"),
        ("HMA_INVALID:HMA_TARGETS_NOT_SUBSET_OF_GENESIS", "SCOPE_AMPLIFICATION"),
        ("HMA_INVALID:HMA_OPERATIONS_NOT_SUBSET_OF_GENESIS", "SCOPE_AMPLIFICATION"),
        ("HMA_INVALID:HMA_PLAN_HASH_MISMATCH", "PLAN_MISMATCH"),
        ("HMA_INVALID:HMA_PLAN_ID_MISMATCH", "PLAN_MISMATCH"),
        ("DAAW_PLAN_HASH_MISMATCH", "PLAN_MISMATCH"),
        ("DAAW_PLAN_ID_MISMATCH", "PLAN_MISMATCH"),
        ("DAAW_ACTION_FIELD_MISMATCH", "ACTION_MISMATCH"),
        ("DAAW_ACTION_NOT_IN_PLAN", "ACTION_MISMATCH"),
        ("EAH_MISMATCH", "EAH_MISMATCH"),
        ("DAAW_ACTION_BASE_NOT_CURRENT_MISSION_TIP", "STALE_BASE"),
        ("DAAW_DEPENDENCY_UNSATISFIED", "DEPENDENCY_UNSATISFIED"),
        ("DAAW_DEPENDENCY_DIGEST_MISMATCH", "DEPENDENCY_UNSATISFIED"),
        ("DAAW_BUDGET_EXCEEDED", "BUDGET_EXCEEDED"),
        ("DAAW_EXECUTED_INDEX_NOT_DERIVED", "BUDGET_EXCEEDED"),
        ("HMA_INVALID:HMA_REVOKED", "REVOKED"),
        ("MISSION_PLAN_COMPLETED", "PLAN_COMPLETED"),
    ]
    for prefix, verdict in table:
        if r.startswith(prefix):
            return verdict
    return "HMA_INVALID"


# ── Fixture réel ─────────────────────────────────────────────────────────
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


def _envelope(*, beid="be-conf-1", target=_TARGET):
    return {
        "batch_execution_id": beid, "test_contract_hash": "e" * 64,
        "decision_authority": "KX108_ONLY",
        "children": [{
            "candidate_entry_id": "ce-1", "child_execution_id": "ch-1",
            "source_kind": "GIT_BLOB", "source_content_sha256": "d" * 64,
            "source_git_commit_sha": "c" * 40, "source_git_historical_path": "p/x.txt",
            "target_path": target, "operation_type": "UPDATE_TARGET_FROM_SOURCE",
        }],
    }


@pytest.fixture(scope="module")
def base_ctx(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("conf")
    main = tmp / "main"
    (main / "periphery" / "xdomain").mkdir(parents=True)
    for f in (_TARGET, _S1, _S2):
        (main / f).write_bytes(f.encode())
    _git(main, "init", "-q")
    _git(main, "config", "user.email", "t@e.com")
    _git(main, "config", "user.name", "t")
    _git(main, "config", "commit.gpgsign", "false")
    _git(main, "add", ".")
    _git(main, "commit", "-q", "-m", "seed")
    base = _git(main, "rev-parse", "HEAD")
    stores = tmp / "missions"
    wt = (tmp / "wt").resolve()
    cr = WU.create_isolated_work_unit(repo_root=main, base_sha=base, branch_name="cbr",
                                      worktree_path=wt, work_unit_id="wu-conf-1")
    assert cr["status"] == WU.WORK_UNIT_CREATED

    def _mission(tag, max_actions, actions):
        g = M.create_bounded_mission(
            objective=f"conf-{tag}", repository_identity="repo://conf",
            canonical_base_sha=base, branch_name="cbr",
            worktree_path=str(wt), main_worktree_path=str(main.resolve()),
            scope={"allowed_operation_shapes": ["UPDATE_TARGET_FROM_SOURCE"],
                   "allowed_target_paths": [_TARGET], "max_actions": max_actions,
                   "max_retries_per_action": 0},
            human_mandate_reference=f"hmr-{tag}", mission_store_dir=stores)
        mid = g["mission_id"]
        M.bind_work_unit(mission_id=mid, work_unit=cr["work_unit"], mission_store_dir=stores)
        r = M.bind_mission_plan(mission_id=mid, actions=actions, mission_store_dir=stores)
        assert r["status"] == M.STATUS_PLAN_BOUND, r
        genesis = M.load_mission_genesis(mid, stores)
        plan = M.load_mission_plan(mid, r["plan_id"], stores)
        hma = MA.build_human_mission_authorization(
            mission_id=mid, plan_id=r["plan_id"],
            human_authorization_reference="TEST_HUMAN_REFERENCE", mission_store_dir=stores)[0]
        return dict(mid=mid, genesis=genesis, plan=plan, hma=hma, stores=stores)

    ab = [
        {"ordinal": 0, "target_path": _TARGET, "source_git_commit": base,
         "source_historical_path": _S1, "test_contract": _contract("cA"),
         "dependency_ordinals": []},
        {"ordinal": 1, "target_path": _TARGET, "source_git_commit": base,
         "source_historical_path": _S2, "test_contract": _contract("cB"),
         "dependency_ordinals": [0]},
    ]
    m3 = _mission("m3", 3, ab)
    m1 = _mission("m1", 1, [ab[0]])
    m_other = _mission("other", 3, ab)

    env = _envelope()
    a0 = m3["plan"]["actions"][0]["action_id"]
    proj0 = {"mission_tip_sha": base, "snapshotted_action_ids": [],
             "plan_completed": False, "current_state": "WORKTREE_BOUND"}
    daaw0 = MA.derive_action_authority_witness(
        hma=m3["hma"], plan=m3["plan"], action_id=a0, projection=proj0,
        execution_envelope=env)[0]
    return {"m3": m3, "m1": m1, "m_other": m_other, "env": env,
            "a0": a0, "proj0": proj0, "daaw0": daaw0, "base_sha": base}


# ── Projection réel → CanonicalVector (Nat) ──────────────────────────────
def _project(vector_id, *, hma, plan, daaw, genesis, projection, envelope, reg):
    rows = []
    for d in plan["actions"]:
        rows.append(dict(
            ordinal=d["ordinal"], actionId=reg(d["action_id"]), target=reg(d["target_path"]),
            operation=0, sourceCommit=reg(d.get("source_git_commit")),
            sourceHist=reg(d.get("source_historical_path")), testContractHash=reg(d.get("test_contract_hash")),
            actionBaseSha=reg(daaw["action_base_sha"]) if d["action_id"] == daaw["action_id"]
            else reg(d["action_id"]),
            dependencyOrds=list(d.get("dependency_ordinals") or []),
        ))
    gs = genesis["scope"]
    env_eah = E.compute_execution_authority_hash(envelope)
    return dict(
        vectorId=vector_id,
        hmaId=reg(hma["human_mission_authorization_id"]),
        hmaIssuerHuman=(hma.get("issuer") == "HUMAN"),
        hmaDomainHma=(hma.get("domain_tag") == MA.HMA_DOMAIN_TAG),
        hmaPlanId=reg(hma["plan_id"]), hmaPlanHash=reg(hma["plan_hash"]),
        hmaMissionId=reg(hma["mission_id"]), hmaGenesisHash=reg(hma["mission_genesis_record_hash"]),
        hmaTargets=[reg(t) for t in (hma.get("allowed_target_paths") or [])],
        hmaOps=[0 for _ in (hma.get("allowed_operation_shapes") or [])],
        hmaMaxActions=int(hma.get("max_actions") or 0),
        hmaMaxRetries=int(hma.get("max_retries_per_action") or 0),
        genTargets=[reg(t) for t in (gs.get("allowed_target_paths") or [])],
        genOps=[0 for _ in (gs.get("allowed_operation_shapes") or [])],
        genMaxActions=int(gs.get("max_actions") or 0),
        genMaxRetries=int(gs.get("max_retries_per_action") or 0),
        repoId=reg(genesis["repository_identity"]), branchId=reg(genesis["branch_name"]),
        canonicalBase=reg(genesis["canonical_base_sha"]), depCommitment=reg(hma["dependency_commitment"]),
        planId=reg(plan["plan_id"]), planHash=reg(plan["plan_hash"]), planRows=rows,
        daawDomainDaaw=(daaw.get("domain_tag") == MA.DAAW_DOMAIN_TAG),
        daawNonSovereign=(daaw.get("sovereignty") == "NON_SOVEREIGN"),
        daawMissionAuthId=reg(daaw["human_mission_authorization_id"]),
        daawMissionId=reg(daaw["mission_id"]),
        daawPlanId=reg(daaw["plan_id"]), daawPlanHash=reg(daaw["plan_hash"]),
        daawActionId=reg(daaw["action_id"]), daawOrdinal=int(daaw["ordinal"]),
        daawOperation=0, daawTarget=reg(daaw["target_path"]),
        daawSourceCommit=reg(daaw.get("source_git_commit")),
        daawSourceHist=reg(daaw.get("source_historical_path")),
        daawTch=reg(daaw.get("test_contract_hash")),
        daawDepOrds=list(_plan_deps(plan, daaw["action_id"])),
        daawActionBase=reg(daaw["action_base_sha"]),
        daawExecIndex=int(daaw["executed_action_index"]),
        daawEAH=reg(daaw["execution_authority_hash"]),
        daawTargets=[reg(t) for t in (daaw.get("allowed_target_paths") or [])],
        daawOps=[0 for _ in (daaw.get("allowed_operation_shapes") or [])],
        daawMaxActions=int(daaw.get("max_actions") or 0),
        daawMaxRetries=int(daaw.get("max_retries_per_action") or 0),
        daawRepoId=reg(daaw.get("repository_identity")), daawBranchId=reg(daaw.get("branch_name")),
        daawCanonicalBase=reg(daaw.get("canonical_base_sha")),
        daawDepCommitment=reg(daaw.get("dependency_commitment")),
        missionTip=reg(projection["mission_tip_sha"]),
        snapshotted=[reg(x) for x in (projection.get("snapshotted_action_ids") or [])],
        executedIndex=len(projection.get("snapshotted_action_ids") or []),
        phaseCompleted=bool(projection.get("plan_completed"))
        or projection.get("current_state") == "CLOSED_AWAITING_NEXT_PLAN",
        revokedList=[reg(daaw["human_mission_authorization_id"])] if projection.get("_revoked") else [],
        envelopeEAH=reg(env_eah),
    )


def _plan_deps(plan, action_id):
    d = next((x for x in plan["actions"] if x["action_id"] == action_id), None)
    return list(d.get("dependency_ordinals") or []) if d else []


def _lean_literal(cv: dict) -> str:
    def lit(v):
        if isinstance(v, bool):
            return "true" if v else "false"
        if isinstance(v, int):
            return str(v)
        if isinstance(v, str):
            return '"' + v.replace('"', '\\"') + '"'
        if isinstance(v, list):
            return "[" + ", ".join(lit(x) for x in v) + "]"
        if isinstance(v, dict):  # PlanRow
            keys = ["ordinal", "actionId", "target", "operation", "sourceCommit",
                    "sourceHist", "testContractHash", "actionBaseSha", "dependencyOrds"]
            return "{ " + ", ".join(f"{k} := {lit(v[k])}" for k in keys) + " }"
        raise TypeError(type(v))
    order = ["vectorId", "hmaId", "hmaIssuerHuman", "hmaDomainHma", "hmaPlanId", "hmaPlanHash",
             "hmaMissionId", "hmaGenesisHash", "hmaTargets", "hmaOps", "hmaMaxActions",
             "hmaMaxRetries", "genTargets", "genOps", "genMaxActions", "genMaxRetries",
             "repoId", "branchId", "canonicalBase", "depCommitment", "planId", "planHash",
             "planRows", "daawDomainDaaw", "daawNonSovereign", "daawMissionAuthId",
             "daawMissionId", "daawPlanId", "daawPlanHash", "daawActionId", "daawOrdinal",
             "daawOperation", "daawTarget", "daawSourceCommit", "daawSourceHist", "daawTch",
             "daawDepOrds", "daawActionBase", "daawExecIndex", "daawEAH", "daawTargets",
             "daawOps", "daawMaxActions", "daawMaxRetries", "daawRepoId", "daawBranchId",
             "daawCanonicalBase", "daawDepCommitment", "missionTip", "snapshotted",
             "executedIndex", "phaseCompleted", "revokedList", "envelopeEAH"]
    return "{ " + ",\n    ".join(f"{k} := {lit(cv[k])}" for k in order) + " }"


def _run_lean_oracle(cvs: list) -> dict:
    _ensure_lean_obsidia_built()
    literals = ",\n  ".join(_lean_literal(cv) for cv in cvs)
    script = (
        "import Obsidia.MissionAuthority.ConformanceVectors\n"
        "open Obsidia.MissionAuthority.Conformance\n"
        "def main : IO Unit := do\n"
        f"  for (id, v) in runVectors [\n  {literals}\n  ] do\n"
        "    IO.println s!\"{id}\\t{v}\"\n"
    )
    p = _LEAN_DIR / "_conformance_run_gen.lean"
    p.write_text(script, encoding="utf-8")
    try:
        r = subprocess.run(["lake", "env", "lean", "--run", str(p)],
                           cwd=str(_LEAN_DIR), capture_output=True, text=True, timeout=400)
        assert r.returncode == 0, f"lean oracle failed:\n{r.stdout}\n{r.stderr}"
        out = {}
        for line in r.stdout.strip().splitlines():
            if "\t" in line:
                vid, verdict = line.split("\t", 1)
                out[vid] = verdict.strip()
        return out
    finally:
        p.unlink(missing_ok=True)


def _rehash_daaw(d):
    d["daaw_record_hash"] = MA._sha256_hex(MA._canon({k: d.get(k) for k in MA._DAAW_BOUND_FIELDS}))
    d["derived_action_authority_witness_id"] = "daaw-" + d["daaw_record_hash"][:32]


def _rehash_hma_and_relink(h, d):
    h["hma_record_hash"] = MA._sha256_hex(MA._canon({k: h.get(k) for k in MA._HMA_BOUND_FIELDS}))
    h["human_mission_authorization_id"] = "hma-" + h["hma_record_hash"][:32]
    d["human_mission_authorization_id"] = h["human_mission_authorization_id"]
    d["hma_record_hash"] = h["hma_record_hash"]
    _rehash_daaw(d)


# ── VECTEURS : une fonction mutate == une source sémantique unique ──────
def _ctx_first(base_ctx):
    m3 = base_ctx["m3"]
    return dict(
        hma=copy.deepcopy(m3["hma"]), plan=copy.deepcopy(m3["plan"]),
        daaw=copy.deepcopy(base_ctx["daaw0"]), genesis=copy.deepcopy(m3["genesis"]),
        projection=copy.deepcopy(base_ctx["proj0"]), envelope=copy.deepcopy(base_ctx["env"]),
        revocations=[])


def _ctx_second(base_ctx):
    """DAAW pour l'action 1, prédécesseur (action 0) snapshoté, tip avancé."""
    m3 = base_ctx["m3"]
    a0 = m3["plan"]["actions"][0]["action_id"]
    a1 = m3["plan"]["actions"][1]["action_id"]
    proj = {"mission_tip_sha": "a" * 40, "snapshotted_action_ids": [a0],
            "plan_completed": False, "current_state": "WORKTREE_BOUND"}
    env = _envelope(beid="be-conf-2")
    daaw = MA.derive_action_authority_witness(
        hma=m3["hma"], plan=m3["plan"], action_id=a1, projection=proj,
        execution_envelope=env)[0]
    return dict(hma=copy.deepcopy(m3["hma"]), plan=copy.deepcopy(m3["plan"]),
                daaw=copy.deepcopy(daaw), genesis=copy.deepcopy(m3["genesis"]),
                projection=copy.deepcopy(proj), envelope=copy.deepcopy(env), revocations=[])


def _ctx_budget(base_ctx):
    m1 = base_ctx["m1"]
    a0 = m1["plan"]["actions"][0]["action_id"]
    proj = {"mission_tip_sha": "z" * 40, "snapshotted_action_ids": [a0],
            "plan_completed": False, "current_state": "WORKTREE_BOUND"}
    env = _envelope(beid="be-conf-budget")
    daaw = MA.derive_action_authority_witness(
        hma=m1["hma"], plan=m1["plan"], action_id=a0, projection=proj,
        execution_envelope=env)[0]
    return dict(hma=copy.deepcopy(m1["hma"]), plan=copy.deepcopy(m1["plan"]),
                daaw=copy.deepcopy(daaw), genesis=copy.deepcopy(m1["genesis"]),
                projection=copy.deepcopy(proj), envelope=copy.deepcopy(env), revocations=[])


def _m_scope_amp(c):
    c["daaw"]["max_actions"] = 99
    _rehash_daaw(c["daaw"])


def _m_gen_scope_amp(c):
    c["hma"]["max_actions"] = 99
    _rehash_hma_and_relink(c["hma"], c["daaw"])


def _m_target_expand(c):
    c["hma"]["allowed_target_paths"] = [_TARGET, "periphery/xdomain/extra.txt"]
    _rehash_hma_and_relink(c["hma"], c["daaw"])


def _m_plan_hash(c):
    c["daaw"]["plan_hash"] = "0" * 64
    _rehash_daaw(c["daaw"])


def _m_action_sub(c):
    c["daaw"]["action_id"] = c["plan"]["actions"][1]["action_id"]
    _rehash_daaw(c["daaw"])


def _m_source_sub(c):
    c["daaw"]["source_historical_path"] = "periphery/xdomain/wrong.txt"
    _rehash_daaw(c["daaw"])


def _m_tc_sub(c):
    c["daaw"]["test_contract_hash"] = "f" * 64
    _rehash_daaw(c["daaw"])


def _m_stale_base(c):
    c["projection"]["mission_tip_sha"] = "b" * 40


def _m_eah_drift(c):
    c["envelope"]["batch_execution_id"] = "be-DRIFT"


def _m_dep_unsat(c):
    c["projection"]["snapshotted_action_ids"] = []
    c["projection"]["mission_tip_sha"] = c["daaw"]["action_base_sha"]  # isole la dépendance


def _m_budget(c):
    pass  # _ctx_budget déjà à l'index 1 avec max_actions=1


def _m_revoke(c):
    rv = {"revocation_schema_version": MA.REVOCATION_SCHEMA_VERSION,
          "domain_tag": MA.REVOCATION_DOMAIN_TAG, "mission_id": c["hma"]["mission_id"],
          "hma_id": c["hma"]["human_mission_authorization_id"],
          "hma_record_hash": c["hma"]["hma_record_hash"],
          "revocation_reference": "TEST_HUMAN_STOP", "actor": "HUMAN"}
    rv["revocation_record_hash"] = MA._sha256_hex(
        MA._canon({k: rv.get(k) for k in MA._REVOCATION_BOUND_FIELDS}))
    rv["mission_authority_revocation_id"] = "rev-" + rv["revocation_record_hash"][:32]
    c["revocations"] = [rv]
    c["projection"]["_revoked"] = True


def _m_completed(c):
    c["projection"]["plan_completed"] = True
    c["projection"]["current_state"] = "CLOSED_AWAITING_NEXT_PLAN"


def _m_wrong_issuer(c):
    c["hma"]["issuer"] = "STACK"
    _rehash_hma_and_relink(c["hma"], c["daaw"])


def _m_wrong_domain(c):
    c["hma"]["domain_tag"] = "OTHER"
    _rehash_hma_and_relink(c["hma"], c["daaw"])


def _m_cross_mission(c, base_ctx):
    mo = base_ctx["m_other"]
    c["hma"] = copy.deepcopy(mo["hma"])
    c["plan"] = copy.deepcopy(mo["plan"])
    c["genesis"] = copy.deepcopy(mo["genesis"])


_VECTORS = [
    ("P1_valid_first", "positive", "ActionWitnessValid", None, _ctx_first, _ALLOWABLE),
    ("P2_valid_second", "positive", "DependencyOrderPreserved", None, _ctx_second, _ALLOWABLE),
    ("N1_plan_substitution", "negative", "PlanRevisionCannotExpandAuthorizedScope",
     _m_plan_hash, _ctx_first, "PLAN_MISMATCH"),
    ("N2_action_substitution", "negative", "CrossActionReplayImpossible",
     _m_action_sub, _ctx_first, "ACTION_MISMATCH"),
    ("N3_target_expansion", "negative", "NoAuthorityAmplification",
     _m_target_expand, _ctx_first, "SCOPE_AMPLIFICATION"),
    ("N5_max_actions_ampl_daaw", "negative", "NoAuthorityAmplification",
     _m_scope_amp, _ctx_first, "SCOPE_AMPLIFICATION"),
    ("N6_max_actions_ampl_hma", "negative", "MissionScopeMonotone",
     _m_gen_scope_amp, _ctx_first, "SCOPE_AMPLIFICATION"),
    ("N7_stale_base", "negative", "ActionBaseEqualsCurrentMissionTip",
     _m_stale_base, _ctx_first, "STALE_BASE"),
    ("N8_dependency_unsatisfied", "negative", "DependencyOrderPreserved",
     _m_dep_unsat, _ctx_second, "DEPENDENCY_UNSATISFIED"),
    ("N9_budget_exhausted", "negative", "MissionActionBudgetNeverExceeded",
     _m_budget, _ctx_budget, "BUDGET_EXCEEDED"),
    ("N10_revoked_hma", "negative", "RevokedMissionCannotAuthorizeAction",
     _m_revoke, _ctx_first, "REVOKED"),
    ("N11_plan_completed", "negative", "ClosedMissionCannotAuthorizeAction",
     _m_completed, _ctx_first, "PLAN_COMPLETED"),
    ("N14_source_mismatch", "negative", "CrossActionReplayImpossible",
     _m_source_sub, _ctx_first, "ACTION_MISMATCH"),
    ("N15_testcontract_mismatch", "negative", "CrossActionReplayImpossible",
     _m_tc_sub, _ctx_first, "ACTION_MISMATCH"),
    ("N16_eah_mismatch", "negative", "ActionAuthorityBindsExactEAH",
     _m_eah_drift, _ctx_first, "EAH_MISMATCH"),
    ("N12_wrong_issuer", "negative", "InvalidAuthorityEvidenceCannotAuthorize",
     _m_wrong_issuer, _ctx_first, "HMA_INVALID"),
    ("N13_wrong_domain", "negative", "InvalidAuthorityEvidenceCannotAuthorize",
     _m_wrong_domain, _ctx_first, "HMA_INVALID"),
]


def _build_case(vid, mutate, ctx_fn, base_ctx):
    reg = _Reg()
    c = ctx_fn(base_ctx)
    if mutate is not None:
        if vid == "N18_cross_mission":
            mutate(c, base_ctx)
        else:
            mutate(c)
    ok, reason = MA.verify_derived_action_authority_witness(
        daaw=c["daaw"], hma=c["hma"], plan=c["plan"], genesis=c["genesis"],
        projection=c["projection"], execution_envelope=c["envelope"],
        revocations=c["revocations"])
    py_verdict = _ALLOWABLE if ok else _norm(reason)
    cv = _project(vid, hma=c["hma"], plan=c["plan"], daaw=c["daaw"], genesis=c["genesis"],
                  projection=c["projection"], envelope=c["envelope"], reg=reg)
    return py_verdict, reason, cv


def test_lean_runtime_canonical_conformance(base_ctx):
    cases = {}
    cvs = []
    for vid, _cat, _pred, mutate, ctx_fn, _exp in _VECTORS:
        py_verdict, reason, cv = _build_case(vid, mutate, ctx_fn, base_ctx)
        cases[vid] = (py_verdict, reason)
        cvs.append(cv)
    lean = _run_lean_oracle(cvs)

    mism = []
    for vid, _cat, _pred, _m, _c, _exp in _VECTORS:
        py_v = cases[vid][0]
        lean_v = lean.get(vid)
        if py_v != lean_v:
            mism.append((vid, _pred, lean_v, py_v, cases[vid][1]))
    assert not mism, "CONFORMANCE DIVERGENCE:\n" + "\n".join(
        f"  {vid} [{pred}] lean={lv} python={pv} (reason={rsn})" for vid, pred, lv, pv, rsn in mism)

    # tous les vecteurs (positifs ET négatifs) concordent
    assert len(lean) == len(_VECTORS)


# ── scopeLE / scope_le conformance (§19) ─────────────────────────────────
_BASE_SCOPE = dict(allowed_target_paths=["t1", "t2"], allowed_operation_shapes=["op"],
                   max_actions=3, max_retries_per_action=1, plan_hash="ph",
                   repository_identity="repo", branch_name="br",
                   canonical_base_sha="base", dependency_commitment="dep")

_SCOPE_PAIRS = [
    ("equal", lambda a: a, True),
    ("strict_subset_targets", lambda a: {**a, "allowed_target_paths": ["t1"]}, True),
    ("target_expansion", lambda a: {**a, "allowed_target_paths": ["t1", "t2", "t3"]}, False),
    ("max_actions_lower", lambda a: {**a, "max_actions": 2}, True),
    ("max_actions_higher", lambda a: {**a, "max_actions": 4}, False),
    ("retry_higher", lambda a: {**a, "max_retries_per_action": 2}, False),
    ("plan_mismatch", lambda a: {**a, "plan_hash": "other"}, False),
    ("repo_mismatch", lambda a: {**a, "repository_identity": "other"}, False),
    ("branch_mismatch", lambda a: {**a, "branch_name": "other"}, False),
    ("base_mismatch", lambda a: {**a, "canonical_base_sha": "other"}, False),
    ("dep_mismatch", lambda a: {**a, "dependency_commitment": "other"}, False),
]


def test_scope_le_conformance():
    _ensure_lean_obsidia_built()
    reg = _Reg()
    lines = []
    py_results = {}
    for name, mk, _exp in _SCOPE_PAIRS:
        a = mk(dict(_BASE_SCOPE))
        b = dict(_BASE_SCOPE)
        py_results[name] = MA.scope_le(a, b)

        def L(xs):
            return "[" + ", ".join(str(reg(x)) for x in xs) + "]"
        args = (
            f"{L(a['allowed_target_paths'])} [0] {reg(a['plan_hash'])} {a['max_actions']} "
            f"{a['max_retries_per_action']} {reg(a['repository_identity'])} {reg(a['branch_name'])} "
            f"{reg(a['canonical_base_sha'])} {reg(a['dependency_commitment'])} "
            f"{L(b['allowed_target_paths'])} [0] {reg(b['plan_hash'])} {b['max_actions']} "
            f"{b['max_retries_per_action']} {reg(b['repository_identity'])} {reg(b['branch_name'])} "
            f"{reg(b['canonical_base_sha'])} {reg(b['dependency_commitment'])}"
        )
        # opérations : a et b partagent la même liste d'ops -> subset trivial sauf op_expansion
        lines.append(f'  IO.println s!"{name}\\t' + "{" + f'scopePairVerdict {args}' + '}"')
    script = ("import Obsidia.MissionAuthority.ConformanceVectors\n"
              "open Obsidia.MissionAuthority.Conformance\n"
              "def main : IO Unit := do\n" + "\n".join(lines) + "\n")
    p = _LEAN_DIR / "_scope_conf_gen.lean"
    p.write_text(script, encoding="utf-8")
    try:
        r = subprocess.run(["lake", "env", "lean", "--run", str(p)],
                           cwd=str(_LEAN_DIR), capture_output=True, text=True, timeout=300)
        assert r.returncode == 0, f"{r.stdout}\n{r.stderr}"
        lean = {}
        for line in r.stdout.strip().splitlines():
            if "\t" in line:
                n, v = line.split("\t", 1)
                lean[n] = (v.strip() == "true")
    finally:
        p.unlink(missing_ok=True)
    mism = [(n, lean.get(n), py_results[n]) for n, _mk, _e in _SCOPE_PAIRS
            if lean.get(n) != py_results[n]]
    assert not mism, f"scope_le divergence: {mism}"
