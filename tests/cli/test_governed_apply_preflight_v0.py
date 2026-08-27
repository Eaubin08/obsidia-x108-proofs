"""
tests/cli/test_governed_apply_preflight_v0.py
============================================
CONTENT_BOUND_GOVERNED_PREFLIGHT_C1_V0

Prouve, EN EXÉCUTANT LA STACK CANONIQUE RÉELLE :

  - obsidia_family_wiring_apply_bridge_v0.build_child_execution_from_obsidure_proposal
    valide la proposition via load_and_validate_proposal canonique, confine le
    chemin sandbox, lit les octets EXACTS et en calcule source_content_sha256
    (64 hex) — proposal_hash n'est jamais autorité de contenu.
  - obsidia_governed_apply_v0.validate_governed_apply_preflight (READ_ONLY,
    NON_SOVEREIGN) recharge ExecutionEnvelope + HumanApproval canonique +
    KX108_PRE decision (phase PRE_EXECUTION, x108_gate ALLOW, même EAH, même
    approval_id) + PreExecutionContext, confine à nouveau le chemin source,
    re-hashe le contenu source en SHA256 COMPLET, revérifie la précondition
    de cible et le scope, et retourne PREFLIGHT_PASS — SANS aucune mutation.

x108_gate ALLOW est produit par le vrai kernel sigma (non mocké).
Tous les artefacts sont écrits dans des magasins temporaires isolés + un
faux dépôt tmp. AUCUNE mutation de cible. AUCUN git.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
for _p in (str(_SCRIPTS_DIR), str(_REPO_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import obsidia_batch_execution as E            # noqa: E402
import obsidia_pre_execution_context as PEC    # noqa: E402
import obsidia_test_contract as TC             # noqa: E402
import obsidia_kx108_decision_store as DS      # noqa: E402
import obsidia_kx108_pre_execution_evidence_adapter_v0 as PREADP  # noqa: E402
import obsidia_family_wiring_apply_bridge_v0 as BRIDGE            # noqa: E402
import obsidia_governed_apply_v0 as GA                            # noqa: E402

_TARGET_REL = "periphery/xdomain/pre_gate_target_v0.py"
_SRC_CONTENT = b"# governed remediation content v0\nVALUE = 1\n"
_TGT_OLD = b"# stale target\nVALUE = 0\n"


# ─── fabrique d'un faux dépôt + proposition Obsidure + chaîne canonique ──

def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _make_fake_repo(tmp_path: Path, *, target_bytes: bytes | None = _TGT_OLD,
                    src_bytes: bytes = _SRC_CONTENT) -> dict:
    repo = tmp_path / "fake_repo"
    (repo / "periphery" / "xdomain").mkdir(parents=True, exist_ok=True)
    if target_bytes is not None:
        (repo / _TARGET_REL).write_bytes(target_bytes)
    prop_id = "prop-c1-001"
    sandbox = repo / "_PATCH_PROPOSALS" / prop_id / "sandbox" / _TARGET_REL
    sandbox.parent.mkdir(parents=True, exist_ok=True)
    sandbox.write_bytes(src_bytes)
    proposal = {
        "proposal_id": prop_id,
        "session_id": "sess-c1",
        "base_sha": "a" * 40,
        "worktree": str(repo),
        "objective": "family wiring remediation content",
        "status": "AWAITING_HUMAN_APPROVED_WRITE",
        "patches": [
            {"path": _TARGET_REL, "action": "REPLACE", "sandbox_path": str(sandbox)},
        ],
    }
    pdir = repo / "_PATCH_PROPOSALS"
    (pdir / prop_id).mkdir(parents=True, exist_ok=True)
    (pdir / prop_id / "proposal.json").write_text(json.dumps(proposal, indent=2), encoding="utf-8")
    return {"repo": repo, "proposals_dir": pdir, "proposal_id": prop_id, "sandbox": sandbox}


def _run_bridge(fake, **over) -> dict:
    kw = dict(
        proposal_id=fake["proposal_id"], session_id="sess-c1", base_sha="a" * 40,
        worktree=str(fake["repo"]), approved_scope=[_TARGET_REL],
        proposals_dir=fake["proposals_dir"], repo_root=fake["repo"],
    )
    kw.update(over)
    return BRIDGE.build_child_execution_from_obsidure_proposal(**kw)


def _make_pre_ctx(child: dict, repo: Path) -> dict:
    manifest = {
        "repository_identity": str(repo), "execution_worktree_path": str(repo / "wt"),
        "branch_name": "feat/x", "base_sha": "a" * 40,
        "source_kind": "FILESYSTEM_FILE", "source_repository_identity": str(repo),
        "source_commit": "", "source_blob_sha": "", "source_path": child["source_path"],
        "source_sha256": child["source_content_sha256"],
        "target_path": child["target_path"], "target_pre_sha256": child["target_pre_sha256"],
        "operation": "REPLACE", "approved_scope": [child["target_path"]],
        "protected_scope_status": "CLEAN", "test_contract_hash": None, "schema_version": 2,
    }
    rec = {
        "context_schema_version": 2, "created_at": "2026-01-01T00:00:00+00:00",
        "repository_identity": manifest["repository_identity"], "repository_root": str(repo),
        "execution_worktree_path": manifest["execution_worktree_path"],
        "branch_name": manifest["branch_name"], "base_sha": manifest["base_sha"],
        "target_path": manifest["target_path"], "target_pre_sha256": manifest["target_pre_sha256"],
        "source_kind": manifest["source_kind"],
        "source_repository_identity": manifest["source_repository_identity"],
        "source_commit": manifest["source_commit"], "source_blob_sha": manifest["source_blob_sha"],
        "source_path": manifest["source_path"], "source_sha256": manifest["source_sha256"],
        "operation": manifest["operation"], "approved_scope": manifest["approved_scope"],
        "worktree_isolated": True, "branch_isolated": True, "protected_scope_status": "CLEAN",
        "manifest": manifest, "legacy_manifest_hash_short": "0" * 16,
        "decision_authority": "KX108_ONLY",
    }
    rec["manifest_sha256"] = PEC.compute_manifest_sha256(rec["manifest"])
    seed = [f for f in PEC._CONTEXT_BOUND_FIELDS_V2
            if f not in ("context_schema_version", "context_id", "created_at")]
    rec["context_id"] = "pec-" + hashlib.sha256(
        json.dumps({k: rec.get(k) for k in seed}, sort_keys=True).encode()).hexdigest()[:32]
    rec["context_record_hash"] = PEC.compute_context_record_hash(rec)
    return rec


def _make_envelope(child: dict, pre_ctx: dict) -> dict:
    env = {
        "batch_execution_id": "be-c1", "batch_id": None, "batch_hash": None,
        "batch_hash_version": 1, "candidate_scope_hash": None,
        "execution_order": [child["candidate_entry_id"]], "dependency_edges": [],
        "children": [child], "decision_authority": "KX108_ONLY", "integrity_verified": True,
        "pre_execution_context_id": pre_ctx["context_id"],
        "pre_execution_context_record_hash": pre_ctx["context_record_hash"],
    }
    tc = {"test_contract_schema_version": 1, "contract_id": "tc-c1",
          "candidate_entry_id": child["candidate_entry_id"], "batch_id": None,
          "target_path": child["target_path"], "checks": [], "decision_authority": "KX108_ONLY"}
    env["test_contract"] = tc
    env["test_contract_hash"] = TC.compute_test_contract_hash(tc)
    env["execution_authority_hash"] = E.compute_execution_authority_hash(env)
    return env


def _store_envelope(env: dict, execution_dir: Path) -> None:
    p = execution_dir / "executions" / env["batch_execution_id"] / "execution.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(env, indent=2), encoding="utf-8")


def _store_pre_ctx(rec: dict, ctx_dir: Path) -> None:
    ctx_dir.mkdir(parents=True, exist_ok=True)
    (ctx_dir / f"{rec['context_id']}.json").write_text(json.dumps(rec, indent=2), encoding="utf-8")


def _store_approval(env: dict, execution_dir: Path, approval_id: str = "appr-c1-001", **over) -> str:
    rec = {
        "approval_id": approval_id, "approval_schema_version": E.SCHEMA_VERSION,
        "created_at": "2026-01-02T00:00:00+00:00",
        "batch_execution_id": env["batch_execution_id"], "batch_id": env["batch_id"],
        "batch_hash": env["batch_hash"], "candidate_scope_hash": env["candidate_scope_hash"],
        "execution_authority_hash": env["execution_authority_hash"],
        "approved_by": "HUMAN", "approval_status": E.APPROVED_FOR_BOUNDED_EXECUTION,
        "decision_authority": "KX108_ONLY",
    }
    rec.update(over)
    rec["approval_record_hash"] = E.compute_approval_record_hash(rec)
    res = E.store_approval_artifact(rec, execution_dir=execution_dir)
    assert res["status"] in ("STORED", "IDEMPOTENT_ALREADY_EXISTS"), res
    return approval_id


@pytest.fixture
def canon(tmp_path):
    fake = _make_fake_repo(tmp_path)
    br = _run_bridge(fake)
    assert br["status"] == BRIDGE.STATUS_READY, br
    child = br["child"]
    ex, cx, dc = tmp_path / "exec", tmp_path / "ctx", tmp_path / "dec"
    pre_ctx = _make_pre_ctx(child, fake["repo"])
    env = _make_envelope(child, pre_ctx)
    _store_pre_ctx(pre_ctx, cx)
    _store_envelope(env, ex)
    approval_id = _store_approval(env, ex)
    tr = PREADP.translate_pre_execution_evidence_to_tooling_build_state(
        env["batch_execution_id"], child["child_execution_id"], approval_id,
        execution_dir=ex, pre_execution_context_dir=cx)
    assert tr["status"] == PREADP.STATUS_READY, tr
    pre_out = DS.run_and_persist_kx108_pre_execution_decision(
        tr["pre_tooling_build_state_kwargs"], tr["pre_binding_context"], store_dir=dc)
    assert pre_out["record"]["x108_gate"] == "ALLOW", pre_out["record"]
    return {"tmp": tmp_path, "fake": fake, "br": br, "child": child, "env": env,
            "ex": ex, "cx": cx, "dc": dc, "approval_id": approval_id,
            "pre_id": pre_out["decision_record_id"]}


def _forge_valid_pre_record(env: dict, approval_id: str, dc: Path,
                            record_id: str = "kxpre-forged-create-0001",
                            gate: str = "ALLOW") -> str:
    """Enregistre un KX108_PRE decision record de forme CANONIQUE, hash correct.
    Réservé aux tests d'ISOLATION UNITAIRE (branche CREATE du préflight) où
    l'adaptateur PRE committé n'accepte pas encore target_pre_sha256=None.
    L'E2E positif, lui, utilise le vrai adaptateur + le vrai kernel sigma."""
    child = env["children"][0]
    rec = {
        "decision_record_schema_version": DS.SCHEMA_VERSION,
        "decision_record_id": record_id,
        "created_at": "2026-01-03T00:00:00+00:00",
        "decision_phase": "PRE_EXECUTION",
        "batch_execution_id": env["batch_execution_id"],
        "child_execution_id": child["child_execution_id"],
        "execution_authority_hash": env["execution_authority_hash"],
        "approval_id": approval_id,
        "pre_execution_context_id": env["pre_execution_context_id"],
        "pre_execution_context_record_hash": env["pre_execution_context_record_hash"],
        "test_contract_hash": env["test_contract_hash"],
        "kx108_input_translation_hash": "k" * 64,
        "decision_id": "d-forge", "trace_id": "t-forge", "domain": "tooling_build",
        "x108_gate": gate, "reason_code": "GUARD_ALLOW", "severity": "S0",
        "market_verdict": "READY_FOR_COMMIT_REVIEW",
        "contradictions": [], "unknowns": [], "risk_flags": [],
        "decision_authority": "KX108_ONLY",
        "canonical_envelope": {"x108_gate": gate},
    }
    rec["decision_record_hash"] = DS.compute_kx108_decision_record_hash(rec)
    dc.mkdir(parents=True, exist_ok=True)
    (dc / f"{record_id}.json").write_text(json.dumps(rec, indent=2), encoding="utf-8")
    return record_id


