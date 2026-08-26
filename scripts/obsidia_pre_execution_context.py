"""
obsidia_pre_execution_context.py
=================================
CLOSE_ACD02_PREEXECUTION_BINDING_GAP_V0 — capture canonique,
vérifiée, immuable, append-only, hors dépôt, du contexte d'exécution
OBSERVÉ avant toute mutation de cible (isolation worktree/branche,
base_sha, identité source, manifeste), pour lier honnêtement ces faits
jusqu'à ToolingBuildState.

Ce module NE DÉCIDE RIEN et NE FAIT JAMAIS CONFIANCE À UNE ASSERTION
DE L'APPELANT. worktree_isolated / branch_isolated ne sont JAMAIS des
paramètres fournis par l'appelant — ils sont DÉRIVÉS d'observations
Git réelles (git worktree list --porcelain, git rev-parse HEAD, git
status --short) et échouent fermé (False) au moindre doute.

decision_authority = KX108_ONLY
"""

from __future__ import annotations

import datetime
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Optional

SCHEMA_VERSION = 1
DECISION_AUTHORITY = "KX108_ONLY"

STATUS_STORED = "STORED"
STATUS_IDEMPOTENT_EXISTING_IDENTICAL = "IDEMPOTENT_EXISTING_IDENTICAL"
STATUS_IMMUTABILITY_VIOLATION = "IMMUTABILITY_VIOLATION"
STATUS_INVALID_CONTEXT_ID = "INVALID_CONTEXT_ID"

ISOLATION_VERIFIED = "ISOLATION_VERIFIED"
ISOLATION_NOT_VERIFIED = "ISOLATION_NOT_VERIFIED"

PRE_EXECUTION_CONTEXT_DIR = Path(os.environ.get("LOCALAPPDATA", "")) / "Obsidia" / "pre_execution_contexts"

_CONTEXT_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,128}$")

REASON_WORKTREE_NOT_REGISTERED = "WORKTREE_NOT_REGISTERED"
REASON_MAIN_WORKTREE_NOT_REGISTERED = "MAIN_WORKTREE_NOT_REGISTERED"
REASON_WORKTREE_NOT_DISTINCT = "WORKTREE_NOT_DISTINCT_FROM_MAIN"
REASON_DETACHED_OR_UNKNOWN_BRANCH = "WORKTREE_DETACHED_OR_UNKNOWN_BRANCH"
REASON_BRANCH_MISMATCH = "BRANCH_MISMATCH_RECORDED_VS_OBSERVED"
REASON_BRANCH_NOT_ISOLATED = "BRANCH_SAME_AS_MAIN_WORKTREE_BRANCH"
REASON_HEAD_MISMATCH = "HEAD_NOT_EQUAL_RECORDED_BASE_SHA"
REASON_WORKTREE_DIRTY = "WORKTREE_DIRTY_AT_CAPTURE"
REASON_TARGET_MISSING = "TARGET_MISSING_AT_CAPTURE"
REASON_TARGET_PRECONDITION_MISMATCH = "TARGET_PRECONDITION_MISMATCH"
REASON_GIT_COMMAND_FAILED = "GIT_COMMAND_FAILED"

_MANIFEST_BOUND_FIELDS = (
    "repository_identity", "execution_worktree_path", "branch_name", "base_sha",
    "source_kind", "source_repository_identity", "source_commit", "source_blob_sha",
    "source_path", "source_sha256",
    "target_path", "target_pre_sha256",
    "operation", "approved_scope", "protected_scope_status",
    "test_contract_hash", "schema_version",
)

