"""
CG42 KX108 Proof Intention Boundary V1
"""

from runtime_wiring.source_adapters import (
    cognitive_to_context_packet,
)

from runtime_wiring.dry_run_packet_router import (
    route_packets,
)


class KX108ProofIntentionBoundary:

    def __init__(self):
        self.decision_authority = "KX108_ONLY"
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def build(
        self,
        metadata,
        action_candidate_type="EMIT_CONTEXT",
    ):

        if not isinstance(metadata, dict):

            return {
                "intention_boundary_status": "REJECTED",
                "checks": {
                    "metadata_object": False,
                },
                "intent_envelope": None,
                "decision": None,
                "decision_authority": "KX108_ONLY",
                "execution_authority": False,
                "memory_write": False,
                "kernel_mutation": False,
                "emits_act": False,
            }

        packet = cognitive_to_context_packet(
            metadata
        )

        decision_ticket, _, envelope = route_packets(
            packets=[packet],
            critical_action_requested=True,
            action_candidate_type=action_candidate_type,
            source_module="kx108_proof_intention_boundary_v1",
        )

        checks = {
            "metadata_object":
                True,

            "intent_created":
                envelope is not None,

            "candidate_only":
                (
                    envelope is not None
                    and envelope.candidate_only is True
                ),

            "requires_x108":
                (
                    envelope is not None
                    and envelope.requires_x108 is True
                ),

            "kx108_only":
                (
                    envelope is not None
                    and envelope.authority
                    == "KX108_ONLY"
                ),

            "no_act":
                (
                    envelope is not None
                    and envelope.emits_act is False
                ),

            "context_bound":
                (
                    envelope is not None
                    and packet.context_id
                    in envelope.context_packet_refs
                ),

            "critical_intent_held":
                decision_ticket.decision == "HOLD",
        }

        valid = all(checks.values())

        return {
            "intention_boundary_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "checks":
                checks,

            "intent_envelope":
                (
                    {
                        "intent_id":
                            envelope.intent_id,

                        "action_candidate_type":
                            envelope.action_candidate_type,

                        "requires_x108":
                            envelope.requires_x108,

                        "authority":
                            envelope.authority,

                        "emits_act":
                            envelope.emits_act,

                        "candidate_only":
                            envelope.candidate_only,

                        "context_packet_refs":
                            list(
                                envelope.context_packet_refs
                            ),
                    }
                    if envelope is not None
                    else None
                ),

            "decision":
                {
                    "decision":
                        decision_ticket.decision,

                    "x108_gate_status":
                        decision_ticket.x108_gate_status,
                },

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

    def status(self):

        return {
            "decision_authority":
                self.decision_authority,

            "execution_authority":
                self.execution_authority,

            "memory_write":
                self.memory_write,

            "kernel_mutation":
                self.kernel_mutation,

            "emits_act":
                self.emits_act,
        }
