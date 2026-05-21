"""
Demo: World action dry-run flow — sovereign ticket → gateway → bus.
All world actions remain dry-run. No real egress ever.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from periphery.world_calls.sovereign_ticket import issue_sovereign_ticket
from periphery.world_calls.world_call_classifier import WorldCallClass
from periphery.world_calls.obsidia_gateway import ObsidiaGateway
from periphery.world_calls.world_action_bus import WorldActionEvent, publish_event
from periphery.world_action_controlled_runtime_stub import run_world_action_stub


def run_world_action_dry_run(action_id: str, domain: str, wcc: WorldCallClass = WorldCallClass.READ_ONLY) -> dict:
    ticket = issue_sovereign_ticket(
        action_id=action_id,
        os3_ticket_id=f"os3_{action_id}",
        x108_gate="ALLOW",
        scope=domain,
        autonomy_level=1,
        world_call_class=wcc.value,
    )

    gateway = ObsidiaGateway()
    decision = gateway.check(ticket, wcc, domain)

    stub_result = run_world_action_stub(action_id, domain, {"demo": True})

    if not decision.egress_allowed:
        evt = WorldActionEvent(
            event_id=uuid.uuid4().hex,
            action_id=action_id,
            ticket_id=ticket.ticket_id,
            world_call_class=wcc.value,
            gate_result=decision.gate_result,
            dry_run_only=True,
            payload={"demo": True},
        )
        publish_event(evt)

    return {
        "action_id": action_id,
        "gate_result": decision.gate_result,
        "egress_allowed": decision.egress_allowed,
        "dry_run_only": stub_result.dry_run_only,
        "world_action_allowed": stub_result.world_action_allowed,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    result = run_world_action_dry_run("demo_waf_001", "bank")
    print(json.dumps(result, indent=2))
    assert result["egress_allowed"] is False
    assert result["dry_run_only"] is True
    assert result["world_action_allowed"] is False
    print("✓ World action dry-run demo complete — no real egress")
