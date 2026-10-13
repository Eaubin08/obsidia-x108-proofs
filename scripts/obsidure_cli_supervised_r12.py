from __future__ import annotations

"""Thin Obsidure CLI client for canonical R12 supervised mission APIs."""

import json
from pathlib import Path
from typing import Any, Mapping
from dataclasses import fields
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import re

SCHEMA_VERSION = "OBSIDURE_CLI_SUPERVISED_R12_CLIENT_V1"
DECISION_AUTHORITY = "KX108_ONLY"

NO_AUTHORITY = {
    "approval_created": False,
    "executor_invoked": False,
    "physical_mutation": False,
    "kx108_called_by_cli": False,
    "binder_mutation": False,
    "memory_write": False,
    "native_memory_write": False,
    "automatic_retry": False,
    "commit_created": False,
    "push_performed": False,
    "merge_performed": False,
}

_HEX64 = re.compile(r"^[0-9a-f]{64}$")


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _emit(payload: Mapping[str, Any], *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return
    print(f"status={payload.get('status') or payload.get('state') or 'UNKNOWN'}")
    if payload.get("reason"):
        print(f"reason={payload['reason']}")
    for key in ("mission_id", "checkpoint_id", "ticket_id", "unique_next_ticket_id"):
        if payload.get(key):
            print(f"{key}={payload[key]}")


def _fail(reason: str, *, as_json: bool, status: str = "HOLD", **extra: Any) -> int:
    _emit(
        {
            "schema_version": SCHEMA_VERSION,
            "status": status,
            "reason": reason,
            "decision_authority": DECISION_AUTHORITY,
            **NO_AUTHORITY,
            **extra,
        },
        as_json=as_json,
    )
    return 1


def _api_json(
    api: str,
    method: str,
    path: str,
    *,
    query: Mapping[str, Any] | None = None,
    body: Mapping[str, Any] | None = None,
) -> tuple[int, dict[str, Any]]:
    url = str(api or "http://127.0.0.1:8000").rstrip("/") + path
    clean_query = {k: v for k, v in dict(query or {}).items() if v not in (None, "")}
    if clean_query:
        url += "?" + urlencode(clean_query)
    headers = {"Accept": "application/json"}
    data = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(req, timeout=30) as response:
            raw = response.read().decode("utf-8")
            return int(response.status), json.loads(raw) if raw else {}
    except HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            payload = {"detail": raw}
        if isinstance(payload.get("detail"), dict):
            payload = dict(payload["detail"])
        return int(exc.code), payload
    except (OSError, URLError) as exc:
        return 0, {"status": "UNAVAILABLE", "reason": f"API_UNAVAILABLE:{type(exc).__name__}:{exc}"}


def _load_payload(path: str | None) -> tuple[dict[str, Any] | None, str | None]:
    if not path:
        return None, "PAYLOAD_FILE_REQUIRED"
    p = Path(path)
    if not p.exists() or not p.is_file():
        return None, "PAYLOAD_FILE_NOT_FOUND"
    try:
        payload = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return None, f"PAYLOAD_FILE_UNREADABLE:{type(exc).__name__}"
    if not isinstance(payload, dict):
        return None, "PAYLOAD_MUST_BE_JSON_OBJECT"
    return payload, None


def _projection_selector(args: Mapping[str, Any]) -> tuple[str | None, dict[str, Any], str | None]:
    mission_id = str(args.get("mission_id") or "").strip()
    checkpoint_id = str(args.get("checkpoint_id") or "").strip()
    if mission_id and checkpoint_id:
        return f"/api/supervised-missions/{mission_id}/projection", {"checkpoint_id": checkpoint_id}, None
    if checkpoint_id:
        return f"/api/supervised-missions/checkpoints/{checkpoint_id}/projection", {}, None
    return None, {}, "MISSION_ID_OR_CHECKPOINT_ID_REQUIRED"


def _holds(projection: Mapping[str, Any]) -> dict[str, Any]:
    tickets = projection.get("tickets") if isinstance(projection.get("tickets"), list) else []
    return {
        "status": "PROJECTED",
        "mission_id": projection.get("mission_id"),
        "checkpoint_id": (projection.get("checkpoint") or {}).get("checkpoint_id")
        if isinstance(projection.get("checkpoint"), Mapping)
        else None,
        "unique_next_ticket_id": projection.get("unique_next_ticket_id"),
        "hold": projection.get("hold"),
        "ticket_holds": [
            {
                "ticket_id": ticket.get("ticket_id"),
                "phase": ticket.get("phase"),
                "status": ticket.get("status"),
                "hold_reason": ticket.get("hold_reason"),
            }
            for ticket in tickets
            if isinstance(ticket, Mapping)
            and (ticket.get("hold_reason") or str(ticket.get("status") or "").upper() in {"HOLD", "BLOCKED"})
        ],
    }


def _evidence(projection: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "status": "PROJECTED",
        "mission_id": projection.get("mission_id"),
        "checkpoint": projection.get("checkpoint"),
        "evidence": projection.get("evidence"),
        "verification": projection.get("verification"),
        "binder_replay": projection.get("binder_replay"),
        "completion": projection.get("completion"),
        "execution_observed_is_verified": False,
    }


def _ticket(projection: Mapping[str, Any], ticket_id: str) -> Mapping[str, Any] | None:
    for item in projection.get("tickets") or ():
        if isinstance(item, Mapping) and str(item.get("ticket_id") or "") == ticket_id:
            return item
    return None


def _projection_patch_hash(projection: Mapping[str, Any], ticket: Mapping[str, Any]) -> str:
    evidence_refs = [str(item) for item in _as_list(ticket.get("evidence_refs"))]
    evidence = projection.get("evidence") if isinstance(projection.get("evidence"), Mapping) else {}
    evidence_refs.extend(str(item) for item in _as_list(evidence.get("evidence_refs")))
    for ref in evidence_refs:
        if _HEX64.fullmatch(ref.lower()):
            return ref.lower()
    return ""


def _projection_action_evidence_refs(projection: Mapping[str, Any], ticket: Mapping[str, Any]) -> list[str]:
    refs: list[str] = []
    for value in (ticket.get("action_evidence_id"), ticket.get("action_evidence_ref")):
        if isinstance(value, str) and value.strip():
            refs.append(value.strip())
    for value in _as_list(ticket.get("action_evidence_refs")) + _as_list(ticket.get("evidence_refs")):
        if isinstance(value, str) and value.startswith("aev-"):
            refs.append(value)
    evidence = projection.get("evidence") if isinstance(projection.get("evidence"), Mapping) else {}
    for key in ("action_evidence_id", "action_evidence_ref"):
        value = evidence.get(key)
        if isinstance(value, str) and value.strip():
            refs.append(value.strip())
    for key in ("action_evidence_refs", "evidence_refs"):
        for value in _as_list(evidence.get(key)):
            if isinstance(value, str) and value.startswith("aev-"):
                refs.append(value)
    return list(dict.fromkeys(refs))


def _dict_for_dataclass(cls: Any, data: Mapping[str, Any]) -> dict[str, Any]:
    allowed = {field.name for field in fields(cls)}
    return {key: value for key, value in data.items() if key in allowed}


def _load_repair_outcome_context(path_raw: str | None) -> tuple[dict[str, Any] | None, str | None]:
    if not path_raw:
        return None, "REPAIR_CONTEXT_FILE_REQUIRED"
    path = Path(path_raw)
    if not path.exists() or not path.is_file():
        return None, "REPAIR_CONTEXT_FILE_NOT_FOUND"
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return None, f"REPAIR_CONTEXT_FILE_UNREADABLE:{type(exc).__name__}"
    if not isinstance(raw, Mapping):
        return None, "REPAIR_CONTEXT_MUST_BE_JSON_OBJECT"
    required = ("repair_request", "repair_proposal", "repair_verdict", "prepared_repair")
    missing = [key for key in required if not isinstance(raw.get(key), Mapping)]
    if missing:
        return None, "REPAIR_CONTEXT_INCOMPLETE:" + ",".join(missing)

    try:
        from periphery.agents.agent_obsidure import AgentObsidure
        from periphery.agents.obsidure_repair_contract import (
            ErrorContextRecord,
            RepairRequest,
            RepairVerdict,
            repair_proposal_from_dict,
        )

        request_data = dict(raw["repair_request"])
        request_data["error_contexts"] = [
            ErrorContextRecord(**_dict_for_dataclass(ErrorContextRecord, item))
            for item in request_data.get("error_contexts", []) or []
            if isinstance(item, Mapping)
        ]
        request = RepairRequest(**_dict_for_dataclass(RepairRequest, request_data))
        proposal = repair_proposal_from_dict(dict(raw["repair_proposal"]))
        verdict = RepairVerdict(**_dict_for_dataclass(RepairVerdict, dict(raw["repair_verdict"])))
        agent = AgentObsidure(api_base="http://127.0.0.1:1", verbose=False)
        agent._last_repair_request = request
        agent._last_repair_proposal = proposal
        agent._last_repair_verdict = verdict
    except Exception as exc:
        return None, f"REPAIR_CONTEXT_INVALID:{type(exc).__name__}:{exc}"

    return {
        "agent": agent,
        "prepared_repair": dict(raw["prepared_repair"]),
        "mission_context": dict(raw.get("mission_context") or {}) if isinstance(raw.get("mission_context"), Mapping) else None,
        "repair_budget": raw.get("repair_budget") if isinstance(raw.get("repair_budget"), int) else None,
        "attempt_history": tuple(item for item in (raw.get("attempt_history") or ()) if isinstance(item, Mapping)),
    }, None


def _inspect_outcome_projection(
    *,
    api: str,
    mission_id: str,
    checkpoint_id: str,
    ticket_id: str,
    action_evidence_id: str,
) -> tuple[dict[str, Any] | None, str | None]:
    status, projection = _api_json(
        api,
        "GET",
        f"/api/supervised-missions/{mission_id}/projection",
        query={"checkpoint_id": checkpoint_id},
    )
    if not 200 <= status < 300:
        return None, str(projection.get("reason") or projection.get("detail") or "OUTCOME_PROJECTION_UNAVAILABLE")
    if str(projection.get("mission_id") or "") != mission_id:
        return None, "MISSION_PROJECTION_MISMATCH"
    checkpoint = projection.get("checkpoint") if isinstance(projection.get("checkpoint"), Mapping) else {}
    if str(checkpoint.get("checkpoint_id") or "") != checkpoint_id:
        return None, "CHECKPOINT_PROJECTION_MISMATCH"
    ticket = _ticket(projection, ticket_id)
    if ticket is None:
        return None, "TICKET_PROJECTION_NOT_FOUND"
    refs = _projection_action_evidence_refs(projection, ticket)
    if not refs:
        return None, "ACTION_EVIDENCE_REFERENCE_NOT_VISIBLE"
    if action_evidence_id not in refs:
        return None, "ACTION_EVIDENCE_ID_PROJECTION_MISMATCH"
    return {
        "projection": projection,
        "ticket": dict(ticket),
        "visible_action_evidence_refs": refs,
    }, None


def _r10_outcome_payload(
    *,
    mission_id: str,
    checkpoint_id: str,
    ticket_id: str,
    projection_context: Mapping[str, Any],
    r10_feedback: Mapping[str, Any],
) -> dict[str, Any]:
    classification = str(r10_feedback.get("derived_outcome_classification") or "EVIDENCE_INCOMPLETE")
    recommendation = str(r10_feedback.get("recommendation") or "ESCALATE")
    limited = bool(r10_feedback.get("limited_verdict"))
    status = "R10_OUTCOME_INGESTED" if str(r10_feedback.get("status") or "").endswith("INGESTED") else "HOLD"
    return {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "mission_id": mission_id,
        "checkpoint_id": checkpoint_id,
        "ticket_id": ticket_id,
        "decision_authority": DECISION_AUTHORITY,
        "r10_outcome_feedback": dict(r10_feedback),
        "derived_outcome_classification": classification,
        "recommendation": recommendation,
        "limited_verdict": limited,
        "binder_limitations_preserved": limited or bool(r10_feedback.get("r8_evidence_limits")),
        "executed_verified": classification == "EXECUTED_VERIFIED",
        "stop_success": classification == "EXECUTED_VERIFIED" and recommendation == "STOP_SUCCESS",
        "evidence_incomplete": classification == "EVIDENCE_INCOMPLETE",
        "outcome_uncertain": classification == "DISPATCHED_OUTCOME_UNCERTAIN",
        "pre_dispatch_retry_candidate": classification == "PRE_DISPATCH_FAILURE" and recommendation == "RETRY_CANDIDATE",
        "execution_observed_is_verified": False,
        "http_success_is_closure": False,
        "verified": False,
        "closed": False,
        "mission_done_verified": False,
        "projection_context": dict(projection_context),
        **NO_AUTHORITY,
    }


def _pre_authorize_inspection(
    *,
    api: str,
    mission_id: str,
    checkpoint_id: str,
    ticket_id: str,
    execution_authority_hash: str,
) -> tuple[dict[str, Any] | None, str | None]:
    status, projection = _api_json(
        api,
        "GET",
        f"/api/supervised-missions/{mission_id}/projection",
        query={"checkpoint_id": checkpoint_id},
    )
    if not 200 <= status < 300:
        reason = str(projection.get("reason") or projection.get("detail") or "PRE_AUTH_INSPECTION_UNAVAILABLE")
        return None, reason
    if str(projection.get("mission_id") or "") != mission_id:
        return None, "MISSION_PROJECTION_MISMATCH"
    checkpoint = projection.get("checkpoint") if isinstance(projection.get("checkpoint"), Mapping) else {}
    if str(checkpoint.get("checkpoint_id") or "") != checkpoint_id:
        return None, "CHECKPOINT_PROJECTION_MISMATCH"
    mandate = projection.get("mandate") if isinstance(projection.get("mandate"), Mapping) else {}
    if mandate.get("revoked") is True or str(mandate.get("status") or "").upper() == "REVOKED":
        return None, "HUMAN_MANDATE_REVOKED"
    ticket = _ticket(projection, ticket_id)
    if ticket is None:
        return None, "PREPARED_TICKET_NOT_FOUND"
    if ticket.get("action_evidence_id"):
        return None, "DUPLICATE_EXECUTION_REQUIRES_RECONCILIATION"
    if str(ticket.get("phase") or "").upper() not in {"PREPARED", "PREPARED_AWAITING_APPROVAL"}:
        return None, "TICKET_NOT_PREPARED_AWAITING_APPROVAL"
    patch_hash = _projection_patch_hash(projection, ticket)
    if not patch_hash:
        return None, "PREPARED_PATCH_HASH_NOT_VISIBLE"
    if not _HEX64.fullmatch(execution_authority_hash):
        return None, "EXECUTION_AUTHORITY_HASH_INVALID"
    return {
        "projection": projection,
        "ticket": dict(ticket),
        "mission_id": mission_id,
        "checkpoint_id": checkpoint_id,
        "ticket_id": ticket_id,
        "project": projection.get("project") if isinstance(projection.get("project"), Mapping) else {},
        "patch_hash": patch_hash,
        "execution_authority_hash": execution_authority_hash,
        "hold": projection.get("hold") if isinstance(projection.get("hold"), Mapping) else {},
        "binder_replay": projection.get("binder_replay") if isinstance(projection.get("binder_replay"), Mapping) else {},
        "verification": projection.get("verification") if isinstance(projection.get("verification"), Mapping) else {},
    }, None


def _safe_status(payload: Mapping[str, Any]) -> bool:
    state = str(payload.get("state") or "").upper()
    status = str(payload.get("status") or "").upper()
    return state not in {"HOLD", "REJECTED", "UNKNOWN", "UNAVAILABLE"} and "REJECTED" not in status and "HELD" not in status


def run_supervised(action: str, api: str, args: dict[str, Any]) -> int:
    as_json = bool(args.get("json"))
    action = str(action or "").strip().lower()

    if action == "prepare":
        payload, reason = _load_payload(args.get("payload_file"))
        if reason:
            return _fail(reason, as_json=as_json, status="REJECTED")
        status, payload = _api_json(api, "POST", "/api/supervised-missions/prepare-only", body=payload)
        payload.setdefault("schema_version", SCHEMA_VERSION)
        payload.setdefault("decision_authority", DECISION_AUTHORITY)
        payload.update({k: payload.get(k, v) for k, v in NO_AUTHORITY.items()})
        _emit(payload, as_json=as_json)
        state = str(payload.get("state") or payload.get("status") or "").upper()
        return 0 if 200 <= status < 300 and state not in {"HOLD", "REJECTED", "UNAVAILABLE"} else 1

    if action in {"status", "inspect", "holds", "evidence"}:
        path, query, reason = _projection_selector(args)
        if reason or path is None:
            return _fail(reason or "PROJECTION_SELECTOR_REQUIRED", as_json=as_json, status="REJECTED")
        status, payload = _api_json(api, "GET", path, query=query)
        if not 200 <= status < 300:
            payload.setdefault("status", "HOLD")
            payload.setdefault("reason", "PROJECTION_UNAVAILABLE")
            _emit(payload, as_json=as_json)
            return 1
        if action == "holds":
            payload = _holds(payload)
        elif action == "evidence":
            payload = _evidence(payload)
        payload.setdefault("schema_version", SCHEMA_VERSION)
        payload.setdefault("decision_authority", DECISION_AUTHORITY)
        payload.update({k: payload.get(k, v) for k, v in NO_AUTHORITY.items()})
        _emit(payload, as_json=as_json)
        return 0

    if action == "verification":
        mission_id = str(args.get("mission_id") or "").strip()
        checkpoint_id = str(args.get("checkpoint_id") or "").strip()
        ticket_id = str(args.get("ticket_id") or "").strip()
        if not (mission_id and checkpoint_id and ticket_id):
            return _fail("MISSION_CHECKPOINT_AND_TICKET_REQUIRED", as_json=as_json, status="REJECTED")
        status, payload = _api_json(
            api,
            "GET",
            f"/api/supervised-missions/{mission_id}/verification-projection",
            query={"checkpoint_id": checkpoint_id, "ticket_id": ticket_id},
        )
        payload.setdefault("schema_version", SCHEMA_VERSION)
        payload.setdefault("decision_authority", DECISION_AUTHORITY)
        payload.update({k: payload.get(k, v) for k, v in NO_AUTHORITY.items()})
        _emit(payload, as_json=as_json)
        return 0 if 200 <= status < 300 else 1

    if action == "outcome":
        mission_id = str(args.get("mission_id") or "").strip()
        checkpoint_id = str(args.get("checkpoint_id") or "").strip()
        ticket_id = str(args.get("ticket_id") or "").strip()
        action_evidence_id = str(args.get("action_evidence_id") or "").strip()
        stores_base_dir = str(args.get("stores_base_dir") or "").strip()
        if not (mission_id and checkpoint_id and ticket_id):
            return _fail("MISSION_CHECKPOINT_AND_TICKET_REQUIRED", as_json=as_json, status="REJECTED")
        if not action_evidence_id:
            return _fail("ACTION_EVIDENCE_ID_REQUIRED", as_json=as_json, status="REJECTED")
        if not stores_base_dir:
            return _fail("STORES_BASE_DIR_REQUIRED", as_json=as_json, status="REJECTED")

        projection_context, reason = _inspect_outcome_projection(
            api=api,
            mission_id=mission_id,
            checkpoint_id=checkpoint_id,
            ticket_id=ticket_id,
            action_evidence_id=action_evidence_id,
        )
        if projection_context is None:
            return _fail(reason or "OUTCOME_PROJECTION_INSPECTION_FAILED", as_json=as_json)

        context, reason = _load_repair_outcome_context(args.get("repair_context_file"))
        if context is None:
            return _fail(reason or "REPAIR_CONTEXT_INVALID", as_json=as_json, status="REJECTED")

        agent = context["agent"]
        r10_feedback = agent.ingest_repair_execution_outcome(
            action_evidence_id=action_evidence_id,
            stores_base_dir=stores_base_dir,
            prepared_repair=context["prepared_repair"],
            mission_context=context.get("mission_context"),
            repair_budget=context.get("repair_budget"),
            attempt_history=context.get("attempt_history") or (),
        )
        payload = _r10_outcome_payload(
            mission_id=mission_id,
            checkpoint_id=checkpoint_id,
            ticket_id=ticket_id,
            projection_context=projection_context,
            r10_feedback=r10_feedback,
        )
        _emit(payload, as_json=as_json)
        return 0 if payload["stop_success"] else 1

    if action == "authorize":
        mission_id = str(args.get("mission_id") or "").strip()
        checkpoint_id = str(args.get("checkpoint_id") or "").strip()
        ticket_id = str(args.get("ticket_id") or "").strip()
        execution_authority_hash = str(args.get("execution_authority_hash") or "").lower().strip()
        human_authorization_reference = str(args.get("human_authorization_reference") or "").strip()
        if not bool(args.get("confirm_human_authorization")):
            return _fail("EXPLICIT_HUMAN_AUTHORIZATION_CONFIRMATION_REQUIRED", as_json=as_json, status="REJECTED")
        if not (mission_id and checkpoint_id and ticket_id):
            return _fail("MISSION_CHECKPOINT_AND_TICKET_REQUIRED", as_json=as_json, status="REJECTED")
        if not execution_authority_hash or not human_authorization_reference:
            return _fail("EXECUTION_AUTHORITY_HASH_AND_HUMAN_REFERENCE_REQUIRED", as_json=as_json, status="REJECTED")

        inspection, reason = _pre_authorize_inspection(
            api=api,
            mission_id=mission_id,
            checkpoint_id=checkpoint_id,
            ticket_id=ticket_id,
            execution_authority_hash=execution_authority_hash,
        )
        if inspection is None:
            return _fail(reason or "PRE_AUTH_INSPECTION_FAILED", as_json=as_json)

        body = {
            "checkpoint_id": checkpoint_id,
            "ticket_id": ticket_id,
            "execution_authority_hash": execution_authority_hash,
            "human_authorization_reference": human_authorization_reference,
            "session_id": str(args.get("session_id") or "obsidure-cli-f8b"),
        }
        status, payload = _api_json(api, "POST", f"/api/supervised-missions/{mission_id}/authorize-execution", body=body)
        if not 200 <= status < 300:
            payload["status"] = "UNKNOWN"
            payload["state"] = "UNKNOWN"
            payload.setdefault("reason", "POST_AUTHORIZATION_RESPONSE_UNAVAILABLE")
            payload["post_authorization_response_lost"] = True
        payload.setdefault("schema_version", SCHEMA_VERSION)
        payload.setdefault("decision_authority", DECISION_AUTHORITY)
        payload.setdefault("pre_authorization_inspection", inspection)
        payload.update({k: payload.get(k, v) for k, v in NO_AUTHORITY.items()})

        followup_status, followup = _api_json(
            api,
            "GET",
            f"/api/supervised-missions/{mission_id}/projection",
            query={"checkpoint_id": str(payload.get("checkpoint_id") or checkpoint_id)},
        )
        if 200 <= followup_status < 300:
            payload["post_authorization_projection"] = followup
        else:
            payload["post_authorization_projection"] = {
                "status": "UNKNOWN",
                "reason": str(followup.get("reason") or "POST_AUTH_PROJECTION_UNAVAILABLE"),
            }
            payload["state"] = "UNKNOWN"
            payload["reason"] = payload.get("reason") or "POST_AUTH_PROJECTION_UNAVAILABLE"
        payload["execution_observed_is_verified"] = False
        payload["http_success_is_closure"] = False
        payload["verified"] = False
        payload["closed"] = False
        payload["mission_done_verified"] = False
        _emit(payload, as_json=as_json)
        return 0 if 200 <= status < 300 and _safe_status(payload) else 1

    return _fail("UNKNOWN_SUPERVISED_ACTION:" + action, as_json=as_json, status="REJECTED")
