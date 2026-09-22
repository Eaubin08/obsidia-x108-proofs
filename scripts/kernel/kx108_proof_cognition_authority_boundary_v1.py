"""
CG60 KX108 Proof Cognition Authority Boundary V1.

Cognitive material is converted to readonly advisory ContextPacket.
Cognition can inform context but cannot decide or ACT.
"""

from runtime_wiring.source_adapters import (
    cognitive_to_context_packet,
)


class KX108ProofCognitionAuthorityBoundary:

    def __init__(self):
        self.decision_authority = "KX108_ONLY"
        self.cognition_authority = False
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def evaluate(self, metadata):

        if not isinstance(metadata, dict):

            return {
                "cognition_authority_boundary_status":
                    "REJECTED",

                "checks":
                    {
                        "metadata_object":
                            False,
                    },

                "packet":
                    None,

                "cognition_authority":
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

        packet = cognitive_to_context_packet(
            metadata
        )

        invariant_valid = True
        invariant_error = None

        try:
            packet.validate_invariants()
        except (AssertionError, ValueError) as exc:
            invariant_valid = False
            invariant_error = str(exc)

        checks = {
            "metadata_object":
                True,

            "packet_invariants":
                invariant_valid,

            "cognitive_source":
                packet.source
                == "cognitive",

            "advisory_only":
                packet.advisory_only
                is True,

            "readonly":
                packet.readonly
                is True,

            "runtime_disabled":
                packet.runtime_allowed_now
                is False,

            "no_act":
                packet.emits_act
                is False,

            "no_decision":
                packet.emits_decision
                is False,

            "kx108_only":
                packet.decision_authority
                == "KX108_ONLY",

            "cognition_cannot_decide":
                packet.payload.get(
                    "_cognitive_can_decide"
                )
                is False,
        }

        valid = all(checks.values())

        return {
            "cognition_authority_boundary_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "checks":
                checks,

            "invariant_error":
                invariant_error,

            "context_id":
                packet.context_id,

            "source":
                packet.source,

            "cognition_authority":
                False,

            "authorizes_decision":
                False,

            "authorizes_act":
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

    def status(self):

        return {
            "decision_authority":
                self.decision_authority,

            "cognition_authority":
                self.cognition_authority,

            "execution_authority":
                self.execution_authority,

            "memory_write":
                self.memory_write,

            "kernel_mutation":
                self.kernel_mutation,

            "emits_act":
                self.emits_act,
        }
