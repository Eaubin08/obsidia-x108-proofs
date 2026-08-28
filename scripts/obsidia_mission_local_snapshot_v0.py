"""
obsidia_mission_local_snapshot_v0.py
====================================
STAGE_3A — primitive de GEL Git LOCAL bornée. Elle transforme le résultat
d'UNE action gouvernée KEEP déjà prouvée
(HumanApproval + EAH exact -> KX108_PRE ALLOW -> apply gouverné C2 ->
 TestContract ALL_REQUIRED_PASS -> KX108_POST ALLOW ->
 D1 KEEP_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW)
en UN commit local, sur la branche de mission isolée, du SEUL chemin
cible gouverné, puis émet un LocalSnapshotReceipt immuable.

Ce module :

  * N'EST PAS une autorité. LOCAL_SNAPSHOT_IS_EXECUTION_AUTHORITY = FALSE.
    Il ne crée AUCUNE HumanApproval, n'invoque AUCUN KX108, n'écrit AUCUNE
    cible de remédiation, n'appelle NI C2 NI D2, ne génère NI source NI
    plan. Il CONSOMME les artefacts canoniques existants en LECTURE SEULE
    et les revérifie indépendamment.
  * N'EST PAS l'acceptation humaine finale.
    LOCAL_SNAPSHOT_IS_FINAL_HUMAN_ACCEPTANCE = FALSE. La porte Git humaine
    finale (push / PR / main / squash) reste requise et hors de ce module.
  * NE FAIT AUCUNE opération Git distante. Ses SEULES mutations Git sont :
        git add -- <chemin cible exact>
        git commit  (un seul, jamais --amend/--all/-A/./wildcard)
        git restore --staged -- <chemin cible exact>   (dé-stage sûr d'échec)
    Aucun reset --hard, aucun clean, aucun checkout -f, aucun branch -d/-D,
    aucun worktree remove, aucun push/fetch/pull/merge/rebase/cherry-pick/
    stash, aucun --force.
  * N'ÉCRIT QUE son magasin immuable de reçus (bounded_mission_snapshots/)
    via l'unique helper `_atomic_publish_json` (primitive os.link).
  * N'APPEND AUCUNE révision de mission (Stage 3B). MISSION_REVISION_WRITES = 0.
  * NE MODIFIE NI PEC, NI Checkpoint 1, NI Checkpoint 2, NI le driver,
    NI KX108, NI l'évidence scellée, NI TestContract.

V0 : rail actuellement prouvé uniquement — enfant unique, cible existante
unique, UPDATE_TARGET_FROM_SOURCE, un résultat KEEP, un commit, un chemin.

Liaison de métadonnées de commit (modèle B, sans dépendance circulaire) :
le message de commit porte un `snapshot_correlation_id` STABLE calculé
AVANT le commit à partir d'entrées qui ne dépendent pas du SHA de commit.
Le reçu lie ensuite correlation_id <-> commit_sha <-> record_hash.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

# Réutilisation LECTURE SEULE des vérificateurs canoniques (jamais leurs writers).
import obsidia_batch_execution as _BE            # load_approval_artifact / verify_approval_artifact / _load_execution / compute_execution_authority_hash / _validate_approval
import obsidia_kx108_decision_store as _DS       # load_kx108_decision_record / verify_kx108_decision_record / compute_kx108_decision_record_hash
import obsidia_test_contract as _TC              # load_test_contract_result / verify_test_contract_result_artifact / AGGREGATE_ALL_REQUIRED_PASS
import obsidia_sealed_evidence_v0 as _SEV        # load/verify sealed apply receipt + sealed rollback evidence

SNAPSHOT_DECISION_AUTHORITY = "NON_SOVEREIGN"
EXPECTED_GOVERNED_DECISION_AUTHORITY = "KX108_ONLY"   # valeur ATTENDUE dans les artefacts lus — jamais écrite
SUPPORTED_OPERATION = "UPDATE_TARGET_FROM_SOURCE"
LOCAL_SNAPSHOT_V0_MAX_TARGETS = 1

LSR_SCHEMA_VERSION = 1
_BOUNDED_MISSION_SNAPSHOT_DIR = Path(os.environ.get("LOCALAPPDATA", "")) / "Obsidia" / "bounded_mission_snapshots"

_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,128}$")

# ── Statuts publics ──
SNAPSHOT_COMMITTED = "SNAPSHOT_COMMITTED"
SNAPSHOT_INELIGIBLE = "SNAPSHOT_INELIGIBLE"
SNAPSHOT_IDEMPOTENT_EXISTING_IDENTICAL = "SNAPSHOT_IDEMPOTENT_EXISTING_IDENTICAL"
SNAPSHOT_RECEIPT_EXISTS_BUT_REPO_DIVERGED = "SNAPSHOT_RECEIPT_EXISTS_BUT_REPO_DIVERGED"
SNAPSHOT_STAGE_FAILED = "SNAPSHOT_STAGE_FAILED"
SNAPSHOT_STAGED_BYTES_MISMATCH = "SNAPSHOT_STAGED_BYTES_MISMATCH"
SNAPSHOT_HEAD_MOVED = "SNAPSHOT_HEAD_MOVED"
SNAPSHOT_PRE_COMMIT_DRIFT = "SNAPSHOT_PRE_COMMIT_DRIFT"
SNAPSHOT_COMMIT_COMMAND_FAILED = "SNAPSHOT_COMMIT_COMMAND_FAILED"
SNAPSHOT_POST_COMMIT_VERIFY_FAILED = "SNAPSHOT_POST_COMMIT_VERIFY_FAILED"
SNAPSHOT_RECEIPT_IMMUTABILITY_VIOLATION = "SNAPSHOT_RECEIPT_IMMUTABILITY_VIOLATION"
SNAPSHOT_HOLD = "SNAPSHOT_HOLD"

_KEEP_STATUS = "GOVERNED_REMEDIATION_KEPT_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW"


# ══════════════════════════════════════════════════════════════════════════
#  Primitives locales (copies minimales — cf. PEC / KX108 store / Checkpoint 2)
# ══════════════════════════════════════════════════════════════════════════

def _sha256_hex_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _sha256_hex_text(t: str) -> str:
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def _canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _record_hash(record: dict, bound_fields: "tuple[str, ...]") -> str:
    return _sha256_hex_text(_canon({k: record.get(k) for k in bound_fields}))


def _is_40_hex(v) -> bool:
    return isinstance(v, str) and len(v) == 40 and all(c in "0123456789abcdef" for c in v.lower())


def _is_64_hex(v) -> bool:
    return isinstance(v, str) and len(v) == 64 and all(c in "0123456789abcdef" for c in v.lower())


def _safe_id_path(base: Path, ident: str) -> Path:
    if not (isinstance(ident, str) and _ID_RE.match(ident)):
        raise ValueError("INVALID_ID")
    p = base / f"{ident}.json"
    try:
        p.relative_to(base)
    except ValueError:
        raise ValueError("INVALID_ID")
    return p


def _atomic_publish_json(path: Path, record: dict) -> str:
    """Publication ATOMIQUE append-only via os.link (même primitive que
    obsidia_pre_execution_context). STORED / IDEMPOTENT_EXISTING_IDENTICAL
    / IMMUTABILITY_VIOLATION. UNIQUE point d'écriture du module."""
    payload = json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.parent / f".{path.name}.{os.getpid()}.{_sha256_hex_text(payload + str(id(record)))[:16]}.tmp"
    tmp.write_text(payload, encoding="utf-8")
    try:
        os.link(tmp, path)
        return "STORED"
    except FileExistsError:
        existing = path.read_text(encoding="utf-8")
        return "IDEMPOTENT_EXISTING_IDENTICAL" if existing == payload else "IMMUTABILITY_VIOLATION"
    finally:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass


# ══════════════════════════════════════════════════════════════════════════
#  Git — LECTURE de faits + les 3 SEULS verbes mutants autorisés
# ══════════════════════════════════════════════════════════════════════════

def _git_text(repo: Path, args: "list[str]") -> "tuple[int, str, str]":
    try:
        p = subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True, timeout=60)
        return p.returncode, p.stdout, p.stderr
    except (subprocess.TimeoutExpired, OSError) as exc:
        return 1, "", str(exc)


def _git_bytes(repo: Path, args: "list[str]") -> "tuple[int, bytes, str]":
    try:
        p = subprocess.run(["git", *args], cwd=str(repo), capture_output=True, timeout=60)
        return p.returncode, p.stdout, p.stderr.decode("utf-8", "replace")
    except (subprocess.TimeoutExpired, OSError) as exc:
        return 1, b"", str(exc)


def _git_add_exact(repo: Path, target_path: str) -> "tuple[int, str]":
    """SEUL staging autorisé : un pathspec explicite après `--`. Jamais
    `.` / `-A` / `--all` / wildcard / répertoire."""
    rc, _out, err = _git_text(repo, ["add", "--", target_path])
    return rc, err


def _git_commit(repo: Path, subject: str, trailer_block: str) -> "tuple[int, str]":
    """UN commit local. Jamais --amend/--all/-A/-a. commit.gpgsign forcé à
    false (parité avec les fixtures de test canoniques)."""
    rc, _out, err = _git_text(
        repo, ["-c", "commit.gpgsign=false", "commit", "-m", subject, "-m", trailer_block],
    )
    return rc, err


def _git_restore_staged_exact(repo: Path, target_path: str) -> "tuple[int, str]":
    """Dé-stage SÛR du SEUL chemin cible exact. `git restore --staged` ne
    touche PAS les octets du worktree."""
    rc, _out, err = _git_text(repo, ["restore", "--staged", "--", target_path])
    return rc, err


def _parse_porcelain(text: str) -> "list[tuple[str, str]]":
    out = []
    for line in text.splitlines():
        if not line:
            continue
        out.append((line[:2], line[3:]))
    return out


def _safe_unstage_exact_path(repo: Path, target_path: str, expected_head: str) -> dict:
    """Utilisable UNIQUEMENT si HEAD n'a pas bougé ET si l'index contient
    EXACTEMENT ce chemin cible gouverné. Sinon : ne touche RIEN, renvoie HOLD."""
    rc, head_out, _ = _git_text(repo, ["rev-parse", "HEAD"])
    if rc != 0 or head_out.strip() != expected_head:
        return {"unstaged": False, "reason": "REFUSED_HEAD_MOVED"}
    rc, cached, _ = _git_text(repo, ["diff", "--cached", "--name-only"])
    staged = [p for p in cached.splitlines() if p.strip()]
    if staged != [target_path]:
        return {"unstaged": False, "reason": "REFUSED_UNEXPECTED_INDEX", "staged": staged}
    rc, err = _git_restore_staged_exact(repo, target_path)
    return {"unstaged": rc == 0, "reason": None if rc == 0 else f"RESTORE_STAGED_FAILED:{err.strip()}"}


# ══════════════════════════════════════════════════════════════════════════
#  Identité pré-commit (déterministe — jamais dépendante du SHA de commit)
# ══════════════════════════════════════════════════════════════════════════

_CORRELATION_SEED_FIELDS = (
    "mission_id", "action_id", "ordinal", "previous_mission_tip_sha",
    "execution_authority_hash", "batch_execution_id", "child_execution_id",
    "approval_id", "kx108_pre_decision_record_id", "kx108_post_decision_record_id",
    "test_contract_result_id", "sealed_apply_receipt_id", "sealed_rollback_evidence_id",
    "target_path",
)


def _correlation_seed(ctx: dict) -> str:
    return _canon({k: ctx.get(k) for k in _CORRELATION_SEED_FIELDS})


def _snapshot_correlation_id(ctx: dict) -> str:
    return "snc-" + _sha256_hex_text(_correlation_seed(ctx))[:32]


def _snapshot_receipt_id(ctx: dict) -> str:
    return "lsr-" + _sha256_hex_text("lsr:" + _correlation_seed(ctx))[:32]