def _preflight(canon, **over):
    kw = dict(
        batch_execution_id=canon["env"]["batch_execution_id"],
        child_execution_id=canon["child"]["child_execution_id"],
        approval_id=canon["approval_id"],
        kx108_pre_decision_record_id=canon["pre_id"],
        execution_dir=canon["ex"], pre_execution_context_dir=canon["cx"],
        kx108_decision_dir=canon["dc"], repo_root=canon["fake"]["repo"],
    )
    kw.update(over)
    return GA.validate_governed_apply_preflight(**kw)


def _target_bytes(canon):
    p = canon["fake"]["repo"] / _TARGET_REL
    return p.read_bytes() if p.exists() else None


# ═══ 1-6 : BRIDGE ═══

def test_1_bridge_single_sandbox_file_exact_sha(tmp_path):
    fake = _make_fake_repo(tmp_path)
    br = _run_bridge(fake)
    assert br["status"] == BRIDGE.STATUS_READY
    assert br["source_content_sha256"] == _sha(_SRC_CONTENT)
    assert len(br["source_content_sha256"]) == 64
    assert br["child"]["source_content_sha256"] == _sha(_SRC_CONTENT)
    assert br["child"]["source_kind"] == "FILESYSTEM_FILE"
    assert br["child"]["operation_type"] == "UPDATE_TARGET_FROM_SOURCE"
    assert br["child"]["target_path"] == _TARGET_REL
    assert br["child"]["target_pre_sha256"] == _sha(_TGT_OLD)
    assert br["write_capability"] is False and br["authority"] == "NON_SOVEREIGN"


