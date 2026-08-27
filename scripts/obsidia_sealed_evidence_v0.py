"""
obsidia_sealed_evidence_v0.py
=============================
C2_D_ATOMIC_PRODUCTION_ACTIVATION_V1 — évidence d'exécution SCELLÉE,
immuable, append-only, hachée, liée à l'autorité d'exécution.

Deux artefacts :

  SealedRollbackEvidence  (id `sre-…`) — la preimage A (octets d'AVANT
      l'écriture), persistée + rechargée + vérifiée AVANT toute mutation
      de cible. Lie directement : execution_authority_hash, approval_id,
      kx108_pre_decision_record_id/_hash, target_path, pre_write_sha256
      (== child.target_pre_sha256), source_content_sha256
      (== child.source_content_sha256).

  SealedApplyReceipt      (id `sar-…`) — le reçu d'application, persisté +
      rechargé + vérifié APRÈS une écriture MESURÉE. Lie en plus
      sealed_rollback_evidence_id/_hash et exige
      target_post_sha256 == child.source_content_sha256 (REPLACE :
      la cible EST devenue exactement les octets source autorisés).

Modèle de stockage : identique à `store_kx108_decision_record` /
`store_rollback_result` — fichier temporaire frère, flush + fsync, puis
publication exclusive via `os.link` :
  - publication réussie                -> STORED
  - déjà existant, octets identiques   -> IDEMPOTENT_EXISTING_IDENTICAL
  - déjà existant, octets différents   -> IMMUTABILITY_VIOLATION
  - id malformé                        -> INVALID_SEALED_EVIDENCE_ID
Jamais d'écrasement, jamais de fichier partiel visible.

Ce module ne DÉCIDE rien et ne mute AUCUNE cible. `decision_authority`
reste KX108_ONLY.
"""
from __future__ import annotations

import base64
import binascii
import datetime
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Optional

SCHEMA_VERSION = 1
DECISION_AUTHORITY = "KX108_ONLY"
OPERATION_TYPE = "UPDATE_TARGET_FROM_SOURCE"

_LOCALAPPDATA = Path(os.environ.get("LOCALAPPDATA", ""))
SEALED_ROLLBACK_EVIDENCE_DIR = _LOCALAPPDATA / "Obsidia" / "sealed_rollback_evidence"
SEALED_APPLY_RECEIPT_DIR = _LOCALAPPDATA / "Obsidia" / "sealed_receipts"

_SRE_ID_RE = re.compile(r"^sre-[0-9a-f]{32}$")
_SAR_ID_RE = re.compile(r"^sar-[0-9a-f]{32}$")
_SHA256_HEX_LEN = 64

STATUS_STORED = "STORED"
STATUS_IDEMPOTENT = "IDEMPOTENT_EXISTING_IDENTICAL"
STATUS_IMMUTABILITY_VIOLATION = "IMMUTABILITY_VIOLATION"
STATUS_INVALID_ID = "INVALID_SEALED_EVIDENCE_ID"
STATUS_TEMP_WRITE_FAILED = "SEALED_EVIDENCE_TEMP_WRITE_FAILED"

# ── Champs liés (ordre canonique — le hash d'enregistrement les couvre tous) ──

_SRE_BOUND_FIELDS = (
    "schema_version", "sealed", "sealed_rollback_evidence_id", "created_at",
    "batch_execution_id", "child_execution_id",
    "execution_authority_hash", "approval_id",
    "kx108_pre_decision_record_id", "kx108_pre_decision_record_hash",
    "target_path",
    "pre_write_sha256", "pre_write_size", "pre_write_bytes_b64",
    "source_content_sha256", "source_kind", "source_identity",
    "operation_type", "decision_authority",
)

_SAR_BOUND_FIELDS = (
    "schema_version", "sealed", "sealed_apply_receipt_id", "created_at",
    "batch_execution_id", "child_execution_id",
    "execution_authority_hash", "approval_id",
    "kx108_pre_decision_record_id", "kx108_pre_decision_record_hash",
    "sealed_rollback_evidence_id", "sealed_rollback_evidence_hash",
    "target_path", "target_pre_sha256", "target_post_sha256",
    "source_content_sha256", "bytes_written",
    "source_kind", "source_identity",
    "operation_type", "status", "decision_authority",
)