_LSR_BOUND_FIELDS = (
    "local_snapshot_receipt_schema_version", "snapshot_receipt_id", "snapshot_correlation_id",
    "mission_id", "action_id", "ordinal",
    "previous_mission_tip_sha", "new_commit_sha", "commit_parent_sha", "commit_tree_sha",
    "committed_paths",
    "target_pre_sha256", "target_post_sha256",
    "execution_authority_hash", "batch_execution_id", "child_execution_id", "approval_id",
    "approval_record_hash",
    "kx108_pre_decision_record_id", "kx108_pre_decision_record_hash",
    "kx108_post_decision_record_id", "kx108_post_decision_record_hash",
    "test_contract_result_id", "test_contract_result_record_hash",
    "sealed_apply_receipt_id", "sealed_apply_receipt_hash",
    "sealed_rollback_evidence_id", "sealed_rollback_evidence_hash",
    "created_at", "decision_authority", "not_final_human_git_disposition",
)


# ══════════════════════════════════════════════════════════════════════════
#  1 — ÉLIGIBILITÉ (fail-closed ; recharge + revérifie l'évidence canonique)
# ══════════════════════════════════════════════════════════════════════════

def _ineligible(reason: str, **extra) -> dict:
    return {"eligible": False, "reason": reason, **extra}