_CONTEXT_BOUND_FIELDS = (
    "context_schema_version", "context_id", "created_at",
    "repository_identity", "repository_root",
    "execution_worktree_path", "branch_name", "base_sha",
    "target_path", "target_pre_sha256",
    "source_kind", "source_repository_identity", "source_commit", "source_blob_sha",
    "source_path", "source_sha256",
    "operation", "approved_scope",
    "worktree_isolated", "branch_isolated",
    "protected_scope_status",
    "manifest_sha256", "legacy_manifest_hash_short",
    "decision_authority",
)


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _run_git(args: list, cwd: Path) -> "tuple[int, str, str]":
    try:
        proc = subprocess.run(
            ["git", *args], cwd=str(cwd), capture_output=True, text=True, timeout=30,
        )
        return proc.returncode, proc.stdout, proc.stderr
    except (subprocess.TimeoutExpired, OSError) as exc:
        return 1, "", str(exc)


def _parse_worktree_list_porcelain(output: str) -> list:
    entries = []
    current: dict = {}
    for line in output.splitlines():
        if line.startswith("worktree "):
            if current:
                entries.append(current)
            current = {"worktree": line[len("worktree "):].strip()}
        elif line.startswith("HEAD "):
            current["head"] = line[len("HEAD "):].strip()
        elif line.startswith("branch "):
            current["branch"] = line[len("branch "):].strip()
        elif line.strip() == "detached":
            current["detached"] = True
        elif line.strip() == "bare":
            current["bare"] = True
    if current:
        entries.append(current)
    return entries


def _fail_closed(reason: str, **extra) -> dict:
    return {
        "status": ISOLATION_NOT_VERIFIED,
        "worktree_isolated": False,
        "branch_isolated": False,
        "reason": reason,
        **extra,
    }


def derive_isolation_evidence(
    execution_worktree_path: "str | Path",
    branch_name: str,
    base_sha: str,
    target_path: str,
    target_pre_sha256: str,
    main_worktree_path: "str | Path",
) -> dict:
    """
    DÉRIVE worktree_isolated / branch_isolated depuis des faits Git
    OBSERVÉS MAINTENANT — jamais depuis une assertion de l'appelant.
    Échoue fermé (False) à la moindre divergence. Voir mandat §4-5 pour
    la liste exhaustive des cas négatifs couverts.
    """
    exec_path = Path(execution_worktree_path).resolve()
    main_path = Path(main_worktree_path).resolve()

    rc, out, err = _run_git(["worktree", "list", "--porcelain"], cwd=exec_path)
    if rc != 0:
        return _fail_closed(REASON_GIT_COMMAND_FAILED, detail=err)

    entries = _parse_worktree_list_porcelain(out)
    match = next((e for e in entries if Path(e["worktree"]).resolve() == exec_path), None)
    if match is None:
        return _fail_closed(REASON_WORKTREE_NOT_REGISTERED)

    main_match = next((e for e in entries if Path(e["worktree"]).resolve() == main_path), None)
    if main_match is None:
        return _fail_closed(REASON_MAIN_WORKTREE_NOT_REGISTERED)

    if exec_path == main_path:
        return _fail_closed(REASON_WORKTREE_NOT_DISTINCT)

    if match.get("detached") or not match.get("branch"):
        return _fail_closed(REASON_DETACHED_OR_UNKNOWN_BRANCH)

    observed_branch = match["branch"].replace("refs/heads/", "")
    if observed_branch != branch_name:
        return _fail_closed(REASON_BRANCH_MISMATCH, detail=observed_branch)

    if not main_match.get("detached") and main_match.get("branch"):
        main_branch = main_match["branch"].replace("refs/heads/", "")
        if main_branch == observed_branch:
            return _fail_closed(REASON_BRANCH_NOT_ISOLATED)

    rc, out, err = _run_git(["rev-parse", "HEAD"], cwd=exec_path)
    if rc != 0:
        return _fail_closed(REASON_GIT_COMMAND_FAILED, detail=err)
    observed_head = out.strip()
    if observed_head != base_sha:
        return _fail_closed(REASON_HEAD_MISMATCH, detail=observed_head)

    rc, out, err = _run_git(["status", "--short"], cwd=exec_path)
    if rc != 0:
        return _fail_closed(REASON_GIT_COMMAND_FAILED, detail=err)
    if out.strip() != "":
        return _fail_closed(REASON_WORKTREE_DIRTY, detail=out.strip())

    target_abs = exec_path / target_path
    if not target_abs.exists() or not target_abs.is_file():
        return _fail_closed(REASON_TARGET_MISSING)
    observed_target_sha256 = hashlib.sha256(target_abs.read_bytes()).hexdigest()
    if observed_target_sha256 != target_pre_sha256:
        return _fail_closed(REASON_TARGET_PRECONDITION_MISMATCH, detail=observed_target_sha256)

    return {
        "status": ISOLATION_VERIFIED,
        "worktree_isolated": True,
        "branch_isolated": True,
        "reason": None,
        "verified_branch": observed_branch,
        "verified_head": observed_head,
    }


