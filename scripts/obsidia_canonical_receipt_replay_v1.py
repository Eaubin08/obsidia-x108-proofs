"""
obsidia_canonical_receipt_replay_v1.py
=====================================

Generic evidence-only replay verifier for CANONICAL_RECEIPT_ENVELOPE_V1.

Replay is historical verification only: it reads persisted evidence, hashes it,
checks relationships, and reports what can be proven. It never calls an
executor, never re-authorizes, never retries, and never performs physical IO
beyond reading evidence files.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Optional

import obsidia_batch_execution as _E
import obsidia_canonical_receipt_envelope_v1 as _CRE
import obsidia_kx108_decision_store as _DS

REPLAY_SCHEMA_VERSION = "CANONICAL_RECEIPT_REPLAY_RESULT_V1"

VERDICT_VERIFIED = "VERIFIED"
VERDICT_VERIFIED_WITH_LIMITS = "VERIFIED_WITH_LIMITS"
VERDICT_INCOMPLETE = "INCOMPLETE"
VERDICT_TAMPERED = "TAMPERED"
VERDICT_CONFLICTING = "CONFLICTING"
VERDICT_NOT_FOUND = "NOT_FOUND"

YES = "YES"
NO = "NO"
UNAVAILABLE = "UNAVAILABLE"
NOT_REACHED = _CRE.STATUS_NOT_REACHED
NOT_APPLICABLE = _CRE.STATUS_NOT_APPLICABLE
INLINE_STATUS_ONLY = "INLINE_STATUS_ONLY"

_ACTION_ID_RE = re.compile(r"^aev-[0-9a-f]{32}$")


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _safe_load_json(path: Path) -> tuple[Optional[dict], Optional[str]]:
    try:
        if not path.exists():
            return None, "MISSING"
        return json.loads(path.read_text(encoding="utf-8")), None
    except (OSError, json.JSONDecodeError):
        return None, "UNREADABLE"


def _stores(stores_base_dir) -> dict:
    base = Path(stores_base_dir)
    return {
        "v2exec": base / "v2exec",
        "approval": base / "approval",
        "kxpre": base / "kxpre",
        "receipts": base / "receipts",
    }


def _descriptor_path(stores: dict, descriptor_ref: str) -> Path:
    return stores["v2exec"] / f"{descriptor_ref}.json"


def _descriptor_hash(record: dict) -> str:
    raw = json.dumps(record, sort_keys=True, ensure_ascii=False)
    return _sha256_text(raw)


def _eah(operation_type: str, descriptor: dict) -> str:
    payload = json.dumps(
        {
            "v2_schema": "PC_CAPABILITIES_V2_EAH_V0",
            "operation_type": operation_type,
            "action_descriptor": descriptor,
        },
        sort_keys=True,
    )
    return _sha256_text(payload)


def _receipt_path(stores: dict, action_evidence_id: str) -> Path:
    return stores["receipts"] / f"{action_evidence_id}.json"


def _load_envelope_for_replay(action_evidence_id: str, stores: dict) -> tuple[Optional[dict], Optional[str]]:
    p = _receipt_path(stores, action_evidence_id)
    if not p.exists():
        return None, "CANONICAL_RECEIPT_MISSING"
    try:
        return json.loads(p.read_text(encoding="utf-8")), None
    except UnicodeDecodeError:
        return None, "CANONICAL_RECEIPT_UTF8_INVALID"
    except json.JSONDecodeError:
        return None, "CANONICAL_RECEIPT_JSON_INVALID"
    except OSError:
        return None, "CANONICAL_RECEIPT_UNREADABLE"


def _tampered_result(action_evidence_id: str, reason: str, stores_base_dir=None) -> dict:
    result = _unknown_result(action_evidence_id, VERDICT_TAMPERED, "", stores_base_dir)
    result["receipt_found"] = True
    result["evidence_missing"] = []
    result["evidence_conflicts"] = [reason]
    return result


def _unknown_result(action_evidence_id: str, verdict: str, reason: str, stores_base_dir=None) -> dict:
    return {
        "schema_version": REPLAY_SCHEMA_VERSION,
        "action_evidence_id": action_evidence_id,
        "stores_base_dir": str(stores_base_dir) if stores_base_dir is not None else "",
        "receipt_found": False,
        "envelope_hash_valid": False,
        "canonical_serialization_valid": False,
        "descriptor_ref_valid": UNAVAILABLE,
        "EAH_binding_valid": UNAVAILABLE,
        "approval_ref_valid": UNAVAILABLE,
        "KX108_ref_valid": UNAVAILABLE,
        "binder_status_reconstructable": UNAVAILABLE,
        "executor_binding_valid": UNAVAILABLE,
        "realized_state_evidence_valid": UNAVAILABLE,
        "outcome_consistency_valid": UNAVAILABLE,
        "outcome": "UNKNOWN",
        "physical_effect_dispatched": None,
        "uncertainty_state": "UNKNOWN",
        "evidence_complete": False,
        "evidence_missing": [reason] if reason else [],
        "evidence_conflicts": [],
        "linked_ids": {},
        "binder_replay_status": UNAVAILABLE,
        "replay_verdict": verdict,
    }


def _stage_reached(value) -> bool:
    return bool(value) and value not in {NOT_REACHED, NOT_APPLICABLE, _CRE.STATUS_NOT_PERSISTED}


def _verify_descriptor(envelope: dict, stores: dict, result: dict) -> tuple[Optional[dict], Optional[str]]:
    prep = envelope.get("prepare") or {}
    descriptor_ref = prep.get("descriptor_ref")
    expected_hash = prep.get("descriptor_hash")
    result["linked_ids"]["descriptor_ref"] = descriptor_ref or ""
    if not descriptor_ref or descriptor_ref in {NOT_REACHED, NOT_APPLICABLE}:
        result["descriptor_ref_valid"] = NOT_REACHED
        result["EAH_binding_valid"] = NOT_REACHED
        return None, None
    record, err = _safe_load_json(_descriptor_path(stores, descriptor_ref))
    if err:
        result["descriptor_ref_valid"] = UNAVAILABLE
        result["evidence_missing"].append("DESCRIPTOR_MISSING")
        return None, None
    actual_hash = _descriptor_hash(record)
    if expected_hash and actual_hash != expected_hash:
        result["descriptor_ref_valid"] = NO
        result["evidence_conflicts"].append("DESCRIPTOR_HASH_MISMATCH")
        return record, None
    result["descriptor_ref_valid"] = YES
    descriptor = record.get("descriptor") or {}
    eah = (envelope.get("authorization") or {}).get("execution_authority_hash")
    recomputed = _eah(envelope.get("operation_type", ""), descriptor)
    if eah and recomputed == eah and record.get("eah") == eah:
        result["EAH_binding_valid"] = YES
    else:
        result["EAH_binding_valid"] = NO
        result["evidence_conflicts"].append("EAH_BINDING_MISMATCH")
    return record, descriptor


def _verify_approval(envelope: dict, stores: dict, result: dict) -> Optional[dict]:
    auth = envelope.get("authorization") or {}
    approval_id = auth.get("approval_id")
    result["linked_ids"]["approval_id"] = approval_id or ""
    if not _stage_reached(approval_id):
        result["approval_ref_valid"] = NOT_REACHED
        return None
    record = _E.load_approval_artifact(approval_id, execution_dir=stores["approval"])
    ok, reason = _E.verify_approval_artifact(record)
    if not ok:
        if reason == "APPROVAL_MISSING":
            result["approval_ref_valid"] = UNAVAILABLE
            result["evidence_missing"].append("APPROVAL_MISSING")
        else:
            result["approval_ref_valid"] = NO
            result["evidence_conflicts"].append(reason or "APPROVAL_INVALID")
        return record
    checks = [
        record.get("approval_id") == approval_id,
        record.get("execution_authority_hash") == auth.get("execution_authority_hash"),
        record.get("approval_status") == auth.get("approval_status"),
        record.get("decision_authority") == _CRE.DECISION_AUTHORITY,
    ]
    if all(checks):
        result["approval_ref_valid"] = YES
    else:
        result["approval_ref_valid"] = NO
        result["evidence_conflicts"].append("APPROVAL_BINDING_MISMATCH")
    return record


def _verify_kx108(envelope: dict, stores: dict, result: dict) -> Optional[dict]:
    auth = envelope.get("authorization") or {}
    record_id = auth.get("kx108_pre_decision_record_id")
    result["linked_ids"]["kx108_pre_decision_record_id"] = record_id or ""
    if not _stage_reached(record_id):
        result["KX108_ref_valid"] = NOT_REACHED
        return None
    record = _DS.load_kx108_decision_record(record_id, store_dir=stores["kxpre"])
    ok, reason = _DS.verify_kx108_decision_record(record)
    if not ok:
        if reason == "DECISION_RECORD_MISSING":
            result["KX108_ref_valid"] = UNAVAILABLE
            result["evidence_missing"].append("KX108_RECORD_MISSING")
        else:
            result["KX108_ref_valid"] = NO
            result["evidence_conflicts"].append(reason or "KX108_RECORD_INVALID")
        return record
    checks = [
        record.get("decision_record_id") == record_id,
        record.get("decision_record_hash") == auth.get("kx108_pre_decision_record_hash"),
        record.get("execution_authority_hash") == auth.get("execution_authority_hash"),
        record.get("approval_id") == auth.get("approval_id"),
        record.get("x108_gate") == auth.get("kx108_verdict"),
    ]
    if all(checks):
        result["KX108_ref_valid"] = YES
    else:
        result["KX108_ref_valid"] = NO
        result["evidence_conflicts"].append("KX108_BINDING_MISMATCH")
    return record


def _verify_executor_binding(envelope: dict, result: dict) -> None:
    execution = envelope.get("execution") or {}
    ref = execution.get("executor_input_ref")
    expected = execution.get("executor_input_hash")
    if ref is None or not expected:
        result["executor_binding_valid"] = UNAVAILABLE
        result["evidence_missing"].append("EXECUTOR_INPUT_REF_MISSING")
        return
    actual = _CRE.compute_ref_hash(ref)
    if actual == expected:
        result["executor_binding_valid"] = YES
    else:
        result["executor_binding_valid"] = NO
        result["evidence_conflicts"].append("EXECUTOR_INPUT_HASH_MISMATCH")


def _verify_realized_state(envelope: dict, result: dict) -> None:
    realized = envelope.get("realized_state") or {}
    ok = True
    for ref_key, hash_key, conflict in (
        ("post_state_ref", "post_state_hash", "POST_STATE_HASH_MISMATCH"),
        ("current_state_ref", "current_state_hash", "CURRENT_STATE_HASH_MISMATCH"),
        ("transport_evidence_ref", "transport_evidence_hash", "TRANSPORT_EVIDENCE_HASH_MISMATCH"),
    ):
        ref = realized.get(ref_key) or (envelope.get("execution") or {}).get(ref_key)
        expected = realized.get(hash_key) or (envelope.get("execution") or {}).get(hash_key)
        if ref is not None and expected and _CRE.compute_ref_hash(ref) != expected:
            ok = False
            result["evidence_conflicts"].append(conflict)
    executor_identity = ((envelope.get("execution") or {}).get("executor_input_ref") or {}).get("element_identity_hash")
    for ref_key in ("post_state_ref",):
        ref = realized.get(ref_key)
        if isinstance(ref, dict) and executor_identity and ref.get("element_identity_hash"):
            if ref.get("element_identity_hash") != executor_identity:
                ok = False
                result["evidence_conflicts"].append("REALIZED_STATE_IDENTITY_MISMATCH")
    if realized.get("proof_strength") in (None, ""):
        ok = False
        result["evidence_missing"].append("PROOF_STRENGTH_MISSING")
    if "realized_state_verified" not in realized:
        ok = False
        result["evidence_missing"].append("REALIZED_STATE_VERIFIED_MISSING")
    result["realized_state_evidence_valid"] = YES if ok else NO


def _verify_outcome_consistency(envelope: dict, result: dict) -> None:
    outcome = result["outcome"]
    execution = envelope.get("execution") or {}
    realized = envelope.get("realized_state") or {}
    replay = envelope.get("replay") or {}
    physical = bool(realized.get("physical_effect_dispatched", execution.get("physical_effect_dispatched", False)))
    mutation = realized.get("mutation_performed", execution.get("mutation_performed"))
    verified = realized.get("realized_state_verified")
    executor_status = execution.get("executor_status")
    ok = True
    if outcome in {_CRE.OUTCOME_KX108_BLOCK, _CRE.OUTCOME_KX108_HOLD, _CRE.OUTCOME_TOCTOU_ABORTED}:
        ok = ok and physical is False and executor_status == NOT_REACHED
    if outcome == _CRE.OUTCOME_REALIZED_STATE_MISMATCH:
        ok = ok and physical is True and executor_status != NOT_REACHED and verified is False
    if outcome == _CRE.OUTCOME_SUCCESS:
        ok = ok and verified is True
    if outcome == _CRE.OUTCOME_NOOP:
        ok = ok and mutation is False and verified is True
    if outcome == _CRE.OUTCOME_DISPATCHED_OUTCOME_UNCERTAIN:
        ok = ok and physical is True
        ok = ok and replay.get("physical_replay_allowed") is False
        ok = ok and bool(realized.get("uncertainty_state"))
    result["outcome_consistency_valid"] = YES if ok else NO
    if not ok:
        result["evidence_conflicts"].append("OUTCOME_CONSISTENCY_MISMATCH")


def _binder_status(envelope: dict, result: dict) -> None:
    status = (envelope.get("authorization") or {}).get("binder_verdict_status")
    if not status or status == NOT_REACHED:
        result["binder_status_reconstructable"] = NOT_REACHED
        result["binder_replay_status"] = NOT_REACHED
    elif status in {"OBSERVED_INLINE", "OBSERVED_INLINE_NOT_SEPARATELY_PERSISTED", "REJECTED_INLINE"}:
        result["binder_status_reconstructable"] = YES
        result["binder_replay_status"] = INLINE_STATUS_ONLY
    else:
        result["binder_status_reconstructable"] = UNAVAILABLE
        result["binder_replay_status"] = INLINE_STATUS_ONLY


def _final_verdict(result: dict) -> str:
    if result["evidence_conflicts"]:
        if any("HASH_MISMATCH" in c or "INVALID" in c for c in result["evidence_conflicts"]):
            return VERDICT_TAMPERED
        return VERDICT_CONFLICTING
    if result["evidence_missing"]:
        return VERDICT_INCOMPLETE
    if result.get("binder_replay_status") == INLINE_STATUS_ONLY:
        return VERDICT_VERIFIED_WITH_LIMITS
    return VERDICT_VERIFIED


def replay_action_evidence(action_evidence_id: str, *, stores_base_dir) -> dict:
    if not isinstance(action_evidence_id, str) or not _ACTION_ID_RE.match(action_evidence_id):
        return _unknown_result(str(action_evidence_id), VERDICT_NOT_FOUND, "INVALID_ACTION_EVIDENCE_ID", stores_base_dir)
    stores = _stores(stores_base_dir)
    envelope, load_error = _load_envelope_for_replay(action_evidence_id, stores)
    if envelope is None:
        if load_error == "CANONICAL_RECEIPT_MISSING":
            return _unknown_result(action_evidence_id, VERDICT_NOT_FOUND, load_error, stores_base_dir)
        return _tampered_result(action_evidence_id, load_error or "CANONICAL_RECEIPT_INVALID", stores_base_dir)
    if envelope.get("action_evidence_id") != action_evidence_id:
        return _tampered_result(action_evidence_id, "ACTION_EVIDENCE_ID_PATH_PAYLOAD_MISMATCH", stores_base_dir)
    result = _unknown_result(action_evidence_id, VERDICT_INCOMPLETE, "", stores_base_dir)
    result["receipt_found"] = True
    result["evidence_missing"] = []
    result["schema_version"] = REPLAY_SCHEMA_VERSION
    result["outcome"] = (envelope.get("realized_state") or {}).get("outcome", "UNKNOWN")
    result["physical_effect_dispatched"] = (envelope.get("realized_state") or {}).get(
        "physical_effect_dispatched", (envelope.get("execution") or {}).get("physical_effect_dispatched")
    )
    result["uncertainty_state"] = (envelope.get("realized_state") or {}).get("uncertainty_state", "")
    result["linked_ids"] = {"action_evidence_id": action_evidence_id}

    result["canonical_serialization_valid"] = _CRE.canonical_json(envelope) == _CRE.canonical_json(json.loads(json.dumps(envelope)))
    result["envelope_hash_valid"] = _CRE.compute_envelope_hash(envelope) == envelope.get("envelope_hash")
    ok, reason = _CRE.verify_canonical_receipt_envelope(envelope)
    if not ok or not result["envelope_hash_valid"]:
        result["replay_verdict"] = VERDICT_TAMPERED
        result["evidence_conflicts"].append(reason or "ENVELOPE_HASH_MISMATCH")
        return result

    _verify_descriptor(envelope, stores, result)
    _verify_approval(envelope, stores, result)
    _verify_kx108(envelope, stores, result)
    _binder_status(envelope, result)
    _verify_executor_binding(envelope, result)
    _verify_realized_state(envelope, result)
    _verify_outcome_consistency(envelope, result)

    result["evidence_complete"] = not result["evidence_missing"] and not result["evidence_conflicts"]
    result["replay_verdict"] = _final_verdict(result)
    return result
