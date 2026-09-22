"""
CG58 KX108 Proof Context Authority Boundary V1.

Context may be accepted as readonly evidence/context only.
Acceptance never grants decision, execution, ACT or mutation authority.
"""

from periphery.context.context_packet_validator import (
    validate_context_packet,
)

from periphery.x108_ingress.x108_context_boundary import (
    check_x108_context_boundary,
)


class KX108ProofContextAuthorityBoundary:

    def __init__(self):
        self.decision_authority = "KX108_ONLY"
        self.context_authority = False
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def validate(self, context_packet):

        if not isinstance(context_packet, dict):

            return {
                "context_authority_boundary_status": "REJECTED",
                "checks": {
                    "context_packet_object": False,
                },
                "context_authority": False,
                "decision_authority": "KX108_ONLY",
                "execution_authority": False,
                "memory_write": False,
                "kernel_mutation": False,
                "emits_act": False,
            }

        validation = validate_context_packet(
            context_packet
        )

        boundary = check_x108_context_boundary(
            context_packet
        )

        validation_dict = validation.to_dict()
        boundary_dict = boundary.to_dict()

        checks = {
            "context_packet_object":
                True,

            "validator_accepts":
                validation_dict.get("valid")
                is True,

            "readonly":
                context_packet.get("readonly")
                is True,

            "context_signal_only":
                context_packet.get(
                    "context_signal_only"
                )
                is True,

            "kx108_only":
                context_packet.get(
                    "decision_authority"
                )
                == "KX108_ONLY",

            "cannot_decide":
                context_packet.get(
                    "allowed_to_decide"
                )
                is False,

            "cannot_act":
                context_packet.get(
                    "allowed_to_act"
                )
                is False,

            "no_memory_write":
                context_packet.get(
                    "memory_write"
                )
                is False,

            "no_kernel_mutation":
                context_packet.get(
                    "kernel_mutation"
                )
                is False,
        }

        valid = all(checks.values())

        return {
            "context_authority_boundary_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "checks":
                checks,

            "context_validation":
                validation_dict,

            "x108_context_boundary":
                boundary_dict,

            "context_authority":
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

            "context_authority":
                self.context_authority,

            "execution_authority":
                self.execution_authority,

            "memory_write":
                self.memory_write,

            "kernel_mutation":
                self.kernel_mutation,

            "emits_act":
                self.emits_act,
        }
