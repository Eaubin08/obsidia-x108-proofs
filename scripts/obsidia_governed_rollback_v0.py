"""
obsidia_governed_rollback_v0.py
==============================
GOVERNED_ROLLBACK_D2_V0 — exécuteur de rollback FAIL_CLOSED_RECOVERY_ACTION.

Restaure la cible d'une exécution bornée gouvernée à son état d'AVANT
l'application, UNIQUEMENT lorsque le classificateur D1 (recalculé ici,
jamais fourni par l'appelant) énonce MUST_ROLLBACK pour l'exécution
exacte, ET que :

  - la décision KX108_PRE est valide (phase PRE_EXECUTION, gate ALLOW,
    même execution_authority_hash recalculé, même approbation)
  - le déclencheur est soit une décision KX108_POST HOLD/BLOCK D1-liée à
    ce même PRE, soit un signal d'échec de pipeline canonique borné
  - l'ApplyReceipt et la RollbackEvidence recoupent la chaîne immuable
    (identité reconstruite depuis ExecutionEnvelope/EAH + KX108_PRE +
    KX108_POST ; les fichiers d'évidence restent des JSON mutables
    "legacy" — hachés au chargement, jamais traités comme autorité
    cryptographique : evidence_sealed = false)
  - la preimage A décode, hash et taille exacts
  - l'état courant de la cible == exactement l'état B produit par l'apply
  - le chemin cible + chaque composant parent sont sûrs (pas de lien
    symbolique / point de reparse Windows), re-vérifié juste avant
    os.replace (double garde TOCTOU)

Toute défaillance -> statut REFUSED_* / FAILED avec sémantique de
QUARANTAINE dans un RollbackResult IMMUABLE. D2 V0 NE MUTE NI
execution_status NI la closure NI le Family Wiring. Le rollback
N'INVOQUE JAMAIS KX108. Aucun caller de production n'est câblé.

D2 V0 : SINGLE_CHILD, REPLACE (operation_type=UPDATE_TARGET_FROM_SOURCE)
uniquement. CREATE / DELETE / multi-child hors périmètre.
"""
from __future__ import annotations

import base64
import datetime
import hashlib
import json
import os
import re
import stat
import sys
import time
from pathlib import Path
from typing import Optional

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import obsidia_batch_execution as _E
import obsidia_content_apply as _C
import obsidia_kx108_decision_store as _DS
import obsidia_post_execution_disposition_v0 as _DISP

DECISION_AUTHORITY = "KX108_ONLY"
RESULT_SCHEMA_VERSION = 1
OPERATION_TYPE = "UPDATE_TARGET_FROM_SOURCE"

ROLLBACK_RESULT_DIR = Path(os.environ.get("LOCALAPPDATA", "")) / "Obsidia" / "rollback_results"
_RESULT_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,128}$")
_SHA256_HEX_LEN = 64

# ── Statuts (aucun "ERROR" générique là où un état précis existe) ──────────
ROLLBACK_SUCCEEDED = "ROLLBACK_SUCCEEDED"
ALREADY_ROLLED_BACK = "ALREADY_ROLLED_BACK"
ROLLBACK_FAILED = "ROLLBACK_FAILED"
ROLLBACK_REFUSED_POST_STATE_DRIFT = "ROLLBACK_REFUSED_POST_STATE_DRIFT"
ROLLBACK_REFUSED_PATH_SAFETY = "ROLLBACK_REFUSED_PATH_SAFETY"
ROLLBACK_REFUSED_IDENTITY_MISMATCH = "ROLLBACK_REFUSED_IDENTITY_MISMATCH"
ROLLBACK_REFUSED_PREIMAGE_INVALID = "ROLLBACK_REFUSED_PREIMAGE_INVALID"
ROLLBACK_REFUSED_NOT_MUST_ROLLBACK = "ROLLBACK_REFUSED_NOT_MUST_ROLLBACK"
ROLLBACK_REFUSED_PRE_DECISION_INVALID = "ROLLBACK_REFUSED_PRE_DECISION_INVALID"
ROLLBACK_REFUSED_POST_DECISION_INVALID = "ROLLBACK_REFUSED_POST_DECISION_INVALID"
ROLLBACK_SUCCEEDED_RESULT_UNPERSISTED = "ROLLBACK_SUCCEEDED_RESULT_UNPERSISTED"

