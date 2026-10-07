"""Generate one exact governed Google Calendar pilot invocation envelope V0.

This script performs no network call. It runs the real Obsidia governance
chain up to the external connector boundary and prints one JSON packet that a
Google Calendar transport can execute exactly.

User authorization basis:
- explicit "go" for the low-risk real Calendar pilot on 2026-10-07.

No credentials or personal email address are included.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import tempfile
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
for candidate in (ROOT, SCRIPTS):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from obsidia_world_action_pre_execution_v0 import (  # noqa: E402
    run_world_action_pre_execution_v0,
)
from periphery.world_calls.external_runtime_activation_policy_v0 import (  # noqa: E402
    build_activation_policy_v0,
)
from periphery.world_calls.google_calendar_connector_adapter_v0 import (  # noqa: E402
    CONNECTOR_ACTION_CREATE,
    CONNECTOR_ID,
    REQUIRED_SCOPE_CREATE,
    build_google_calendar_invocation_v0,
    canonical_google_calendar_call_hash,
)
from periphery.world_calls.live_sovereign_ticket_v0 import (  # noqa: E402
    issue_live_sovereign_ticket_v0,
)


def h(value) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            ensure_ascii=False,
            default=str,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


def build_connector_args() -> dict:
    return {
        "calendar_id": "primary",
        "title": "[OBSIDIA PILOT] Governed Calendar Adapter V0",
        "attendees": [],
        "start_time": "2026-10-08T12:30:00+02:00",
        "end_time": "2026-10-08T12:45:00+02:00",
        "timezone_str": "Europe/Paris",
        "description": (
            "Pilote réel Obsidia WORLD_ACTION Google Calendar adapter V0. "
            "Sans invité, sans notification externe; suppression après "
            "lecture de vérification."
        ),
        "visibility": "private",
        "transparency": "transparent",
        "add_google_meet": False,
        "self_attendance": "omit",
        "reminders": {"use_default": False, "overrides": []},
    }


def build_request(connector_args: dict) -> dict:
    target_ref = "google-calendar:primary:test-event"
    target_prestate_hash = h(
        {
            "calendar": "primary",
            "pilot_slot": "2026-10-08T12:30:00+02:00",
            "expected_state": "NO_OBSIDIA_PILOT_EVENT",
        }
    )
    proposal_hash = h(
        {
            "domain": "administration",
            "surface": "CALENDAR",
            "operation": "CREATE_TEST_EVENT",
            "pilot": "GOOGLE_CALENDAR_ADAPTER_V0",
        }
    )
    connector_call_hash = canonical_google_calendar_call_hash(connector_args)
    idempotency_key = h(
        {
            "schema": "UNIVERSAL_WORLD_ACTION_IDEMPOTENCY_V0",
            "proposal_hash": proposal_hash,
            "connector_call_hash": connector_call_hash,
            "target_prestate_hash": target_prestate_hash,
            "required_scope": REQUIRED_SCOPE_CREATE,
        }
    )
    request = {
        "request_id": "world-calendar-real-adapter-pilot-v0",
        "proposal_id": "proposal-calendar-real-adapter-pilot-v0",
        "proposal_hash": proposal_hash,
        "domain_id": "administration",
        "surface_id": "CALENDAR",
        "operation_id": "CREATE_TEST_EVENT",
        "effect_class": "EXTERNAL_DATA_MUTATION",
        "connector_id": CONNECTOR_ID,
        "connector_action": CONNECTOR_ACTION_CREATE,
        "connector_args": connector_args,
        "connector_call_hash": connector_call_hash,
        "target_ref": target_ref,
        "target_prestate_hash": target_prestate_hash,
        "required_scope": REQUIRED_SCOPE_CREATE,
        "world_call_class": "REVERSIBLE_WORLD_CALL",
        "action_risk_class": "ACTION_EXTERNAL_API",
        "autonomy_level": 4,
        "irreversible": False,
        "retry_policy": "NEVER_AUTORETRY_ON_UNKNOWN",
        "idempotency_key": idempotency_key,
        "decision_authority": "KX108_ONLY",
        "allowed_to_decide": False,
        "allowed_to_act": False,
        "emits_act": False,
    }
    request["request_hash"] = h(
        {
            "schema": "UNIVERSAL_WORLD_ACTION_REQUEST_V0",
            "request_id": request["request_id"],
            "proposal_id": request["proposal_id"],
            "proposal_hash": request["proposal_hash"],
            "domain_id": request["domain_id"],
            "surface_id": request["surface_id"],
            "operation_id": request["operation_id"],
            "effect_class": request["effect_class"],
            "connector_id": request["connector_id"],
            "connector_action": request["connector_action"],
            "connector_args": request["connector_args"],
            "connector_call_hash": request["connector_call_hash"],
            "target_ref": request["target_ref"],
            "target_prestate_hash": request["target_prestate_hash"],
            "required_scope": request["required_scope"],
            "world_call_class": request["world_call_class"],
            "action_risk_class": request["action_risk_class"],
            "autonomy_level": request["autonomy_level"],
            "irreversible": request["irreversible"],
            "retry_policy": request["retry_policy"],
            "idempotency_key": request["idempotency_key"],
            "decision_authority": request["decision_authority"],
        }
    )
    return request


def build_approval(request: dict) -> dict:
    approval = {
        "schema": "UNIVERSAL_WORLD_ACTION_HUMAN_APPROVAL_V0",
        "approval_id": "approval-calendar-real-adapter-pilot-v0",
        "approved_by": "HUMAN:USER_EXPLICIT_GO_2026-10-07",
        "approval_reference": "CHAT_EXPLICIT_GO_CALENDAR_REAL_ADAPTER_V0",
        "request_id": request["request_id"],
        "request_hash": request["request_hash"],
        "proposal_hash": request["proposal_hash"],
        "domain_id": request["domain_id"],
        "surface_id": request["surface_id"],
        "operation_id": request["operation_id"],
        "connector_id": request["connector_id"],
        "connector_action": request["connector_action"],
        "connector_call_hash": request["connector_call_hash"],
        "target_ref": request["target_ref"],
        "target_prestate_hash": request["target_prestate_hash"],
        "required_scope": request["required_scope"],
        "idempotency_key": request["idempotency_key"],
        "decision_authority": "KX108_ONLY",
        "is_execution_authority": False,
    }
    approval["approval_hash"] = h(approval)
    return approval


def generate_packet() -> dict:
    connector_args = build_connector_args()
    request = build_request(connector_args)
    approval = build_approval(request)

    with tempfile.TemporaryDirectory(prefix="obsidia-gcal-pilot-") as temp:
        root = Path(temp)
        pre = run_world_action_pre_execution_v0(
            request=request,
            human_approval=approval,
            evidence_refs=[
                "pilot:GOOGLE_CALENDAR_REAL_ADAPTER_V0",
                "authorization:CHAT_EXPLICIT_GO_2026-10-07",
            ],
            context_store_dir=root / "contexts",
            decision_store_dir=root / "decisions",
        )
        if pre.x108_gate != "ALLOW":
            raise RuntimeError(f"KX108_PRE_NOT_ALLOW:{pre.x108_gate}")

        now = datetime.datetime.now(datetime.timezone.utc)
        policy = build_activation_policy_v0(
            policy_id="google-calendar-real-pilot-v0",
            environment="REAL_PROVIDER_PILOT",
            enabled=True,
            allowed_operations=[
                (
                    CONNECTOR_ID,
                    CONNECTOR_ACTION_CREATE,
                    REQUIRED_SCOPE_CREATE,
                )
            ],
            allowed_world_call_classes=["REVERSIBLE_WORLD_CALL"],
            allowed_action_risk_classes=["ACTION_EXTERNAL_API"],
            max_autonomy_level=4,
            created_at=now.isoformat(),
            expires_at=(now + datetime.timedelta(minutes=10)).isoformat(),
            operator_approval_ref="CHAT_EXPLICIT_GO_CALENDAR_REAL_ADAPTER_V0",
        )
        ticket = issue_live_sovereign_ticket_v0(
            decision_record_id=pre.decision_record_id,
            activation_policy=policy,
            decision_store_dir=root / "decisions",
            context_store_dir=root / "contexts",
            ttl_seconds=300,
            now=now.isoformat(),
        )
        invocation = build_google_calendar_invocation_v0(
            ticket=ticket,
            activation_policy=policy,
            connector_args=connector_args,
            observed_target_ref=request["target_ref"],
            observed_target_prestate_hash=request["target_prestate_hash"],
            now=now.isoformat(),
        )
        return {
            "schema": "GOOGLE_CALENDAR_REAL_PILOT_PACKET_V0",
            "generated_at": now.isoformat(),
            "request_hash": request["request_hash"],
            "human_approval_hash": approval["approval_hash"],
            "kx108_pre": {
                "decision_record_id": pre.decision_record_id,
                "decision_record_hash": pre.decision_record_hash,
                "x108_gate": pre.x108_gate,
            },
            "activation_policy_hash": policy.policy_hash,
            "ticket": ticket.to_dict(),
            "invocation": invocation.to_dict(),
        }


if __name__ == "__main__":
    print(json.dumps(generate_packet(), ensure_ascii=False, sort_keys=True))
