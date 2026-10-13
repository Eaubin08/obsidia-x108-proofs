from __future__ import annotations

"""Thin Obsidure CLI client for canonical R12 supervised mission APIs."""

import json
from pathlib import Path
from typing import Any, Mapping
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
    if str(ticket.get("phase") or "").upper() not in {"PREPARED", "PREPARED_AWAITING_APPROVAL"}:
        return None, "TICKET_NOT_PREPARED_AWAITING_APPROVAL"
    if ticket.get("action_evidence_id"):
        return None, "DUPLICATE_EXECUTION_REQUIRES_RECONCILIATION"
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
