"""
CG94 KX108 Proof Agent Canonical Envelope V1.

Validates separation between the bounded agent-decision proof surface
and an already-produced CanonicalDecisionEnvelope.

The canonical AgentResult -> ContextPacket adapter now exists in the
runtime, but it binds context only and is not on this envelope path.

Therefore:
- the agent does not create the canonical decision envelope;
- the agent does not submit directly to X108;
- the envelope remains CANDIDATE_ONLY;
- no agent-to-envelope authority binding is invented.
"""

from scripts.kernel.canonical_decision_envelope_v1 import (
    CanonicalDecisionEnvelope,
)


class KX108ProofAgentCanonicalEnvelope:

    def __init__(self):
        self.envelope_authority = False
        self.agent_authority = False
        self.decision_authority = "KX108_ONLY"
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def validate(
        self,
        agent_decision_flow,
        canonical_envelope,
    ):
        flow_valid = isinstance(
            agent_decision_flow,
            dict,
        )

        envelope_valid = isinstance(
            canonical_envelope,
            CanonicalDecisionEnvelope,
        )

        checks = {
            "agent_decision_flow_object":
                flow_valid,

            "agent_decision_boundary_validated":
                (
                    flow_valid
                    and agent_decision_flow.get(
                        "agent_decision_flow_status"
                    )
                    == "BOUNDARY_VALIDATED"
                ),

            "agent_did_not_create_decision":
                (
                    flow_valid
                    and agent_decision_flow.get(
                        "agent_decision_created"
                    )
                    is False
                ),

            "no_direct_agent_decision_flow":
                (
                    flow_valid
                    and agent_decision_flow.get(
                        "direct_agent_decision_flow"
                    )
                    is False
                ),

            "agent_did_not_create_context_packet":
                (
                    flow_valid
                    and agent_decision_flow.get(
                        "context_packet_created_here"
                    )
                    is False
                ),

            "agent_did_not_submit_x108":
                (
                    flow_valid
                    and agent_decision_flow.get(
                        "x108_submitted_here"
                    )
                    is False
                ),

            "canonical_adapter_still_required":
                (
                    flow_valid
                    and agent_decision_flow.get(
                        "requires_canonical_context_adapter"
                    )
                    is True
                ),

            "flow_kx108_only":
                (
                    flow_valid
                    and agent_decision_flow.get(
                        "decision_authority"
                    )
                    == "KX108_ONLY"
                ),

            "canonical_envelope_object":
                envelope_valid,

            "canonical_envelope_identity":
                (
                    envelope_valid
                    and canonical_envelope.envelope_id
                    == "decision-envelope-v1"
                ),

            "canonical_candidate_only":
                (
                    envelope_valid
                    and canonical_envelope.decision_status
                    == "CANDIDATE_ONLY"
                ),

            "canonical_source_present":
                (
                    envelope_valid
                    and bool(
                        canonical_envelope.source_provider
                    )
                ),

            "canonical_runtime_present":
                (
                    envelope_valid
                    and bool(
                        canonical_envelope.runtime_ref
                    )
                ),

            "canonical_guard_status_present":
                (
                    envelope_valid
                    and bool(
                        canonical_envelope.guard_status
                    )
                ),

            "flow_no_execution_authority":
                (
                    flow_valid
                    and agent_decision_flow.get(
                        "execution_authority"
                    )
                    is False
                ),

            "flow_no_memory_write":
                (
                    flow_valid
                    and agent_decision_flow.get(
                        "memory_write"
                    )
                    is False
                ),

            "flow_no_kernel_mutation":
                (
                    flow_valid
                    and agent_decision_flow.get(
                        "kernel_mutation"
                    )
                    is False
                ),

            "flow_no_act":
                (
                    flow_valid
                    and agent_decision_flow.get(
                        "emits_act"
                    )
                    is False
                ),
        }

        valid = all(checks.values())

        return {
            "agent_canonical_envelope_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "checks":
                checks,

            "canonical_envelope":
                (
                    canonical_envelope.to_dict()
                    if envelope_valid
                    else None
                ),

            "agent_envelope_created_here":
                False,

            "agent_binding_claimed":
                False,

            "canonical_envelope_is_agent_authority":
                False,

            "context_adapter_invoked_here":
                False,

            "x108_submitted_here":
                False,

            "envelope_authority":
                False,

            "agent_authority":
                False,

            "decision_authority":
                "KX108_ONLY",

            "execution_authority":
                False,

            "memory_write":
                False,

            "kernel_mutation":
                False,

            "emits_act":
                False,
        }
