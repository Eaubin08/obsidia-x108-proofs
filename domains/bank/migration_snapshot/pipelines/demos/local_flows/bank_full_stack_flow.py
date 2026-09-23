"""
V5A Internal Flow: Bank domain full-stack scenario. Dry-run only.
"""
from __future__ import annotations
import json, uuid
from datetime import datetime, timezone

from periphery.common import ActionCandidate
from periphery.data_gate import run_data_gate
from periphery.provenance_gate import run_provenance_gate
from periphery.memory_governor import run_memory_governor
from periphery.control_plane import run_control_plane
from periphery.os3_ticket import OS3ProofTicket
from periphery.world_calls.sovereign_ticket import issue_sovereign_ticket
from periphery.world_calls.world_call_classifier import WorldCallClass
from periphery.world_calls.obsidia_gateway import ObsidiaGateway
from periphery.math_core.governed_state import GovernedStateVector, DecisionEnvelopeTheta
from periphery.math_core.lyapunov import compute_lyapunov
from periphery.math_core.proof_of_governance import proof_of_governance


def run(action_id="v5a_bank_001", intent="balance_inquiry"):
    action = ActionCandidate(
        action_id=action_id, domain="bank", actor_id="bank_flow",
        intent=intent, action_type="READ_ONLY", irreversible=False,
        timestamp_plan=datetime.now(timezone.utc).isoformat(),
    )
    packet = run_control_plane(action)
    data_result = run_data_gate(action)
    provenance = run_provenance_gate(action)
    memory = run_memory_governor(action)

    os3 = OS3ProofTicket(
        ticket_id=f"os3_{action_id}", action_id=action_id, domain="bank",
        x108_gate="ALLOW", reason_code="ALLOW_STANDARD", severity="INFO",
        scores={}, unknowns=[], risk_flags=[], contradictions=[], evidence_refs=[],
        input_hash=uuid.uuid4().hex, output_hash=uuid.uuid4().hex,
        trace_hash=uuid.uuid4().hex, merkle_root=uuid.uuid4().hex,
        replay_status="NOT_RUN",
    )
    ticket = issue_sovereign_ticket(
        action_id=action_id, os3_ticket_id=os3.ticket_id,
        x108_gate="ALLOW", scope="bank", autonomy_level=1,
        world_call_class=WorldCallClass.READ_ONLY_WORLD_CALL.value,
    )
    gateway = ObsidiaGateway()
    decision = gateway.check(ticket, WorldCallClass.READ_ONLY_WORLD_CALL, "bank")

    sv = GovernedStateVector()
    lyapunov = compute_lyapunov(action_id, sv)
    theta = DecisionEnvelopeTheta(theta_id="theta_bank", x108_gate="ALLOW", confidence=0.9, reason_code="ALLOW_STANDARD")
    pog = proof_of_governance(action_id, theta, lyapunov, os3)

    return {
        "action_id": action_id, "domain": "bank",
        "data_gate_recommended": data_result.recommended_gate,
        "gate_result": decision.gate_result,
        "egress_allowed": decision.egress_allowed,
        "dry_run_only": decision.dry_run_only,
        "pog_valid": pog.pog_valid,
        "non_sovereign": not packet.can_emit_act,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    r = run()
    print(json.dumps(r, indent=2))
    assert r["egress_allowed"] is False
    assert r["dry_run_only"] is True
    assert r["non_sovereign"] is True
    print("OK bank_full_stack_flow")
