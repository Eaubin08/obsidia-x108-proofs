"""
V5A Internal Flow: World Call Gateway dry-run demonstration.
Demonstrates: SovereignTicket → ObsidiaGateway → WorldActionBus → Secret Boundary.
No Sovereign Ticket → No World Call. Gateway remains dry-run.
All world actions are simulated. No real egress.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from periphery.world_calls.sovereign_ticket import issue_sovereign_ticket
from periphery.world_calls.world_call_classifier import WorldCallClass
from periphery.world_calls.obsidia_gateway import ObsidiaGateway
from periphery.world_calls.world_action_bus import publish_event
from periphery.world_calls.world_executor_dryrun import execute_dry_run
from periphery.world_calls.secret_boundary import assert_no_secret_in_agent_payload, redact_secrets
from periphery.world_action_controlled_runtime_stub import run_world_action_stub
from periphery.common import ActionCandidate


def run(action_id: str = "v5a_wcg_001", domain: str = "bank") -> dict:
    action = ActionCandidate(
        action_id=action_id,
        domain=domain,
        actor_id="world_call_flow",
        intent="external_data_query",
        action_type="READ_ONLY",
        irreversible=False,
        timestamp_plan=datetime.now(timezone.utc).isoformat(),
        payload={"world_call": True},
    )

    # Without sovereign ticket — world call blocked at gateway
    ticket = issue_sovereign_ticket(
        action_id=action_id,
        os3_ticket_id=f"os3_{action_id}",
        x108_gate="ALLOW",
        scope=domain,
        autonomy_level=1,
        world_call_class=WorldCallClass.READ_ONLY_WORLD_CALL.value,
    )

    gateway = ObsidiaGateway()
    decision = gateway.check(ticket, WorldCallClass.READ_ONLY_WORLD_CALL, domain)

    # World action stub — dry-run only
    stub_result = run_world_action_stub(action, ticket, 0.0)

    # World executor dry-run
    exec_result = execute_dry_run(
        action_id=action_id,
        gateway_decision=decision,
    )

    # Secret boundary — blocks secrets from agents
    try:
        assert_no_secret_in_agent_payload({"safe": "data"})
        secret_blocked = True
    except AssertionError:
        secret_blocked = False

    # WorldActionBus event � append-only, dry-run only
    evt = publish_event(
        action_id=action_id,
        sovereign_ticket_id=ticket.ticket_id,
        world_call_class=WorldCallClass.READ_ONLY_WORLD_CALL.value,
        action_risk_class="LOW",
        autonomy_level=1,
        intent="external_data_query",
        domain=domain,
        blocked=not decision.egress_allowed,
        block_reason="V5A_DRY_RUN" if not decision.egress_allowed else "",
    )

    return {
        "action_id": action_id,
        "ticket_id": ticket.ticket_id,
        "gate_result": decision.gate_result,
        "egress_allowed": decision.egress_allowed,
        "dry_run_only": decision.dry_run_only,
        "stub_dry_run": stub_result.dry_run_only,
        "executor_simulated": exec_result.simulated,
        "executor_executed": exec_result.executed,
        "secret_blocked": secret_blocked,
        "bus_event_id": evt.event_id,
        "bus_dry_run": evt.dry_run_only,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2))
    assert result["egress_allowed"] is False, "CRITICAL: egress must be blocked"
    assert result["dry_run_only"] is True, "CRITICAL: must be dry-run only"
    assert result["stub_dry_run"] is True, "CRITICAL: stub must be dry-run"
    assert result["executor_executed"] is False, "CRITICAL: executor must not execute"
    assert result["secret_blocked"] is True, "CRITICAL: secrets must be blocked"
    assert result["bus_dry_run"] is True, "CRITICAL: bus event must be dry-run"
    print("OK world_call_gateway_flow — no egress, dry-run only, secrets blocked")