D2_ROLLBACK_STATUSES = frozenset({
    ROLLBACK_SUCCEEDED, ALREADY_ROLLED_BACK, ROLLBACK_FAILED,
    ROLLBACK_REFUSED_POST_STATE_DRIFT, ROLLBACK_REFUSED_PATH_SAFETY,
    ROLLBACK_REFUSED_IDENTITY_MISMATCH, ROLLBACK_REFUSED_PREIMAGE_INVALID,
    ROLLBACK_REFUSED_NOT_MUST_ROLLBACK, ROLLBACK_REFUSED_PRE_DECISION_INVALID,
    ROLLBACK_REFUSED_POST_DECISION_INVALID, ROLLBACK_SUCCEEDED_RESULT_UNPERSISTED,
})

_NON_QUARANTINE_STATUSES = frozenset({ROLLBACK_SUCCEEDED, ALREADY_ROLLED_BACK, ROLLBACK_SUCCEEDED_RESULT_UNPERSISTED})

TRIGGER_KX108_POST_DECISION = "KX108_POST_DECISION"
TRIGGER_POST_PIPELINE_FAILURE = "POST_PIPELINE_FAILURE"

_STORE_STATUS_STORED = "STORED"
_STORE_STATUS_IDEMPOTENT = "IDEMPOTENT_EXISTING_IDENTICAL"
_STORE_STATUS_IMMUTABILITY_VIOLATION = "IMMUTABILITY_VIOLATION"
_STORE_STATUS_INVALID_ID = "INVALID_ROLLBACK_RESULT_ID"

_REPARSE_ATTR = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _is_full_sha256(v) -> bool:
    return isinstance(v, str) and len(v) == _SHA256_HEX_LEN and all(c in "0123456789abcdef" for c in v.lower())


# ── RollbackResult : hash / identité / magasin immuable (modèle KX108 store) ──

_RESULT_BOUND_FIELDS = (
    "rollback_result_schema_version", "rollback_result_id", "created_at",
    "status", "reason",
    "batch_execution_id", "child_execution_id", "execution_authority_hash", "approval_id",
    "kx108_pre_decision_record_id", "kx108_pre_decision_record_hash",
    "rollback_trigger_type", "rollback_trigger_code",
    "kx108_post_decision_record_id", "kx108_post_decision_record_hash",
    "apply_receipt_sha256", "rollback_evidence_sha256",
    "target_path", "expected_post_sha256",
    "observed_before_rollback_sha256", "restored_pre_sha256", "observed_after_rollback_sha256",
    "preimage_size", "evidence_sealed", "decision_authority",
)
_IDENTITY_SEED_FIELDS = tuple(
    f for f in _RESULT_BOUND_FIELDS if f not in ("rollback_result_id", "created_at")
)


