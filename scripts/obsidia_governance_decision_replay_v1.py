"""
obsidia_governance_decision_replay_v1.py
=======================================

Deterministic governance decision replay over frozen R8 evidence.

This module is read-only. It reuses the R8-B3 evidence replay oracle, then
verifies and compares frozen descriptor/EAH/approval/KX108/Binder inputs. It
never calls the live KX108 persistence path, any executor, network, provider,
or current-world observer.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Optional

import obsidia_batch_execution as _E
import obsidia_canonical_receipt_envelope_v1 as _CRE
import obsidia_canonical_receipt_replay_v1 as _R3
import obsidia_kx108_decision_store as _DS

RESULT_SCHEMA_VERSION = "GOVERNANCE_DECISION_REPLAY_RESULT_V1"

VERDICT_MATCH = "MATCH"
VERDICT_MISMATCH = "MISMATCH"
VERDICT_INCOMPLETE = "INCOMPLETE"
VERDICT_TAMPERED = "TAMPERED"
VERDICT_NOT_REPLAYABLE = "NOT_REPLAYABLE"
VERDICT_NOT_FOUND = "NOT_FOUND"

YES = "YES"
NO = "NO"
PARTIAL = "PARTIAL"
UNAVAILABLE = "UNAVAILABLE"
NOT_REACHED = _CRE.STATUS_NOT_REACHED
INLINE_STATUS_ONLY = "INLINE_STATUS_ONLY"

_ACTION_ID_RE = re.compile(r"^aev-[0-9a-f]{32}$")


def _sha256_json(data: dict) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


def _stores(stores_base_dir) -> dict:
    base = Path(stores_base_dir)
    return {
        "v2exec": base / "v2exec",
        "approval": base / "approval",
        "kxpre": base / "kxpre",
        "receipts": base / "receipts",
    }


def _eah(operation_type: str, descriptor: dict) -> str:
    payload = json.dumps(
        {
            "v2_schema": "PC_CAPABILITIES_V2_EAH_V0",
            "operation_type": operation_type,
            "action_descriptor": descriptor,
        },
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _descriptor_hash(record: dict) -> str:
    return hashlib.sha256(json.dumps(record, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def _load_json(path: Path) -> tuple[Optional[dict], Optional[str]]:
    try:
        if not path.exists():
            return None, "MISSING"
        return json.loads(path.read_text(encoding="utf-8")), None
    except UnicodeDecodeError:
        return None, "UTF8_INVALID"
    except json.JSONDecodeError:
        return None, "JSON_INVALID"
    except OSError:
        return None, "UNREADABLE"


def _base_result(action_evidence_id: str, stores_base_dir) -> dict:
    return {
        "schema_version": RESULT_SCHEMA_VERSION,
        "action_evidence_id": action_evidence_id,
        "stores_base_dir": str(stores_base_dir),
        "historical_kx108_verdict": "UNKNOWN",
        "replayed_kx108_verdict": "UNKNOWN",
        "kx108_match": UNAVAILABLE,
        "historical_binder_status": "UNKNOWN",
        "replayed_binder_status": "UNKNOWN",
        "binder_match": UNAVAILABLE,
        "EAH_valid": UNAVAILABLE,
        "approval_valid": UNAVAILABLE,
        "decision_inputs_complete": False,
        "deterministic_inputs_hash": "",
        "replay_verdict": VERDICT_INCOMPLETE,
        "evidence_limits": [],
        "missing_inputs": [],
        "conflicts": [],
        "B3_integrity_replay_reused": True,
        "config_version_bound": NO,
        "config_drift_handling": "CURRENT_RUNTIME_POLICY_NOT_USED",
        "current_runtime_policy_dependence": NO,
    }


def _finish(result: dict) -> dict:
    if result["conflicts"]:
        result["replay_verdict"] = VERDICT_TAMPERED if any("HASH" in c or "INVALID" in c or "MISMATCH" in c for c in result["conflicts"]) else VERDICT_MISMATCH
    elif result["missing_inputs"]:
        result["replay_verdict"] = VERDICT_INCOMPLETE
    elif result["kx108_match"] == YES and result["binder_match"] in {YES, PARTIAL}:
        result["replay_verdict"] = VERDICT_MATCH
    elif result["kx108_match"] == NO or result["binder_match"] == NO:
        result["replay_verdict"] = VERDICT_MISMATCH
    else:
        result["replay_verdict"] = VERDICT_NOT_REPLAYABLE
    result["decision_inputs_complete"] = not result["missing_inputs"] and not result["conflicts"]
    return result


def _load_envelope(action_evidence_id: str, stores: dict) -> tuple[Optional[dict], Optional[str]]:
    return _load_json(stores["receipts"] / f"{action_evidence_id}.json")


def _load_descriptor(envelope: dict, stores: dict, result: dict) -> Optional[dict]:
    prep = envelope.get("prepare") or {}
    ref = prep.get("descriptor_ref")
    if not ref or ref == NOT_REACHED:
        result["missing_inputs"].append("DESCRIPTOR_REF_MISSING")
        return None
    record, err = _load_json(stores["v2exec"] / f"{ref}.json")
    if err:
        result["missing_inputs"].append("DESCRIPTOR_MISSING")
        return None
    if _descriptor_hash(record) != prep.get("descriptor_hash"):
        result["conflicts"].append("DESCRIPTOR_HASH_MISMATCH")
        return None
    descriptor = record.get("descriptor") or {}
    recomputed = _eah(envelope.get("operation_type", ""), descriptor)
    eah = (envelope.get("authorization") or {}).get("execution_authority_hash")
    if recomputed == eah and record.get("eah") == eah:
        result["EAH_valid"] = YES
    else:
        result["EAH_valid"] = NO
        result["conflicts"].append("EAH_MISMATCH")
    return record


def _load_approval(envelope: dict, stores: dict, result: dict) -> Optional[dict]:
    auth = envelope.get("authorization") or {}
    approval_id = auth.get("approval_id")
    if not approval_id or approval_id == NOT_REACHED:
        result["missing_inputs"].append("APPROVAL_ID_MISSING")
        return None
    record = _E.load_approval_artifact(approval_id, execution_dir=stores["approval"])
    ok, reason = _E.verify_approval_artifact(record)
    if not ok:
        result["conflicts" if reason != "APPROVAL_MISSING" else "missing_inputs"].append(reason or "APPROVAL_INVALID")
        return record
    checks = [
        record.get("approval_id") == approval_id,
        record.get("execution_authority_hash") == auth.get("execution_authority_hash"),
        record.get("approval_status") == auth.get("approval_status"),
        record.get("decision_authority") == _CRE.DECISION_AUTHORITY,
    ]
    if all(checks):
        result["approval_valid"] = YES
    else:
        result["approval_valid"] = NO
        result["conflicts"].append("APPROVAL_BINDING_MISMATCH")
    return record


def _replay_kx108_from_frozen_record(envelope: dict, approval: Optional[dict], stores: dict, result: dict) -> Optional[dict]:
    auth = envelope.get("authorization") or {}
    record_id = auth.get("kx108_pre_decision_record_id")
    if not record_id or record_id == NOT_REACHED:
        result["missing_inputs"].append("KX108_PRE_RECORD_ID_MISSING")
        return None
    record = _DS.load_kx108_decision_record(record_id, store_dir=stores["kxpre"])
    ok, reason = _DS.verify_kx108_decision_record(record)
    if not ok:
        result["conflicts" if reason != "DECISION_RECORD_MISSING" else "missing_inputs"].append(reason or "KX108_RECORD_INVALID")
        return record
    historical = auth.get("kx108_verdict")
    canonical = record.get("canonical_envelope") or {}
    replayed = canonical.get("x108_gate", record.get("x108_gate"))
    result["historical_kx108_verdict"] = historical
    result["replayed_kx108_verdict"] = replayed
    checks = [
        record.get("decision_record_id") == record_id,
        record.get("decision_record_hash") == auth.get("kx108_pre_decision_record_hash"),
        record.get("execution_authority_hash") == auth.get("execution_authority_hash"),
        record.get("x108_gate") == historical,
        replayed == historical,
    ]
    if approval is not None:
        checks.append(record.get("approval_id") == approval.get("approval_id"))
    result["kx108_match"] = YES if all(checks) else NO
    if not all(checks):
        result["conflicts"].append("KX108_REPLAY_MISMATCH")
    # Current records bind the schema/phase and canonical decision envelope, but not a separate policy version.
    if "policy_version" not in canonical and "policy_version" not in record:
        result["evidence_limits"].append("KX108_POLICY_VERSION_NOT_SEPARATELY_BOUND")
        result["config_version_bound"] = NO
    else:
        result["config_version_bound"] = YES
    return record


def _replay_binder(envelope: dict, result: dict) -> None:
    status = (envelope.get("authorization") or {}).get("binder_verdict_status")
    result["historical_binder_status"] = status or "UNKNOWN"
    if status in {"OBSERVED_INLINE", "OBSERVED_INLINE_NOT_SEPARATELY_PERSISTED", "REJECTED_INLINE"}:
        result["replayed_binder_status"] = status
        result["binder_match"] = PARTIAL
        result["evidence_limits"].append("BINDER_INLINE_STATUS_ONLY_NOT_SEPARATELY_PERSISTED")
    elif status == NOT_REACHED:
        result["replayed_binder_status"] = NOT_REACHED
        result["binder_match"] = YES
    else:
        result["replayed_binder_status"] = "UNKNOWN"
        result["binder_match"] = NO
        result["conflicts"].append("BINDER_STATUS_UNREPLAYABLE")


def _decision_inputs_hash(envelope: dict, descriptor: Optional[dict], approval: Optional[dict], kx: Optional[dict]) -> str:
    frozen = {
        "schema": RESULT_SCHEMA_VERSION,
        "action_evidence_id": envelope.get("action_evidence_id"),
        "operation_type": envelope.get("operation_type"),
        "descriptor_hash": (envelope.get("prepare") or {}).get("descriptor_hash"),
        "descriptor_eah": descriptor.get("eah") if descriptor else None,
        "physical_state_anchor": (envelope.get("prepare") or {}).get("physical_state_anchor"),
        "execution_authority_hash": (envelope.get("authorization") or {}).get("execution_authority_hash"),
        "approval_id": approval.get("approval_id") if approval else None,
        "approval_hash": approval.get("approval_record_hash") if approval else None,
        "kx108_record_id": kx.get("decision_record_id") if kx else None,
        "kx108_record_hash": kx.get("decision_record_hash") if kx else None,
        "kx108_verdict": kx.get("x108_gate") if kx else None,
        "binder_status": (envelope.get("authorization") or {}).get("binder_verdict_status"),
    }
    return _sha256_json(frozen)


def replay_governance_decision(action_evidence_id: str, *, stores_base_dir) -> dict:
    if not isinstance(action_evidence_id, str) or not _ACTION_ID_RE.match(action_evidence_id):
        r = _base_result(str(action_evidence_id), stores_base_dir)
        r["replay_verdict"] = VERDICT_NOT_FOUND
        r["missing_inputs"].append("INVALID_ACTION_EVIDENCE_ID")
        return r
    result = _base_result(action_evidence_id, stores_base_dir)
    integrity = _R3.replay_action_evidence(action_evidence_id, stores_base_dir=stores_base_dir)
    result["integrity_replay_verdict"] = integrity.get("replay_verdict")
    if integrity.get("replay_verdict") == _R3.VERDICT_NOT_FOUND:
        result["replay_verdict"] = VERDICT_NOT_FOUND
        result["missing_inputs"].append("CANONICAL_RECEIPT_MISSING")
        return result
    if integrity.get("replay_verdict") in {_R3.VERDICT_TAMPERED, _R3.VERDICT_CONFLICTING}:
        result["replay_verdict"] = VERDICT_TAMPERED
        result["conflicts"].append("B3_INTEGRITY_REPLAY_FAILED:" + str(integrity.get("replay_verdict")))
        return result
    stores = _stores(stores_base_dir)
    envelope, err = _load_envelope(action_evidence_id, stores)
    if err or envelope is None:
        result["replay_verdict"] = VERDICT_NOT_FOUND if err == "MISSING" else VERDICT_TAMPERED
        result["missing_inputs"].append("CANONICAL_RECEIPT_MISSING" if err == "MISSING" else "CANONICAL_RECEIPT_INVALID")
        return result
    descriptor = _load_descriptor(envelope, stores, result)
    approval = _load_approval(envelope, stores, result)
    kx = _replay_kx108_from_frozen_record(envelope, approval, stores, result)
    _replay_binder(envelope, result)
    result["deterministic_inputs_hash"] = _decision_inputs_hash(envelope, descriptor, approval, kx)
    return _finish(result)
