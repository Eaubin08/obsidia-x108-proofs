"""
obsidia_canonical_receipt_envelope_v1.py
=======================================

CANONICAL_RECEIPT_ENVELOPE_V1 - immutable, append-only evidence envelope
for one governed action chain.

This module does not decide, authorize, execute, replay, or replace existing
per-capability receipts. It only links existing evidence references into a
canonical envelope suitable for later evidence-only replay.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Optional

SCHEMA_VERSION = "CANONICAL_RECEIPT_ENVELOPE_V1"
DECISION_AUTHORITY = "KX108_ONLY"

STATUS_STORED = "STORED"
STATUS_IDEMPOTENT = "IDEMPOTENT_EXISTING_IDENTICAL"
STATUS_IMMUTABILITY_VIOLATION = "CANONICAL_RECEIPT_IMMUTABILITY_VIOLATION"
STATUS_INVALID_ID = "INVALID_ACTION_EVIDENCE_ID"
STATUS_TEMP_WRITE_FAILED = "CANONICAL_RECEIPT_TEMP_WRITE_FAILED"

DEFAULT_REDACTION_POLICY = "HASHES_AND_REFS_ONLY"

OUTCOME_SUCCESS = "SUCCESS"
OUTCOME_NOOP = "NOOP"
OUTCOME_PREPARE_REJECTED = "PREPARE_REJECTED"
OUTCOME_APPROVAL_MISSING_OR_INVALID = "APPROVAL_MISSING_OR_INVALID"
OUTCOME_KX108_HOLD = "KX108_HOLD"
OUTCOME_KX108_BLOCK = "KX108_BLOCK"
OUTCOME_BINDER_REJECTED = "BINDER_REJECTED"
OUTCOME_TOCTOU_ABORTED = "TOCTOU_ABORTED"
OUTCOME_EXECUTOR_FAILED_BEFORE_ACTION = "EXECUTOR_FAILED_BEFORE_ACTION"
OUTCOME_REALIZED_STATE_MISMATCH = "REALIZED_STATE_MISMATCH"
OUTCOME_DISPATCHED_OUTCOME_UNCERTAIN = "DISPATCHED_OUTCOME_UNCERTAIN"

DISPATCH_PRE_FAILURE = "PRE_DISPATCH_FAILURE"
DISPATCH_POST_UNCERTAINTY = "POST_DISPATCH_UNCERTAINTY"
DISPATCH_POST_CONFIRMED = "POST_DISPATCH_CONFIRMED"

STAGE_REQUEST = "REQUEST"
STAGE_PREPARE = "PREPARE"
STAGE_APPROVAL = "APPROVAL"
STAGE_KX108 = "KX108"
STAGE_BINDER = "BINDER"
STAGE_TOCTOU = "TOCTOU"
STAGE_EXECUTOR = "EXECUTOR"
STAGE_POST_OBSERVATION = "POST_OBSERVATION"
STAGE_RECONCILIATION = "RECONCILIATION"

STATUS_NOT_REACHED = "NOT_REACHED"
STATUS_NOT_APPLICABLE = "NOT_APPLICABLE"
STATUS_NOT_PERSISTED = "NOT_PERSISTED"
_ACTION_EVIDENCE_ID_RE = re.compile(r"^aev-[0-9a-f]{32}$")
_LOCALAPPDATA = Path(os.environ.get("LOCALAPPDATA", ""))
CANONICAL_RECEIPT_DIR = _LOCALAPPDATA / "Obsidia" / "canonical_receipts"


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def canonical_json(data: dict) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def compute_envelope_hash(envelope: dict) -> str:
    payload = dict(envelope)
    payload.pop("envelope_hash", None)
    return _sha256_text(canonical_json(payload))


def compute_ref_hash(ref: object) -> str:
    return _sha256_text(canonical_json(ref if isinstance(ref, dict) else {"value": ref}))


def _action_identity_seed(envelope: dict) -> dict:
    if isinstance(envelope.get("action_identity"), dict) and envelope.get("action_identity"):
        return envelope["action_identity"]
    return {
        "schema_version": envelope.get("schema_version"),
        "capability": envelope.get("capability"),
        "operation_type": envelope.get("operation_type"),
        "request_ref": envelope.get("request_ref"),
        "session_ref": envelope.get("session_ref"),
        "prepare": envelope.get("prepare"),
        "authorization": envelope.get("authorization"),
        "execution": {
            "executor_kind": (envelope.get("execution") or {}).get("executor_kind"),
            "executor_operation": (envelope.get("execution") or {}).get("executor_operation"),
            "executor_input_hash": (envelope.get("execution") or {}).get("executor_input_hash"),
        },
    }


def compute_action_evidence_id(envelope: dict) -> str:
    return "aev-" + _sha256_text(canonical_json(_action_identity_seed(envelope)))[:32]


def build_canonical_receipt_envelope(
    *,
    capability: str,
    operation_type: str,
    request_ref: dict,
    session_ref: dict,
    prepare: dict,
    authorization: dict,
    execution: dict,
    realized_state: dict,
    receipt: dict,
    replay: Optional[dict] = None,
    privacy: Optional[dict] = None,
    domain: str = "PC_BROWSER",
    layer: str = "GOVERNED_ACTION",
    created_at: Optional[str] = None,
    action_identity: Optional[dict] = None,
) -> dict:
    envelope = {
        "schema_version": SCHEMA_VERSION,
        "created_at": created_at or _now(),
        "domain": domain,
        "layer": layer,
        "capability": capability,
        "operation_type": operation_type,
        "decision_authority": DECISION_AUTHORITY,
        "authority": "NONE",
        "jarvis_authority": "NONE",
        "openjarvis_authority": "NONE",
        "request_ref": dict(request_ref),
        "action_identity": dict(action_identity or {}),
        "session_ref": dict(session_ref),
        "prepare": dict(prepare),
        "authorization": dict(authorization),
        "execution": dict(execution),
        "realized_state": dict(realized_state),
        "receipt": dict(receipt),
        "replay": {
            "physical_replay_allowed": False,
            "evidence_replay_allowed": True,
            **(replay or {}),
        },
        "privacy": {
            "redaction_policy": DEFAULT_REDACTION_POLICY,
            "plaintext_sensitive_data_present": False,
            **(privacy or {}),
        },
    }
    envelope["action_evidence_id"] = compute_action_evidence_id(envelope)
    envelope["envelope_hash"] = compute_envelope_hash(envelope)
    return envelope


def verify_canonical_receipt_envelope(envelope: Optional[dict]) -> tuple[bool, Optional[str]]:
    if envelope is None:
        return False, "CANONICAL_RECEIPT_MISSING"
    if envelope.get("schema_version") != SCHEMA_VERSION:
        return False, "CANONICAL_RECEIPT_SCHEMA_UNSUPPORTED"
    action_evidence_id = envelope.get("action_evidence_id")
    if not isinstance(action_evidence_id, str) or not _ACTION_EVIDENCE_ID_RE.match(action_evidence_id):
        return False, STATUS_INVALID_ID
    if envelope.get("decision_authority") != DECISION_AUTHORITY:
        return False, "DECISION_AUTHORITY_NOT_KX108_ONLY"
    if envelope.get("authority") != "NONE" or envelope.get("jarvis_authority") != "NONE":
        return False, "UNEXPECTED_EXECUTION_AUTHORITY"
    if envelope.get("openjarvis_authority") != "NONE":
        return False, "UNEXPECTED_OPENJARVIS_AUTHORITY"
    if (envelope.get("privacy") or {}).get("plaintext_sensitive_data_present") is not False:
        return False, "PLAINTEXT_SENSITIVE_DATA_PRESENT"
    if (envelope.get("replay") or {}).get("physical_replay_allowed") is not False:
        return False, "PHYSICAL_REPLAY_ALLOWED"
    if compute_action_evidence_id(envelope) != action_evidence_id:
        return False, "ACTION_EVIDENCE_ID_MISMATCH"
    if compute_envelope_hash(envelope) != envelope.get("envelope_hash"):
        return False, "ENVELOPE_HASH_MISMATCH"
    return True, None


def _envelope_path(action_evidence_id: str, store_dir: Optional[Path] = None) -> Path:
    if not isinstance(action_evidence_id, str) or not _ACTION_EVIDENCE_ID_RE.match(action_evidence_id):
        raise ValueError(STATUS_INVALID_ID)
    d = store_dir or CANONICAL_RECEIPT_DIR
    return d / f"{action_evidence_id}.json"


def store_canonical_receipt_envelope(envelope: dict, store_dir: Optional[Path] = None) -> dict:
    ok, reason = verify_canonical_receipt_envelope(envelope)
    if not ok:
        return {"status": reason, "action_evidence_id": envelope.get("action_evidence_id")}
    action_evidence_id = envelope["action_evidence_id"]
    try:
        p = _envelope_path(action_evidence_id, store_dir)
    except ValueError:
        return {"status": STATUS_INVALID_ID, "action_evidence_id": action_evidence_id}
    payload = json.dumps(envelope, ensure_ascii=False, indent=2, sort_keys=True)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.parent / f".{p.name}.{os.getpid()}.{_sha256_text(payload + str(id(envelope)))[:16]}.tmp"
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
        return {"status": STATUS_TEMP_WRITE_FAILED, "action_evidence_id": action_evidence_id}
    try:
        os.link(tmp, p)
        return {"status": STATUS_STORED, "action_evidence_id": action_evidence_id}
    except FileExistsError:
        existing = p.read_text(encoding="utf-8")
        if existing == payload:
            return {"status": STATUS_IDEMPOTENT, "action_evidence_id": action_evidence_id}
        return {"status": STATUS_IMMUTABILITY_VIOLATION, "action_evidence_id": action_evidence_id}
    finally:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass


def load_canonical_receipt_envelope(action_evidence_id: str, store_dir: Optional[Path] = None) -> Optional[dict]:
    try:
        p = _envelope_path(action_evidence_id, store_dir)
    except ValueError:
        return None
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