def compute_rollback_result_hash(record: dict) -> str:
    payload = json.dumps({k: record.get(k) for k in _RESULT_BOUND_FIELDS}, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _compute_rollback_result_identity(seed: dict) -> str:
    payload = json.dumps({k: seed.get(k) for k in _IDENTITY_SEED_FIELDS}, sort_keys=True)
    return f"rbk-{hashlib.sha256(payload.encode('utf-8')).hexdigest()[:32]}"


def _rollback_result_path(rollback_result_id: "str | None", store_dir: Optional[Path] = None) -> Path:
    if not rollback_result_id or not _RESULT_ID_RE.match(rollback_result_id):
        raise ValueError("INVALID_ROLLBACK_RESULT_ID")
    d = store_dir or ROLLBACK_RESULT_DIR
    return d / f"{rollback_result_id}.json"


def store_rollback_result(record: dict, store_dir: Optional[Path] = None) -> dict:
    """Publication ATOMIQUE immuable via os.link — jamais d'écrasement."""
    rid = record.get("rollback_result_id")
    try:
        p = _rollback_result_path(rid, store_dir)
    except ValueError:
        return {"status": _STORE_STATUS_INVALID_ID, "rollback_result_id": rid}
    payload = json.dumps(record, ensure_ascii=False, indent=2)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.parent / f".{p.name}.{os.getpid()}.{hashlib.sha256((payload + str(id(record))).encode('utf-8')).hexdigest()[:16]}.tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as fh:
            fh.write(payload)
            fh.flush()
            os.fsync(fh.fileno())
    except OSError:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass
        return {"status": ROLLBACK_FAILED, "reason": "RESULT_TEMP_WRITE_FAILED", "rollback_result_id": rid}
    try:
        os.link(tmp, p)
        return {"status": _STORE_STATUS_STORED, "rollback_result_id": rid}
    except FileExistsError:
        existing = p.read_text(encoding="utf-8")
        if existing == payload:
            return {"status": _STORE_STATUS_IDEMPOTENT, "rollback_result_id": rid}
        return {"status": _STORE_STATUS_IMMUTABILITY_VIOLATION, "rollback_result_id": rid}
    finally:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass


def load_rollback_result(rollback_result_id: str, store_dir: Optional[Path] = None) -> Optional[dict]:
    try:
        p = _rollback_result_path(rollback_result_id, store_dir)
    except ValueError:
        return None
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def verify_rollback_result(record: Optional[dict]) -> "tuple[bool, Optional[str]]":
    if record is None:
        return False, "ROLLBACK_RESULT_MISSING"
    if record.get("rollback_result_schema_version") != RESULT_SCHEMA_VERSION:
        return False, "ROLLBACK_RESULT_SCHEMA_UNSUPPORTED"
    for f in _RESULT_BOUND_FIELDS:
        if f not in record:
            return False, f"ROLLBACK_RESULT_FIELD_MISSING:{f}"
    if record.get("decision_authority") != DECISION_AUTHORITY:
        return False, "DECISION_AUTHORITY_NOT_KX108_ONLY"
    if record.get("status") not in D2_ROLLBACK_STATUSES:
        return False, "ROLLBACK_RESULT_STATUS_INVALID"
    if record.get("rollback_result_hash") != compute_rollback_result_hash(record):
        return False, "ROLLBACK_RESULT_HASH_MISMATCH"
    return True, None


# ── Sécurité de chemin (portable Windows : lstat + attribut de reparse) ────

def _is_unsafe_link_or_reparse(path: Path) -> bool:
    try:
        st = os.lstat(str(path))
    except OSError:
        return False  # inexistant : l'existence est gérée séparément
    if stat.S_ISLNK(st.st_mode):
        return True
    return bool(getattr(st, "st_file_attributes", 0) & _REPARSE_ATTR)


def _verify_no_reparse_on_path(repo_root: Path, target_literal: Path) -> "tuple[bool, Optional[str]]":
    """Chaque composant EXISTANT entre repo_root et target_literal.parent : pas de lien / reparse."""
    root = Path(repo_root).resolve()
    try:
        rel_parts = Path(target_literal).parent.relative_to(root).parts
    except ValueError:
        return False, "TARGET_PARENT_OUTSIDE_REPO"
    if _is_unsafe_link_or_reparse(root):
        return False, "REPO_ROOT_IS_REPARSE"
    cur = root
    for part in rel_parts:
        cur = cur / part
        if cur.exists() and _is_unsafe_link_or_reparse(cur):
            return False, f"PARENT_COMPONENT_REPARSE:{cur.name}"
    return True, None


# ── Lecture de hash cible (fonction dédiée pour l'isolation de test TOCTOU) ──

def _read_target_sha256(path: Path) -> "Optional[str]":
    try:
        if not path.exists() or not path.is_file():
            return None
        return _sha256_hex(path.read_bytes())
    except OSError:
        return None


# ── Restauration atomique dédiée (JAMAIS atomic_replace_with_bytes) ───────

def _atomic_restore(target_literal: Path, target_canonical: Path, preimage: bytes,
                    expected_pre_sha256: str, expected_post_sha256: str,
                    repo_root: Path) -> dict:
    """Retourne {status, reason, observed_after}. N'écrit la cible qu'après
    une 2e garde TOCTOU (état == expected_post_sha256) + re-vérification
    lien/reparse (cible + composants parent) immédiatement avant os.replace."""
    # (re)canonicalisation + re-lstat
    tgt_c, treason = _C.canonicalize_write_target(str(target_literal.relative_to(Path(repo_root).resolve())), repo_root)
    if treason or tgt_c is None or tgt_c != target_canonical:
        return {"status": ROLLBACK_REFUSED_PATH_SAFETY, "reason": f"RECANONICALIZE:{treason or 'PATH_CHANGED'}"}
    if _is_unsafe_link_or_reparse(target_literal):
        return {"status": ROLLBACK_REFUSED_PATH_SAFETY, "reason": "TARGET_IS_LINK_OR_REPARSE"}
    ok_p, reason_p = _verify_no_reparse_on_path(repo_root, target_literal)
    if not ok_p:
        return {"status": ROLLBACK_REFUSED_PATH_SAFETY, "reason": reason_p}

    tmp = target_literal.parent / f".{target_literal.name}.obsidia_rollback.{os.getpid()}.{hashlib.sha256(str(time.time_ns()).encode()).hexdigest()[:16]}.tmp"
    try:
        with open(tmp, "wb") as fh:
            fh.write(preimage)
            fh.flush()
            os.fsync(fh.fileno())
    except OSError:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass
        return {"status": ROLLBACK_FAILED, "reason": "TEMP_WRITE_FAILED"}

    try:
        if _sha256_hex(tmp.read_bytes()) != expected_pre_sha256:
            tmp.unlink(missing_ok=True)
            return {"status": ROLLBACK_FAILED, "reason": "TEMP_HASH_MISMATCH"}

        # 2e garde TOCTOU : la cible DOIT encore être exactement l'état B.
        if _read_target_sha256(target_literal) != expected_post_sha256:
            tmp.unlink(missing_ok=True)
            return {"status": ROLLBACK_REFUSED_POST_STATE_DRIFT, "reason": "DRIFT_BEFORE_REPLACE"}
        if _is_unsafe_link_or_reparse(target_literal):
            tmp.unlink(missing_ok=True)
            return {"status": ROLLBACK_REFUSED_PATH_SAFETY, "reason": "TARGET_BECAME_LINK_OR_REPARSE"}
        ok_p2, reason_p2 = _verify_no_reparse_on_path(repo_root, target_literal)
        if not ok_p2:
            tmp.unlink(missing_ok=True)
            return {"status": ROLLBACK_REFUSED_PATH_SAFETY, "reason": reason_p2}

        try:
            os.replace(str(tmp), str(target_literal))
        except OSError as exc:
            try:
                tmp.unlink(missing_ok=True)
            except OSError:
                pass
            return {"status": ROLLBACK_FAILED, "reason": f"ATOMIC_REPLACE_FAILED:{exc.__class__.__name__}"}
    finally:
        try:
            if tmp.exists():
                tmp.unlink(missing_ok=True)
        except OSError:
            pass

    observed_after = _read_target_sha256(target_literal)
    if observed_after != expected_pre_sha256:
        return {"status": ROLLBACK_FAILED, "reason": "POST_RESTORE_HASH_MISMATCH",
                "observed_after": observed_after}
    return {"status": ROLLBACK_SUCCEEDED, "reason": None, "observed_after": observed_after}


# ── Entrypoint ───────────────────────────────────────────────────────────

def _finalize(*, status, reason, ctx, observed_before=None, observed_after=None,
              rollback_result_dir=None) -> dict:
    """Construit + publie (immuable) le RollbackResult ; retourne le dict complet."""
    record = {
        "rollback_result_schema_version": RESULT_SCHEMA_VERSION,
        "created_at": _now(),
        "status": status,
        "reason": reason,
        "batch_execution_id": ctx.get("batch_execution_id"),
        "child_execution_id": ctx.get("child_execution_id"),
        "execution_authority_hash": ctx.get("execution_authority_hash"),
        "approval_id": ctx.get("approval_id"),
        "kx108_pre_decision_record_id": ctx.get("kx108_pre_decision_record_id"),
        "kx108_pre_decision_record_hash": ctx.get("kx108_pre_decision_record_hash"),
        "rollback_trigger_type": ctx.get("rollback_trigger_type"),
        "rollback_trigger_code": ctx.get("rollback_trigger_code"),
        "kx108_post_decision_record_id": ctx.get("kx108_post_decision_record_id"),
        "kx108_post_decision_record_hash": ctx.get("kx108_post_decision_record_hash"),
        "apply_receipt_sha256": ctx.get("apply_receipt_sha256"),
        "rollback_evidence_sha256": ctx.get("rollback_evidence_sha256"),
        "target_path": ctx.get("target_path"),
        "expected_post_sha256": ctx.get("expected_post_sha256"),
        "observed_before_rollback_sha256": observed_before,
        "restored_pre_sha256": ctx.get("restored_pre_sha256"),
        "observed_after_rollback_sha256": observed_after,
        "preimage_size": ctx.get("preimage_size"),
        "evidence_sealed": False,
        "decision_authority": DECISION_AUTHORITY,
    }
    seed = {k: record.get(k) for k in _IDENTITY_SEED_FIELDS}
    record["rollback_result_id"] = _compute_rollback_result_identity(seed)
    record["rollback_result_hash"] = compute_rollback_result_hash(record)

    store_res = store_rollback_result(record, rollback_result_dir)
    persisted = store_res.get("status") in (_STORE_STATUS_STORED, _STORE_STATUS_IDEMPOTENT)
    reloaded = load_rollback_result(record["rollback_result_id"], rollback_result_dir) if persisted else None

    final_status = status
    if status == ROLLBACK_SUCCEEDED and not persisted:
        # Vérité : la cible EST restaurée ; seul l'enregistrement a échoué.
        final_status = ROLLBACK_SUCCEEDED_RESULT_UNPERSISTED

    quarantine_required = final_status not in _NON_QUARANTINE_STATUSES
    return {
        "status": final_status,
        "reason": reason,
        "rollback_result_id": record["rollback_result_id"],
        "rollback_result": reloaded,
        "rollback_result_persisted": persisted,
        "store_result": store_res,
        "observed_before_rollback_sha256": observed_before,
        "observed_after_rollback_sha256": observed_after,
        "commit_review_eligible": False,
        "rollback_required": final_status not in (ROLLBACK_SUCCEEDED, ALREADY_ROLLED_BACK,
                                                  ROLLBACK_SUCCEEDED_RESULT_UNPERSISTED),
        "quarantine_required": quarantine_required,
        "kx108_invocations_during_rollback": 0,
        "evidence_sealed": False,
    }


def run_governed_rollback(
    child_execution_id: str,
    kx108_pre_decision_record_id: str,
    *,
    kx108_post_decision_record_id: Optional[str] = None,
    rollback_trigger_code: Optional[str] = None,
    execution_dir: Optional[Path] = None,
    evidence_dir: Optional[Path] = None,
    pre_decision_store_dir: Optional[Path] = None,
    post_decision_store_dir: Optional[Path] = None,
    rollback_result_dir: Optional[Path] = None,
    repo_root: Optional[Path] = None,
) -> dict:
    """
    FAIL_CLOSED_RECOVERY_ACTION. N'invoque JAMAIS KX108. Ne mute que la
    cible tmp/canonique via restauration atomique gardée ; JAMAIS
    execution_status / closure / Family Wiring / Ledger.
    L'appelant ne fournit que des identifiants + un déclencheur canonique.
    """
    root = Path(repo_root or _C._REPO_ROOT).resolve()
    ctx: dict = {"child_execution_id": child_execution_id,
                 "kx108_pre_decision_record_id": kx108_pre_decision_record_id}

    # 0. Forme du déclencheur : EXACTEMENT une.
    has_post = bool(kx108_post_decision_record_id and str(kx108_post_decision_record_id).strip())
    has_code = bool(rollback_trigger_code and str(rollback_trigger_code).strip())
    if has_post == has_code:
        return _finalize(status=ROLLBACK_REFUSED_NOT_MUST_ROLLBACK,
                         reason="TRIGGER_FORM_INVALID_EXACTLY_ONE_REQUIRED", ctx=ctx,
                         rollback_result_dir=rollback_result_dir)
    if has_code and str(rollback_trigger_code).strip() not in _DISP.CANONICAL_FAILURE_SIGNALS:
        return _finalize(status=ROLLBACK_REFUSED_NOT_MUST_ROLLBACK,
                         reason=f"ROLLBACK_TRIGGER_CODE_UNKNOWN:{rollback_trigger_code}", ctx=ctx,
                         rollback_result_dir=rollback_result_dir)

    # 1. KX108_PRE
    pre = _DS.load_kx108_decision_record(kx108_pre_decision_record_id, pre_decision_store_dir)
    if pre is None:
        return _finalize(status=ROLLBACK_REFUSED_PRE_DECISION_INVALID, reason="PRE_NOT_FOUND",
                         ctx=ctx, rollback_result_dir=rollback_result_dir)
    ok, r = _DS.verify_kx108_decision_record(pre)
    if not ok:
        return _finalize(status=ROLLBACK_REFUSED_PRE_DECISION_INVALID, reason=f"PRE_INVALID:{r}",
                         ctx=ctx, rollback_result_dir=rollback_result_dir)
    if _DS.decision_phase_of(pre) != _DS.PRE_DECISION_PHASE:
        return _finalize(status=ROLLBACK_REFUSED_PRE_DECISION_INVALID, reason="PRE_NOT_PRE_PHASE",
                         ctx=ctx, rollback_result_dir=rollback_result_dir)
    if pre.get("x108_gate") != "ALLOW":
        return _finalize(status=ROLLBACK_REFUSED_PRE_DECISION_INVALID, reason="PRE_GATE_NOT_ALLOW",
                         ctx=ctx, rollback_result_dir=rollback_result_dir)
    batch_execution_id = pre.get("batch_execution_id")
    approval_id = pre.get("approval_id")
    ctx.update({"batch_execution_id": batch_execution_id, "approval_id": approval_id,
                "kx108_pre_decision_record_hash": pre.get("decision_record_hash")})

    # 2. ExecutionEnvelope + EAH recalculé
    env = _E._load_execution(batch_execution_id, execution_dir)
    if env is None or not env.get("integrity_verified") or env.get("decision_authority") != DECISION_AUTHORITY:
        return _finalize(status=ROLLBACK_REFUSED_IDENTITY_MISMATCH, reason="EXECUTION_ENVELOPE_INVALID",
                         ctx=ctx, rollback_result_dir=rollback_result_dir)
    current_eah = _E.compute_execution_authority_hash(env)
    if current_eah != env.get("execution_authority_hash"):
        return _finalize(status=ROLLBACK_REFUSED_IDENTITY_MISMATCH, reason="EXECUTION_AUTHORITY_HASH_DRIFT",
                         ctx=ctx, rollback_result_dir=rollback_result_dir)
    ctx["execution_authority_hash"] = current_eah
    if pre.get("execution_authority_hash") != current_eah:
        return _finalize(status=ROLLBACK_REFUSED_PRE_DECISION_INVALID, reason="PRE_EAH_MISMATCH",
                         ctx=ctx, rollback_result_dir=rollback_result_dir)

    child = next((c for c in (env.get("children") or []) if c.get("child_execution_id") == child_execution_id), None)
    if child is None:
        return _finalize(status=ROLLBACK_REFUSED_IDENTITY_MISMATCH, reason="CHILD_NOT_FOUND",
                         ctx=ctx, rollback_result_dir=rollback_result_dir)
    if child.get("operation_type") != OPERATION_TYPE:
        return _finalize(status=ROLLBACK_REFUSED_IDENTITY_MISMATCH, reason="UNSUPPORTED_OPERATION",
                         ctx=ctx, rollback_result_dir=rollback_result_dir)
    if child.get("target_pre_sha256") is None:
        return _finalize(status=ROLLBACK_REFUSED_IDENTITY_MISMATCH, reason="NOT_REPLACE_CREATE_UNSUPPORTED",
                         ctx=ctx, rollback_result_dir=rollback_result_dir)

    # 3. HumanApproval
    approval = _E.load_approval_artifact(approval_id, execution_dir)
    if approval is None:
        return _finalize(status=ROLLBACK_REFUSED_IDENTITY_MISMATCH, reason="APPROVAL_NOT_FOUND",
                         ctx=ctx, rollback_result_dir=rollback_result_dir)
    ok_a, ra = _E.verify_approval_artifact(approval)
    if not ok_a:
        return _finalize(status=ROLLBACK_REFUSED_IDENTITY_MISMATCH, reason=f"APPROVAL_ARTIFACT_INVALID:{ra}",
                         ctx=ctx, rollback_result_dir=rollback_result_dir)
    ok_v, rv = _E._validate_approval(approval, env)
    if not ok_v or approval.get("execution_authority_hash") != current_eah:
        return _finalize(status=ROLLBACK_REFUSED_IDENTITY_MISMATCH, reason=f"APPROVAL_NOT_BOUND:{rv}",
                         ctx=ctx, rollback_result_dir=rollback_result_dir)

    # 4. Déclencheur + recalcul de disposition D1 (jamais fourni par l'appelant)
    pre_hash = pre.get("decision_record_hash")
    if has_post:
        pid = str(kx108_post_decision_record_id).strip()
        post = _DS.load_kx108_decision_record(pid, post_decision_store_dir)
        if post is None:
            return _finalize(status=ROLLBACK_REFUSED_POST_DECISION_INVALID, reason="POST_NOT_FOUND",
                             ctx=ctx, rollback_result_dir=rollback_result_dir)
        ok_p, rp = _DS.verify_kx108_decision_record(post)
        if not ok_p:
            return _finalize(status=ROLLBACK_REFUSED_POST_DECISION_INVALID, reason=f"POST_INVALID:{rp}",
                             ctx=ctx, rollback_result_dir=rollback_result_dir)
        if (_DS.decision_phase_of(post) != _DS.POST_DECISION_PHASE
                or post.get("execution_authority_hash") != current_eah
                or post.get("approval_id") != approval_id
                or post.get("kx108_pre_decision_record_id") != kx108_pre_decision_record_id
                or post.get("kx108_pre_decision_record_hash") != pre_hash):
            return _finalize(status=ROLLBACK_REFUSED_POST_DECISION_INVALID, reason="POST_NOT_LINKED_TO_PRE",
                             ctx=ctx, rollback_result_dir=rollback_result_dir)
        if post.get("x108_gate") not in ("HOLD", "BLOCK"):
            return _finalize(status=ROLLBACK_REFUSED_NOT_MUST_ROLLBACK, reason=f"POST_GATE_{post.get('x108_gate')}",
                             ctx=ctx, rollback_result_dir=rollback_result_dir)
        disp = _DISP.classify_post_execution_disposition(post_decision_record_id=pid,
                                                         post_decision_store_dir=post_decision_store_dir)
        ctx.update({"rollback_trigger_type": TRIGGER_KX108_POST_DECISION,
                    "rollback_trigger_code": post.get("x108_gate"),
                    "kx108_post_decision_record_id": pid,
                    "kx108_post_decision_record_hash": post.get("decision_record_hash")})
    else:
        code = str(rollback_trigger_code).strip()
        disp = _DISP.classify_post_execution_disposition(failure_signal=code)
        ctx.update({"rollback_trigger_type": TRIGGER_POST_PIPELINE_FAILURE,
                    "rollback_trigger_code": code,
                    "kx108_post_decision_record_id": None,
                    "kx108_post_decision_record_hash": None})

    if disp.get("disposition") != _DISP.MUST_ROLLBACK:
        return _finalize(status=ROLLBACK_REFUSED_NOT_MUST_ROLLBACK,
                         reason=f"DISPOSITION_{disp.get('disposition')}", ctx=ctx,
                         rollback_result_dir=rollback_result_dir)

    # 5. ApplyReceipt — octets exacts hachés au chargement + recoupements sémantiques
    receipt_path = _C._apply_receipt_path(child_execution_id, evidence_dir)
    if not receipt_path.exists():
        return _finalize(status=ROLLBACK_REFUSED_IDENTITY_MISMATCH, reason="APPLY_RECEIPT_NOT_FOUND",
                         ctx=ctx, rollback_result_dir=rollback_result_dir)
    try:
        receipt_bytes = receipt_path.read_bytes()
        receipt = json.loads(receipt_bytes.decode("utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return _finalize(status=ROLLBACK_REFUSED_IDENTITY_MISMATCH, reason="APPLY_RECEIPT_UNPARSEABLE",
                         ctx=ctx, rollback_result_dir=rollback_result_dir)
    ctx["apply_receipt_sha256"] = _sha256_hex(receipt_bytes)
    target_path = child.get("target_path")
    if (receipt.get("status") != "CONTENT_APPLIED"
            or receipt.get("child_execution_id") != child_execution_id
            or receipt.get("batch_execution_id") != batch_execution_id
            or receipt.get("target_path") != target_path
            or receipt.get("operation_type") != OPERATION_TYPE
            or receipt.get("decision_authority") != DECISION_AUTHORITY
            or receipt.get("source_full_sha256") != child.get("source_content_sha256")
            or receipt.get("target_pre_sha256") != child.get("target_pre_sha256")
            or not _is_full_sha256(receipt.get("target_post_sha256"))):
        return _finalize(status=ROLLBACK_REFUSED_IDENTITY_MISMATCH, reason="APPLY_RECEIPT_CROSS_LINK_MISMATCH",
                         ctx=ctx, rollback_result_dir=rollback_result_dir)
    expected_post = receipt["target_post_sha256"]
    ctx.update({"target_path": target_path, "expected_post_sha256": expected_post})

    # 6. RollbackEvidence — octets exacts hachés au chargement + recoupements
    evidence_path = _C._rollback_evidence_path(child_execution_id, evidence_dir)
    if not evidence_path.exists():
        return _finalize(status=ROLLBACK_REFUSED_IDENTITY_MISMATCH, reason="ROLLBACK_EVIDENCE_NOT_FOUND",
                         ctx=ctx, rollback_result_dir=rollback_result_dir)
    try:
        evidence_bytes = evidence_path.read_bytes()
        evidence = json.loads(evidence_bytes.decode("utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return _finalize(status=ROLLBACK_REFUSED_IDENTITY_MISMATCH, reason="ROLLBACK_EVIDENCE_UNPARSEABLE",
                         ctx=ctx, rollback_result_dir=rollback_result_dir)
    ctx["rollback_evidence_sha256"] = _sha256_hex(evidence_bytes)
    if (evidence.get("child_execution_id") != child_execution_id
            or evidence.get("batch_execution_id") != batch_execution_id
            or evidence.get("target_path") != target_path
            or evidence.get("operation_type") != OPERATION_TYPE
            or evidence.get("decision_authority") != DECISION_AUTHORITY):
        return _finalize(status=ROLLBACK_REFUSED_IDENTITY_MISMATCH, reason="ROLLBACK_EVIDENCE_CROSS_LINK_MISMATCH",
                         ctx=ctx, rollback_result_dir=rollback_result_dir)

    # 7. Intégrité de la preimage
    b64 = evidence.get("pre_write_bytes_b64")
    pre_write_sha256 = evidence.get("pre_write_sha256")
    pre_write_size = evidence.get("pre_write_size")
    if not b64 or not _is_full_sha256(pre_write_sha256) or pre_write_size is None:
        return _finalize(status=ROLLBACK_REFUSED_PREIMAGE_INVALID, reason="PREIMAGE_FIELDS_MISSING",
                         ctx=ctx, rollback_result_dir=rollback_result_dir)
    try:
        preimage = base64.b64decode(b64, validate=True)
    except (ValueError, base64.binascii.Error):
        return _finalize(status=ROLLBACK_REFUSED_PREIMAGE_INVALID, reason="PREIMAGE_BASE64_INVALID",
                         ctx=ctx, rollback_result_dir=rollback_result_dir)
    if _sha256_hex(preimage) != pre_write_sha256:
        return _finalize(status=ROLLBACK_REFUSED_PREIMAGE_INVALID, reason="PREIMAGE_SHA256_MISMATCH",
                         ctx=ctx, rollback_result_dir=rollback_result_dir)
    if len(preimage) != pre_write_size:
        return _finalize(status=ROLLBACK_REFUSED_PREIMAGE_INVALID, reason="PREIMAGE_SIZE_MISMATCH",
                         ctx=ctx, rollback_result_dir=rollback_result_dir)
    if pre_write_sha256 != receipt.get("target_pre_sha256"):
        return _finalize(status=ROLLBACK_REFUSED_PREIMAGE_INVALID, reason="PREIMAGE_NEQ_RECEIPT_TARGET_PRE",
                         ctx=ctx, rollback_result_dir=rollback_result_dir)
    ctx.update({"preimage_size": pre_write_size, "restored_pre_sha256": pre_write_sha256})

    # 8. Identité + sécurité du chemin cible
    if evidence.get("target_path") != target_path or receipt.get("target_path") != target_path:
        return _finalize(status=ROLLBACK_REFUSED_IDENTITY_MISMATCH, reason="TARGET_PATH_DIVERGENCE",
                         ctx=ctx, rollback_result_dir=rollback_result_dir)
    target_canonical, treason = _C.canonicalize_write_target(target_path, root)
    if treason or target_canonical is None:
        return _finalize(status=ROLLBACK_REFUSED_PATH_SAFETY, reason=f"CANONICALIZE:{treason}",
                         ctx=ctx, rollback_result_dir=rollback_result_dir)
    target_literal = (root / Path(str(target_path).replace("\\", "/"))).resolve() if False else (root / Path(str(target_path).replace("\\", "/")))
    try:
        target_literal.relative_to(root)
    except ValueError:
        return _finalize(status=ROLLBACK_REFUSED_PATH_SAFETY, reason="TARGET_LITERAL_OUTSIDE_REPO",
                         ctx=ctx, rollback_result_dir=rollback_result_dir)
    if target_literal.exists() and target_literal.is_dir():
        return _finalize(status=ROLLBACK_REFUSED_PATH_SAFETY, reason="TARGET_IS_DIRECTORY",
                         ctx=ctx, rollback_result_dir=rollback_result_dir)
    if _is_unsafe_link_or_reparse(target_literal):
        return _finalize(status=ROLLBACK_REFUSED_PATH_SAFETY, reason="TARGET_IS_LINK_OR_REPARSE",
                         ctx=ctx, rollback_result_dir=rollback_result_dir)
    ok_par, reason_par = _verify_no_reparse_on_path(root, target_literal)
    if not ok_par:
        return _finalize(status=ROLLBACK_REFUSED_PATH_SAFETY, reason=reason_par,
                         ctx=ctx, rollback_result_dir=rollback_result_dir)

    # 9. Garde d'état courant (fail-closed)
    observed_before = _read_target_sha256(target_literal)
    if observed_before == pre_write_sha256:
        return _finalize(status=ALREADY_ROLLED_BACK, reason="TARGET_ALREADY_AT_PREIMAGE",
                         ctx=ctx, observed_before=observed_before, observed_after=observed_before,
                         rollback_result_dir=rollback_result_dir)
    if observed_before != expected_post:
        return _finalize(status=ROLLBACK_REFUSED_POST_STATE_DRIFT,
                         reason="CURRENT_TARGET_NEITHER_POST_NOR_PRE", ctx=ctx,
                         observed_before=observed_before, rollback_result_dir=rollback_result_dir)

    # 10. Restauration atomique gardée (double TOCTOU + re-check reparse)
    restore = _atomic_restore(target_literal, target_canonical, preimage,
                              pre_write_sha256, expected_post, root)
    return _finalize(status=restore["status"], reason=restore.get("reason"), ctx=ctx,
                     observed_before=observed_before, observed_after=restore.get("observed_after"),
                     rollback_result_dir=rollback_result_dir)
