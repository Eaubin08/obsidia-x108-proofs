"""
CG43 KX108 Proof Cognition Boundary V1
"""

from runtime_wiring.source_adapters import (
    cognitive_to_context_packet,
)


class KX108ProofCognitionBoundary:

    def __init__(self):
        self.decision_authority = "KX108_ONLY"
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def build(self, metadata):

        if not isinstance(metadata, dict):

            return {
                "cognition_boundary_status": "REJECTED",
                "checks": {
                    "metadata_object": False,
                },
                "context": None,
                "decision_authority": "KX108_ONLY",
                "execution_authority": False,
                "memory_write": False,
                "kernel_mutation": False,
                "emits_act": False,
            }

        packet = cognitive_to_context_packet(
            metadata
        )

        checks = {
            "metadata_object":
                True,

            "cognitive_source":
                packet.source == "cognitive",

            "advisory_only":
                packet.advisory_only is True,

            "readonly":
                packet.readonly is True,

            "runtime_disabled":
                packet.runtime_allowed_now is False,

            "no_act":
                packet.emits_act is False,

            "no_decision":
                packet.emits_decision is False,

            "kx108_only":
                packet.decision_authority
                == "KX108_ONLY",

            "cognitive_cannot_decide":
                packet.payload.get(
                    "_cognitive_can_decide"
                )
                is False,
        }

        valid = all(checks.values())

        return {
            "cognition_boundary_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "checks":
                checks,

            "context":
                {
                    "context_id":
                        packet.context_id,

                    "source":
                        packet.source,

                    "boundary":
                        packet.boundary,

                    "advisory_only":
                        packet.advisory_only,

                    "readonly":
                        packet.readonly,

                    "runtime_allowed_now":
                        packet.runtime_allowed_now,

                    "emits_act":
                        packet.emits_act,

                    "emits_decision":
                        packet.emits_decision,

                    "decision_authority":
                        packet.decision_authority,
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