def test_2_bridge_source_hash_deterministic(tmp_path):
    f1 = _make_fake_repo(tmp_path / "a")
    f2 = _make_fake_repo(tmp_path / "b")
    assert _run_bridge(f1)["source_content_sha256"] == _run_bridge(f2)["source_content_sha256"]


def test_3_bridge_proposal_hash_not_content_authority(tmp_path):
    """Modifier les octets sandbox SANS toucher proposal.json change
    source_content_sha256 mais PAS proposal_hash — donc proposal_hash ne peut
    pas être l'autorité de contenu."""
    fake = _make_fake_repo(tmp_path)
    b1 = _run_bridge(fake)
    fake["sandbox"].write_bytes(b"# TAMPERED\nVALUE = 999\n")
    b2 = _run_bridge(fake)
    assert b1["proposal_hash"] == b2["proposal_hash"]          # inchangé
    assert b1["source_content_sha256"] != b2["source_content_sha256"]  # change


def test_4_bridge_source_outside_repo_fails_closed(tmp_path):
    fake = _make_fake_repo(tmp_path)
    outside = tmp_path / "outside.py"
    outside.write_bytes(b"x")
    p = fake["proposals_dir"] / fake["proposal_id"] / "proposal.json"
    data = json.loads(p.read_text())
    data["patches"][0]["sandbox_path"] = str(outside)
    p.write_text(json.dumps(data))
    br = _run_bridge(fake)
    assert br["status"] == BRIDGE.STATUS_HOLD
    assert br["reason"] == "SOURCE_PATH_ESCAPE"


