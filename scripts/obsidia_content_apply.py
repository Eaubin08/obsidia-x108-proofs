"""
obsidia_content_apply.py
=========================
GENERIC_SOURCE_CONTENT_APPLY_BRIDGE_V0 — pont borné source -> cible.

Ce module N'EST PAS souverain. Il ne decide jamais si un travail doit
avoir lieu — il execute une operation de contenu deja pleinement
autorisee EN AMONT (Ledger -> BatchProposal -> approbation humaine
stockee -> integrite d'execution), sur EXACTEMENT une cible explicite.

Chaine complete (rappel, pour memoire — ce module se situe entre la
precondition de cible et les tests/KX108) :

    source Ledger
    -> BatchProposal
    -> artefact d'approbation humaine stocke
    -> enveloppe d'execution
    -> gate d'integrite de source
    -> gate de precondition de cible
    -> PONT DE CONTENU BORNE (ce module)
    -> tests/preuves
    -> KX108
    -> ACT/HOLD/BLOCK
    -> revue humaine de commit

AUTORITE :
  CAN_READ_SOURCE = TRUE     CAN_WRITE_ONE_TARGET = TRUE (si autorise)
  CAN_DECIDE      = FALSE    CAN_EMIT_ACT         = FALSE
  CAN_COMMIT      = FALSE    CAN_PUSH             = FALSE

decision_authority = KX108_ONLY

Une application de contenu reussie (CONTENT_APPLIED) n'est JAMAIS un
ACT. Le contenu peut etre applique localement puis rejete par KX108
apres tests — ce module ne fabrique jamais kx108_decision.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import os
import time
from pathlib import Path
from typing import Optional

SCHEMA_VERSION = "V0"
DECISION_AUTHORITY = "KX108_ONLY"

APPLY_EVIDENCE_DIR = Path(os.environ.get("LOCALAPPDATA", "")) / "Obsidia" / "content_apply"

_REPO_ROOT = Path(__file__).resolve().parent.parent

SUPPORTED_OPERATIONS = frozenset(["UPDATE_TARGET_FROM_SOURCE"])

# ─── Statuts (fail-closed, explicites) ───────────────────────────────────────

CONTENT_APPLY_READY        = "CONTENT_APPLY_READY"
SOURCE_INTEGRITY_MISMATCH  = "SOURCE_INTEGRITY_MISMATCH"
TARGET_PRECONDITION_MISMATCH = "TARGET_PRECONDITION_MISMATCH"
REFUSED_PROTECTED_TARGET   = "REFUSED_PROTECTED_TARGET"
UNSUPPORTED_OPERATION      = "UNSUPPORTED_OPERATION"
TEMP_WRITE_FAILED          = "TEMP_WRITE_FAILED"
TEMP_HASH_MISMATCH         = "TEMP_HASH_MISMATCH"
ATOMIC_REPLACE_FAILED      = "ATOMIC_REPLACE_FAILED"
POST_WRITE_HASH_MISMATCH   = "POST_WRITE_HASH_MISMATCH"
CONTENT_APPLIED            = "CONTENT_APPLIED"
ROLLBACK_EVIDENCE_FAILED   = "ROLLBACK_EVIDENCE_FAILED"
ALREADY_APPLIED_SAME_CONTENT = "ALREADY_APPLIED_SAME_CONTENT"
SCOPE_MISMATCH             = "SCOPE_MISMATCH"
BATCH_BINDING_MISMATCH     = "BATCH_BINDING_MISMATCH"
APPROVAL_INVALID           = "APPROVAL_INVALID"
ENVELOPE_NOT_FOUND         = "ENVELOPE_NOT_FOUND"
CHILD_NOT_FOUND            = "CHILD_NOT_FOUND"
CHILD_NOT_READY            = "CHILD_NOT_READY"


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _sha16(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _full_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _batch_execution_module():
    import sys as _sys
    _scripts = str(Path(__file__).resolve().parent)
    if _scripts not in _sys.path:
        _sys.path.insert(0, _scripts)
    import obsidia_batch_execution as _mod
    return _mod


def _ledger_module():
    import sys as _sys
    _scripts = str(Path(__file__).resolve().parent)
    if _scripts not in _sys.path:
        _sys.path.insert(0, _scripts)
    import obsidia_branching_ledger as _mod
    return _mod


def _selector_module():
    import sys as _sys
    _scripts = str(Path(__file__).resolve().parent)
    if _scripts not in _sys.path:
        _sys.path.insert(0, _scripts)
    import obsidia_batch_selector as _mod
    return _mod


# ─── Resolution de la source — lecture reelle, jamais fabriquee ─────────────

def resolve_source_bytes(child: dict, repo_root: Path) -> "tuple[Optional[bytes], Optional[str]]":
    """
    Retourne (octets_source, raison_echec). octets_source est None si la
    resolution echoue pour QUELQUE raison que ce soit (fail-closed) —
    jamais d'octets partiels/fabriques.

    FILESYSTEM_FILE : lecture disque reelle de source_path (relatif a
    repo_root).

    GIT_BLOB : lecture IMMUABLE via (source_git_commit_sha,
    source_git_historical_path) enregistres — jamais une branche/ref
    mutable, jamais le chemin filesystem courant. Verifie le blob_sha
    resolu au commit exact, PUIS le SHA256 complet des octets lus,
    contre les valeurs enregistrees sur le child.
    """
    source_kind = child.get("source_kind") or "FILESYSTEM_FILE"

    if source_kind == "FILESYSTEM_FILE":
        path_str = child.get("source_path")
        if not path_str:
            return None, "SOURCE_PATH_MISSING"
        p = Path(path_str)
        if not p.is_absolute():
            p = repo_root / path_str
        if not p.exists() or not p.is_file():
            return None, "SOURCE_FILE_MISSING"
        try:
            data = p.read_bytes()
        except OSError:
            return None, "SOURCE_FILE_UNREADABLE"
        expected_hash16 = child.get("source_hash")
        if expected_hash16 and _full_sha256(data)[:16] != expected_hash16:
            return None, "SOURCE_INTEGRITY_MISMATCH"
        return data, None

    if source_kind == "GIT_BLOB":
        commit_sha = child.get("source_git_commit_sha")
        historical_path = child.get("source_git_historical_path")
        expected_blob_sha = child.get("source_git_blob_sha")
        expected_full_sha256 = child.get("source_content_sha256")
        expected_repo_identity = child.get("source_repository_identity")
        if not commit_sha or not historical_path:
            return None, "GIT_SOURCE_FIELDS_MISSING"

        actual_repo_identity = str(repo_root.resolve())
        if expected_repo_identity and expected_repo_identity != actual_repo_identity:
            return None, "SOURCE_REPOSITORY_IDENTITY_MISMATCH"

        led = _ledger_module()
        blob_sha = led._git_blob_sha_at_commit(repo_root, commit_sha, historical_path)
        if not blob_sha or (expected_blob_sha and blob_sha != expected_blob_sha):
            return None, "GIT_SOURCE_BLOB_SHA_MISMATCH"

        blob_bytes = led._git_read_blob_bytes(repo_root, blob_sha)
        if blob_bytes is None:
            return None, "GIT_SOURCE_BLOB_UNREADABLE"

        full_sha256 = _full_sha256(blob_bytes)
        if expected_full_sha256 and full_sha256 != expected_full_sha256:
            return None, "GIT_SOURCE_FULL_SHA256_MISMATCH"

        return blob_bytes, None

    return None, f"UNSUPPORTED_SOURCE_KIND:{source_kind}"


# ─── Validation de la cible d'ecriture — canonique, jamais historical_path ──

def canonicalize_write_target(
    target_path: "str | None", repo_root: Optional[Path] = None,
) -> "tuple[Optional[Path], Optional[str]]":
    """
    Chemin d'ecriture ABSOLU, canonique, ancre a repo_root (par defaut le
    depot Obsidia canonique _REPO_ROOT en production) — jamais derive de
    historical_path. Rejette vide, wildcard, hors-depot, racine du depot,
    cible protegee. N'exige pas que la cible existe deja (une cible
    absente est un etat valide, gere separement par la precondition).

    Le confinement (hors-namespace) est verifie contre repo_root — le
    MEME depot que celui dans lequel l'ecriture aura effectivement lieu
    (jamais d'autorite scindee). Le statut PROTEGE reste toujours ancre
    au depot Obsidia canonique (_REPO_ROOT) : une invariante globale de
    CE depot, sans effet sur un depot synthetique de test distinct.
    """
    root = repo_root or _REPO_ROOT
    if not target_path or not str(target_path).strip():
        return None, "TARGET_EMPTY"
    raw = str(target_path).strip()
    if "*" in raw or "?" in raw:
        return None, "TARGET_WILDCARD_REJECTED"
    norm = raw.replace("\\", "/")
    if norm.startswith("/") or (len(norm) > 1 and norm[1] == ":"):
        candidate = Path(raw).resolve()
    else:
        candidate = (root / norm).resolve()
    try:
        rel = candidate.relative_to(root.resolve())
    except ValueError:
        return None, "TARGET_OUTSIDE_REPO_NAMESPACE"
    if rel.as_posix() == ".":
        return None, "TARGET_REPO_ROOT_REJECTED"

    led = _ledger_module()
    if led._is_protected_resolved((_REPO_ROOT / rel).resolve()):
        return None, "REFUSED_PROTECTED_TARGET"

    return candidate, None


# ─── Ecriture atomique bas niveau (aide de test / primitive interne) ────────

def atomic_replace_with_bytes(
    target_abs: Path,
    content: bytes,
    expected_target_pre_sha256: "Optional[str]",
) -> dict:
    """
    Primitive PURE d'ecriture atomique — aucune verification d'approbation,
    de batch, ni de portee. Reservee a un appelant deja entierement
    autorise (apply_validated_source_content), ou a des tests unitaires
    exercant directement la mecanique d'ecriture sur une cible temporaire.

    Garde TOCTOU immediate : relit la cible juste avant l'ecriture et
    compare a expected_target_pre_sha256 (None = cible doit rester
    absente). Ecrit dans un fichier temporaire frere (meme repertoire,
    meme systeme de fichiers) puis remplace atomiquement via os.replace.
    Verifie le hash du temporaire AVANT remplacement, et le hash de la
    cible APRES remplacement. Nettoie systematiquement le temporaire.
    """
    # Recheck TOCTOU immediat.
    if target_abs.exists():
        try:
            current_bytes = target_abs.read_bytes()
        except OSError:
            return {"status": TARGET_PRECONDITION_MISMATCH, "reason": "TARGET_UNREADABLE"}
        current_hash = _full_sha256(current_bytes)
    else:
        current_hash = None

    if current_hash != expected_target_pre_sha256:
        return {
            "status": TARGET_PRECONDITION_MISMATCH,
            "expected_target_pre_sha256": expected_target_pre_sha256,
            "actual_target_sha256": current_hash,
        }

    expected_sha256 = _full_sha256(content)
    tmp = target_abs.parent / f".{target_abs.name}.obsidia_apply.{os.getpid()}.{_sha16(str(time.time_ns()))}.tmp"

    try:
        _ensure_dir(target_abs.parent)
        with open(tmp, "wb") as fh:
            fh.write(content)
            fh.flush()
            os.fsync(fh.fileno())
    except OSError:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass
        return {"status": TEMP_WRITE_FAILED}

    try:
        tmp_bytes = tmp.read_bytes()
    except OSError:
        tmp.unlink(missing_ok=True)
        return {"status": TEMP_WRITE_FAILED}

    if _full_sha256(tmp_bytes) != expected_sha256:
        tmp.unlink(missing_ok=True)
        return {"status": TEMP_HASH_MISMATCH}

    try:
        os.replace(tmp, target_abs)
    except OSError:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass
        return {"status": ATOMIC_REPLACE_FAILED}

    try:
        post_bytes = target_abs.read_bytes()
    except OSError:
        return {"status": POST_WRITE_HASH_MISMATCH, "reason": "TARGET_UNREADABLE_AFTER_REPLACE"}

    post_sha256 = _full_sha256(post_bytes)
    if post_sha256 != expected_sha256:
        return {
            "status": POST_WRITE_HASH_MISMATCH,
            "expected_sha256": expected_sha256,
            "actual_sha256": post_sha256,
        }

    return {
        "status": CONTENT_APPLIED,
        "target_pre_sha256": expected_target_pre_sha256,
        "target_post_sha256": post_sha256,
        "bytes_written": len(content),
    }


# ─── Preuve de rollback ──────────────────────────────────────────────────────

def _rollback_evidence_path(child_execution_id: str, evidence_dir: Optional[Path] = None) -> Path:
    d = evidence_dir or APPLY_EVIDENCE_DIR
    return d / "rollback" / f"{child_execution_id}.json"


def _save_rollback_evidence(record: dict, evidence_dir: Optional[Path] = None) -> "tuple[bool, Optional[Path]]":
    p = _rollback_evidence_path(record["child_execution_id"], evidence_dir)
    try:
        _ensure_dir(p.parent)
        p.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        return True, p
    except OSError:
        return False, None


def load_rollback_evidence(child_execution_id: str, evidence_dir: Optional[Path] = None) -> Optional[dict]:
    p = _rollback_evidence_path(child_execution_id, evidence_dir)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _apply_receipt_path(child_execution_id: str, evidence_dir: Optional[Path] = None) -> Path:
    d = evidence_dir or APPLY_EVIDENCE_DIR
    return d / "receipts" / f"{child_execution_id}.json"


def _save_apply_receipt(record: dict, evidence_dir: Optional[Path] = None) -> None:
    p = _apply_receipt_path(record["child_execution_id"], evidence_dir)
    _ensure_dir(p.parent)
    p.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")


def load_apply_receipt(child_execution_id: str, evidence_dir: Optional[Path] = None) -> Optional[dict]:
    p = _apply_receipt_path(child_execution_id, evidence_dir)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


# ─── Orchestration complete — production, derriere approbation ─────────────

def apply_validated_source_content(
    batch_execution_id: str,
    child_execution_id: str,
    approval_id: str,
    execution_dir: Optional[Path] = None,
    selector_dir: Optional[Path] = None,
    ledger_dir: Optional[Path] = None,
    repo_root: Optional[Path] = None,
    evidence_dir: Optional[Path] = None,
) -> dict:
    """
    Chemin de PRODUCTION unique. Refuse d'ecrire sans :
      - enveloppe d'execution existante et integrity_verified
      - artefact d'approbation CHARGE depuis le magasin canonique (jamais
        un dict fourni par l'appelant) et valide contre l'enveloppe
      - BatchProposal d'origine relu et reverifie (verify_batch_integrity)
      - enfant PLANNED, operation supportee, cible non protegee
      - source relue MAINTENANT (TOCTOU) et conforme
      - cible relue MAINTENANT (TOCTOU) et conforme a la precondition

    Ne fabrique JAMAIS kx108_decision. Une application reussie
    (CONTENT_APPLIED) n'est PAS un ACT.
    """
    root = repo_root or _REPO_ROOT
    E = _batch_execution_module()
    S = _selector_module()

    envelope = E._load_execution(batch_execution_id, execution_dir)
    if envelope is None:
        return {"status": ENVELOPE_NOT_FOUND, "batch_execution_id": batch_execution_id}
    if not envelope.get("integrity_verified"):
        return {"status": ENVELOPE_NOT_FOUND, "reason": "ENVELOPE_INTEGRITY_NOT_VERIFIED"}

    approval = E.load_approval_artifact(approval_id, execution_dir) if approval_id else None
    ok, reason = E._validate_approval(approval, envelope)
    if not ok:
        return {"status": APPROVAL_INVALID, "reason": reason}

    child = next(
        (c for c in envelope.get("children", []) if c.get("child_execution_id") == child_execution_id),
        None,
    )
    if child is None:
        return {"status": CHILD_NOT_FOUND, "child_execution_id": child_execution_id}
    if child.get("execution_status") != E.PLANNED:
        return {"status": CHILD_NOT_READY, "actual_execution_status": child.get("execution_status")}

    # Liaison au batch immuable d'origine — toute derive (cible, provenance
    # Git complete, intention d'operation, ordre...) refuse l'ecriture.
    proposal = S._load_batch(envelope.get("batch_id"), selector_dir)
    if proposal is None:
        return {"status": BATCH_BINDING_MISMATCH, "reason": "PROPOSAL_NOT_FOUND"}
    if proposal.get("batch_hash") != envelope.get("batch_hash"):
        return {"status": BATCH_BINDING_MISMATCH, "reason": "BATCH_HASH_MISMATCH"}
    integrity_ok, integrity_reason = E.verify_batch_integrity(proposal, ledger_dir)
    if not integrity_ok:
        return {"status": BATCH_BINDING_MISMATCH, "reason": integrity_reason}

    operation_type = child.get("operation_type")
    if operation_type not in SUPPORTED_OPERATIONS:
        return {"status": UNSUPPORTED_OPERATION, "operation_type": operation_type}

    target_abs, target_reason = canonicalize_write_target(child.get("target_path"), root)
    if target_reason == "REFUSED_PROTECTED_TARGET":
        return {"status": REFUSED_PROTECTED_TARGET, "target_path": child.get("target_path")}
    if target_reason:
        return {"status": SCOPE_MISMATCH, "reason": target_reason, "target_path": child.get("target_path")}

    # Portee : le chemin canonicalise doit correspondre EXACTEMENT au
    # target_path porte par le child issu du BatchProposal approuve —
    # aucune substitution de cible n'est jamais tolérée.
    expected_target_abs, _ = canonicalize_write_target(
        next(
            (c.get("target_path") for c in proposal.get("selected_entries", [])
             if c.get("candidate_id") == child.get("candidate_entry_id")),
            None,
        ),
        root,
    )
    if expected_target_abs is None or expected_target_abs != target_abs:
        return {"status": SCOPE_MISMATCH, "reason": "TARGET_NOT_IN_APPROVED_SCOPE"}

    # Source TOCTOU — relue MAINTENANT, jamais reutilisee depuis un cache.
    source_bytes, source_reason = resolve_source_bytes(child, root)
    if source_bytes is None:
        return {"status": SOURCE_INTEGRITY_MISMATCH, "reason": source_reason}
    source_full_sha256 = _full_sha256(source_bytes)

    # Precondition de cible relue MAINTENANT (TOCTOU) — jamais reutilisee
    # depuis prepare_execution.
    if target_abs.exists():
        try:
            current_bytes = target_abs.read_bytes()
        except OSError:
            return {"status": TARGET_PRECONDITION_MISMATCH, "reason": "TARGET_UNREADABLE"}
        current_target_sha256 = _full_sha256(current_bytes)
    else:
        current_target_sha256 = None
        current_bytes = None

    # Idempotence — verifiee AVANT la precondition stricte : un rejeu
    # exact du meme child, apres un CONTENT_APPLIED anterieur reussi avec
    # la meme source et ayant deja convergé vers ces octets exacts, ne
    # doit jamais etre refuse comme une "derive" — la cible EST l'etat
    # attendu apres application. Compare le receipt anterieur (source +
    # octets post-ecriture) a l'etat courant, jamais a la precondition
    # pre-ecriture (qui a change PAR CONSTRUCTION lors du premier apply).
    prior_receipt = load_apply_receipt(child_execution_id, evidence_dir)
    if (
        prior_receipt
        and prior_receipt.get("status") == CONTENT_APPLIED
        and prior_receipt.get("source_full_sha256") == source_full_sha256
        and prior_receipt.get("target_post_sha256") == current_target_sha256
        and current_target_sha256 == source_full_sha256
    ):
        return {
            "status": ALREADY_APPLIED_SAME_CONTENT,
            "child_execution_id": child_execution_id,
            "target_post_sha256": current_target_sha256,
        }

    expected_pre_hash16 = child.get("target_pre_hash")
    actual_pre_hash16 = current_target_sha256[:16] if current_target_sha256 else None
    if actual_pre_hash16 != expected_pre_hash16:
        return {
            "status": TARGET_PRECONDITION_MISMATCH,
            "expected_target_pre_hash": expected_pre_hash16,
            "actual_target_pre_hash": actual_pre_hash16,
        }

    # Preuve de rollback AVANT toute ecriture.
    rollback_record = {
        "schema_version": SCHEMA_VERSION,
        "child_execution_id": child_execution_id,
        "batch_execution_id": batch_execution_id,
        "target_path": child.get("target_path"),
        "pre_write_sha256": current_target_sha256,
        "pre_write_size": len(current_bytes) if current_bytes is not None else None,
        "pre_write_bytes_b64": __import__("base64").b64encode(current_bytes).decode("ascii") if current_bytes is not None else None,
        "timestamp": _now(),
        "source_kind": child.get("source_kind"),
        "source_identity": {
            "source_git_commit_sha": child.get("source_git_commit_sha"),
            "source_git_blob_sha": child.get("source_git_blob_sha"),
            "source_git_historical_path": child.get("source_git_historical_path"),
            "source_path": child.get("source_path"),
        },
        "operation_type": operation_type,
        "decision_authority": DECISION_AUTHORITY,
    }
    saved, _p = _save_rollback_evidence(rollback_record, evidence_dir)
    if not saved:
        return {"status": ROLLBACK_EVIDENCE_FAILED}

    write_result = atomic_replace_with_bytes(target_abs, source_bytes, current_target_sha256)

    receipt = {
        "schema_version": SCHEMA_VERSION,
        "child_execution_id": child_execution_id,
        "batch_execution_id": batch_execution_id,
        "batch_id": envelope.get("batch_id"),
        "target_path": child.get("target_path"),
        "target_pre_sha256": current_target_sha256,
        "source_full_sha256": source_full_sha256,
        "target_post_sha256": write_result.get("target_post_sha256"),
        "bytes_written": write_result.get("bytes_written"),
        "operation_type": operation_type,
        "source_kind": child.get("source_kind"),
        "source_identity": rollback_record["source_identity"],
        "status": write_result.get("status"),
        "timestamp": _now(),
        "decision_authority": DECISION_AUTHORITY,
    }
    if write_result.get("status") == CONTENT_APPLIED:
        _save_apply_receipt(receipt, evidence_dir)

    return receipt
