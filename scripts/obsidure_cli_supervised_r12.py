from __future__ import annotations

"""Thin Obsidure CLI client for canonical R12 supervised mission APIs."""

import json
from pathlib import Path
from typing import Any, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

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
        return _fail("AUTHORIZATION_HANDOFF_NOT_EXPOSED_IN_F7", as_json=as_json)

    return _fail("UNKNOWN_SUPERVISED_ACTION:" + action, as_json=as_json, status="REJECTED")
