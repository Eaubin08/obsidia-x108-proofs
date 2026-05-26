"""
Demo: Full action lifecycle — from ActionCandidate through X-108 gate to OS3 proof chain.
Dry-run only. No real egress. X-108 is the sole sovereign authority.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from periphery.agents.control_plane import ActionCandidate
from periphery.world_calls.action_risk_classifier import classify_action_risk
from periphery.world_calls.world_call_classifier import classify_world_call
from periphery.world_calls.sovereign_ticket import issue_sovereign_ticket
from periphery.world_calls.obsidia_gateway import ObsidiaGateway
from periphery.os3_replay_manifest import OS3ProofTicket, build_replay_manifest
from periphery.math_core.governed_state import GovernedStateVector, DecisionEnvelopeTheta
from periphery.math_core.lyapunov import compute_lyapunov
from periphery.math_core.proof_of_governance import proof_of_governance


def run_action_lifecycle(action_id: str, domain: str, intent: str) -> dict:
    action = ActionCandidate(
        action_id=action_id,
        domain=domain,
        actor_id="demo_actor",
        intent=intent,
        action_type="READ_ONLY",
        irreversible=False,
        payload={"demo": True},
    )

    risk = classify_action_risk(action)
    wcc = classify_world_call(action)

    os3 = OS3ProofTicket(
        ticket_id=f"os3_{action_id}",
        action_id=action_id,
        input_hash=uuid.uuid4().hex,
        output_hash=uuid.uuid4().hex,
        trace_hash=uuid.uuid4().hex,
        merkle_root=uuid.uuid4().hex,
        replay_status="PASS",
        gate="ALLOW",
    )

    ticket = issue_sovereign_ticket(
        action_id=action_id,
        os3_ticket_id=os3.ticket_id,
        x108_gate="ALLOW",
        scope=domain,
        autonomy_level=1,
        world_call_class=wcc.value,
    )

    gateway = ObsidiaGateway()
    decision = gateway.check(ticket, wcc, domain)

    sv = GovernedStateVector()
    lyapunov = compute_lyapunov(action_id, sv)
    theta = DecisionEnvelopeTheta(theta_id="theta_demo", x108_gate="ALLOW", confidence=0.9, reason_code="ALLOW_STANDARD")
    pog = proof_of_governance(action_id, theta, lyapunov, os3)

    report = {
        "action_id": action_id,
        "domain": domain,
        "risk_class": risk.value,
        "world_call_class": wcc.value,
        "ticket_id": ticket.ticket_id,
        "gate_result": decision.gate_result,
        "egress_allowed": decision.egress_allowed,
        "dry_run_only": decision.dry_run_only,
        "pog_valid": pog.pog_valid,
        "lyapunov_stable": pog.lyapunov_stable,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    return report


if __name__ == "__main__":
    result = run_action_lifecycle("demo_act_001", "bank", "check_balance")
    print(json.dumps(result, indent=2))
    assert result["egress_allowed"] is False
    assert result["dry_run_only"] is True
    assert result["pog_valid"] is True
    print("✓ Action lifecycle demo complete — dry_run_only=True, egress_allowed=False")