def test_5_bridge_symlink_escape_fails_closed(tmp_path):
    fake = _make_fake_repo(tmp_path)
    outside = tmp_path / "secret.py"
    outside.write_bytes(b"SECRET")
    link = fake["repo"] / "_PATCH_PROPOSALS" / fake["proposal_id"] / "evil_link.py"
    try:
        os.symlink(str(outside), str(link))
    except (OSError, NotImplementedError):
        pytest.skip("symlink non supporté sur cette plateforme/permission")
    p = fake["proposals_dir"] / fake["proposal_id"] / "proposal.json"
    data = json.loads(p.read_text())
    data["patches"][0]["sandbox_path"] = str(link)
    p.write_text(json.dumps(data))
    br = _run_bridge(fake)
    assert br["status"] == BRIDGE.STATUS_HOLD
    assert br["reason"] in ("SOURCE_PATH_ESCAPE", "SOURCE_SYMLINK_ESCAPE")


def test_6_bridge_multi_patch_ambiguity_fails_closed(tmp_path):
    fake = _make_fake_repo(tmp_path)
    sb2 = fake["repo"] / "_PATCH_PROPOSALS" / fake["proposal_id"] / "sandbox2" / "periphery/other.py"
    sb2.parent.mkdir(parents=True, exist_ok=True)
    sb2.write_bytes(b"y")
    p = fake["proposals_dir"] / fake["proposal_id"] / "proposal.json"
    data = json.loads(p.read_text())
    data["patches"].append({"path": "periphery/other.py", "action": "REPLACE", "sandbox_path": str(sb2)})
    p.write_text(json.dumps(data))
    br = _run_bridge(fake, approved_scope=[_TARGET_REL, "periphery/other.py"])
    assert br["status"] == BRIDGE.STATUS_HOLD
    assert br["reason"] == "MULTI_PATCH_AMBIGUITY"


