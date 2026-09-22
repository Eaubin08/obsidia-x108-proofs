"""
CG39 KX108 Proof Context Boundary V1
"""

from periphery.context.context_packet_validator import (
    validate_context_packet,
)

from periphery.x108_ingress.x108_context_boundary import (
    check_x108_context_boundary,
)


class KX108ProofContextBoundary:

    def __init__(self):
        self.decision_authority = "KX108_ONLY"
        self.allowed_to_decide = False
        self.allowed_to_act = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def validate(self, packet):

        if not isinstance(packet, dict):

            return {
                "context_boundary_status":
                    "REJECTED",

                "checks":
                    {
                        "packet_object":
                            False,
                    },

                "packet_validation":
                    None,

                "x108_boundary":
                    None,

                "decision_authority":
                    "KX108_ONLY",

                "allowed_to_decide":
                    False,

                "allowed_to_act":
                    False,

                "memory_write":
                    False,

                "kernel_mutation":
                    False,

                "emits_act":
                    False,
            }

        validation = validate_context_packet(
            packet
        )

        boundary = check_x108_context_boundary(
            packet
        )

        validation_data = validation.to_dict()
        boundary_data = boundary.to_dict()

        checks = {
            "packet_object":
                True,

            "packet_valid":
                validation.valid is True,

            "x108_boundary_passed":
                boundary.passed is True,

            "readonly":
                packet.get("readonly") is True,

            "context_signal_only":
                packet.get("context_signal_only")
                is True,

            "kx108_only":
                packet.get("decision_authority")
                == "KX108_ONLY",

            "cannot_decide":
                packet.get("allowed_to_decide")
                is False,

            "cannot_act":
                packet.get("allowed_to_act")
                is False,

            "no_memory_write":
                packet.get("memory_write")
                is False,

            "no_kernel_mutation":
                packet.get("kernel_mutation")
                is False,
        }

        valid = all(checks.values())

        return {
            "context_boundary_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "checks":
                checks,

            "packet_validation":
                validation_data,

            "x108_boundary":
                boundary_data,

            "decision_authority":
                "KX108_ONLY",

            "allowed_to_decide":
                False,

            "allowed_to_act":
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

            "allowed_to_decide":
                self.allowed_to_decide,

            "allowed_to_act":
                self.allowed_to_act,

            "memory_write":
                self.memory_write,

            "kernel_mutation":
                self.kernel_mutation,

            "emits_act":
                self.emits_act,
        }