def check_local_snapshot_eligibility(
    *,
    mission_id: str, action_id: str, ordinal: int,
    expected_branch_name: str, expected_worktree_path: "str | Path",
    expected_previous_mission_tip_sha: str,
    expected_repository_common_dir: "Optional[str]" = None,
    batch_execution_id: str, child_execution_id: str,
    execution_authority_hash: str, approval_id: str,
    kx108_pre_decision_record_id: str, kx108_post_decision_record_id: str,
    test_contract_result_id: str,
    sealed_apply_receipt_id: str, sealed_rollback_evidence_id: str,
    target_path: str,
    execution_dir: "str | Path",
    kx108_pre_decision_dir: "str | Path", kx108_post_decision_dir: "str | Path",
    test_contract_results_dir: "str | Path",
    sealed_receipt_dir: "str | Path", sealed_rollback_evidence_dir: "str | Path",
    rollback_result_dir: "str | Path",
    approval_dir: "Optional[str | Path]" = None,
) -> dict:
    wt = Path(expected_worktree_path)
    approval_dir = Path(approval_dir) if approval_dir is not None else Path(execution_dir)

    # 0. validation lexicale
    if not (isinstance(mission_id, str) and mission_id.strip()):
        return _ineligible("MISSION_ID_REQUIRED")
    if not (isinstance(action_id, str) and action_id.strip()):
        return _ineligible("ACTION_ID_REQUIRED")
    if not (isinstance(ordinal, int) and not isinstance(ordinal, bool) and ordinal >= 0):
        return _ineligible("ORDINAL_INVALID")
    if not _is_64_hex(execution_authority_hash):
        return _ineligible("EXECUTION_AUTHORITY_HASH_NOT_64_HEX")
    if not _is_40_hex(expected_previous_mission_tip_sha):
        return _ineligible("EXPECTED_PREVIOUS_MISSION_TIP_SHA_NOT_40_HEX")
    tp = str(target_path).replace("\\", "/")
    if tp.startswith("/") or ".." in tp.split("/") or (len(tp) > 1 and tp[1] == ":"):
        return _ineligible("TARGET_PATH_NOT_REPO_RELATIVE")

    # 1. SAR
    sar = _SEV.load_sealed_apply_receipt(sealed_apply_receipt_id, Path(sealed_receipt_dir))
    ok, why = _SEV.verify_sealed_apply_receipt(sar)
    if not ok:
        return _ineligible(f"SEALED_APPLY_RECEIPT_INVALID:{why}")
    for k, v in (("batch_execution_id", batch_execution_id), ("child_execution_id", child_execution_id),
                 ("execution_authority_hash", execution_authority_hash), ("approval_id", approval_id),
                 ("kx108_pre_decision_record_id", kx108_pre_decision_record_id), ("target_path", tp)):
        if sar.get(k) != v:
            return _ineligible(f"SAR_FIELD_MISMATCH:{k}")
    if sar.get("status") != "CONTENT_APPLIED":
        return _ineligible(f"SAR_STATUS_NOT_CONTENT_APPLIED:{sar.get('status')}")
    if sar.get("operation_type") != SUPPORTED_OPERATION:
        return _ineligible(f"SAR_OPERATION_UNSUPPORTED:{sar.get('operation_type')}")
    if sar.get("decision_authority") != EXPECTED_GOVERNED_DECISION_AUTHORITY:
        return _ineligible("SAR_DECISION_AUTHORITY_NOT_KX108_ONLY")
    target_post_sha256 = sar.get("target_post_sha256")
    target_pre_sha256 = sar.get("target_pre_sha256")
    if not _is_64_hex(target_post_sha256) or target_post_sha256 != sar.get("source_content_sha256"):
        return _ineligible("SAR_TARGET_POST_NEQ_SOURCE_CONTENT_SHA256")
    if sar.get("sealed_rollback_evidence_id") != sealed_rollback_evidence_id:
        return _ineligible("SAR_SRE_ID_MISMATCH")

    # 2. SRE
    sre = _SEV.load_sealed_rollback_evidence(sealed_rollback_evidence_id, Path(sealed_rollback_evidence_dir))
    ok, why = _SEV.verify_sealed_rollback_evidence(sre)
    if not ok:
        return _ineligible(f"SEALED_ROLLBACK_EVIDENCE_INVALID:{why}")
    for k, v in (("batch_execution_id", batch_execution_id), ("child_execution_id", child_execution_id),
                 ("execution_authority_hash", execution_authority_hash), ("approval_id", approval_id),
                 ("target_path", tp)):
        if sre.get(k) != v:
            return _ineligible(f"SRE_FIELD_MISMATCH:{k}")

    # 3. KX108_PRE
    pre = _DS.load_kx108_decision_record(kx108_pre_decision_record_id, Path(kx108_pre_decision_dir))
    ok, why = _DS.verify_kx108_decision_record(pre)
    if not ok:
        return _ineligible(f"KX108_PRE_INVALID:{why}")
    if pre.get("x108_gate") != "ALLOW":
        return _ineligible(f"KX108_PRE_GATE_NOT_ALLOW:{pre.get('x108_gate')}")
    if pre.get("decision_phase") != _DS.PRE_DECISION_PHASE:
        return _ineligible(f"KX108_PRE_PHASE_NOT_PRE:{pre.get('decision_phase')}")
    if pre.get("execution_authority_hash") != execution_authority_hash or pre.get("approval_id") != approval_id:
        return _ineligible("KX108_PRE_BINDING_MISMATCH")
    pre_hash = _DS.compute_kx108_decision_record_hash(pre)

    # 4. KX108_POST — lié à PRE exact
    post = _DS.load_kx108_decision_record(kx108_post_decision_record_id, Path(kx108_post_decision_dir))
    ok, why = _DS.verify_kx108_decision_record(post)
    if not ok:
        return _ineligible(f"KX108_POST_INVALID:{why}")
    if post.get("x108_gate") != "ALLOW":
        return _ineligible(f"KX108_POST_GATE_NOT_ALLOW:{post.get('x108_gate')}")
    if post.get("decision_phase") != _DS.POST_DECISION_PHASE:
        return _ineligible(f"KX108_POST_PHASE_NOT_POST:{post.get('decision_phase')}")
    if post.get("execution_authority_hash") != execution_authority_hash:
        return _ineligible("KX108_POST_EAH_MISMATCH")
    if post.get("kx108_pre_decision_record_id") != kx108_pre_decision_record_id:
        return _ineligible("KX108_POST_NOT_BOUND_TO_PRE_ID")
    if post.get("kx108_pre_decision_record_hash") != pre_hash:
        return _ineligible("KX108_POST_NOT_BOUND_TO_PRE_HASH")
    post_hash = _DS.compute_kx108_decision_record_hash(post)

    # 5. TestContractResult
    tcr = _TC.load_test_contract_result(test_contract_result_id, Path(test_contract_results_dir))
    ok, why = _TC.verify_test_contract_result_artifact(tcr)
    if not ok:
        return _ineligible(f"TEST_CONTRACT_RESULT_INVALID:{why}")
    if tcr.get("aggregate_status") != _TC.AGGREGATE_ALL_REQUIRED_PASS:
        return _ineligible(f"TEST_CONTRACT_AGGREGATE_NOT_ALL_REQUIRED_PASS:{tcr.get('aggregate_status')}")
    for k, v in (("batch_execution_id", batch_execution_id), ("child_execution_id", child_execution_id),
                 ("execution_authority_hash", execution_authority_hash), ("approval_id", approval_id)):
        if tcr.get(k) != v:
            return _ineligible(f"TCR_FIELD_MISMATCH:{k}")
    tcr_hash = _TC.compute_test_contract_result_hash(tcr)

    # 6. HumanApproval + enveloppe + EAH recalculé
    envelope = _BE._load_execution(batch_execution_id, Path(execution_dir))
    if envelope is None:
        return _ineligible("EXECUTION_ENVELOPE_NOT_FOUND")
    if not envelope.get("integrity_verified"):
        return _ineligible("EXECUTION_ENVELOPE_INTEGRITY_NOT_VERIFIED")
    recomputed_eah = _BE.compute_execution_authority_hash(envelope)
    if recomputed_eah != execution_authority_hash or recomputed_eah != envelope.get("execution_authority_hash"):
        return _ineligible("EXECUTION_AUTHORITY_HASH_DRIFT")
    approval = _BE.load_approval_artifact(approval_id, execution_dir=approval_dir)
    ok, why = _BE.verify_approval_artifact(approval)
    if not ok:
        return _ineligible(f"HUMAN_APPROVAL_ARTIFACT_INVALID:{why}")
    ok, why = _BE._validate_approval(approval, envelope)
    if not ok:
        return _ineligible(f"HUMAN_APPROVAL_NOT_BOUND_TO_EXECUTION:{why}")
    if approval.get("execution_authority_hash") != execution_authority_hash:
        return _ineligible("HUMAN_APPROVAL_EAH_MISMATCH")
    if approval.get("approval_status") != _BE.APPROVED_FOR_BOUNDED_EXECUTION:
        return _ineligible("HUMAN_APPROVAL_STATUS_NOT_APPROVED_FOR_BOUNDED_EXECUTION")
    approval_record_hash = approval.get("approval_record_hash")

    child = next((c for c in (envelope.get("children") or [])
                 if c.get("child_execution_id") == child_execution_id), None)
    if child is None:
        return _ineligible("CHILD_NOT_FOUND_IN_ENVELOPE")
    if child.get("operation_type") != SUPPORTED_OPERATION:
        return _ineligible(f"CHILD_OPERATION_UNSUPPORTED:{child.get('operation_type')}")
    if child.get("target_path") != tp:
        return _ineligible("CHILD_TARGET_PATH_MISMATCH")
    child_source_sha = child.get("source_content_sha256")
    if not _is_64_hex(child_source_sha):
        return _ineligible("CHILD_SOURCE_CONTENT_SHA256_NOT_64_HEX")

    # 7. cohérence croisée octets gouvernés
    if sar.get("target_pre_sha256") != child.get("target_pre_sha256"):
        return _ineligible("SAR_TARGET_PRE_NEQ_CHILD")
    if target_post_sha256 != child_source_sha:
        return _ineligible("SAR_TARGET_POST_NEQ_CHILD_SOURCE")
    if sar.get("source_content_sha256") != child_source_sha:
        return _ineligible("SAR_SOURCE_CONTENT_NEQ_CHILD")

    # 8. AUCUN RollbackResult pour cette (batch, child)
    rrd = Path(rollback_result_dir)
    if rrd.exists():
        for f in rrd.glob("*.json"):
            try:
                rr = json.loads(f.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                return _ineligible("ROLLBACK_RESULT_DIR_UNPARSEABLE_ENTRY")
            if rr.get("batch_execution_id") == batch_execution_id and \
               rr.get("child_execution_id") == child_execution_id:
                return _ineligible("ROLLBACK_RESULT_EXISTS_FOR_THIS_ACTION")

    # 9. Faits Git du worktree de mission
    if not wt.is_dir():
        return _ineligible("WORKTREE_PATH_NOT_A_DIRECTORY")
    rc, cd_out, _ = _git_text(wt, ["rev-parse", "--git-common-dir"])
    if rc != 0 or not cd_out.strip():
        return _ineligible("WORKTREE_NOT_A_GIT_WORKTREE")
    if expected_repository_common_dir is not None:
        try:
            observed_cd = str((wt / cd_out.strip()).resolve())
        except OSError:
            observed_cd = cd_out.strip()
        if observed_cd != str(Path(expected_repository_common_dir).resolve()):
            return _ineligible("REPOSITORY_COMMON_DIR_MISMATCH")
    rc, br_out, _ = _git_text(wt, ["rev-parse", "--abbrev-ref", "HEAD"])
    if rc != 0 or br_out.strip() != expected_branch_name:
        return _ineligible(f"BRANCH_MISMATCH:{br_out.strip()}")
    rc, head_out, _ = _git_text(wt, ["rev-parse", "HEAD"])
    if rc != 0 or head_out.strip() != expected_previous_mission_tip_sha:
        return _ineligible(f"HEAD_NOT_AT_EXPECTED_PREVIOUS_MISSION_TIP:{head_out.strip()}")
    rc, cached_out, _ = _git_text(wt, ["diff", "--cached", "--name-only"])
    if rc != 0 or [p for p in cached_out.splitlines() if p.strip()]:
        return _ineligible("INDEX_NOT_EMPTY")
    rc, st_out, _ = _git_text(wt, ["status", "--porcelain"])
    if rc != 0:
        return _ineligible("STATUS_UNREADABLE")
    entries = _parse_porcelain(st_out)
    if any(code.strip() == "??" for code, _ in entries):
        return _ineligible("UNTRACKED_PRESENT")
    if len(entries) == 0:
        return _ineligible("WORKTREE_CLEAN_NOTHING_TO_SNAPSHOT")
    if entries != [(" M", tp)]:
        return _ineligible(f"WORKTREE_STATE_NOT_EXACTLY_GOVERNED_TARGET_MODIFICATION:{entries}")
    rc, diff_out, _ = _git_text(wt, ["diff", "--name-only"])
    if rc != 0 or [p for p in diff_out.splitlines() if p.strip()] != [tp]:
        return _ineligible("DIFF_SCOPE_NOT_EXACTLY_TARGET")

    # 10. Liaison d'octets : worktree == SAR.target_post == child.source_content
    target_abs = (wt / tp)
    try:
        if target_abs.is_symlink():
            return _ineligible("TARGET_IS_SYMLINK")
        resolved = target_abs.resolve()
        resolved.relative_to(wt.resolve())
    except (OSError, ValueError):
        return _ineligible("TARGET_PATH_ESCAPES_WORKTREE")
    if not target_abs.is_file():
        return _ineligible("TARGET_FILE_MISSING")
    worktree_sha256 = _sha256_hex_bytes(target_abs.read_bytes())
    if worktree_sha256 != target_post_sha256 or worktree_sha256 != child_source_sha:
        return _ineligible(f"TARGET_BYTES_DRIFT:{worktree_sha256}")

    return {
        "eligible": True, "reason": None,
        "resolved": {
            "previous_mission_tip_sha": expected_previous_mission_tip_sha,
            "target_pre_sha256": target_pre_sha256,
            "target_post_sha256": target_post_sha256,
            "child_source_content_sha256": child_source_sha,
            "approval_record_hash": approval_record_hash,
            "kx108_pre_decision_record_hash": pre_hash,
            "kx108_post_decision_record_hash": post_hash,
            "test_contract_result_record_hash": tcr_hash,
            "sealed_apply_receipt_hash": sar.get("sealed_apply_receipt_hash"),
            "sealed_rollback_evidence_hash": sre.get("sealed_rollback_evidence_hash"),
            "worktree_target_sha256": worktree_sha256,
        },
    }


# ══════════════════════════════════════════════════════════════════════════
#  2 — CRÉATION du snapshot local (staging exact -> commit unique -> reçu)
# ══════════════════════════════════════════════════════════════════════════

def create_local_snapshot(
    *,
    mission_id: str, action_id: str, ordinal: int,
    expected_branch_name: str, expected_worktree_path: "str | Path",
    expected_previous_mission_tip_sha: str,
    expected_repository_common_dir: "Optional[str]" = None,
    batch_execution_id: str, child_execution_id: str,
    execution_authority_hash: str, approval_id: str,
    kx108_pre_decision_record_id: str, kx108_post_decision_record_id: str,
    test_contract_result_id: str,
    sealed_apply_receipt_id: str, sealed_rollback_evidence_id: str,
    target_path: str,
    execution_dir: "str | Path",
    kx108_pre_decision_dir: "str | Path", kx108_post_decision_dir: "str | Path",
    test_contract_results_dir: "str | Path",
    sealed_receipt_dir: "str | Path", sealed_rollback_evidence_dir: "str | Path",
    rollback_result_dir: "str | Path",
    snapshot_store_dir: "str | Path",
    approval_dir: "Optional[str | Path]" = None,
) -> dict:
    wt = Path(expected_worktree_path)
    tp = str(target_path).replace("\\", "/")
    sstore = Path(snapshot_store_dir)
    ctx = {
        "mission_id": mission_id, "action_id": action_id, "ordinal": ordinal,
        "previous_mission_tip_sha": expected_previous_mission_tip_sha,
        "execution_authority_hash": execution_authority_hash,
        "batch_execution_id": batch_execution_id, "child_execution_id": child_execution_id,
        "approval_id": approval_id,
        "kx108_pre_decision_record_id": kx108_pre_decision_record_id,
        "kx108_post_decision_record_id": kx108_post_decision_record_id,
        "test_contract_result_id": test_contract_result_id,
        "sealed_apply_receipt_id": sealed_apply_receipt_id,
        "sealed_rollback_evidence_id": sealed_rollback_evidence_id,
        "target_path": tp,
    }
    correlation_id = _snapshot_correlation_id(ctx)
    receipt_id = _snapshot_receipt_id(ctx)

    # ── Idempotence : reçu déjà présent pour CETTE identité pré-commit ──
    try:
        rpath = _safe_id_path(sstore, receipt_id)
    except ValueError:
        return {"status": SNAPSHOT_HOLD, "reason": "RECEIPT_ID_INVALID"}
    if rpath.exists():
        try:
            existing = json.loads(rpath.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {"status": SNAPSHOT_RECEIPT_EXISTS_BUT_REPO_DIVERGED, "reason": "RECEIPT_UNPARSEABLE"}
        ok, why = verify_local_snapshot_receipt(existing, repo_root=wt)
        if not ok:
            return {"status": SNAPSHOT_RECEIPT_EXISTS_BUT_REPO_DIVERGED, "reason": f"RECEIPT_VERIFY_FAILED:{why}"}
        rc, head_out, _ = _git_text(wt, ["rev-parse", "HEAD"])
        if rc == 0 and head_out.strip() == existing.get("new_commit_sha"):
            return {"status": SNAPSHOT_IDEMPOTENT_EXISTING_IDENTICAL,
                    "snapshot_receipt": existing, "snapshot_receipt_id": receipt_id,
                    "new_commit_sha": existing.get("new_commit_sha"),
                    "committed_paths": existing.get("committed_paths"),
                    "mission_revision_writes": 0}
        return {"status": SNAPSHOT_RECEIPT_EXISTS_BUT_REPO_DIVERGED,
                "reason": "HEAD_NOT_AT_RECEIPT_COMMIT", "new_commit_sha": existing.get("new_commit_sha")}

    # ── Éligibilité (recharge + revérifie toute l'évidence canonique) ──
    elig = check_local_snapshot_eligibility(
        mission_id=mission_id, action_id=action_id, ordinal=ordinal,
        expected_branch_name=expected_branch_name, expected_worktree_path=wt,
        expected_previous_mission_tip_sha=expected_previous_mission_tip_sha,
        expected_repository_common_dir=expected_repository_common_dir,
        batch_execution_id=batch_execution_id, child_execution_id=child_execution_id,
        execution_authority_hash=execution_authority_hash, approval_id=approval_id,
        kx108_pre_decision_record_id=kx108_pre_decision_record_id,
        kx108_post_decision_record_id=kx108_post_decision_record_id,
        test_contract_result_id=test_contract_result_id,
        sealed_apply_receipt_id=sealed_apply_receipt_id,
        sealed_rollback_evidence_id=sealed_rollback_evidence_id,
        target_path=tp, execution_dir=execution_dir,
        kx108_pre_decision_dir=kx108_pre_decision_dir, kx108_post_decision_dir=kx108_post_decision_dir,
        test_contract_results_dir=test_contract_results_dir,
        sealed_receipt_dir=sealed_receipt_dir, sealed_rollback_evidence_dir=sealed_rollback_evidence_dir,
        rollback_result_dir=rollback_result_dir, approval_dir=approval_dir,
    )
    if not elig["eligible"]:
        return {"status": SNAPSHOT_INELIGIBLE, "reason": elig["reason"], "detail": elig}
    r = elig["resolved"]
    target_post_sha256 = r["target_post_sha256"]

    # ── Staging exact ──
    rc, err = _git_add_exact(wt, tp)
    if rc != 0:
        undo = _safe_unstage_exact_path(wt, tp, expected_previous_mission_tip_sha)
        return {"status": SNAPSHOT_STAGE_FAILED, "reason": err.strip(), "unstage": undo}
    rc, cached_out, _ = _git_text(wt, ["diff", "--cached", "--name-only"])
    if rc != 0 or [p for p in cached_out.splitlines() if p.strip()] != [tp]:
        undo = _safe_unstage_exact_path(wt, tp, expected_previous_mission_tip_sha)
        return {"status": SNAPSHOT_STAGE_FAILED, "reason": "STAGED_SCOPE_NOT_EXACT", "unstage": undo}
    rc, unstaged_out, _ = _git_text(wt, ["diff", "--name-only"])
    if rc != 0 or [p for p in unstaged_out.splitlines() if p.strip()]:
        undo = _safe_unstage_exact_path(wt, tp, expected_previous_mission_tip_sha)
        return {"status": SNAPSHOT_STAGE_FAILED, "reason": "UNSTAGED_RESIDUE_AFTER_ADD", "unstage": undo}

    # ── Vérification des octets du blob STAGÉ (pas seulement le nom) ──
    rc, staged_blob, err = _git_bytes(wt, ["show", f":{tp}"])
    if rc != 0:
        undo = _safe_unstage_exact_path(wt, tp, expected_previous_mission_tip_sha)
        return {"status": SNAPSHOT_STAGED_BYTES_MISMATCH, "reason": f"STAGED_BLOB_UNREADABLE:{err.strip()}", "unstage": undo}
    staged_sha = _sha256_hex_bytes(staged_blob)
    worktree_sha = _sha256_hex_bytes((wt / tp).read_bytes())
    if not (staged_sha == worktree_sha == target_post_sha256):
        undo = _safe_unstage_exact_path(wt, tp, expected_previous_mission_tip_sha)
        return {"status": SNAPSHOT_STAGED_BYTES_MISMATCH,
                "reason": f"staged={staged_sha} worktree={worktree_sha} sar_post={target_post_sha256}",
                "unstage": undo}

    # ── Re-check anti-course JUSTE avant le commit ──
    rc, head_out, _ = _git_text(wt, ["rev-parse", "HEAD"])
    if rc != 0 or head_out.strip() != expected_previous_mission_tip_sha:
        undo = _safe_unstage_exact_path(wt, tp, expected_previous_mission_tip_sha)
        return {"status": SNAPSHOT_HEAD_MOVED, "reason": head_out.strip(), "unstage": undo}
    rc, st_out, _ = _git_text(wt, ["status", "--porcelain"])
    entries = _parse_porcelain(st_out)
    if any(code.strip() == "??" for code, _ in entries):
        undo = _safe_unstage_exact_path(wt, tp, expected_previous_mission_tip_sha)
        return {"status": SNAPSHOT_PRE_COMMIT_DRIFT, "reason": "UNTRACKED_APPEARED", "unstage": undo}
    if entries != [("M ", tp)]:
        undo = _safe_unstage_exact_path(wt, tp, expected_previous_mission_tip_sha)
        return {"status": SNAPSHOT_PRE_COMMIT_DRIFT, "reason": f"INDEX_STATE_NOT_EXACTLY_STAGED_TARGET:{entries}", "unstage": undo}

    # ── Commit unique ──
    subject = f"obsidia(work): local snapshot {mission_id[:12]} {action_id[:12]} ordinal {ordinal}"
    trailer_block = (
        f"Obsidia-Mission: {mission_id}\n"
        f"Obsidia-Action: {action_id}\n"
        f"Obsidia-Snapshot-Correlation: {correlation_id}\n"
        f"Obsidia-Snapshot-Receipt-Id: {receipt_id}"
    )
    rc, err = _git_commit(wt, subject, trailer_block)
    if rc != 0:
        undo = _safe_unstage_exact_path(wt, tp, expected_previous_mission_tip_sha)
        return {"status": SNAPSHOT_COMMIT_COMMAND_FAILED, "reason": err.strip(), "unstage": undo}

    # ── Vérification post-commit (aucun reset/amend/force en cas d'échec) ──
    rc, new_sha_out, _ = _git_text(wt, ["rev-parse", "HEAD"])
    new_commit_sha = new_sha_out.strip()
    rc2, parents_out, _ = _git_text(wt, ["rev-list", "--parents", "-n", "1", "HEAD"])
    parents = parents_out.strip().split()
    rc3, tree_out, _ = _git_text(wt, ["rev-parse", "HEAD^{tree}"])
    commit_tree_sha = tree_out.strip()
    rc4, showpaths_out, _ = _git_text(wt, ["show", "--name-only", "--pretty=format:", "HEAD"])
    committed_paths = [p for p in showpaths_out.splitlines() if p.strip()]
    rc5, commit_blob, _ = _git_bytes(wt, ["show", f"{new_commit_sha}:{tp}"])
    rc6, st_after, _ = _git_text(wt, ["status", "--porcelain"])
    rc7, cached_after, _ = _git_text(wt, ["diff", "--cached", "--name-only"])

    mismatches = []
    if rc or not _is_40_hex(new_commit_sha):
        mismatches.append("HEAD_UNREADABLE")
    if rc2 or len(parents) != 2:
        mismatches.append(f"NOT_EXACTLY_ONE_PARENT:{parents}")
    elif parents[1] != expected_previous_mission_tip_sha:
        mismatches.append(f"PARENT_NOT_PREVIOUS_TIP:{parents[1]}")
    if rc3 or not _is_40_hex(commit_tree_sha):
        mismatches.append("TREE_UNREADABLE")
    if rc4 or committed_paths != [tp]:
        mismatches.append(f"COMMITTED_PATHS_NOT_EXACTLY_TARGET:{committed_paths}")
    if rc5 != 0 or _sha256_hex_bytes(commit_blob) != target_post_sha256:
        mismatches.append("COMMITTED_BLOB_NEQ_GOVERNED_POST_BYTES")
    if rc6 != 0 or st_after.strip() != "":
        mismatches.append(f"WORKTREE_NOT_CLEAN_AFTER_COMMIT:{st_after.strip()}")
    if rc7 != 0 or [p for p in cached_after.splitlines() if p.strip()]:
        mismatches.append("INDEX_NOT_EMPTY_AFTER_COMMIT")
    if mismatches:
        return {"status": SNAPSHOT_POST_COMMIT_VERIFY_FAILED,
                "abnormal_commit_sha": new_commit_sha, "mismatch": mismatches}

    # ── LocalSnapshotReceipt immuable ──
    from datetime import datetime, timezone
    rec = {
        "local_snapshot_receipt_schema_version": LSR_SCHEMA_VERSION,
        "snapshot_receipt_id": receipt_id,
        "snapshot_correlation_id": correlation_id,
        "mission_id": mission_id, "action_id": action_id, "ordinal": ordinal,
        "previous_mission_tip_sha": expected_previous_mission_tip_sha,
        "new_commit_sha": new_commit_sha,
        "commit_parent_sha": parents[1],
        "commit_tree_sha": commit_tree_sha,
        "committed_paths": [tp],
        "target_pre_sha256": r["target_pre_sha256"],
        "target_post_sha256": target_post_sha256,
        "execution_authority_hash": execution_authority_hash,
        "batch_execution_id": batch_execution_id,
        "child_execution_id": child_execution_id,
        "approval_id": approval_id,
        "approval_record_hash": r["approval_record_hash"],
        "kx108_pre_decision_record_id": kx108_pre_decision_record_id,
        "kx108_pre_decision_record_hash": r["kx108_pre_decision_record_hash"],
        "kx108_post_decision_record_id": kx108_post_decision_record_id,
        "kx108_post_decision_record_hash": r["kx108_post_decision_record_hash"],
        "test_contract_result_id": test_contract_result_id,
        "test_contract_result_record_hash": r["test_contract_result_record_hash"],
        "sealed_apply_receipt_id": sealed_apply_receipt_id,
        "sealed_apply_receipt_hash": r["sealed_apply_receipt_hash"],
        "sealed_rollback_evidence_id": sealed_rollback_evidence_id,
        "sealed_rollback_evidence_hash": r["sealed_rollback_evidence_hash"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "decision_authority": SNAPSHOT_DECISION_AUTHORITY,
        "not_final_human_git_disposition": True,
    }
    rec["local_snapshot_receipt_record_hash"] = _record_hash(rec, _LSR_BOUND_FIELDS)
    st = _atomic_publish_json(rpath, rec)
    if st == "IMMUTABILITY_VIOLATION":
        return {"status": SNAPSHOT_RECEIPT_IMMUTABILITY_VIOLATION, "new_commit_sha": new_commit_sha}
    reloaded = json.loads(rpath.read_text(encoding="utf-8"))
    ok, why = verify_local_snapshot_receipt(reloaded, repo_root=wt)
    if not ok:
        return {"status": SNAPSHOT_POST_COMMIT_VERIFY_FAILED, "abnormal_commit_sha": new_commit_sha,
                "mismatch": [f"RECEIPT_REVERIFY_FAILED:{why}"]}

    return {
        "status": SNAPSHOT_COMMITTED, "reason": None,
        "new_commit_sha": new_commit_sha, "commit_parent_sha": parents[1],
        "commit_tree_sha": commit_tree_sha, "committed_paths": [tp],
        "snapshot_receipt": reloaded, "snapshot_receipt_id": receipt_id,
        "snapshot_correlation_id": correlation_id,
        "receipt_store_status": st,
        "decision_authority": SNAPSHOT_DECISION_AUTHORITY,
        "local_snapshot_is_execution_authority": False,
        "local_snapshot_is_final_human_acceptance": False,
        "mission_revision_writes": 0,
    }


# ══════════════════════════════════════════════════════════════════════════
#  3 — VÉRIFICATION du reçu (autonome ; optionnellement contre le dépôt)
# ══════════════════════════════════════════════════════════════════════════

def verify_local_snapshot_receipt(record: Optional[dict], *,
                                  repo_root: "Optional[str | Path]" = None) -> "tuple[bool, Optional[str]]":
    if not isinstance(record, dict):
        return False, "RECEIPT_MISSING"
    if record.get("local_snapshot_receipt_schema_version") != LSR_SCHEMA_VERSION:
        return False, "RECEIPT_SCHEMA_UNSUPPORTED"
    for f in _LSR_BOUND_FIELDS:
        if f not in record:
            return False, f"RECEIPT_FIELD_MISSING:{f}"
    if record.get("decision_authority") != SNAPSHOT_DECISION_AUTHORITY:
        return False, "RECEIPT_DECISION_AUTHORITY_NOT_NON_SOVEREIGN"
    if record.get("not_final_human_git_disposition") is not True:
        return False, "RECEIPT_MISSING_NOT_FINAL_HUMAN_GIT_DISPOSITION_MARKER"
    # Le reçu ne DOIT PAS porter la signature structurelle d'une HumanApproval / décision KX108
    for forbidden in ("approval_status", "approved_by", "x108_gate", "approval_schema_version"):
        if forbidden in record:
            return False, f"RECEIPT_CARRIES_FORBIDDEN_GOVERNED_FIELD:{forbidden}"
    ctx = {
        "mission_id": record.get("mission_id"), "action_id": record.get("action_id"),
        "ordinal": record.get("ordinal"),
        "previous_mission_tip_sha": record.get("previous_mission_tip_sha"),
        "execution_authority_hash": record.get("execution_authority_hash"),
        "batch_execution_id": record.get("batch_execution_id"),
        "child_execution_id": record.get("child_execution_id"),
        "approval_id": record.get("approval_id"),
        "kx108_pre_decision_record_id": record.get("kx108_pre_decision_record_id"),
        "kx108_post_decision_record_id": record.get("kx108_post_decision_record_id"),
        "test_contract_result_id": record.get("test_contract_result_id"),
        "sealed_apply_receipt_id": record.get("sealed_apply_receipt_id"),
        "sealed_rollback_evidence_id": record.get("sealed_rollback_evidence_id"),
        "target_path": (record.get("committed_paths") or [None])[0],
    }
    if record.get("snapshot_correlation_id") != _snapshot_correlation_id(ctx):
        return False, "RECEIPT_CORRELATION_ID_MISMATCH"
    if record.get("snapshot_receipt_id") != _snapshot_receipt_id(ctx):
        return False, "RECEIPT_ID_MISMATCH"
    if record.get("local_snapshot_receipt_record_hash") != _record_hash(record, _LSR_BOUND_FIELDS):
        return False, "RECEIPT_RECORD_HASH_MISMATCH"
    if record.get("commit_parent_sha") != record.get("previous_mission_tip_sha"):
        return False, "RECEIPT_PARENT_NEQ_PREVIOUS_TIP"
    if record.get("committed_paths") != [ctx["target_path"]] or len(record.get("committed_paths") or []) != LOCAL_SNAPSHOT_V0_MAX_TARGETS:
        return False, "RECEIPT_COMMITTED_PATHS_NOT_EXACTLY_ONE_TARGET"
    if record.get("target_post_sha256") != record.get("target_post_sha256"):  # placeholder (always true)
        return False, "UNREACHABLE"

    if repo_root is None:
        return True, None   # vérification historique autonome (aucune dépendance à un HEAD mutable)

    wt = Path(repo_root)
    new_sha = record["new_commit_sha"]
    rc, _o, _e = _git_text(wt, ["cat-file", "-e", f"{new_sha}^{{commit}}"])
    if rc != 0:
        return False, "RECEIPT_COMMIT_NOT_PRESENT_LOCALLY"
    rc, parents_out, _ = _git_text(wt, ["rev-list", "--parents", "-n", "1", new_sha])
    parents = parents_out.strip().split()
    if len(parents) != 2 or parents[1] != record["commit_parent_sha"]:
        return False, "RECEIPT_COMMIT_PARENTAGE_MISMATCH"
    rc, tree_out, _ = _git_text(wt, ["rev-parse", f"{new_sha}^{{tree}}"])
    if rc != 0 or tree_out.strip() != record["commit_tree_sha"]:
        return False, "RECEIPT_COMMIT_TREE_MISMATCH"
    rc, showpaths_out, _ = _git_text(wt, ["show", "--name-only", "--pretty=format:", new_sha])
    if [p for p in showpaths_out.splitlines() if p.strip()] != record["committed_paths"]:
        return False, "RECEIPT_COMMITTED_PATHS_MISMATCH_VS_REPO"
    rc, blob, _ = _git_bytes(wt, ["show", f"{new_sha}:{record['committed_paths'][0]}"])
    if rc != 0 or _sha256_hex_bytes(blob) != record["target_post_sha256"]:
        return False, "RECEIPT_COMMITTED_BLOB_NEQ_GOVERNED_POST"
    return True, None
