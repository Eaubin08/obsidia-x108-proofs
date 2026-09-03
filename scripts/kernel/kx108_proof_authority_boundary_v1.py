"""
CG46 KX108 Proof Authority Boundary V1.

Observes provider invocation authorization evidence without
granting execution or KX108 decision authority.
"""

from scripts.providers.provider_invocation_authorization_receipt_v0 import (
    build_authorization_receipt,
    verify_authorization_receipt,
)


class KX108ProofAuthorityBoundary:

    def __init__(self):
        self.decision_authority = "KX108_ONLY"
        self.execution_authority = False
        self.kx_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def validate_receipt(self, receipt):

        verified, reason = verify_authorization_receipt(
            receipt
        )

        checks = {
            "receipt_object":
                isinstance(receipt, dict),

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
            "authority_boundary_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "checks":
                checks,

            "verification_reason":
                reason,

            "receipt":
                receipt
                if isinstance(receipt, dict)
                else None,

            "authority_observed_only":
                True,

            "decision_authority":
                "KX108_ONLY",

            "execution_authority":
                False,

            "kx_authority":
                False,

            "memory_write":
                False,

            "kernel_mutation":
                False,

            "emits_act":
                False,
        }

    def issue_and_validate(
        self,
        *,
        mission_submission_id,
        capability_request_ref,
        provider_id,
        activation_status,
        adapter_id,
    ):

        receipt = build_authorization_receipt(
            mission_submission_id=mission_submission_id,
            capability_request_ref=capability_request_ref,
            provider_id=provider_id,
            activation_status=activation_status,
            adapter_id=adapter_id,
        )

        return self.validate_receipt(
            receipt
        )

    def status(self):

        return {
            "decision_authority":
                self.decision_authority,

            "execution_authority":
                self.execution_authority,

            "kx_authority":
                self.kx_authority,

            "memory_write":
                self.memory_write,

            "kernel_mutation":
                self.kernel_mutation,

            "emits_act":
                self.emits_act,
        }