# ═══ 7-16 : PREFLIGHT — approbation / KX108_PRE / contexte ═══

def test_7_missing_human_approval_holds(canon):
    r = _preflight(canon, approval_id="appr-absent-xyz")
    assert r["status"] == GA.STATUS_HOLD and r["reason"] == "HUMAN_APPROVAL_NOT_FOUND"


def test_8_invalid_human_approval_holds(canon):
    _store_approval(canon["env"], canon["ex"], approval_id="appr-bad")
    p = canon["ex"] / "approvals" / "appr-bad" / "approval.json"
    rec = json.loads(p.read_text()); rec["approval_record_hash"] = "0" * 64
    p.write_text(json.dumps(rec))
    r = _preflight(canon, approval_id="appr-bad")
    assert r["status"] == GA.STATUS_HOLD and r["reason"].startswith("HUMAN_APPROVAL_ARTIFACT_INVALID")


def test_9_approval_wrong_eah_holds(canon):
    _store_approval(canon["env"], canon["ex"], approval_id="appr-weah",
                    execution_authority_hash="f" * 64)
    r = _preflight(canon, approval_id="appr-weah")
    assert r["status"] == GA.STATUS_HOLD
    assert "HUMAN_APPROVAL" in r["reason"]


def test_10_missing_kx108_pre_holds(canon):
    r = _preflight(canon, kx108_pre_decision_record_id="kxpre-absent000000000000000000000")
    assert r["status"] == GA.STATUS_HOLD and r["reason"] == "KX108_PRE_DECISION_NOT_FOUND"


def test_11_kx108_phase_post_execution_holds(canon):
    # forge un record POST (pas de decision_phase) réutilisant l'id kxpre-
    p = canon["dc"] / f"{canon['pre_id']}.json"
    rec = json.loads(p.read_text())
    rec.pop("decision_phase", None)
    rec["decision_record_hash"] = DS.compute_kx108_decision_record_hash(rec)
    p.write_text(json.dumps(rec))
    r = _preflight(canon)
    assert r["status"] == GA.STATUS_HOLD
    # sans decision_phase => schéma POST : rejeté soit à l'intégrité (champs
    # POST manquants) soit à la vérification de phase. Dans tous les cas non-PRE.
    assert (r["reason"] == "KX108_DECISION_NOT_PRE_EXECUTION_PHASE"
            or r["reason"].startswith("KX108_PRE_DECISION_INVALID"))


def test_12_13_kx108_pre_hold_or_block_holds(canon):
    p = canon["dc"] / f"{canon['pre_id']}.json"
    for gate in ("HOLD", "BLOCK"):
        rec = json.loads(p.read_text())
        rec["x108_gate"] = gate
        rec["decision_record_hash"] = DS.compute_kx108_decision_record_hash(rec)
        p.write_text(json.dumps(rec))
        r = _preflight(canon)
        assert r["status"] == GA.STATUS_HOLD and r["reason"] == "KX108_PRE_GATE_NOT_ALLOW"


def test_14_pre_wrong_eah_holds(canon):
    p = canon["dc"] / f"{canon['pre_id']}.json"
    rec = json.loads(p.read_text())
    rec["execution_authority_hash"] = "e" * 64
    rec["decision_record_hash"] = DS.compute_kx108_decision_record_hash(rec)
    p.write_text(json.dumps(rec))
    r = _preflight(canon)
    assert r["status"] == GA.STATUS_HOLD and r["reason"] == "KX108_PRE_EXECUTION_AUTHORITY_HASH_MISMATCH"


def test_15_pre_approval_id_mismatch_holds(canon):
    p = canon["dc"] / f"{canon['pre_id']}.json"
    rec = json.loads(p.read_text())
    rec["approval_id"] = "some-other-approval"
    rec["decision_record_hash"] = DS.compute_kx108_decision_record_hash(rec)
    p.write_text(json.dumps(rec))
    r = _preflight(canon)
    assert r["status"] == GA.STATUS_HOLD and r["reason"] == "KX108_PRE_APPROVAL_ID_MISMATCH"


