"""
tests/cli/test_bounded_mission_v0.py
====================================
MINIMAL_AUTONOMOUS_WORK_WIRING_CHECKPOINT_2

Prouve, sur des dépôts / worktrees / magasins TEMPORAIRES et isolés
(kernel sigma canonique RÉEL via le pont Checkpoint 1), que
obsidia_bounded_mission_v0 fournit une identité de mission bornée
PERSISTANTE + HOLD sémantique structuré + décision humaine sémantique
liée-contenu + reprise fail-closed + abort, SANS :

  * nouvelle autorité (la mission n'autorise jamais une exécution) ;
  * séquenceur multi-actions ;
  * BoundedMissionAuthority / pré-approbation / retry automatique ;
  * fabrication de HumanApproval / record KX108 / SRE-SAR / RollbackResult ;
  * duplication du rail / du driver / du pont Checkpoint 1 / de PEC ;
  * opération Git distante ou mutante ;
  * mutation de audit/world_action_bus ;
  * migration de schéma d'un magasin gouverné existant ;
  * réécriture de l'archive de preuve C2 canonique.

L'état courant de mission est TOUJOURS dérivé du rejeu de la chaîne de
révisions immuables hash-chaînée.
"""
from __future__ import annotations

import hashlib
import inspect
import json
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
for _p in (str(_SCRIPTS_DIR), str(_REPO_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import obsidia_test_contract as TC                    # noqa: E402
import obsidia_isolated_work_unit_v0 as WU            # noqa: E402
import obsidia_bounded_mission_v0 as M                # noqa: E402
import obsidia_pre_execution_context as PEC           # noqa: E402
import obsidia_batch_execution as BE                  # noqa: E402
import obsidia_kx108_decision_store as DS             # noqa: E402
import obsidia_mission_local_snapshot_v0 as LS        # noqa: E402  (Stage 3B)

_TARGET_REL = "periphery/xdomain/bm_target_v0.txt"
_SOURCE_REL = "periphery/xdomain/bm_source_v0.txt"
_A = b"BOUNDED_MISSION_FIXTURE\nstate: BEFORE\n"
_B = b"BOUNDED_MISSION_FIXTURE\nstate: AFTER_GOVERNED_APPLY\n"

_ARCHIVE = _REPO_ROOT / "docs" / "proof" / "canonical_c2_conformance_pilot_v0"


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _git(repo: Path, *args: str) -> str:
    r = subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True)
    assert r.returncode == 0, f"git {args}: {r.stderr}"
    return r.stdout.strip()


@pytest.fixture
def env(tmp_path):
    main = tmp_path / "main"
    (main / "periphery" / "xdomain").mkdir(parents=True)
    (main / _TARGET_REL).write_bytes(_A)
    (main / _SOURCE_REL).write_bytes(_B)
    _git(main, "init", "-q")
    _git(main, "config", "user.email", "t@example.com")
    _git(main, "config", "user.name", "t")
    _git(main, "config", "commit.gpgsign", "false")
    _git(main, "add", _TARGET_REL, _SOURCE_REL)
    _git(main, "commit", "-q", "-m", "seed")
    base_sha = _git(main, "rev-parse", "HEAD")

    stores = {k: tmp_path / k for k in (
        "ledger", "selector", "exec", "pec", "kxpre", "kxpost", "tcr",
        "sar", "sre", "rbk", "missions", "holds", "decisions")}

    wt_path = (tmp_path / "wt_bm").resolve()
    cr = WU.create_isolated_work_unit(
        repo_root=main, base_sha=base_sha, branch_name="bmbr",
        worktree_path=wt_path, work_unit_id="wu-bm-0001",
    )
    assert cr["status"] == WU.WORK_UNIT_CREATED, cr
    wu = cr["work_unit"]

    return {"root": tmp_path, "main": main, "base_sha": base_sha,
            "stores": stores, "wu": wu, "wt_path": wt_path}


_DEFAULT_SCOPE = {
    "allowed_operation_shapes": ["UPDATE_TARGET_FROM_SOURCE"],
    "allowed_target_paths": [_TARGET_REL],
    "max_actions": 1,
    "max_retries_per_action": 1,
}


def _genesis(env, *, scope=None, objective="checkpoint-2 conformance",
            mandate="human-mandate-ref-0001", **over):
    kw = dict(
        objective=objective,
        repository_identity="repo://bounded-mission-fixture",
        canonical_base_sha=env["base_sha"],
        branch_name="bmbr",
        worktree_path=str(env["wt_path"]),
        main_worktree_path=str(env["main"].resolve()),
        scope=scope or dict(_DEFAULT_SCOPE),
        human_mandate_reference=mandate,
        mission_store_dir=env["stores"]["missions"],
    )
    kw.update(over)
    return M.create_bounded_mission(**kw)


def _bind(env, mid):
    return M.bind_work_unit(mission_id=mid, work_unit=env["wu"],
                            mission_store_dir=env["stores"]["missions"])


def _positive_contract():
    checks = [
        TC.build_check("post-sha", TC.CHECK_TYPE_TARGET_SHA256, target_path=_TARGET_REL,
                       expected_target_sha256=_sha(_B), required=True),
        TC.build_check("diff-scope", TC.CHECK_TYPE_DIFF_SCOPE,
                       expected_diff_paths=[_TARGET_REL], required=True),
    ]
    return TC.build_test_contract("bm-positive-v0", "cand", "batch", _TARGET_REL, checks)


def _negative_contract():
    checks = [TC.build_check("no-change-expected", TC.CHECK_TYPE_DIFF_SCOPE,
                             expected_diff_paths=[], required=True)]
    return TC.build_test_contract("bm-negative-v0", "cand", "batch", _TARGET_REL, checks)


def _prepare(env, mid, contract=None):
    return M.prepare_mission_action(
        mission_id=mid, work_unit=env["wu"],
        source_git_commit=env["base_sha"], source_historical_path=_SOURCE_REL,
        target_path=_TARGET_REL, test_contract=contract or _positive_contract(),
        ledger_dir=env["stores"]["ledger"], selector_dir=env["stores"]["selector"],
        execution_dir=env["stores"]["exec"], pre_execution_context_dir=env["stores"]["pec"],
        mission_store_dir=env["stores"]["missions"],
    )


def _execute(env, mid, prep, eah=None, ref="human-turn-ref-0001"):
    s = env["stores"]
    return M.execute_mission_action(
        mission_id=mid, work_unit=env["wu"],
        batch_execution_id=prep["batch_execution_id"],
        child_execution_id=prep["child_execution_id"],
        human_authorized_execution_authority_hash=eah if eah is not None else prep["execution_authority_hash"],
        human_authorization_reference=ref,
        execution_dir=s["exec"], pre_execution_context_dir=s["pec"],
        selector_dir=s["selector"], ledger_dir=s["ledger"],
        kx108_pre_decision_dir=s["kxpre"], kx108_post_decision_dir=s["kxpost"],
        test_contract_results_dir=s["tcr"], sealed_receipt_dir=s["sar"],
        sealed_rollback_evidence_dir=s["sre"], rollback_result_dir=s["rbk"],
        mission_store_dir=s["missions"],
    )


def _proj(env, mid):
    return M.project_mission(mission_id=mid, mission_store_dir=env["stores"]["missions"],
                             hold_store_dir=env["stores"]["holds"])


# ══════════════════════════════════════════════════════════════════════════
#  A — identité / hash de genèse déterministes
# ══════════════════════════════════════════════════════════════════════════

def test_A_deterministic_genesis_identity_and_hash(env):
    r1 = _genesis(env)
    assert r1["status"] == M.STATUS_MISSION_CREATED and r1["reason"] is None
    mid = r1["mission_id"]
    assert mid.startswith("msn-") and len(mid) == 36
    # 2e appel, mêmes entrées d'identité -> IDEMPOTENT, MÊME id, MÊME hash de genèse
    r2 = _genesis(env)
    assert r2["status"] == M.STATUS_MISSION_CREATED
    assert r2["reason"] == "IDEMPOTENT_EXISTING_IDENTICAL"
    assert r2["mission_id"] == mid
    assert r2["genesis_record_hash"] == r1["genesis_record_hash"]
    # created_at (provenance) NE fait PAS partie de l'identité
    g = json.loads((env["stores"]["missions"] / mid / "genesis.json").read_text(encoding="utf-8"))
    assert "created_at" in g
    seed_fields = M._GENESIS_IDENTITY_SEED_FIELDS
    assert "created_at" not in seed_fields and "mission_id" not in seed_fields


def test_A_distinct_objective_yields_distinct_mission_id(env):
    a = _genesis(env, objective="obj-A")["mission_id"]
    b = _genesis(env, objective="obj-B")["mission_id"]
    assert a != b


# ══════════════════════════════════════════════════════════════════════════
#  B — persist + reload + projection identique
# ══════════════════════════════════════════════════════════════════════════

def test_B_persist_reload_projection_identical(env):
    mid = _genesis(env)["mission_id"]
    _bind(env, mid)
    p1 = _proj(env, mid)
    assert p1["status"] == M.STATUS_PROJECTION_OK and p1["current_state"] == M.S_WORKTREE_BOUND
    # rechargement "à froid" : ré-import du module + relecture depuis la même racine
    import importlib
    m2 = importlib.reload(M)
    p2 = m2.project_mission(mission_id=mid, mission_store_dir=env["stores"]["missions"],
                            hold_store_dir=env["stores"]["holds"])
    importlib.reload(M)  # restaure l'alias global pour les tests suivants
    for k in ("current_state", "revision", "mission_revision_record_hash",
              "mission_genesis_record_hash", "objective", "canonical_base_sha"):
        assert p1[k] == p2[k]


# ══════════════════════════════════════════════════════════════════════════
#  C — genèse dupliquée conflictuelle rejetée
# ══════════════════════════════════════════════════════════════════════════

def test_C_conflicting_duplicate_genesis_rejected(env):
    r1 = _genesis(env)
    mid = r1["mission_id"]
    gpath = env["stores"]["missions"] / mid / "genesis.json"
    tampered = json.loads(gpath.read_text(encoding="utf-8"))
    tampered["objective"] = "SILENTLY_WIDENED_OBJECTIVE"
    gpath.write_text(json.dumps(tampered, indent=2, sort_keys=True), encoding="utf-8")
    r2 = _genesis(env)  # mêmes entrées d'identité -> recalcule le MÊME mission_id
    assert r2["status"] == M.STATUS_MISSION_CREATE_REJECTED
    assert r2["reason"] == "MISSION_GENESIS_IMMUTABILITY_VIOLATION"
    # la projection de la mission trafiquée échoue fermé
    assert _proj(env, mid)["status"] == M.STATUS_MISSION_PROJECTION_INVALID


# ══════════════════════════════════════════════════════════════════════════
#  D — liaison worktree/branche/base exacte
# ══════════════════════════════════════════════════════════════════════════

def test_D_binds_exact_worktree_branch_base(env):
    mid = _genesis(env)["mission_id"]
    r = _bind(env, mid)
    assert r["status"] == M.STATUS_WORKTREE_BOUND
    assert r["mission_worktree_binding_reuses_pec"] is True
    p = _proj(env, mid)
    assert p["current_state"] == M.S_WORKTREE_BOUND
    assert p["branch_name"] == "bmbr" and p["canonical_base_sha"] == env["base_sha"]


def test_D_bind_rejects_branch_mismatch(env):
    mid = _genesis(env, branch_name="different-branch")["mission_id"]
    r = _bind(env, mid)
    assert r["status"] == M.STATUS_BIND_REJECTED
    assert r["reason"] == "BIND_BRANCH_MISMATCH"


def test_D_bind_rejects_base_sha_mismatch(env):
    mid = _genesis(env, canonical_base_sha="0" * 40)["mission_id"]
    r = _bind(env, mid)
    assert r["status"] == M.STATUS_BIND_REJECTED
    assert r["reason"] == "BIND_BASE_SHA_MISMATCH"


# ══════════════════════════════════════════════════════════════════════════
#  E — la mission lie le résultat prepare EXACT de Checkpoint 1
# ══════════════════════════════════════════════════════════════════════════

def test_E_links_exact_checkpoint1_prepare_result(env):
    mid = _genesis(env)["mission_id"]
    _bind(env, mid)
    p = _prepare(env, mid)
    assert p["status"] == M.STATUS_ACTION_PREPARED
    c1 = p["checkpoint1_result"]
    assert c1["status"] == WU._DRV.PREPARED_AWAITING_HUMAN_APPROVAL
    rev_files = sorted((env["stores"]["missions"] / mid / "revisions").glob("*.json"))
    last = json.loads(rev_files[-1].read_text(encoding="utf-8"))
    assert last["event"] == M.E_ACTION_PREPARE_SUCCEEDED
    ev = last["evidence_refs"]
    for k in ("batch_execution_id", "child_execution_id", "execution_authority_hash",
              "pre_execution_context_id", "pre_execution_context_record_hash", "test_contract_hash"):
        assert ev[k] == c1[k]


# ══════════════════════════════════════════════════════════════════════════
#  F — transition valide WORKTREE_BOUND -> ACTION_PREPARED
# ══════════════════════════════════════════════════════════════════════════

def test_F_worktree_bound_to_action_prepared(env):
    mid = _genesis(env)["mission_id"]
    _bind(env, mid)
    assert _proj(env, mid)["current_state"] == M.S_WORKTREE_BOUND
    p = _prepare(env, mid)
    assert p["current_state"] == M.S_ACTION_PREPARED
    assert _proj(env, mid)["current_state"] == M.S_ACTION_PREPARED
    # ré-préparer alors qu'on est déjà préparé -> refus
    p2 = _prepare(env, mid)
    assert p2["status"] == M.STATUS_PREPARE_REJECTED and p2["reason"] == "ACTION_ALREADY_PREPARED"


# ══════════════════════════════════════════════════════════════════════════
#  G — création de HOLD structuré
# ══════════════════════════════════════════════════════════════════════════

def _open_hold(env, mid, **over):
    kw = dict(
        mission_id=mid, hold_type="AMBIGUOUS_WIRE_OR_DEPRECATE",
        reason="canonical next_action is an explicit disjunction",
        question_for_human="Wire the family or deprecate the target?",
        bounded_options=["WIRE", "DEPRECATE"], free_form_decision_allowed=False,
        evidence_refs=[{"kind": "FamilyRemediationCandidate", "id": "frc-x", "hash": "abc"}],
        mission_store_dir=env["stores"]["missions"], hold_store_dir=env["stores"]["holds"],
    )
    kw.update(over)
    return M.open_mission_hold(**kw)


def test_G_structured_hold_creation(env):
    mid = _genesis(env)["mission_id"]
    _bind(env, mid)
    r = _open_hold(env, mid)
    assert r["status"] == M.STATUS_HOLD_OPENED
    hid = r["hold_id"]
    assert hid.startswith("hld-")
    hrec = json.loads((env["stores"]["holds"] / f"{hid}.json").read_text(encoding="utf-8"))
    ok, reason = M.verify_hold_record(hrec)
    assert ok, reason
    assert "resolution_state" not in hrec  # jamais stocké
    assert hrec["held_from_state"] == M.S_WORKTREE_BOUND
    assert hrec["hold_type"] in M.HOLD_TYPES
    p = _proj(env, mid)
    assert p["current_state"] == M.S_HELD and p["active_hold_id"] == hid
    assert p["holds"][hid]["resolution_state"] == "OPEN"  # DÉRIVÉ


def test_G_unknown_hold_type_rejected(env):
    mid = _genesis(env)["mission_id"]
    _bind(env, mid)
    r = _open_hold(env, mid, hold_type="TOTALLY_MADE_UP")
    assert r["status"] == M.STATUS_HOLD_OPEN_REJECTED
    assert r["reason"] == "UNKNOWN_HOLD_TYPE:TOTALLY_MADE_UP"


# ══════════════════════════════════════════════════════════════════════════
#  H — le HOLD ne produit AUCUNE mutation de cible
# ══════════════════════════════════════════════════════════════════════════

def test_H_hold_produces_zero_target_mutation(env):
    mid = _genesis(env)["mission_id"]
    _bind(env, mid)
    before = (env["wt_path"] / _TARGET_REL).read_bytes()
    _open_hold(env, mid)
    assert (env["wt_path"] / _TARGET_REL).read_bytes() == before == _A
    # aucun magasin gouverné écrit par l'ouverture du HOLD
    for k in ("exec", "kxpre", "kxpost", "sar", "sre", "rbk", "tcr"):
        assert not list(env["stores"][k].rglob("*.json"))
    # HEAD inchangé
    assert _git(env["wt_path"], "rev-parse", "HEAD") == env["base_sha"]


# ══════════════════════════════════════════════════════════════════════════
#  I / J — HumanMissionDecision liée au HOLD exact ; mauvais HOLD rejeté
# ══════════════════════════════════════════════════════════════════════════

def _decide(env, mid, hid, hhash, **over):
    kw = dict(mission_id=mid, hold_id=hid, hold_record_hash=hhash, chosen_option="WIRE",
              human_decision_ref="human-semantic-turn-1",
              mission_store_dir=env["stores"]["missions"], hold_store_dir=env["stores"]["holds"],
              decision_store_dir=env["stores"]["decisions"])
    kw.update(over)
    return M.record_human_mission_decision(**kw)


def test_I_human_decision_binds_exact_hold(env):
    mid = _genesis(env)["mission_id"]
    _bind(env, mid)
    h = _open_hold(env, mid)
    d = _decide(env, mid, h["hold_id"], h["mission_hold_record_hash"])
    assert d["status"] == M.STATUS_DECISION_RECORDED
    assert d["decision_authority"] == "NON_SOVEREIGN"
    assert d["semantic_decision_is_execution_approval"] is False
    hmd = json.loads((env["stores"]["decisions"] / f"{d['human_mission_decision_id']}.json").read_text(encoding="utf-8"))
    ok, reason = M.verify_human_mission_decision(hmd)
    assert ok, reason
    assert hmd["hold_id"] == h["hold_id"]
    assert hmd["hold_record_hash"] == h["mission_hold_record_hash"]
    # enregistrer une décision NE change PAS l'état (toujours HELD)
    assert _proj(env, mid)["current_state"] == M.S_HELD


def test_J_wrong_hold_hash_decision_rejected(env):
    mid = _genesis(env)["mission_id"]
    _bind(env, mid)
    h = _open_hold(env, mid)
    d = _decide(env, mid, h["hold_id"], "0" * 64)
    assert d["status"] == M.STATUS_DECISION_REJECTED
    assert d["reason"] == "HOLD_RECORD_DRIFT"


def test_J_decision_for_another_hold_rejected(env):
    mid = _genesis(env)["mission_id"]
    _bind(env, mid)
    h = _open_hold(env, mid)
    d = _decide(env, mid, "hld-nonexistent", h["mission_hold_record_hash"])
    assert d["status"] == M.STATUS_DECISION_REJECTED
    assert d["reason"] == "HOLD_NOT_ACTIVE"


def test_J_option_out_of_bounds_rejected(env):
    mid = _genesis(env)["mission_id"]
    _bind(env, mid)
    h = _open_hold(env, mid)
    d = _decide(env, mid, h["hold_id"], h["mission_hold_record_hash"], chosen_option="NUKE_IT")
    assert d["status"] == M.STATUS_DECISION_REJECTED
    assert d["reason"] == "DECISION_OPTION_OUT_OF_BOUNDS"


def test_J_ambiguous_and_empty_decision_rejected(env):
    mid = _genesis(env)["mission_id"]
    _bind(env, mid)
    h = _open_hold(env, mid, bounded_options=["WIRE"], free_form_decision_allowed=True)
    both = _decide(env, mid, h["hold_id"], h["mission_hold_record_hash"],
                   chosen_option="WIRE", free_form_answer="also this")
    assert both["reason"] == "DECISION_AMBIGUOUS_OPTION_AND_FREEFORM"
    neither = _decide(env, mid, h["hold_id"], h["mission_hold_record_hash"],
                      chosen_option=None, free_form_answer=None)
    assert neither["reason"] == "DECISION_EMPTY"


# ══════════════════════════════════════════════════════════════════════════
#  K / L — resume ref liée à la révision exacte ; resume périmé rejeté
# ══════════════════════════════════════════════════════════════════════════

def _hold_and_resolve(env, mid, **hold_over):
    h = _open_hold(env, mid, **hold_over)
    d = _decide(env, mid, h["hold_id"], h["mission_hold_record_hash"])
    r = M.resolve_mission_hold(
        mission_id=mid, hold_id=h["hold_id"],
        human_mission_decision_id=d["human_mission_decision_id"], work_unit=env["wu"],
        mission_store_dir=env["stores"]["missions"], hold_store_dir=env["stores"]["holds"],
        decision_store_dir=env["stores"]["decisions"],
        execution_dir=env["stores"]["exec"], pre_execution_context_dir=env["stores"]["pec"],
    )
    return h, d, r


def test_K_resume_reference_binds_exact_mission_revision(env):
    mid = _genesis(env)["mission_id"]
    _bind(env, mid)
    h, d, r = _hold_and_resolve(env, mid)
    assert r["status"] == M.STATUS_HOLD_RESOLVED
    assert r["current_state"] == M.S_WORKTREE_BOUND
    assert r["no_eah_created_by_hold_resolution"] is True
    assert r["no_kx108_required_for_semantic_hold_decision"] is True
    ref = r["resume_reference"]
    ok, reason = M.verify_resume_reference(ref)
    assert ok, reason
    p = _proj(env, mid)
    assert ref["mission_revision"] == p["revision"]
    assert ref["mission_revision_record_hash"] == p["mission_revision_record_hash"]
    chk = M.check_resume_preconditions(
        resume_reference=ref, mission_id=mid, work_unit=env["wu"],
        mission_store_dir=env["stores"]["missions"], hold_store_dir=env["stores"]["holds"],
        decision_store_dir=env["stores"]["decisions"])
    assert chk["resumable"] is True


def test_L_stale_resume_rejected(env):
    mid = _genesis(env)["mission_id"]
    _bind(env, mid)
    h, d, r = _hold_and_resolve(env, mid)
    ref = r["resume_reference"]
    # la mission avance -> le token devient périmé
    _prepare(env, mid)
    chk = M.check_resume_preconditions(
        resume_reference=ref, mission_id=mid, work_unit=env["wu"],
        mission_store_dir=env["stores"]["missions"], hold_store_dir=env["stores"]["holds"],
        decision_store_dir=env["stores"]["decisions"])
    assert chk["resumable"] is False
    assert chk["reason"] == "STALE_MISSION_REVISION"


def test_L_tampered_resume_reference_fails_closed(env):
    mid = _genesis(env)["mission_id"]
    _bind(env, mid)
    _, _, r = _hold_and_resolve(env, mid)
    ref = dict(r["resume_reference"])
    ref["next_allowed_transition"] = "SOMETHING_ELSE"
    ok, reason = M.verify_resume_reference(ref)
    assert ok is False and reason == "RESUME_REFERENCE_TAMPERED"


# ══════════════════════════════════════════════════════════════════════════
#  M — dérive réelle branche/worktree rejetée
# ══════════════════════════════════════════════════════════════════════════

def test_M_real_branch_worktree_drift_rejected(env):
    mid = _genesis(env)["mission_id"]
    _bind(env, mid)
    h = _open_hold(env, mid)
    d = _decide(env, mid, h["hold_id"], h["mission_hold_record_hash"])
    # dérive : la branche du worktree est déplacée par un commit étranger
    (env["wt_path"] / "stranger.txt").write_text("x")
    _git(env["wt_path"], "add", "stranger.txt")
    _git(env["wt_path"], "commit", "-q", "-m", "drift")
    r = M.resolve_mission_hold(
        mission_id=mid, hold_id=h["hold_id"],
        human_mission_decision_id=d["human_mission_decision_id"], work_unit=env["wu"],
        mission_store_dir=env["stores"]["missions"], hold_store_dir=env["stores"]["holds"],
        decision_store_dir=env["stores"]["decisions"])
    assert r["status"] == M.STATUS_HOLD_RESOLVE_REJECTED
    assert r["reason"].startswith("WORKTREE_DRIFT:HEAD")


# ══════════════════════════════════════════════════════════════════════════
#  N — la HumanMissionDecision sémantique ne peut PAS satisfaire une HumanApproval
# ══════════════════════════════════════════════════════════════════════════

def test_N_semantic_decision_cannot_satisfy_human_approval(env):
    mid = _genesis(env)["mission_id"]
    _bind(env, mid)
    h = _open_hold(env, mid)
    d = _decide(env, mid, h["hold_id"], h["mission_hold_record_hash"])
    hmd = json.loads((env["stores"]["decisions"] / f"{d['human_mission_decision_id']}.json").read_text(encoding="utf-8"))
    # le vérificateur d'artefact d'approbation canonique la refuse
    ok, reason = BE.verify_approval_artifact(hmd)
    assert ok is False
    # elle ne porte AUCUN champ structurel d'une HumanApproval
    for forbidden in ("approval_schema_version", "approval_status", "approved_by",
                      "execution_authority_hash", "approval_record_hash"):
        assert forbidden not in hmd
    assert hmd["decision_authority"] == "NON_SOVEREIGN"
    assert hmd["not_an_execution_approval"] is True


def test_N_mission_layer_never_writes_human_approval(env):
    mid = _genesis(env)["mission_id"]
    _bind(env, mid)
    p = _prepare(env, mid)
    assert p["human_approval_created_by_mission_layer"] is False
    # aucune approval.json dans le magasin d'exécution APRÈS prepare
    assert not list(env["stores"]["exec"].rglob("approval.json"))


# ══════════════════════════════════════════════════════════════════════════
#  O — BoundedMissionRecord ne peut PAS autoriser une exécution
# ══════════════════════════════════════════════════════════════════════════

def test_O_mission_record_cannot_authorize_execution(env):
    mid = _genesis(env)["mission_id"]
    _bind(env, mid)
    p = _prepare(env, mid)
    # exécuter sans EAH humain valide -> le driver (via le pont) refuse AVANT mutation
    r = _execute(env, mid, p, eah="0" * 64)
    assert r["status"] == M.STATUS_MISSION_EXECUTE_BLOCKED_ENVELOPE_DRIFT
    assert r["checkpoint1_result"]["status"] == WU._DRV.PRE_EXECUTION_REJECTED
    assert (env["wt_path"] / _TARGET_REL).read_bytes() == _A
    assert _proj(env, mid)["current_state"] == M.S_ACTION_PREPARED  # inchangé


def test_O_full_keep_flow_records_evidence_only(env):
    mid = _genesis(env)["mission_id"]
    _bind(env, mid)
    p = _prepare(env, mid)
    r = _execute(env, mid, p)  # EAH exact révélé par prepare = autorisation humaine simulée
    assert r["status"] == M.STATUS_ACTION_RECORDED
    assert r["driver_status"] == WU._DRV.KEPT_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW
    assert r["mission_layer_decided_keep_or_block"] is False
    assert (env["wt_path"] / _TARGET_REL).read_bytes() == _B
    p2 = _proj(env, mid)
    assert p2["current_state"] == M.S_ACTION_EXECUTED_KEPT
    le = p2["linked_governed_executions"][0]
    assert le["outcome_status"] == WU._DRV.KEPT_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW
    assert le["kx108_pre_gate"] == "ALLOW"
    c = M.close_mission_no_plan(mission_id=mid, mission_store_dir=env["stores"]["missions"])
    assert c["status"] == M.STATUS_MISSION_CLOSED
    assert c["current_state"] == M.S_CLOSED_AWAITING_NEXT_PLAN
    assert c["multi_action_sequencer_included"] is False
    assert "NO_SEQUENCER_PLAN" in _proj(env, mid)["unknowns"]


def test_O_negative_flow_rolled_back(env):
    mid = _genesis(env)["mission_id"]
    _bind(env, mid)
    p = _prepare(env, mid, contract=_negative_contract())
    r = _execute(env, mid, p)
    assert r["status"] == M.STATUS_ACTION_RECORDED
    assert r["driver_status"] == WU._DRV.REJECTED_ROLLED_BACK
    assert (env["wt_path"] / _TARGET_REL).read_bytes() == _A
    p2 = _proj(env, mid)
    assert p2["current_state"] == M.S_ACTION_EXECUTED_ROLLED_BACK
    assert p2["actions_failed"] == 1


# ══════════════════════════════════════════════════════════════════════════
#  P — exécution gouvernée historique SANS mission_id se vérifie toujours
# ══════════════════════════════════════════════════════════════════════════

@pytest.mark.skipif(not _ARCHIVE.exists(), reason="canonical C2 proof archive absent")
def test_P_historical_c2_packets_still_verify_without_mission_id():
    for side in ("negative", "positive"):
        pec_f = next((_ARCHIVE / side / "pre_execution_context").glob("pec-*.json"))
        pec = json.loads(pec_f.read_text(encoding="utf-8"))
        assert "mission_id" not in pec
        ok, reason = PEC.verify_pre_execution_context_record(pec)
        assert ok, f"{side} PEC: {reason}"

        for store in ("kx108_pre", "kx108_post"):
            kf = next((_ARCHIVE / side / store).glob("kx*.json"))
            krec = json.loads(kf.read_text(encoding="utf-8"))
            assert "mission_id" not in krec
            ok, reason = DS.verify_kx108_decision_record(krec)
            assert ok, f"{side}/{store}: {reason}"

        appr_f = next((_ARCHIVE / side / "executions" / "approvals").rglob("approval.json"))
        appr = json.loads(appr_f.read_text(encoding="utf-8"))
        ok, reason = BE.verify_approval_artifact(appr)
        assert ok, f"{side} approval: {reason}"
        assert "mission_id" not in appr


# ══════════════════════════════════════════════════════════════════════════
#  Q — redémarrage / reload restaure la projection de mission
# ══════════════════════════════════════════════════════════════════════════

def test_Q_restart_reload_restores_projection(env):
    mid = _genesis(env)["mission_id"]
    _bind(env, mid)
    _prepare(env, mid)
    before = _proj(env, mid)

    # "redémarrage" : purge le module de sys.modules et ré-importe à froid
    for name in ("obsidia_bounded_mission_v0",):
        sys.modules.pop(name, None)
    import obsidia_bounded_mission_v0 as M2
    after = M2.project_mission(mission_id=mid, mission_store_dir=env["stores"]["missions"],
                               hold_store_dir=env["stores"]["holds"])
    assert after["status"] == M2.STATUS_PROJECTION_OK
    assert after["current_state"] == before["current_state"] == "ACTION_PREPARED"
    assert after["mission_revision_record_hash"] == before["mission_revision_record_hash"]
    assert after["last_prepared_evidence"] == before["last_prepared_evidence"]


# ══════════════════════════════════════════════════════════════════════════
#  R — sémantique d'abort fail-safe
# ══════════════════════════════════════════════════════════════════════════

def test_R_abort_before_mutation_is_cleanup_eligible(env):
    mid = _genesis(env)["mission_id"]
    _bind(env, mid)
    a = M.abort_bounded_mission(mission_id=mid, abort_class="ABORT_BEFORE_MUTATION",
                                abort_reference="human-abort-1",
                                mission_store_dir=env["stores"]["missions"], work_unit=env["wu"])
    assert a["status"] == M.STATUS_MISSION_ABORTED
    assert a["automatic_destructive_cleanup"] is False
    assert a["safe_cleanup_eligibility"]["eligible"] is True
    assert _proj(env, mid)["current_state"] == M.S_ABORTED
    # le worktree existe toujours — aucun nettoyage automatique
    assert env["wt_path"].exists()


def test_R_abort_after_kept_is_not_cleanup_eligible(env):
    mid = _genesis(env)["mission_id"]
    _bind(env, mid)
    p = _prepare(env, mid)
    _execute(env, mid, p)
    a = M.abort_bounded_mission(mission_id=mid,
                                abort_class="ABORT_AFTER_EXECUTION_KEPT_BEFORE_GIT_DISPOSITION",
                                abort_reference="human-abort-2",
                                mission_store_dir=env["stores"]["missions"], work_unit=env["wu"])
    assert a["status"] == M.STATUS_MISSION_ABORTED
    assert a["safe_cleanup_eligibility"]["eligible"] is False
    assert a["safe_cleanup_eligibility"]["reason"] == "GOVERNED_EXECUTION_EVIDENCE_PRESENT"


def test_R_abort_unknown_class_rejected(env):
    mid = _genesis(env)["mission_id"]
    _bind(env, mid)
    a = M.abort_bounded_mission(mission_id=mid, abort_class="ABORT_EVERYTHING",
                                abort_reference="x", mission_store_dir=env["stores"]["missions"])
    assert a["status"] == M.STATUS_ABORT_REJECTED
    assert a["reason"] == "UNKNOWN_ABORT_CLASS:ABORT_EVERYTHING"


def test_R_abort_from_closed_state_rejected(env):
    mid = _genesis(env)["mission_id"]
    _bind(env, mid)
    p = _prepare(env, mid)
    _execute(env, mid, p)
    M.close_mission_no_plan(mission_id=mid, mission_store_dir=env["stores"]["missions"])
    a = M.abort_bounded_mission(mission_id=mid, abort_class="ABORT_BEFORE_MUTATION",
                                abort_reference="x", mission_store_dir=env["stores"]["missions"])
    assert a["status"] == M.STATUS_ABORT_REJECTED
    assert a["reason"].startswith("MISSION_NOT_ABORT_ELIGIBLE_FROM_STATE")


# ══════════════════════════════════════════════════════════════════════════
#  S — aucune opération Git distante / mutante dans le module
# ══════════════════════════════════════════════════════════════════════════

def test_S_no_remote_or_mutating_git_static():
    src = Path(M.__file__).read_text(encoding="utf-8")
    for banned in ("git push", "git fetch", "git pull", "git remote", "set-upstream",
                   "--set-upstream", "git commit", "git add", "git merge", "git rebase",
                   "git cherry-pick", "git stash", "git reset", "git checkout",
                   "gh pr", "pull request",
                   '"worktree", "add"', '"worktree", "remove"', '"branch", "-d"',
                   '"branch", "-D"', "--force"):
        assert banned not in src, banned
    assert "REMOTE_GIT_OPERATIONS" not in src or "[]" in src


def test_S_git_calls_are_read_only_facts_only():
    src = Path(M.__file__).read_text(encoding="utf-8")
    # tous les appels Git passent par les helpers PEC READ-ONLY
    assert "_PEC._run_git(" in src
    # sous-commandes autorisées : lecture de faits uniquement
    for allowed in ('"rev-parse"', '"worktree", "list"', '"status", "--porcelain"'):
        assert allowed in src


# ══════════════════════════════════════════════════════════════════════════
#  T — audit/world_action_bus jamais référencé
# ══════════════════════════════════════════════════════════════════════════

def test_T_no_audit_world_action_bus_reference():
    src = Path(M.__file__).read_text(encoding="utf-8")
    assert "world_action_bus" not in src
    assert "audit/" not in src


# ══════════════════════════════════════════════════════════════════════════
#  U — transition illégale rejetée sans révision persistée
# ══════════════════════════════════════════════════════════════════════════

def test_U_illegal_transition_rejected_no_revision(env):
    mid = _genesis(env)["mission_id"]
    # execute sans bind ni prepare -> refus, aucune révision au-delà de la genèse (rev 1)
    r = M.execute_mission_action(
        mission_id=mid, work_unit=env["wu"], batch_execution_id="x", child_execution_id="y",
        human_authorized_execution_authority_hash="0" * 64, human_authorization_reference="r",
        execution_dir=env["stores"]["exec"], pre_execution_context_dir=env["stores"]["pec"],
        selector_dir=env["stores"]["selector"], ledger_dir=env["stores"]["ledger"],
        kx108_pre_decision_dir=env["stores"]["kxpre"], kx108_post_decision_dir=env["stores"]["kxpost"],
        test_contract_results_dir=env["stores"]["tcr"], sealed_receipt_dir=env["stores"]["sar"],
        sealed_rollback_evidence_dir=env["stores"]["sre"], rollback_result_dir=env["stores"]["rbk"],
        mission_store_dir=env["stores"]["missions"])
    assert r["status"] == M.STATUS_EXECUTE_REJECTED
    assert r["reason"].startswith("MISSION_NOT_IN_ACTION_PREPARED_STATE")
    rev_files = list((env["stores"]["missions"] / mid / "revisions").glob("*.json"))
    assert len(rev_files) == 1  # seule la révision de genèse


def test_U_hold_from_illegal_state_rejected(env):
    mid = _genesis(env)["mission_id"]  # état CREATED
    r = _open_hold(env, mid)
    assert r["status"] == M.STATUS_HOLD_OPEN_REJECTED
    assert r["reason"].startswith("MISSION_NOT_HOLDABLE_FROM_STATE")


# ══════════════════════════════════════════════════════════════════════════
#  V — rupture de chaîne de révision détectée
# ══════════════════════════════════════════════════════════════════════════

def test_V_revision_chain_break_detected(env):
    mid = _genesis(env)["mission_id"]
    _bind(env, mid)
    _prepare(env, mid)
    revs = sorted((env["stores"]["missions"] / mid / "revisions").glob("*.json"))
    rec = json.loads(revs[1].read_text(encoding="utf-8"))
    rec["parent_revision_hash"] = "0" * 64  # casse le maillon
    revs[1].write_text(json.dumps(rec, indent=2, sort_keys=True), encoding="utf-8")
    p = _proj(env, mid)
    assert p["status"] == M.STATUS_MISSION_PROJECTION_INVALID
    assert "REVISION_RECORD_HASH_MISMATCH" in p["reason"] or "REVISION_CHAIN_BREAK" in p["reason"]


def test_V_revision_index_gap_detected(env):
    mid = _genesis(env)["mission_id"]
    _bind(env, mid)
    _prepare(env, mid)
    revs = sorted((env["stores"]["missions"] / mid / "revisions").glob("*.json"))
    revs[1].unlink()  # supprime la révision 2, laisse la 3
    p = _proj(env, mid)
    assert p["status"] == M.STATUS_MISSION_PROJECTION_INVALID


# ══════════════════════════════════════════════════════════════════════════
#  W — champ lié trafiqué -> projection invalide
# ══════════════════════════════════════════════════════════════════════════

def test_W_tampered_bound_field_invalidates_projection(env):
    mid = _genesis(env)["mission_id"]
    _bind(env, mid)
    revs = sorted((env["stores"]["missions"] / mid / "revisions").glob("*.json"))
    rec = json.loads(revs[-1].read_text(encoding="utf-8"))
    rec["to_state"] = "ACTION_EXECUTED_KEPT"  # saut d'état arbitraire
    revs[-1].write_text(json.dumps(rec, indent=2, sort_keys=True), encoding="utf-8")
    p = _proj(env, mid)
    assert p["status"] == M.STATUS_MISSION_PROJECTION_INVALID


def test_W_tampered_genesis_scope_invalidates(env):
    mid = _genesis(env)["mission_id"]
    gpath = env["stores"]["missions"] / mid / "genesis.json"
    g = json.loads(gpath.read_text(encoding="utf-8"))
    g["scope"]["max_actions"] = 99  # tentative d'élargissement de portée
    gpath.write_text(json.dumps(g, indent=2, sort_keys=True), encoding="utf-8")
    p = _proj(env, mid)
    assert p["status"] == M.STATUS_MISSION_PROJECTION_INVALID
    assert p["reason"] == "MISSION_GENESIS_RECORD_HASH_MISMATCH"


# ══════════════════════════════════════════════════════════════════════════
#  X — rejeu / résolution d'un HOLD supersédé rejeté
# ══════════════════════════════════════════════════════════════════════════

def test_X_resolve_already_resolved_hold_rejected(env):
    mid = _genesis(env)["mission_id"]
    _bind(env, mid)
    h, d, r = _hold_and_resolve(env, mid)
    assert r["status"] == M.STATUS_HOLD_RESOLVED
    # rejouer la même résolution -> la mission n'est plus HELD
    again = M.resolve_mission_hold(
        mission_id=mid, hold_id=h["hold_id"],
        human_mission_decision_id=d["human_mission_decision_id"], work_unit=env["wu"],
        mission_store_dir=env["stores"]["missions"], hold_store_dir=env["stores"]["holds"],
        decision_store_dir=env["stores"]["decisions"])
    assert again["status"] == M.STATUS_HOLD_RESOLVE_REJECTED
    assert again["reason"] == "MISSION_NOT_HELD"


def test_X_superseded_hold_after_abort_while_hold(env):
    mid = _genesis(env)["mission_id"]
    _bind(env, mid)
    h = _open_hold(env, mid)
    a = M.abort_bounded_mission(mission_id=mid, abort_class="ABORT_WHILE_HOLD",
                                abort_reference="x", mission_store_dir=env["stores"]["missions"])
    assert a["status"] == M.STATUS_MISSION_ABORTED
    p = _proj(env, mid)
    assert p["holds"][h["hold_id"]]["resolution_state"] == "SUPERSEDED"


# ══════════════════════════════════════════════════════════════════════════
#  §31 — tests d'attaque d'autorité supplémentaires
# ══════════════════════════════════════════════════════════════════════════

def test_attack_mission_scope_cannot_widen_through_revision(env):
    # scope max_actions=1 ; après une action KEPT, une 2e prepare est refusée
    mid = _genesis(env)["mission_id"]
    _bind(env, mid)
    p = _prepare(env, mid)
    _execute(env, mid, p)
    M.close_mission_no_plan(mission_id=mid, mission_store_dir=env["stores"]["missions"])
    # la mission est CLOSED ; même en forçant un retour, le scope reste la borne
    p2 = _prepare(env, mid)
    assert p2["status"] == M.STATUS_PREPARE_REJECTED


def test_attack_scope_refusal_never_becomes_authorization(env):
    scope = dict(_DEFAULT_SCOPE)
    scope["allowed_target_paths"] = ["some/other/path.txt"]
    mid = _genesis(env, scope=scope)["mission_id"]
    _bind(env, mid)
    p = _prepare(env, mid)  # target = _TARGET_REL, hors scope
    assert p["status"] == M.STATUS_PREPARE_REJECTED
    assert p["reason"].startswith("MISSION_SCOPE_TARGET_PATH_NOT_ALLOWED")
    assert p["mission_scope_is_upper_bound"] is True


def test_attack_mission_record_writes_no_target_bytes(env):
    src = Path(M.__file__).read_text(encoding="utf-8")
    # unique helper d'écriture ; aucune écriture binaire ; aucune ouverture de cible
    assert src.count("def _atomic_publish_json(") == 1
    assert ".write_bytes(" not in src
    assert 'open(' not in src or src.count("open(") == src.count("os.link")  # aucune open() nue
    # write_text n'apparaît que dans le helper de publication
    assert src.count("write_text(") == 1


def test_attack_hmd_with_forged_approval_field_rejected(env):
    mid = _genesis(env)["mission_id"]
    _bind(env, mid)
    h = _open_hold(env, mid)
    d = _decide(env, mid, h["hold_id"], h["mission_hold_record_hash"])
    dpath = env["stores"]["decisions"] / f"{d['human_mission_decision_id']}.json"
    rec = json.loads(dpath.read_text(encoding="utf-8"))
    rec["execution_authority_hash"] = "f" * 64  # champ d'approbation forgé
    dpath.write_text(json.dumps(rec, indent=2, sort_keys=True), encoding="utf-8")
    ok, reason = M.verify_human_mission_decision(rec)
    assert ok is False
    assert reason == "HMD_CARRIES_FORBIDDEN_APPROVAL_FIELD:execution_authority_hash"


def test_attack_mission_object_passed_as_human_approval_rejected(env):
    mid = _genesis(env)["mission_id"]
    _bind(env, mid)
    genesis = json.loads((env["stores"]["missions"] / mid / "genesis.json").read_text(encoding="utf-8"))
    ok, reason = BE.verify_approval_artifact(genesis)
    assert ok is False


# ══════════════════════════════════════════════════════════════════════════
#  §32 — invariants formels + §33 audit de graphe d'appels statique
# ══════════════════════════════════════════════════════════════════════════

def test_static_no_rail_duplication_first_real_caller_only():
    src = Path(M.__file__).read_text(encoding="utf-8")
    for banned in ("register_git_blob_source", "propose_batch",
                   "store_approval_artifact(", "run_and_persist_kx108",
                   "run_governed_content_apply(", "run_governed_rollback(",
                   "run_tooling_build_pipeline", "create_pre_execution_context(",
                   "GuardX108", "translate_pre_execution_evidence"):
        assert banned not in src, banned
    # délègue au pont Checkpoint 1 — exactement un site par phase
    assert src.count("_WU.prepare_work_unit_execution(") == 1
    assert src.count("_WU.execute_work_unit_remediation(") == 1
    # ne fabrique jamais d'autorité (patterns d'IMPLÉMENTATION, pas les
    # mentions du docstring ni la liste défensive de rejet de verify_*)
    for banned in ("class BoundedMissionAuthority", "class MissionAuthority",
                   "def preapprove", "def pre_approve", "APPROVED_FOR_MISSION",
                   '"approved_by": "', '"approval_status": ', "APPROVED_FOR_BOUNDED_EXECUTION"):
        assert banned not in src, banned


def test_static_mission_layer_direct_write_targets_only_own_stores():
    src = Path(M.__file__).read_text(encoding="utf-8")
    # les seuls magasins écrits sont ceux de la mission
    assert "_atomic_publish_json(" in src
    # aucun appel direct aux constructeurs de records gouvernés
    for banned in ("compute_approval_record_hash", "compute_kx108_decision_record_hash",
                   "store_kx108_decision_record", "store_test_contract_result",
                   "store_sealed_apply_receipt", "store_rollback_result"):
        assert banned not in src, banned


def test_static_reserved_authority_fields_absent():
    src = Path(M.__file__).read_text(encoding="utf-8")
    # AUCUN champ / classe réservé d'autorité de mission (le docstring peut
    # nommer le concept pour dire qu'il ne l'implémente PAS — cf. Checkpoint 1)
    assert "bounded_mission_authority_ref" not in src
    assert "stage3_plan_ref" not in src
    assert "class BoundedMissionAuthority" not in src
    assert "KX108_ONLY" in src and "NON_SOVEREIGN" in src


def test_static_execute_requires_exact_human_authorization_inputs():
    # Stage 4G : les paramètres d'EAH humain deviennent Optional pour le dispatch
    # de mode (`authority_mode`), mais en mode historique PER_ACTION_HUMAN_EAH
    # (défaut) leur exigence exacte reste portée par le driver. En mode Stage 4,
    # tout EAH humain par action est REJETÉ.
    sig = inspect.signature(M.execute_mission_action)
    for pn in ("human_authorized_execution_authority_hash", "human_authorization_reference"):
        assert pn in sig.parameters
    assert sig.parameters["authority_mode"].default == "PER_ACTION_HUMAN_EAH"
    src = Path(M.__file__).read_text(encoding="utf-8")
    assert "STAGE4_MODE_REJECTS_PER_ACTION_HUMAN_EAH" in src


def test_static_no_multi_action_sequencer():
    src = Path(M.__file__).read_text(encoding="utf-8")
    for banned in ("for ", "while "):
        pass  # (des boucles de projection légitimes existent)
    # aucune fonction ne combine prepare + execute + sélection d'action suivante
    assert "def run_mission" not in src
    assert "next_action_select" not in src and "select_next_action" not in src
    assert "def sequence" not in src


def test_invariant_current_state_is_derived_never_stored(env):
    mid = _genesis(env)["mission_id"]
    _bind(env, mid)
    files = {p.name for p in (env["stores"]["missions"] / mid).rglob("*") if p.is_file()}
    assert "current_state.json" not in files
    assert "state.json" not in files
    g = json.loads((env["stores"]["missions"] / mid / "genesis.json").read_text(encoding="utf-8"))
    assert "current_state" not in g
    # chaque révision ne stocke que from_state/to_state (transition), jamais un "état courant"
    for rp in (env["stores"]["missions"] / mid / "revisions").glob("*.json"):
        r = json.loads(rp.read_text(encoding="utf-8"))
        assert set(r["evidence_refs"]) or r["event"] == M.E_MISSION_CREATED
        assert "current_state" not in r


def test_invariant_no_governed_store_schema_migration():
    # les jeux de champs liés des magasins gouvernés sont inchangés (versions figées)
    assert BE.SCHEMA_VERSION == "V0"
    assert PEC.SCHEMA_VERSION == 2
    assert DS.SCHEMA_VERSION == 1
    assert TC.SCHEMA_VERSION == 1


def test_invariant_audit_world_action_bus_untouched():
    # le module mission n'écrit jamais dans le dépôt canonique
    p = _REPO_ROOT / "audit" / "world_action_bus.jsonl"
    src = Path(M.__file__).read_text(encoding="utf-8")
    assert str(p) not in src and "world_action_bus" not in src


# ══════════════════════════════════════════════════════════════════════════
#  STAGE 3B — intégration du mission_tip DÉRIVÉ à partir de snapshots Stage 3A
# ══════════════════════════════════════════════════════════════════════════

_S3B_ACTION_ID = "act-ck2-stage3b-0001"


def _snap_dir(env):
    d = env["root"] / "snap3b"
    return d


def _drive_mission_to_kept(env, *, objective="stage3b", contract=None):
    r = _genesis(env, objective=objective)
    mid = r["mission_id"]
    assert _bind(env, mid)["status"] == M.STATUS_WORKTREE_BOUND
    p = _prepare(env, mid, contract=contract)
    assert p["status"] == M.STATUS_ACTION_PREPARED, p
    ex = _execute(env, mid, p)
    return mid, p, ex


def _stage3a_snapshot(env, mid, p, ex, *, action_id=_S3B_ACTION_ID, ordinal=0, **over):
    s = env["stores"]
    c1 = ex["checkpoint1_result"]
    kw = dict(
        mission_id=mid, action_id=action_id, ordinal=ordinal,
        expected_branch_name="bmbr", expected_worktree_path=env["wt_path"],
        expected_previous_mission_tip_sha=env["base_sha"],
        batch_execution_id=p["batch_execution_id"], child_execution_id=p["child_execution_id"],
        execution_authority_hash=c1["execution_authority_hash"], approval_id=c1["approval_id"],
        kx108_pre_decision_record_id=c1["kx108_pre_decision_record_id"],
        kx108_post_decision_record_id=c1["kx108_post_decision_record_id"],
        test_contract_result_id=c1["test_contract_result_id"],
        sealed_apply_receipt_id=c1["sealed_apply_receipt_id"],
        sealed_rollback_evidence_id=c1["sealed_rollback_evidence_id"],
        target_path=_TARGET_REL,
        execution_dir=s["exec"], kx108_pre_decision_dir=s["kxpre"],
        kx108_post_decision_dir=s["kxpost"], test_contract_results_dir=s["tcr"],
        sealed_receipt_dir=s["sar"], sealed_rollback_evidence_dir=s["sre"],
        rollback_result_dir=s["rbk"], snapshot_store_dir=_snap_dir(env),
    )
    kw.update(over)
    return LS.create_local_snapshot(**kw)


def _record(env, mid, snap, *, action_id=_S3B_ACTION_ID):
    return M.record_local_snapshot(
        mission_id=mid, action_id=action_id, snapshot_receipt_id=snap["snapshot_receipt_id"],
        work_unit=env["wu"], snapshot_store_dir=_snap_dir(env),
        mission_store_dir=env["stores"]["missions"])


# ── A / D — mission historique sans snapshot : tip == canonical_base_sha ──

def test_S3B_A_historical_mission_tip_equals_canonical_base(env):
    mid = _genesis(env)["mission_id"]
    _bind(env, mid)
    proj = _proj(env, mid)
    assert proj["mission_tip_sha"] == proj["canonical_base_sha"] == env["base_sha"]
    assert proj["has_local_mission_snapshots"] is False
    assert proj["local_snapshot_count"] == 0


# ── B / C / D / E / F — snapshot vérifié -> tip avance ──

def test_S3B_BC_verified_receipt_advances_mission_tip(env):
    mid, p, ex = _drive_mission_to_kept(env)
    assert ex["driver_status"] == WU._DRV.KEPT_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW
    assert _proj(env, mid)["current_state"] == M.S_ACTION_EXECUTED_KEPT
    snap = _stage3a_snapshot(env, mid, p, ex)
    assert snap["status"] == LS.SNAPSHOT_COMMITTED, snap
    rec = _record(env, mid, snap)
    assert rec["status"] == M.STATUS_LOCAL_SNAPSHOT_RECORDED, rec
    proj = _proj(env, mid)
    assert proj["mission_tip_sha"] == snap["new_commit_sha"]                  # C
    assert proj["canonical_base_sha"] == env["base_sha"]                      # D
    assert proj["current_state"] == M.S_WORKTREE_BOUND                        # E
    assert proj["has_local_mission_snapshots"] is True
    assert proj["local_snapshot_count"] == 1
    # F — la révision ne stocke que des références exactes du reçu
    revs = sorted((env["stores"]["missions"] / mid / "revisions").glob("*.json"))
    last = json.loads(revs[-1].read_text(encoding="utf-8"))
    assert last["event"] == M.E_ACTION_LOCAL_SNAPSHOT_COMMITTED
    ev = last["evidence_refs"]
    assert ev["new_commit_sha"] == snap["new_commit_sha"]
    assert ev["commit_parent_sha"] == env["base_sha"]
    assert ev["new_mission_tip_sha"] == snap["new_commit_sha"]
    assert ev["snapshot_receipt_id"] == snap["snapshot_receipt_id"]
    assert ev["committed_paths"] == [_TARGET_REL]
    assert "target_post_sha256" not in ev  # détail canonique -> reste dans le reçu


# ── G / H / I / J / K / L — reçu invalide / mal lié rejeté ──

def test_S3B_G_invalid_receipt_rejected(env):
    mid, p, ex = _drive_mission_to_kept(env)
    _stage3a_snapshot(env, mid, p, ex)
    # trafiquer le reçu stocké
    rid = LS._snapshot_receipt_id  # sanity: helper exists
    files = list(_snap_dir(env).glob("lsr-*.json"))
    assert files
    rec = json.loads(files[0].read_text(encoding="utf-8"))
    rec["new_commit_sha"] = "0" * 40
    files[0].write_text(json.dumps(rec, indent=2, sort_keys=True), encoding="utf-8")
    out = M.record_local_snapshot(
        mission_id=mid, action_id=_S3B_ACTION_ID, snapshot_receipt_id=rec["snapshot_receipt_id"],
        work_unit=env["wu"], snapshot_store_dir=_snap_dir(env), mission_store_dir=env["stores"]["missions"])
    assert out["status"] == M.STATUS_LOCAL_SNAPSHOT_RECORD_REJECTED
    assert out["reason"].startswith("SNAPSHOT_RECEIPT_INVALID")
    assert _proj(env, mid)["mission_tip_sha"] == env["base_sha"]  # tip inchangé


def test_S3B_H_wrong_mission_receipt_rejected(env):
    mid, p, ex = _drive_mission_to_kept(env)
    snap = _stage3a_snapshot(env, mid, p, ex)
    # créer une 2e mission au même worktree/base
    other = _genesis(env, objective="other-mission")["mission_id"]
    _bind(env, other)
    # ... mais elle n'est pas KEPT
    out = M.record_local_snapshot(
        mission_id=other, action_id=_S3B_ACTION_ID, snapshot_receipt_id=snap["snapshot_receipt_id"],
        work_unit=env["wu"], snapshot_store_dir=_snap_dir(env), mission_store_dir=env["stores"]["missions"])
    assert out["status"] == M.STATUS_LOCAL_SNAPSHOT_RECORD_REJECTED
    assert out["reason"].startswith("ONLY_KEEP_CAN_ADVANCE_MISSION_TIP")


def test_S3B_I_wrong_action_receipt_rejected(env):
    mid, p, ex = _drive_mission_to_kept(env)
    snap = _stage3a_snapshot(env, mid, p, ex, action_id="act-real")
    out = M.record_local_snapshot(
        mission_id=mid, action_id="act-DIFFERENT", snapshot_receipt_id=snap["snapshot_receipt_id"],
        work_unit=env["wu"], snapshot_store_dir=_snap_dir(env), mission_store_dir=env["stores"]["missions"])
    assert out["status"] == M.STATUS_LOCAL_SNAPSHOT_RECORD_REJECTED
    assert out["reason"] == "SNAPSHOT_RECEIPT_ACTION_MISMATCH"


def test_S3B_M_non_keep_state_cannot_record_snapshot(env):
    mid, p, ex = _drive_mission_to_kept(env, contract=_negative_contract())
    assert ex["driver_status"] == WU._DRV.REJECTED_ROLLED_BACK
    # pas de reçu Stage 3A possible ; on tente record avec un id bidon
    out = M.record_local_snapshot(
        mission_id=mid, action_id=_S3B_ACTION_ID, snapshot_receipt_id="lsr-bogus",
        work_unit=env["wu"], snapshot_store_dir=_snap_dir(env), mission_store_dir=env["stores"]["missions"])
    assert out["status"] == M.STATUS_LOCAL_SNAPSHOT_RECORD_REJECTED
    assert out["reason"].startswith("ONLY_KEEP_CAN_ADVANCE_MISSION_TIP")


def test_S3B_N_double_incompatible_snapshot_rejected(env):
    mid, p, ex = _drive_mission_to_kept(env)
    snap = _stage3a_snapshot(env, mid, p, ex)
    r1 = _record(env, mid, snap)
    assert r1["status"] == M.STATUS_LOCAL_SNAPSHOT_RECORDED
    # même action, id de reçu différent -> fork rejeté
    out = M.record_local_snapshot(
        mission_id=mid, action_id=_S3B_ACTION_ID, snapshot_receipt_id="lsr-other",
        work_unit=env["wu"], snapshot_store_dir=_snap_dir(env), mission_store_dir=env["stores"]["missions"])
    # état déjà WORKTREE_BOUND -> refus "only KEEP" (défense en profondeur)
    assert out["status"] == M.STATUS_LOCAL_SNAPSHOT_RECORD_REJECTED


def test_S3B_idempotent_same_receipt(env):
    mid, p, ex = _drive_mission_to_kept(env)
    snap = _stage3a_snapshot(env, mid, p, ex)
    r1 = _record(env, mid, snap)
    n_before = _proj(env, mid)["revision"]
    # ré-appel identique alors qu'on est déjà WORKTREE_BOUND -> pas de 2e révision
    # (l'état n'est plus ACTION_EXECUTED_KEPT ; défense en profondeur)
    r2 = M.record_local_snapshot(
        mission_id=mid, action_id=_S3B_ACTION_ID, snapshot_receipt_id=snap["snapshot_receipt_id"],
        work_unit=env["wu"], snapshot_store_dir=_snap_dir(env), mission_store_dir=env["stores"]["missions"])
    assert r2["status"] in (M.STATUS_LOCAL_SNAPSHOT_EVENT_IDEMPOTENT, M.STATUS_LOCAL_SNAPSHOT_RECORD_REJECTED)
    assert _proj(env, mid)["revision"] == n_before


# ── O / P — chaîne de tip dérivée + fail-closed (fixtures de révision contrôlées) ──

def _raw_append(env, mid, *, event, from_state, to_state, evidence_refs):
    d = env["stores"]["missions"] / mid / "revisions"
    revs = sorted(d.glob("*.json"))
    last = json.loads(revs[-1].read_text(encoding="utf-8"))
    n = last["revision"] + 1
    rec = {
        "mission_record_schema_version": M.REVISION_SCHEMA_VERSION,
        "mission_id": mid, "revision": n,
        "parent_revision_hash": last["mission_revision_record_hash"],
        "event": event, "from_state": from_state, "to_state": to_state,
        "evidence_refs": evidence_refs, "actor": "STACK",
        "created_at": "2026-08-28T00:00:00+00:00",
    }
    rec["mission_revision_record_hash"] = M._record_hash(rec, M._REVISION_BOUND_FIELDS)
    (d / f"{n:06d}-{rec['mission_revision_record_hash'][:12]}.json").write_text(
        json.dumps(rec, indent=2, sort_keys=True), encoding="utf-8")
    return rec


def _kept_ev(bid, cid, eah):
    return {"driver_status": WU._DRV.KEPT_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW,
            "batch_execution_id": bid, "child_execution_id": cid,
            "execution_authority_hash": eah, "approval_id": "appr-x",
            "kx108_pre_decision_record_id": "kxpre-x", "kx108_pre_gate": "ALLOW",
            "kx108_post_gate": "ALLOW", "rollback_result_id": None,
            "sealed_apply_receipt_id": "sar-x", "sealed_rollback_evidence_id": "sre-x",
            "target_mutated": True}


def _snap_ev(action_id, prev_tip, commit):
    return {"mission_id": None, "action_id": action_id, "ordinal": 0,
            "previous_mission_tip_sha": prev_tip, "new_mission_tip_sha": commit,
            "new_commit_sha": commit, "commit_parent_sha": prev_tip,
            "committed_paths": [_TARGET_REL], "snapshot_receipt_id": f"lsr-{action_id}",
            "local_snapshot_receipt_record_hash": "h" * 64}


def test_S3B_OP_two_snapshot_projection_chain(env):
    # base -> A -> B via fixtures de révision valides ; prouve la DÉRIVATION du tip
    mid, p, ex = _drive_mission_to_kept(env)
    snap = _stage3a_snapshot(env, mid, p, ex)
    _record(env, mid, snap)                        # base -> A (réel)
    commit_a = snap["new_commit_sha"]
    # fabriquer une 2e action KEEP + snapshot B (fixtures — Stage 3C absent)
    commit_b = "b" * 40
    _raw_append(env, mid, event=M.E_ACTION_PREPARE_SUCCEEDED, from_state=M.S_WORKTREE_BOUND,
                to_state=M.S_ACTION_PREPARED,
                evidence_refs={"batch_execution_id": "be2", "child_execution_id": "ce2",
                               "execution_authority_hash": "e" * 64, "pre_execution_context_id": "pec2",
                               "pre_execution_context_record_hash": "p" * 64, "test_contract_hash": "t" * 64,
                               "ledger_entry_id": "le2", "target_path": _TARGET_REL,
                               "operation": "UPDATE_TARGET_FROM_SOURCE"})
    _raw_append(env, mid, event=M.E_ACTION_EXECUTE_KEPT, from_state=M.S_ACTION_PREPARED,
                to_state=M.S_ACTION_EXECUTED_KEPT, evidence_refs=_kept_ev("be2", "ce2", "e" * 64))
    _raw_append(env, mid, event=M.E_ACTION_LOCAL_SNAPSHOT_COMMITTED,
                from_state=M.S_ACTION_EXECUTED_KEPT, to_state=M.S_WORKTREE_BOUND,
                evidence_refs=_snap_ev("act-B", commit_a, commit_b))
    proj = _proj(env, mid)
    assert proj["status"] == M.STATUS_PROJECTION_OK
    assert proj["mission_tip_sha"] == commit_b
    assert proj["local_snapshot_count"] == 2
    assert proj["local_snapshots"][0]["new_commit_sha"] == commit_a
    assert proj["local_snapshots"][1]["commit_parent_sha"] == commit_a
    assert proj["canonical_base_sha"] == env["base_sha"]


def test_S3B_O_broken_snapshot_chain_projection_invalid(env):
    mid, p, ex = _drive_mission_to_kept(env)
    snap = _stage3a_snapshot(env, mid, p, ex)
    _record(env, mid, snap)
    # snapshot B avec un previous_tip FAUX (ne descend pas de A)
    _raw_append(env, mid, event=M.E_ACTION_PREPARE_SUCCEEDED, from_state=M.S_WORKTREE_BOUND,
                to_state=M.S_ACTION_PREPARED,
                evidence_refs={"batch_execution_id": "be2", "child_execution_id": "ce2",
                               "execution_authority_hash": "e" * 64, "pre_execution_context_id": "pec2",
                               "pre_execution_context_record_hash": "p" * 64, "test_contract_hash": "t" * 64})
    _raw_append(env, mid, event=M.E_ACTION_EXECUTE_KEPT, from_state=M.S_ACTION_PREPARED,
                to_state=M.S_ACTION_EXECUTED_KEPT, evidence_refs=_kept_ev("be2", "ce2", "e" * 64))
    _raw_append(env, mid, event=M.E_ACTION_LOCAL_SNAPSHOT_COMMITTED,
                from_state=M.S_ACTION_EXECUTED_KEPT, to_state=M.S_WORKTREE_BOUND,
                evidence_refs=_snap_ev("act-B", "f" * 40, "b" * 40))   # previous_tip faux
    proj = _proj(env, mid)
    assert proj["status"] == M.STATUS_MISSION_PROJECTION_INVALID
    assert "SNAPSHOT_TIP_CHAIN_BREAK" in proj["reason"]


def test_S3B_non_keep_snapshot_event_rejected_in_fold(env):
    mid = _genesis(env)["mission_id"]
    _bind(env, mid)
    # tenter d'appender un snapshot depuis WORKTREE_BOUND (transition illégale)
    _raw_append(env, mid, event=M.E_ACTION_LOCAL_SNAPSHOT_COMMITTED,
                from_state=M.S_WORKTREE_BOUND, to_state=M.S_WORKTREE_BOUND,
                evidence_refs=_snap_ev("act-x", env["base_sha"], "a" * 40))
    proj = _proj(env, mid)
    assert proj["status"] == M.STATUS_MISSION_PROJECTION_INVALID
    assert "MISSION_TRANSITION_ILLEGAL" in proj["reason"]


# ── R / S / T — liaison worktree tip-aware ──

def test_S3B_R_worktree_binding_accepts_head_equal_derived_tip(env):
    mid, p, ex = _drive_mission_to_kept(env)
    snap = _stage3a_snapshot(env, mid, p, ex)
    _record(env, mid, snap)
    proj = _proj(env, mid)
    # HEAD du worktree == nouveau tip (Stage 3A a committé) ; require_clean OK
    ok, reason = M._verify_mission_worktree_binding(
        M._load_genesis(mid, env["stores"]["missions"]),
        env["wt_path"], env["main"].resolve(),
        require_clean=True, expected_head_sha=proj["mission_tip_sha"])
    assert ok, reason


def test_S3B_S_worktree_binding_rejects_head_at_old_canonical_base(env):
    mid, p, ex = _drive_mission_to_kept(env)
    snap = _stage3a_snapshot(env, mid, p, ex)
    _record(env, mid, snap)
    ok, reason = M._verify_mission_worktree_binding(
        M._load_genesis(mid, env["stores"]["missions"]),
        env["wt_path"], env["main"].resolve(),
        require_clean=True, expected_head_sha=env["base_sha"])   # ancien base, tip a avancé
    assert ok is False
    assert reason.startswith("WORKTREE_DRIFT:HEAD")


def test_S3B_T_worktree_binding_still_rejects_dirty(env):
    mid, p, ex = _drive_mission_to_kept(env)
    snap = _stage3a_snapshot(env, mid, p, ex)
    _record(env, mid, snap)
    (env["wt_path"] / _TARGET_REL).write_bytes(b"dirty again\n")
    proj = _proj(env, mid)
    ok, reason = M._verify_mission_worktree_binding(
        M._load_genesis(mid, env["stores"]["missions"]),
        env["wt_path"], env["main"].resolve(),
        require_clean=True, expected_head_sha=proj["mission_tip_sha"])
    assert ok is False and reason == "WORKTREE_DRIFT:DIRTY"


# ── W — mission avec snapshot n'est pas auto-cleanup-eligible ──

def test_S3B_W_snapshot_mission_not_auto_cleanup_eligible(env):
    mid, p, ex = _drive_mission_to_kept(env)
    snap = _stage3a_snapshot(env, mid, p, ex)
    _record(env, mid, snap)
    elig = M.compute_safe_cleanup_eligibility(_proj(env, mid), env["wu"])
    assert elig["eligible"] is False
    assert elig["reason"] == "SNAPSHOT_MISSION_REQUIRES_HUMAN_GIT_DISPOSITION"


# ── static / invariance ──

def test_S3B_static_no_git_mutation_and_reuses_receipt():
    src = Path(M.__file__).read_text(encoding="utf-8")
    for banned in ('"add", "--"', '"add", "."', '"commit", "-m"', '"restore", "--staged"',
                   '"reset"', '"--hard"', '"clean"', '"checkout"', '"push"', '"merge"',
                   '"rebase"', '"cherry-pick"', "create_local_snapshot("):
        assert banned not in src, banned
    # réutilise le VÉRIFICATEUR canonique Stage 3A, ne le duplique pas
    assert "verify_local_snapshot_receipt" in src
    assert src.count("_LS.verify_local_snapshot_receipt(") == 1
    # ne réimplémente pas la vérification de reçu
    assert "_LS_BOUND_FIELDS" not in src and "snapshot_correlation_id" not in src


def test_S3B_stage3a_module_and_pec_byte_unchanged():
    # Stage 3B ne touche NI le module de snapshot Stage 3A NI le PEC.
    # (Le driver `obsidia_governed_execution_driver_v0.py` est modifié plus tard,
    #  par Stage 4F — intégration d'autorité PRE dérivée ; hors périmètre 3B.)
    r = subprocess.run(["git", "status", "--porcelain",
                        "scripts/obsidia_mission_local_snapshot_v0.py",
                        "scripts/obsidia_pre_execution_context.py"],
                       cwd=str(_REPO_ROOT), capture_output=True, text=True)
    assert r.stdout.strip() == "", f"unexpected changes: {r.stdout}"


def test_S3B_canonical_base_never_mutated_by_snapshot(env):
    mid, p, ex = _drive_mission_to_kept(env)
    g_before = json.loads((env["stores"]["missions"] / mid / "genesis.json").read_text(encoding="utf-8"))
    snap = _stage3a_snapshot(env, mid, p, ex)
    _record(env, mid, snap)
    g_after = json.loads((env["stores"]["missions"] / mid / "genesis.json").read_text(encoding="utf-8"))
    assert g_before == g_after
    assert g_after["canonical_base_sha"] == env["base_sha"]
    ok, why = M._verify_genesis(g_after)
    assert ok, why


def test_S3B_real_keep_snapshot_to_mission_tip_proof(env):
    """§22 — preuve d'intégration bout-en-bout, dépôt temporaire réel."""
    mid, p, ex = _drive_mission_to_kept(env)
    assert ex["driver_status"] == WU._DRV.KEPT_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW
    snap = _stage3a_snapshot(env, mid, p, ex)
    assert snap["status"] == LS.SNAPSHOT_COMMITTED
    ok, why = LS.verify_local_snapshot_receipt(snap["snapshot_receipt"], repo_root=env["wt_path"])
    assert ok, why
    rec = _record(env, mid, snap)
    assert rec["status"] == M.STATUS_LOCAL_SNAPSHOT_RECORDED
    assert rec["mission_layer_creates_local_git_commit"] is False
    assert rec["mission_layer_reuses_stage_3a_receipt"] is True
    # rechargement à froid
    for name in ("obsidia_bounded_mission_v0",):
        sys.modules.pop(name, None)
    import obsidia_bounded_mission_v0 as M2
    proj = M2.project_mission(mission_id=mid, mission_store_dir=env["stores"]["missions"])
    import obsidia_bounded_mission_v0  # noqa: restaure l'alias
    assert proj["canonical_base_sha"] == env["base_sha"]
    assert proj["mission_tip_sha"] == snap["new_commit_sha"]
    assert proj["current_state"] == "WORKTREE_BOUND"
    assert _git(env["wt_path"], "status", "--porcelain") == ""
    assert _git(env["wt_path"], "rev-parse", "HEAD") == snap["new_commit_sha"]


# ══════════════════════════════════════════════════════════════════════════
#  STAGE 3D — MissionActionPlan borné immuable (primitives dans ce module)
# ══════════════════════════════════════════════════════════════════════════

_PLAN_SCOPE_3 = {
    "allowed_operation_shapes": ["UPDATE_TARGET_FROM_SOURCE"],
    "allowed_target_paths": [_TARGET_REL],
    "max_actions": 3,
    "max_retries_per_action": 0,
}


def _plan_actions(env, *, deps1=(0,), deps2=(1,)):
    return [
        {"ordinal": 0, "target_path": _TARGET_REL, "source_git_commit": env["base_sha"],
         "source_historical_path": _SOURCE_REL, "test_contract": _positive_contract(),
         "dependency_ordinals": []},
        {"ordinal": 1, "target_path": _TARGET_REL, "source_git_commit": env["base_sha"],
         "source_historical_path": _SOURCE_REL, "test_contract": _positive_contract(),
         "dependency_ordinals": list(deps1)},
        {"ordinal": 2, "target_path": _TARGET_REL, "source_git_commit": env["base_sha"],
         "source_historical_path": _SOURCE_REL, "test_contract": _positive_contract(),
         "dependency_ordinals": list(deps2)},
    ]


def test_S3D_bind_plan_valid_projection_metadata(env):
    mid = _genesis(env, scope=dict(_PLAN_SCOPE_3))["mission_id"]
    _bind(env, mid)
    r = M.bind_mission_plan(mission_id=mid, actions=_plan_actions(env),
                            mission_store_dir=env["stores"]["missions"])
    assert r["status"] == M.STATUS_PLAN_BOUND, r
    assert r["plan_id"].startswith("mpl-")
    proj = _proj(env, mid)
    assert proj["current_state"] == M.S_WORKTREE_BOUND          # PLAN_BOUND ne change pas l'état
    assert proj["active_plan_id"] == r["plan_id"]
    assert proj["active_plan_hash"] == r["plan_hash"]
    assert proj["plan_completed"] is False
    assert proj["plan_bound_revision"] == proj["revision"]
    # identité non circulaire : action_id dérive d'ordinaux + champs propres
    plan = M.load_mission_plan(mid, r["plan_id"], env["stores"]["missions"])
    assert plan["execution_order"] == [a["action_id"] for a in plan["actions"]]  # topo: 0->1->2
    g = M.load_mission_genesis(mid, env["stores"]["missions"])
    ok, why = M.verify_mission_plan(plan, genesis=g)
    assert ok, why


def test_S3D_plan_is_write_once(env):
    mid = _genesis(env, scope=dict(_PLAN_SCOPE_3))["mission_id"]
    _bind(env, mid)
    r1 = M.bind_mission_plan(mission_id=mid, actions=_plan_actions(env),
                             mission_store_dir=env["stores"]["missions"])
    assert r1["status"] == M.STATUS_PLAN_BOUND
    r2 = M.bind_mission_plan(mission_id=mid, actions=_plan_actions(env),
                             mission_store_dir=env["stores"]["missions"])
    assert r2["status"] == M.STATUS_PLAN_BIND_REJECTED and r2["reason"] == "PLAN_ALREADY_BOUND"


def test_S3D_plan_tamper_detected_by_verify(env):
    mid = _genesis(env, scope=dict(_PLAN_SCOPE_3))["mission_id"]
    _bind(env, mid)
    r = M.bind_mission_plan(mission_id=mid, actions=_plan_actions(env),
                            mission_store_dir=env["stores"]["missions"])
    ppath = next((env["stores"]["missions"] / mid / "plans").glob("mpl-*.json"))
    p = json.loads(ppath.read_text(encoding="utf-8"))
    p["actions"][1]["source_historical_path"] = "periphery/xdomain/elsewhere.txt"
    g = M.load_mission_genesis(mid, env["stores"]["missions"])
    ok, why = M.verify_mission_plan(p, genesis=g)
    assert ok is False
    assert why.startswith("ACTION_ID_NOT_DERIVED") or why == "PLAN_HASH_MISMATCH"


def test_S3D_close_plan_requires_all_snapshotted(env):
    mid = _genesis(env, scope=dict(_PLAN_SCOPE_3))["mission_id"]
    _bind(env, mid)
    r = M.bind_mission_plan(mission_id=mid, actions=_plan_actions(env),
                            mission_store_dir=env["stores"]["missions"])
    c = M.close_plan(mission_id=mid, plan_id=r["plan_id"], mission_store_dir=env["stores"]["missions"])
    assert c["status"] == M.STATUS_PLAN_CLOSE_REJECTED
    assert c["reason"].startswith("PLAN_ACTIONS_NOT_ALL_SNAPSHOTTED")


def test_S3D_plan_cycle_rejected_at_bind(env):
    mid = _genesis(env, scope=dict(_PLAN_SCOPE_3))["mission_id"]
    _bind(env, mid)
    r = M.bind_mission_plan(mission_id=mid, actions=_plan_actions(env, deps1=(2,), deps2=(1,)),
                            mission_store_dir=env["stores"]["missions"])
    assert r["status"] == M.STATUS_PLAN_BIND_REJECTED
    assert r["reason"].startswith("PLAN_MALFORMED:DEPENDENCY_CYCLE")


def test_S3D_retries_used_per_action_id_not_prepare_count(env):
    # une projection avec 3 préparations d'ACTIONS DISTINCTES -> retries_used == 0
    mid = _genesis(env, scope=dict(_PLAN_SCOPE_3))["mission_id"]
    _bind(env, mid)
    # fabrique 3 révisions PREPARE_SUCCEEDED avec des action_id distincts (fixtures)
    def _raw(evt, frm, to, ev):
        d = env["stores"]["missions"] / mid / "revisions"
        last = json.loads(sorted(d.glob("*.json"))[-1].read_text(encoding="utf-8"))
        n = last["revision"] + 1
        rec = {"mission_record_schema_version": M.REVISION_SCHEMA_VERSION, "mission_id": mid,
               "revision": n, "parent_revision_hash": last["mission_revision_record_hash"],
               "event": evt, "from_state": frm, "to_state": to, "evidence_refs": ev,
               "actor": "STACK", "created_at": "2026-08-28T00:00:00+00:00"}
        rec["mission_revision_record_hash"] = M._record_hash(rec, M._REVISION_BOUND_FIELDS)
        (d / f"{n:06d}-{rec['mission_revision_record_hash'][:12]}.json").write_text(
            json.dumps(rec, indent=2, sort_keys=True), encoding="utf-8")
    prep_ev = {"batch_execution_id": "b", "child_execution_id": "c", "execution_authority_hash": "e" * 64,
               "pre_execution_context_id": "p", "pre_execution_context_record_hash": "h" * 64,
               "test_contract_hash": "t" * 64}
    kept_ev = {"driver_status": WU._DRV.KEPT_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW,
               "batch_execution_id": "b", "child_execution_id": "c", "execution_authority_hash": "e" * 64}
    _raw(M.E_ACTION_PREPARE_SUCCEEDED, M.S_WORKTREE_BOUND, M.S_ACTION_PREPARED, {**prep_ev, "action_id": "act-1"})
    _raw(M.E_ACTION_EXECUTE_KEPT, M.S_ACTION_PREPARED, M.S_ACTION_EXECUTED_KEPT, {**kept_ev, "action_id": "act-1"})
    _raw(M.E_ACTION_LOCAL_SNAPSHOT_COMMITTED, M.S_ACTION_EXECUTED_KEPT, M.S_WORKTREE_BOUND,
         {"action_id": "act-1", "previous_mission_tip_sha": env["base_sha"], "new_mission_tip_sha": "a" * 40,
          "new_commit_sha": "a" * 40, "commit_parent_sha": env["base_sha"], "committed_paths": [_TARGET_REL],
          "snapshot_receipt_id": "lsr-1", "local_snapshot_receipt_record_hash": "x" * 64})
    _raw(M.E_ACTION_PREPARE_SUCCEEDED, M.S_WORKTREE_BOUND, M.S_ACTION_PREPARED, {**prep_ev, "action_id": "act-2"})
    proj = _proj(env, mid)
    assert proj["status"] == M.STATUS_PROJECTION_OK
    assert proj["retries_used"] == 0                 # 2 action_id distincts -> 0 retry
    assert set(proj["kept_action_ids"]) == {"act-1"}
    assert set(proj["snapshotted_action_ids"]) == {"act-1"}


def test_S3D_historical_mission_without_plan_projects_as_before(env):
    mid = _genesis(env, scope=dict(_PLAN_SCOPE_3))["mission_id"]
    _bind(env, mid)
    proj = _proj(env, mid)
    assert proj["active_plan_id"] is None
    assert proj["active_plan_hash"] is None
    assert proj["plan_completed"] is False
    assert proj["mission_tip_sha"] == proj["canonical_base_sha"]