def compute_manifest_sha256(fields: dict) -> str:
    """SHA256 COMPLET (64 hex) — jamais le hash 16-hex de compatibilité."""
    payload = json.dumps({k: fields.get(k) for k in _MANIFEST_BOUND_FIELDS}, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def compute_context_record_hash(record: dict) -> str:
    payload = json.dumps({k: record.get(k) for k in _CONTEXT_BOUND_FIELDS}, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _context_path(context_id: "str | None", store_dir: Optional[Path] = None) -> Path:
    if not context_id or not _CONTEXT_ID_RE.match(context_id):
        raise ValueError("INVALID_CONTEXT_ID")
    d = store_dir or PRE_EXECUTION_CONTEXT_DIR
    return d / f"{context_id}.json"


def store_pre_execution_context_record(record: dict, store_dir: Optional[Path] = None) -> dict:
    context_id = record.get("context_id")
    try:
        p = _context_path(context_id, store_dir)
    except ValueError:
        return {"status": STATUS_INVALID_CONTEXT_ID, "context_id": context_id}

    payload = json.dumps(record, ensure_ascii=False, indent=2)
    p.parent.mkdir(parents=True, exist_ok=True)

    tmp_name = f".{p.name}.{os.getpid()}.{hashlib.sha256((payload + str(id(record))).encode('utf-8')).hexdigest()[:16]}.tmp"
    tmp = p.parent / tmp_name
    tmp.write_text(payload, encoding="utf-8")
    try:
        os.link(tmp, p)
        return {"status": STATUS_STORED, "context_id": context_id}
    except FileExistsError:
        existing = p.read_text(encoding="utf-8")
        if existing == payload:
            return {"status": STATUS_IDEMPOTENT_EXISTING_IDENTICAL, "context_id": context_id}
        return {"status": STATUS_IMMUTABILITY_VIOLATION, "context_id": context_id}
    finally:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass


def load_pre_execution_context_record(context_id: str, store_dir: Optional[Path] = None) -> Optional[dict]:
    try:
        p = _context_path(context_id, store_dir)
    except ValueError:
        return None
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def verify_pre_execution_context_record(record: Optional[dict]) -> "tuple[bool, Optional[str]]":
    if record is None:
        return False, "CONTEXT_RECORD_MISSING"
    if record.get("context_schema_version") != SCHEMA_VERSION:
        return False, "CONTEXT_RECORD_SCHEMA_UNSUPPORTED"
    for f in _CONTEXT_BOUND_FIELDS:
        if f not in record:
            return False, f"CONTEXT_RECORD_FIELD_MISSING:{f}"
    if record.get("decision_authority") != DECISION_AUTHORITY:
        return False, "DECISION_AUTHORITY_NOT_KX108_ONLY"
    expected_hash = compute_context_record_hash(record)
    if record.get("context_record_hash") != expected_hash:
        return False, "CONTEXT_RECORD_HASH_MISMATCH"
    return True, None


def create_pre_execution_context(
    execution_worktree_path: "str | Path",
    branch_name: str,
    base_sha: str,
    main_worktree_path: "str | Path",
    repository_identity: str,
    target_path: str,
    target_pre_sha256: str,
    source_kind: str,
    source_repository_identity: str,
    source_commit: str,
    source_blob_sha: str,
    source_path: str,
    source_sha256: str,
    operation: str,
    approved_scope: list,
    protected_scope_status: str,
    test_contract_hash: Optional[str] = None,
    legacy_manifest_hash_short: Optional[str] = None,
    store_dir: Optional[Path] = None,
) -> dict:
    """
    Chemin de production UNIQUE : dérive l'isolation depuis des faits
    Git observés (jamais depuis un argument booléen fourni par
    l'appelant — cette fonction n'accepte même pas un tel paramètre),
    calcule le manifeste SHA256 complet, publie atomiquement, recharge,
    vérifie. Échoue fermé si l'isolation ne peut pas être vérifiée —
    aucun enregistrement n'est créé dans ce cas.
    """
    if protected_scope_status != "CLEAN":
        return {
            "status": "REFUSED_PROTECTED_TARGET",
            "reason": "PROTECTED_SCOPE_STATUS_NOT_CLEAN",
            "context_id": None,
            "record": None,
        }

    isolation = derive_isolation_evidence(
        execution_worktree_path, branch_name, base_sha,
        target_path, target_pre_sha256, main_worktree_path,
    )
    if isolation["status"] != ISOLATION_VERIFIED:
        return {
            "status": ISOLATION_NOT_VERIFIED,
            "reason": isolation["reason"],
            "context_id": None,
            "record": None,
        }

    manifest_fields = {
        "repository_identity": repository_identity,
        "execution_worktree_path": str(Path(execution_worktree_path).resolve()),
        "branch_name": branch_name,
        "base_sha": base_sha,
        "source_kind": source_kind,
        "source_repository_identity": source_repository_identity,
        "source_commit": source_commit,
        "source_blob_sha": source_blob_sha,
        "source_path": source_path,
        "source_sha256": source_sha256,
        "target_path": target_path,
        "target_pre_sha256": target_pre_sha256,
        "operation": operation,
        "approved_scope": approved_scope,
        "protected_scope_status": protected_scope_status,
        "test_contract_hash": test_contract_hash,
        "schema_version": SCHEMA_VERSION,
    }
    manifest_sha256 = compute_manifest_sha256(manifest_fields)

    record: dict = {
        "context_schema_version": SCHEMA_VERSION,
        "created_at": _now(),
        "repository_identity": repository_identity,
        "repository_root": str(Path(main_worktree_path).resolve()),
        "execution_worktree_path": str(Path(execution_worktree_path).resolve()),
        "branch_name": branch_name,
        "base_sha": base_sha,
        "target_path": target_path,
        "target_pre_sha256": target_pre_sha256,
        "source_kind": source_kind,
        "source_repository_identity": source_repository_identity,
        "source_commit": source_commit,
        "source_blob_sha": source_blob_sha,
        "source_path": source_path,
        "source_sha256": source_sha256,
        "operation": operation,
        "approved_scope": approved_scope,
        "worktree_isolated": isolation["worktree_isolated"],
        "branch_isolated": isolation["branch_isolated"],
        "protected_scope_status": protected_scope_status,
        "manifest_sha256": manifest_sha256,
        "legacy_manifest_hash_short": legacy_manifest_hash_short,
        "decision_authority": DECISION_AUTHORITY,
    }
    record["context_id"] = f"pec-{hashlib.sha256(json.dumps({k: record.get(k) for k in _CONTEXT_BOUND_FIELDS if k not in ('context_schema_version','context_id','created_at')}, sort_keys=True).encode('utf-8')).hexdigest()[:32]}"
    record["context_record_hash"] = compute_context_record_hash(record)

    store_result = store_pre_execution_context_record(record, store_dir)
    reloaded = load_pre_execution_context_record(record["context_id"], store_dir)
    verify_ok, verify_reason = verify_pre_execution_context_record(reloaded)

    return {
        "status": STATUS_STORED if verify_ok else "VERIFY_FAILED",
        "context_id": record["context_id"],
        "store_result": store_result,
        "record": reloaded,
        "verify_ok": verify_ok,
        "verify_reason": verify_reason,
    }