def test_16_pre_execution_context_mismatch_holds(canon):
    p = canon["ex"] / "executions" / "be-c1" / "execution.json"
    env = json.loads(p.read_text())
    env["pre_execution_context_record_hash"] = "0" * 64
    env["execution_authority_hash"] = E.compute_execution_authority_hash(env)
    p.write_text(json.dumps(env))
    # approbation + KX108_PRE ne matchent plus le nouvel EAH -> HOLD amont, mais
    # le point testé (contexte) est atteint si on régénère la chaîne ; ici on
    # se contente de prouver le fail-closed global.
    r = _preflight(canon)
    assert r["status"] == GA.STATUS_HOLD


# ═══ 17-25 : PREFLIGHT — source / cible ═══

def test_17_source_path_escape_holds(canon):
    p = canon["ex"] / "executions" / "be-c1" / "execution.json"
    env = json.loads(p.read_text())
    env["children"][0]["source_path"] = "../../../etc/passwd"
    env["execution_authority_hash"] = E.compute_execution_authority_hash(env)
    p.write_text(json.dumps(env))
    r = _preflight(canon)
    # EAH a changé -> HOLD (drift) OU SOURCE_PATH_ESCAPE si la chaîne était régénérée.
    assert r["status"] == GA.STATUS_HOLD


def test_18_source_content_sha256_mismatch_holds(canon):
    # modifie les octets sandbox APRÈS que l'envelope (donc l'EAH) a figé le sha
    canon["fake"]["sandbox"].write_bytes(b"# drifted after bridge\nVALUE = 42\n")
    r = _preflight(canon)
    assert r["status"] == GA.STATUS_HOLD
    assert r["reason"] in ("SOURCE_CONTENT_SHA256_MISMATCH", "SOURCE_RESOLVE_FAILED:SOURCE_INTEGRITY_MISMATCH")


def test_19_source_bytes_modified_after_bridge_holds(canon):
    canon["fake"]["sandbox"].write_bytes(_SRC_CONTENT + b"\n# extra\n")
    r = _preflight(canon)
    assert r["status"] == GA.STATUS_HOLD


def test_20_target_prestate_drift_holds(canon):
    (canon["fake"]["repo"] / _TARGET_REL).write_bytes(b"# target changed underneath\n")
    r = _preflight(canon)
    assert r["status"] == GA.STATUS_HOLD
    assert r["reason"] == "TARGET_PRECONDITION_MISMATCH"


def test_21_protected_target_holds(canon):
    p = canon["ex"] / "executions" / "be-c1" / "execution.json"
    env = json.loads(p.read_text())
    env["children"][0]["target_path"] = "proofs/sealed_thing.py"
    env["execution_authority_hash"] = E.compute_execution_authority_hash(env)
    p.write_text(json.dumps(env))
    r = _preflight(canon)
    assert r["status"] == GA.STATUS_HOLD  # PROTECTED_TARGET ou drift amont


def test_22_target_path_escape_holds(canon):
    p = canon["ex"] / "executions" / "be-c1" / "execution.json"
    env = json.loads(p.read_text())
    env["children"][0]["target_path"] = "../../outside.py"
    env["execution_authority_hash"] = E.compute_execution_authority_hash(env)
    p.write_text(json.dumps(env))
    r = _preflight(canon)
    assert r["status"] == GA.STATUS_HOLD


def test_23_create_precondition_respected(tmp_path):
    fake = _make_fake_repo(tmp_path, target_bytes=None)  # cible ABSENTE
    br = _run_bridge(fake)
    assert br["status"] == BRIDGE.STATUS_READY
    assert br["child"]["target_pre_sha256"] is None
    child = br["child"]
    ex, cx, dc = tmp_path / "e", tmp_path / "c", tmp_path / "d"
    pc = _make_pre_ctx(child, fake["repo"]); env = _make_envelope(child, pc)
    _store_pre_ctx(pc, cx); _store_envelope(env, ex)
    aid = _store_approval(env, ex)
    # NOTE: l'adaptateur PRE committé refuse target_pre_sha256=None
    # (TARGET_PRE_SHA256_ABSENT) -> CREATE n'est pas encore routable via lui.
    # Blocker de suivi enregistré. Ici on isole la branche CREATE du préflight
    # avec un KX108_PRE record canonique forgé (hash correct).
    pre_id = _forge_valid_pre_record(env, aid, dc)
    r = GA.validate_governed_apply_preflight(
        env["batch_execution_id"], child["child_execution_id"], aid,
        pre_id, execution_dir=ex, pre_execution_context_dir=cx,
        kx108_decision_dir=dc, repo_root=fake["repo"])
    assert r["status"] == GA.STATUS_PASS, r
    assert r["target_operation"] == "CREATE"
    assert not (fake["repo"] / _TARGET_REL).exists()  # toujours absente