_SRE_IDENTITY_SEED = tuple(
    f for f in _SRE_BOUND_FIELDS if f not in ("sealed_rollback_evidence_id", "created_at")
)
_SAR_IDENTITY_SEED = tuple(
    f for f in _SAR_BOUND_FIELDS if f not in ("sealed_apply_receipt_id", "created_at")
)


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _is_full_sha256(v) -> bool:
    return isinstance(v, str) and len(v) == _SHA256_HEX_LEN and all(
        c in "0123456789abcdef" for c in v.lower()
    )


# ── Hash / identité ───────────────────────────────────────────────────────

def compute_sealed_rollback_evidence_hash(record: dict) -> str:
    payload = json.dumps({k: record.get(k) for k in _SRE_BOUND_FIELDS}, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def compute_sealed_apply_receipt_hash(record: dict) -> str:
    payload = json.dumps({k: record.get(k) for k in _SAR_BOUND_FIELDS}, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _sre_identity(seed: dict) -> str:
    payload = json.dumps({k: seed.get(k) for k in _SRE_IDENTITY_SEED}, sort_keys=True)
    return f"sre-{hashlib.sha256(payload.encode('utf-8')).hexdigest()[:32]}"


def _sar_identity(seed: dict) -> str:
    payload = json.dumps({k: seed.get(k) for k in _SAR_IDENTITY_SEED}, sort_keys=True)
    return f"sar-{hashlib.sha256(payload.encode('utf-8')).hexdigest()[:32]}"


# ── Magasin immuable (os.link exclusif) ──────────────────────────────────

def _sealed_path(sealed_id: "str | None", id_re: re.Pattern, default_dir: Path,
                 store_dir: Optional[Path] = None) -> Path:
    if not sealed_id or not id_re.match(str(sealed_id)):
        raise ValueError("INVALID_SEALED_EVIDENCE_ID")
    d = store_dir or default_dir
    return d / f"{sealed_id}.json"


def _store_sealed(record: dict, id_key: str, id_re: re.Pattern, default_dir: Path,
                  store_dir: Optional[Path] = None) -> dict:
    sealed_id = record.get(id_key)
    try:
        p = _sealed_path(sealed_id, id_re, default_dir, store_dir)
    except ValueError:
        return {"status": STATUS_INVALID_ID, id_key: sealed_id}
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
        return {"status": STATUS_TEMP_WRITE_FAILED, id_key: sealed_id}
    try:
        os.link(tmp, p)
        return {"status": STATUS_STORED, id_key: sealed_id}
    except FileExistsError:
        existing = p.read_text(encoding="utf-8")
        if existing == payload:
            return {"status": STATUS_IDEMPOTENT, id_key: sealed_id}
        return {"status": STATUS_IMMUTABILITY_VIOLATION, id_key: sealed_id}
    finally:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass


def _load_sealed(sealed_id: str, id_re: re.Pattern, default_dir: Path,
                 store_dir: Optional[Path] = None) -> Optional[dict]:
    try:
        p = _sealed_path(sealed_id, id_re, default_dir, store_dir)
    except ValueError:
        return None
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


# ── SealedRollbackEvidence ──────────────────────────────────────────────

def build_sealed_rollback_evidence(
    *, batch_execution_id: str, child: dict,
    execution_authority_hash: str, approval_id: str,
    kx108_pre_decision_record_id: str, kx108_pre_decision_record_hash: str,
    preimage_bytes: bytes,
) -> "tuple[Optional[dict], Optional[str]]":
    """Construit (jamais ne persiste) le record scellé. Fail-closed sur toute
    incohérence de preimage ou de liaison. Retourne (record, None) ou
    (None, reason)."""
    target_path = child.get("target_path")
    child_target_pre = child.get("target_pre_sha256")
    child_source_sha = child.get("source_content_sha256")
    if not target_path:
        return None, "TARGET_PATH_MISSING"
    if not _is_full_sha256(child_target_pre):
        return None, "CHILD_TARGET_PRE_SHA256_NOT_FULL_64_HEX"
    if not _is_full_sha256(child_source_sha):
        return None, "CHILD_SOURCE_CONTENT_SHA256_NOT_FULL_64_HEX"
    if child.get("operation_type") != OPERATION_TYPE:
        return None, "UNSUPPORTED_OPERATION"

    if not isinstance(preimage_bytes, (bytes, bytearray)):
        return None, "PREIMAGE_NOT_BYTES"
    preimage_bytes = bytes(preimage_bytes)
    pre_write_sha256 = _sha256_hex(preimage_bytes)
    if pre_write_sha256 != child_target_pre:
        return None, "PREIMAGE_SHA256_NEQ_CHILD_TARGET_PRE"
    pre_write_size = len(preimage_bytes)
    b64 = base64.b64encode(preimage_bytes).decode("ascii")
    # round-trip strict — la preimage doit se redécoder exactement
    try:
        if base64.b64decode(b64, validate=True) != preimage_bytes:
            return None, "PREIMAGE_BASE64_ROUNDTRIP_MISMATCH"
    except (ValueError, binascii.Error):
        return None, "PREIMAGE_BASE64_INVALID"

    record: dict = {
        "schema_version": SCHEMA_VERSION,
        "sealed": True,
        "created_at": _now(),
        "batch_execution_id": batch_execution_id,
        "child_execution_id": child.get("child_execution_id"),
        "execution_authority_hash": execution_authority_hash,
        "approval_id": approval_id,
        "kx108_pre_decision_record_id": kx108_pre_decision_record_id,
        "kx108_pre_decision_record_hash": kx108_pre_decision_record_hash,
        "target_path": target_path,
        "pre_write_sha256": pre_write_sha256,
        "pre_write_size": pre_write_size,
        "pre_write_bytes_b64": b64,
        "source_content_sha256": child_source_sha,
        "source_kind": child.get("source_kind"),
        "source_identity": {
            "source_path": child.get("source_path"),
            "source_git_commit_sha": child.get("source_git_commit_sha"),
            "source_git_blob_sha": child.get("source_git_blob_sha"),
            "source_git_historical_path": child.get("source_git_historical_path"),
        },
        "operation_type": OPERATION_TYPE,
        "decision_authority": DECISION_AUTHORITY,
    }
    seed = {k: record.get(k) for k in _SRE_IDENTITY_SEED}
    record["sealed_rollback_evidence_id"] = _sre_identity(seed)
    record["sealed_rollback_evidence_hash"] = compute_sealed_rollback_evidence_hash(record)
    return record, None


def store_sealed_rollback_evidence(record: dict, store_dir: Optional[Path] = None) -> dict:
    return _store_sealed(record, "sealed_rollback_evidence_id", _SRE_ID_RE,
                         SEALED_ROLLBACK_EVIDENCE_DIR, store_dir)


def load_sealed_rollback_evidence(sealed_id: str, store_dir: Optional[Path] = None) -> Optional[dict]:
    return _load_sealed(sealed_id, _SRE_ID_RE, SEALED_ROLLBACK_EVIDENCE_DIR, store_dir)


def verify_sealed_rollback_evidence(record: Optional[dict]) -> "tuple[bool, Optional[str]]":
    if record is None:
        return False, "SEALED_ROLLBACK_EVIDENCE_MISSING"
    if record.get("schema_version") != SCHEMA_VERSION:
        return False, "SEALED_ROLLBACK_EVIDENCE_SCHEMA_UNSUPPORTED"
    if record.get("sealed") is not True:
        return False, "NOT_SEALED"
    for f in _SRE_BOUND_FIELDS:
        if f not in record:
            return False, f"SEALED_ROLLBACK_EVIDENCE_FIELD_MISSING:{f}"
    if record.get("decision_authority") != DECISION_AUTHORITY:
        return False, "DECISION_AUTHORITY_NOT_KX108_ONLY"
    if record.get("operation_type") != OPERATION_TYPE:
        return False, "UNSUPPORTED_OPERATION"
    if not _is_full_sha256(record.get("pre_write_sha256")):
        return False, "PRE_WRITE_SHA256_NOT_FULL_64_HEX"
    if not _is_full_sha256(record.get("source_content_sha256")):
        return False, "SOURCE_CONTENT_SHA256_NOT_FULL_64_HEX"
    b64 = record.get("pre_write_bytes_b64")
    try:
        preimage = base64.b64decode(b64, validate=True) if b64 is not None else None
    except (ValueError, binascii.Error):
        return False, "PREIMAGE_BASE64_INVALID"
    if preimage is None:
        return False, "PREIMAGE_ABSENT"
    if _sha256_hex(preimage) != record.get("pre_write_sha256"):
        return False, "PREIMAGE_SHA256_MISMATCH"
    if len(preimage) != record.get("pre_write_size"):
        return False, "PREIMAGE_SIZE_MISMATCH"
    if record.get("sealed_rollback_evidence_hash") != compute_sealed_rollback_evidence_hash(record):
        return False, "SEALED_ROLLBACK_EVIDENCE_HASH_MISMATCH"
    return True, None


def decode_sealed_preimage(record: dict) -> "tuple[Optional[bytes], Optional[str]]":
    try:
        preimage = base64.b64decode(record.get("pre_write_bytes_b64"), validate=True)
    except (ValueError, binascii.Error, TypeError):
        return None, "PREIMAGE_BASE64_INVALID"
    if _sha256_hex(preimage) != record.get("pre_write_sha256"):
        return None, "PREIMAGE_SHA256_MISMATCH"
    if len(preimage) != record.get("pre_write_size"):
        return None, "PREIMAGE_SIZE_MISMATCH"
    return preimage, None


# ── SealedApplyReceipt ─────────────────────────────────────────────────

def build_sealed_apply_receipt(
    *, batch_execution_id: str, child: dict,
    execution_authority_hash: str, approval_id: str,
    kx108_pre_decision_record_id: str, kx108_pre_decision_record_hash: str,
    sealed_rollback_evidence_id: str, sealed_rollback_evidence_hash: str,
    target_pre_sha256: str, target_post_sha256: str, bytes_written: int,
) -> "tuple[Optional[dict], Optional[str]]":
    """Construit (jamais ne persiste) le reçu scellé. Exige
    target_post_sha256 == child.source_content_sha256 (REPLACE mesuré)."""
    child_source_sha = child.get("source_content_sha256")
    if not _is_full_sha256(child_source_sha):
        return None, "CHILD_SOURCE_CONTENT_SHA256_NOT_FULL_64_HEX"
    if not _is_full_sha256(target_pre_sha256):
        return None, "TARGET_PRE_SHA256_NOT_FULL_64_HEX"
    if not _is_full_sha256(target_post_sha256):
        return None, "TARGET_POST_SHA256_NOT_FULL_64_HEX"
    if target_pre_sha256 != child.get("target_pre_sha256"):
        return None, "TARGET_PRE_SHA256_NEQ_CHILD"
    if target_post_sha256 != child_source_sha:
        return None, "TARGET_POST_SHA256_NEQ_CHILD_SOURCE_CONTENT_SHA256"
    if child.get("operation_type") != OPERATION_TYPE:
        return None, "UNSUPPORTED_OPERATION"

    record: dict = {
        "schema_version": SCHEMA_VERSION,
        "sealed": True,
        "created_at": _now(),
        "batch_execution_id": batch_execution_id,
        "child_execution_id": child.get("child_execution_id"),
        "execution_authority_hash": execution_authority_hash,
        "approval_id": approval_id,
        "kx108_pre_decision_record_id": kx108_pre_decision_record_id,
        "kx108_pre_decision_record_hash": kx108_pre_decision_record_hash,
        "sealed_rollback_evidence_id": sealed_rollback_evidence_id,
        "sealed_rollback_evidence_hash": sealed_rollback_evidence_hash,
        "target_path": child.get("target_path"),
        "target_pre_sha256": target_pre_sha256,
        "target_post_sha256": target_post_sha256,
        "source_content_sha256": child_source_sha,
        "bytes_written": bytes_written,
        "source_kind": child.get("source_kind"),
        "source_identity": {
            "source_path": child.get("source_path"),
            "source_git_commit_sha": child.get("source_git_commit_sha"),
            "source_git_blob_sha": child.get("source_git_blob_sha"),
            "source_git_historical_path": child.get("source_git_historical_path"),
        },
        "operation_type": OPERATION_TYPE,
        "status": "CONTENT_APPLIED",
        "decision_authority": DECISION_AUTHORITY,
    }
    seed = {k: record.get(k) for k in _SAR_IDENTITY_SEED}
    record["sealed_apply_receipt_id"] = _sar_identity(seed)
    record["sealed_apply_receipt_hash"] = compute_sealed_apply_receipt_hash(record)
    return record, None


def store_sealed_apply_receipt(record: dict, store_dir: Optional[Path] = None) -> dict:
    return _store_sealed(record, "sealed_apply_receipt_id", _SAR_ID_RE,
                         SEALED_APPLY_RECEIPT_DIR, store_dir)


def load_sealed_apply_receipt(sealed_id: str, store_dir: Optional[Path] = None) -> Optional[dict]:
    return _load_sealed(sealed_id, _SAR_ID_RE, SEALED_APPLY_RECEIPT_DIR, store_dir)


def verify_sealed_apply_receipt(record: Optional[dict]) -> "tuple[bool, Optional[str]]":
    if record is None:
        return False, "SEALED_APPLY_RECEIPT_MISSING"
    if record.get("schema_version") != SCHEMA_VERSION:
        return False, "SEALED_APPLY_RECEIPT_SCHEMA_UNSUPPORTED"
    if record.get("sealed") is not True:
        return False, "NOT_SEALED"
    for f in _SAR_BOUND_FIELDS:
        if f not in record:
            return False, f"SEALED_APPLY_RECEIPT_FIELD_MISSING:{f}"
    if record.get("decision_authority") != DECISION_AUTHORITY:
        return False, "DECISION_AUTHORITY_NOT_KX108_ONLY"
    if record.get("operation_type") != OPERATION_TYPE:
        return False, "UNSUPPORTED_OPERATION"
    if record.get("status") != "CONTENT_APPLIED":
        return False, "STATUS_NOT_CONTENT_APPLIED"
    for f in ("target_pre_sha256", "target_post_sha256", "source_content_sha256"):
        if not _is_full_sha256(record.get(f)):
            return False, f"{f.upper()}_NOT_FULL_64_HEX"
    if record.get("target_post_sha256") != record.get("source_content_sha256"):
        return False, "TARGET_POST_SHA256_NEQ_SOURCE_CONTENT_SHA256"
    if record.get("sealed_apply_receipt_hash") != compute_sealed_apply_receipt_hash(record):
        return False, "SEALED_APPLY_RECEIPT_HASH_MISMATCH"
    return True, None


def as_legacy_receipt_dict(sealed_receipt: dict) -> dict:
    """Vue « forme legacy » d'un SealedApplyReceipt — pour l'adaptateur POST
    canonique et D2 (chemins qui lisent le receipt mutable historique).
    Ne persiste rien ; ne fabrique aucune autorité."""
    return {
        "schema_version": "V0",
        "child_execution_id": sealed_receipt.get("child_execution_id"),
        "batch_execution_id": sealed_receipt.get("batch_execution_id"),
        "batch_id": sealed_receipt.get("batch_id"),
        "target_path": sealed_receipt.get("target_path"),
        "target_pre_sha256": sealed_receipt.get("target_pre_sha256"),
        "source_full_sha256": sealed_receipt.get("source_content_sha256"),
        "target_post_sha256": sealed_receipt.get("target_post_sha256"),
        "bytes_written": sealed_receipt.get("bytes_written"),
        "operation_type": sealed_receipt.get("operation_type"),
        "source_kind": sealed_receipt.get("source_kind"),
        "source_identity": sealed_receipt.get("source_identity"),
        "status": sealed_receipt.get("status"),
        "decision_authority": sealed_receipt.get("decision_authority"),
        "sealed_apply_receipt_id": sealed_receipt.get("sealed_apply_receipt_id"),
        "sealed_apply_receipt_hash": sealed_receipt.get("sealed_apply_receipt_hash"),
    }
