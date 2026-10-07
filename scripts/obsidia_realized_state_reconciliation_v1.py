"""
obsidia_realized_state_reconciliation_v1.py
==========================================

Evidence-only realized-state reconciliation for canonical R8 receipts.

This module compares the frozen authorized effect to the persisted historical
post-observation proof. It does not authorize, execute, repair, or read any
live world state.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Callable, Optional
from urllib.parse import urlsplit, urlunsplit

import obsidia_canonical_receipt_envelope_v1 as _CRE
import obsidia_canonical_receipt_replay_v1 as _R3

RESULT_SCHEMA_VERSION = "REALIZED_STATE_RECONCILIATION_RESULT_V1"

STATUS_MATCH = "MATCH"
STATUS_NOOP_CONFIRMED = "NOOP_CONFIRMED"
STATUS_MISMATCH = "MISMATCH"
STATUS_UNCERTAIN = "UNCERTAIN"
STATUS_NOT_REALIZED = "NOT_REALIZED"
STATUS_INCOMPLETE = "INCOMPLETE"
STATUS_NOT_APPLICABLE = "NOT_APPLICABLE"
STATUS_TAMPERED = "TAMPERED"
STATUS_NOT_FOUND = "NOT_FOUND"

YES = "YES"
NO = "NO"
PARTIAL = "PARTIAL"
UNAVAILABLE = "UNAVAILABLE"

_ACTION_ID_RE = re.compile(r"^aev-[0-9a-f]{32}$")

_NEGATIVE_NOT_REALIZED = {
    _CRE.OUTCOME_KX108_HOLD,
    _CRE.OUTCOME_KX108_BLOCK,
    _CRE.OUTCOME_BINDER_REJECTED,
    _CRE.OUTCOME_PREPARE_REJECTED,
    _CRE.OUTCOME_APPROVAL_MISSING_OR_INVALID,
    _CRE.OUTCOME_TOCTOU_ABORTED,
}


def _stores(stores_base_dir) -> dict:
    base = Path(stores_base_dir)
    return {
        "v2exec": base / "v2exec",
        "receipts": base / "receipts",
    }


def _sha256_json(data: dict) -> str:
    return hashlib.sha256(
        json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()


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


def _canon_url(url: str) -> str:
    p = urlsplit(str(url or ""))
    scheme = p.scheme.lower()
    netloc = p.netloc.lower()
    path = p.path or "/"
    return urlunsplit((scheme, netloc, path, p.query, ""))


def _base_result(action_evidence_id: str, stores_base_dir) -> dict:
    return {
        "schema_version": RESULT_SCHEMA_VERSION,
        "action_evidence_id": action_evidence_id,
        "stores_base_dir": str(stores_base_dir),
        "capability": "",
        "operation_type": "",
        "public_action": "",
        "outcome": "UNKNOWN",
        "authorized_effect_available": False,
        "execution_evidence_available": False,
        "realized_state_available": False,
        "authorized_effect_hash": "",
        "realized_state_hash": "",
        "proof_strength": UNAVAILABLE,
        "reconciliation_status": STATUS_INCOMPLETE,
        "mutation_performed": None,
        "physical_effect_dispatched": None,
        "uncertainty_state": "UNKNOWN",
        "uncertainty_reason": "",
        "evidence_limits": [],
        "conflicts": [],
        "missing_evidence": [],
        "B3_integrity_reused": True,
        "integrity_replay_verdict": "",
    }


def _finish(result: dict, status: str) -> dict:
    result["reconciliation_status"] = status
    return result


def _load_envelope(action_evidence_id: str, stores: dict) -> tuple[Optional[dict], Optional[str]]:
    return _load_json(stores["receipts"] / f"{action_evidence_id}.json")


def _load_descriptor(envelope: dict, stores: dict, result: dict) -> Optional[dict]:
    prep = envelope.get("prepare") or {}
    ref = prep.get("descriptor_ref")
    if not ref or ref in {_CRE.STATUS_NOT_REACHED, _CRE.STATUS_NOT_APPLICABLE}:
        result["missing_evidence"].append("DESCRIPTOR_REF_MISSING")
        return None
    record, err = _load_json(stores["v2exec"] / f"{ref}.json")
    if err:
        result["missing_evidence"].append("DESCRIPTOR_MISSING")
        return None
    actual = hashlib.sha256(json.dumps(record, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
    if actual != prep.get("descriptor_hash"):
        result["conflicts"].append("DESCRIPTOR_HASH_MISMATCH")
        return None
    return record.get("descriptor") or {}


def _hydrate_common(result: dict, envelope: dict) -> None:
    realized = envelope.get("realized_state") or {}
    execution = envelope.get("execution") or {}
    result["capability"] = envelope.get("capability", "")
    result["operation_type"] = envelope.get("operation_type", "")
    result["public_action"] = (envelope.get("request_ref") or {}).get("public_action", "")
    result["outcome"] = realized.get("outcome", "UNKNOWN")
    result["execution_evidence_available"] = bool(execution)
    result["realized_state_available"] = bool(realized)
    result["proof_strength"] = realized.get("proof_strength", UNAVAILABLE)
    result["mutation_performed"] = realized.get("mutation_performed")
    result["physical_effect_dispatched"] = realized.get("physical_effect_dispatched")
    result["uncertainty_state"] = realized.get("uncertainty_state", "UNKNOWN")
    result["uncertainty_reason"] = realized.get("uncertainty_reason", "")
    result["realized_state_hash"] = realized.get("post_state_hash") or realized.get("transport_evidence_hash") or ""


def _authorized(result: dict, payload: dict) -> dict:
    result["authorized_effect_available"] = True
    result["authorized_effect_hash"] = _sha256_json(payload)
    return payload


def _realized(result: dict, payload: dict) -> dict:
    result["realized_state_available"] = True
    if not result["realized_state_hash"]:
        result["realized_state_hash"] = _sha256_json(payload)
    return payload


def _missing(result: dict, reason: str) -> dict:
    result["missing_evidence"].append(reason)
    return _finish(result, STATUS_INCOMPLETE)


def _checkbox_adapter(envelope: dict, descriptor: dict, result: dict) -> dict:
    target = descriptor.get("target_checked", (envelope.get("request_ref") or {}).get("target_checked"))
    if not isinstance(target, bool):
        return _missing(result, "AUTHORIZED_TARGET_CHECKED_MISSING")
    _authorized(result, {"public_action": "BROWSER_SET_CHECKED", "target_checked": target})
    post = (envelope.get("realized_state") or {}).get("post_state_ref") or {}
    if "checked" not in post:
        return _missing(result, "POST_CHECKED_MISSING")
    got = _realized(result, {"checked": post.get("checked"), "element_identity_hash": post.get("element_identity_hash")})
    if got["checked"] != target:
        return _finish(result, STATUS_MISMATCH)
    if result["outcome"] == _CRE.OUTCOME_NOOP and result["mutation_performed"] is False:
        return _finish(result, STATUS_NOOP_CONFIRMED)
    return _finish(result, STATUS_MATCH)


def _field_adapter(envelope: dict, descriptor: dict, result: dict) -> dict:
    target_hash = descriptor.get("target_value_sha256")
    target_length = descriptor.get("target_value_length")
    if not target_hash or target_length is None:
        return _missing(result, "AUTHORIZED_TARGET_VALUE_HASH_OR_LENGTH_MISSING")
    _authorized(result, {
        "public_action": "BROWSER_SET_FIELD_VALUE",
        "target_value_sha256": target_hash,
        "target_value_length": target_length,
    })
    realized = envelope.get("realized_state") or {}
    post = realized.get("post_state_ref") or {}
    post_hash = post.get("post_value_sha256") or post.get("current_value_sha256") or realized.get("post_value_sha256")
    post_length = post.get("post_value_length")
    if post_length is None:
        post_length = post.get("current_value_length", realized.get("post_value_length"))
    if not post_hash or post_length is None:
        return _missing(result, "POST_VALUE_HASH_OR_LENGTH_MISSING")
    _realized(result, {"post_value_sha256": post_hash, "post_value_length": post_length})
    if post_hash == target_hash and post_length == target_length:
        if result["outcome"] == _CRE.OUTCOME_NOOP and result["mutation_performed"] is False:
            return _finish(result, STATUS_NOOP_CONFIRMED)
        return _finish(result, STATUS_MATCH)
    return _finish(result, STATUS_MISMATCH)


def _navigate_adapter(envelope: dict, descriptor: dict, result: dict) -> dict:
    target = descriptor.get("canon_requested_url") or descriptor.get("requested_url")
    if not target:
        return _missing(result, "AUTHORIZED_NAVIGATION_TARGET_MISSING")
    target_canon = _canon_url(target)
    _authorized(result, {"public_action": "BROWSER_NAVIGATE", "canon_requested_url": target_canon})
    realized = envelope.get("realized_state") or {}
    post = realized.get("post_state_ref") or {}
    post_url = post.get("post_url") or post.get("url") or realized.get("post_url")
    if not post_url:
        return _missing(result, "POST_NAVIGATION_URL_MISSING")
    got = _realized(result, {"post_url": _canon_url(post_url)})
    return _finish(result, STATUS_MATCH if got["post_url"] == target_canon else STATUS_MISMATCH)


def _submit_adapter(envelope: dict, descriptor: dict, result: dict) -> dict:
    action_hash = descriptor.get("resolved_action_hash")
    manifest_hash = descriptor.get("field_manifest_hash")
    if not action_hash or not manifest_hash:
        return _missing(result, "AUTHORIZED_SUBMIT_HASHES_MISSING")
    _authorized(result, {
        "public_action": "BROWSER_SUBMIT_FORM_NAVIGATION_V0",
        "field_manifest_hash": manifest_hash,
        "resolved_action_hash": action_hash,
    })
    execution = envelope.get("execution") or {}
    realized = envelope.get("realized_state") or {}
    state = realized.get("execution_state") or execution.get("execution_state")
    result["uncertainty_state"] = realized.get("uncertainty_state") or state or "UNKNOWN"
    if state == "DISPATCHED_OUTCOME_UNCERTAIN":
        result["evidence_limits"].append("APPLICATION_SUCCESS_NOT_CLAIMED")
        return _finish(result, STATUS_UNCERTAIN)
    if state in {"DISPATCHED", "RESPONSE_OBSERVED"}:
        result["evidence_limits"].append("APPLICATION_SUCCESS_NOT_CLAIMED")
        return _finish(result, STATUS_UNCERTAIN)
    if state == "POSTCONDITION_CONFIRMED":
        transport = execution.get("transport_evidence_ref") or realized.get("transport_evidence_ref") or {}
        final_hash = transport.get("final_url_hash") or realized.get("final_url_hash")
        nav_proof = transport.get("navigation_proof") or realized.get("navigation_proof") or result["proof_strength"]
        if final_hash and nav_proof in {"STRONG", "CONFIRMED"}:
            _realized(result, {"final_url_hash": final_hash, "navigation_proof": nav_proof})
            result["evidence_limits"].append("APPLICATION_SUCCESS_NOT_CLAIMED")
            return _finish(result, STATUS_MATCH)
        return _missing(result, "SUBMIT_POSTCONDITION_PROOF_MISSING")
    return _missing(result, "SUBMIT_EXECUTION_STATE_MISSING_OR_UNSUPPORTED")


_ADAPTERS: dict[str, Callable[[dict, dict, dict], dict]] = {
    "BROWSER_SET_CHECKED": _checkbox_adapter,
    "V2_BROWSER_SET_CHECKED": _checkbox_adapter,
    "BROWSER_SET_FIELD_VALUE": _field_adapter,
    "V2_BROWSER_SET_FIELD_VALUE": _field_adapter,
    "BROWSER_NAVIGATE": _navigate_adapter,
    "V2_BROWSER_NAVIGATE": _navigate_adapter,
    "BROWSER_SUBMIT_FORM_NAVIGATION_V0": _submit_adapter,
    "V2_BROWSER_SUBMIT_FORM_NAVIGATION": _submit_adapter,
}


def reconcile_action_evidence(action_evidence_id: str, *, stores_base_dir) -> dict:
    if not isinstance(action_evidence_id, str) or not _ACTION_ID_RE.match(action_evidence_id):
        r = _base_result(str(action_evidence_id), stores_base_dir)
        r["missing_evidence"].append("INVALID_ACTION_EVIDENCE_ID")
        return _finish(r, STATUS_NOT_FOUND)

    result = _base_result(action_evidence_id, stores_base_dir)
    integrity = _R3.replay_action_evidence(action_evidence_id, stores_base_dir=stores_base_dir)
    verdict = integrity.get("replay_verdict")
    result["integrity_replay_verdict"] = verdict or ""
    if verdict == _R3.VERDICT_NOT_FOUND:
        result["missing_evidence"].append("CANONICAL_RECEIPT_MISSING")
        return _finish(result, STATUS_NOT_FOUND)
    if verdict in {_R3.VERDICT_TAMPERED, _R3.VERDICT_CONFLICTING}:
        result["conflicts"].append("B3_INTEGRITY_REPLAY_FAILED:" + str(verdict))
        return _finish(result, STATUS_TAMPERED)

    stores = _stores(stores_base_dir)
    envelope, err = _load_envelope(action_evidence_id, stores)
    if err or envelope is None:
        result["missing_evidence"].append("CANONICAL_RECEIPT_MISSING" if err == "MISSING" else "CANONICAL_RECEIPT_INVALID")
        return _finish(result, STATUS_NOT_FOUND if err == "MISSING" else STATUS_TAMPERED)

    _hydrate_common(result, envelope)
    outcome = result["outcome"]
    if outcome in _NEGATIVE_NOT_REALIZED and result["physical_effect_dispatched"] is not True:
        return _finish(result, STATUS_NOT_REALIZED)
    if outcome == _CRE.OUTCOME_EXECUTOR_FAILED_BEFORE_ACTION and result["physical_effect_dispatched"] is False:
        return _finish(result, STATUS_NOT_REALIZED)
    if result["uncertainty_state"] == _CRE.OUTCOME_DISPATCHED_OUTCOME_UNCERTAIN:
        return _finish(result, STATUS_UNCERTAIN)

    descriptor = _load_descriptor(envelope, stores, result)
    if result["conflicts"]:
        return _finish(result, STATUS_TAMPERED)
    if descriptor is None:
        return _finish(result, STATUS_INCOMPLETE)

    action = result["public_action"] or result["operation_type"]
    adapter = _ADAPTERS.get(action) or _ADAPTERS.get(result["operation_type"])
    if adapter is None:
        result["evidence_limits"].append("RECONCILIATION_ADAPTER_NOT_REGISTERED")
        return _finish(result, STATUS_NOT_APPLICABLE)
    return adapter(envelope, descriptor, result)
