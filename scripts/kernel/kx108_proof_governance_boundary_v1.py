"""
CG45 KX108 Proof Governance Boundary V1
"""

from runtime_wiring.source_adapters import (
    cognitive_to_context_packet,
)

from runtime_wiring.dry_run_packet_router import (
    route_packets,
)

from scripts.providers.provider_invocation_authorization_receipt_v0 import (
    verify_authorization_receipt,
)


class KX108ProofGovernanceBoundary:

    def __init__(self):
        self.decision_authority = "KX108_ONLY"
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def validate_authorization_receipt(
        self,
        receipt,
    ):

        verified, reason = (
            verify_authorization_receipt(
                receipt
            )
        )

        checks = {
            "receipt_verified":
                verified is True,

            "execution_authority_forbidden":
                (
                    isinstance(receipt, dict)
                    and receipt.get(
                        "execution_authority"
                    )
                    is False
                ),

            "kx_authority_forbidden":
                (
                    isinstance(receipt, dict)
                    and receipt.get(
                        "kx_authority"
                    )
                    is False
                ),

            "memory_write_forbidden":
                (
                    isinstance(receipt, dict)
                    and receipt.get(
                        "memory_write"
                    )
                    is False
                ),
        }

        valid = all(checks.values())

        return {
            "governance_receipt_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "checks":
                checks,

            "verification_reason":
                reason,

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

    def evaluate(
        self,
        metadata,
        critical_action_requested=False,
    ):

        if not isinstance(metadata, dict):

            return {
                "governance_boundary_status":
                    "REJECTED",

                "decision":
                    None,

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

        ticket, _, envelope = route_packets(
            packets=[packet],
            critical_action_requested=(
                critical_action_requested
            ),
            action_candidate_type=(
                "WORLD_ACTION"
                if critical_action_requested
                else "EMIT_CONTEXT"
            ),
            source_module="kx108_proof_governance_boundary_v1",
        )

        allowed_outcomes = {
            "ALLOW_CONTEXT_ONLY",
            "HOLD",
            "BLOCK",
        }

        valid = (
            ticket.decision in allowed_outcomes
        )

        return {
            "governance_boundary_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "decision":
                ticket.decision,

            "x108_gate_status":
                ticket.x108_gate_status,

            "intent_candidate_present":
                envelope is not None,

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

            "execution_authority":
                self.execution_authority,

            "memory_write":
                self.memory_write,

            "kernel_mutation":
                self.kernel_mutation,

            "emits_act":
                self.emits_act,
        }