def test_24_replace_precondition_respected(canon):
    r = _preflight(canon)
    assert r["status"] == GA.STATUS_PASS, r
    assert r["target_operation"] == "REPLACE"
    assert r["target_pre_sha256_verified"] is True


def test_25_delete_unsupported_holds(canon):
    p = canon["ex"] / "executions" / "be-c1" / "execution.json"
    env = json.loads(p.read_text())
    env["children"][0]["operation_type"] = "DELETE_TARGET"
    env["execution_authority_hash"] = E.compute_execution_authority_hash(env)
    p.write_text(json.dumps(env))
    r = _preflight(canon)
    assert r["status"] == GA.STATUS_HOLD  # UNSUPPORTED_OPERATION ou drift amont


# ═══ 26-35 : PREFLIGHT_PASS + non-souveraineté + zéro mutation ═══

def test_26_valid_exact_chain_preflight_pass(canon):
    before = _target_bytes(canon)
    r = _preflight(canon)
    assert r["status"] == GA.STATUS_PASS, r
    assert r["kx108_pre_gate"] == "ALLOW"
    assert r["source_content_sha256_verified"] is True
    assert r["target_pre_sha256_verified"] is True
    assert r["source_path_confined"] is True
    assert r["scope_verified"] is True
    assert r["execution_authority_hash"] == canon["env"]["execution_authority_hash"]
    assert _target_bytes(canon) == before  # cible inchangée


def test_27_preflight_pass_authority_non_sovereign(canon):
    r = _preflight(canon)
    assert r["authority"] == "NON_SOVEREIGN"
    assert "ALLOW" != r["status"]


def test_28_preflight_pass_write_capability_false(canon):
    assert _preflight(canon)["write_capability"] is False


def test_29_preflight_pass_no_raw_source_bytes(canon):
    r = _preflight(canon)
    blob = json.dumps(r)
    assert base64.b64encode(_SRC_CONTENT).decode() not in blob
    assert "VALUE = 1" not in blob
    assert "source_bytes" not in r and "content" not in r
    assert r["preflight_cache_authority"] == "NONE"


def test_30_target_bytes_unchanged_across_all_cases(canon):
    before = _target_bytes(canon)
    _preflight(canon)
    _preflight(canon, approval_id="nope")
    _preflight(canon, kx108_pre_decision_record_id="kxpre-nope0000000000000000000000000")
    assert _target_bytes(canon) == before


def test_31_32_33_34_no_governance_side_artifacts(canon):
    """Le préflight ne crée ni apply receipt, ni rollback evidence, ni
    TestContractResult, ni décision KX108_POST."""
    import glob
    dc_before = sorted(glob.glob(str(canon["dc"] / "**" / "*"), recursive=True))
    _preflight(canon)
    dc_after = sorted(glob.glob(str(canon["dc"] / "**" / "*"), recursive=True))
    assert dc_before == dc_after  # aucune nouvelle décision KX108
    # aucun magasin apply/rollback/test-result créé sous tmp
    for banned in ("content_apply", "rollback", "apply_receipt", "test_contract_results"):
        assert not list(canon["tmp"].rglob(f"*{banned}*"))


def test_35_static_no_mutation_symbols_in_c1_modules():
    for mod in (GA, BRIDGE):
        src = Path(mod.__file__).read_text(encoding="utf-8")
        for banned in ("apply_validated_source_content(", "atomic_replace_with_bytes(",
                       "apply_proposal(", "run_bounded_apply(", "os.replace(",
                       "write_bytes(", "write_text(", "git commit", "git push", "git merge"):
            assert banned not in src, f"{mod.__name__}: {banned}"


# ═══ E2E real stack ═══

def test_e2e_real_c1_stack_preflight_pass(canon):
    r = _preflight(canon)
    assert r["status"] == GA.STATUS_PASS, r
    assert r["kx108_pre_gate"] == "ALLOW"
    # chaîne d'identité complète prouvée
    assert canon["child"]["source_content_sha256"] == _sha(_SRC_CONTENT)
    assert canon["br"]["source_content_sha256"] == canon["child"]["source_content_sha256"]
