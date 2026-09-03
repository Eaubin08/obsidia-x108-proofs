"""
CG78 KX108 Proof Provider Security Runtime V1.

Composes a validated provider boundary with the existing security
sanitization boundary.

Security processing may sanitize provider payload evidence.
It never grants provider, execution, memory or ACT authority.
"""

from scripts.kernel.kx108_proof_security_boundary_v1 import (
    KX108ProofSecurityBoundary,
)


class KX108ProofProviderSecurityRuntime:

    def __init__(self):

        self.security_boundary = (
            KX108ProofSecurityBoundary()
        )

        self.security_authority = False
        self.provider_authority = False
        self.decision_authority = "KX108_ONLY"
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def validate(
        self,
        provider_boundary,
        payload,
    ):

        provider_valid = isinstance(
            provider_boundary,
            dict,
        )

        security_result = (
            self.security_boundary.sanitize(
                payload
            )
        )

        security_checks = (
            security_result.get("checks")
            if isinstance(
                security_result,
                dict,
            )
            else None
        )

        security_checks_valid = (
            isinstance(
                security_checks,
                dict,
            )
            and len(security_checks) > 0
            and all(
                security_checks.values()
            )
        )

        checks = {
            "provider_boundary_object":
                provider_valid,

            "provider_boundary_validated":
                (
                    provider_valid
                    and provider_boundary.get(
                        "provider_boundary_status"
                    )
                    == "VALIDATED"
                ),

            "provider_identity_present":
                (
                    provider_valid
                    and bool(
                        provider_boundary.get(
                            "provider_id"
                        )
                    )
                ),

            "provider_kx108_only":
                (
                    provider_valid
                    and provider_boundary.get(
                        "decision_authority"
                    )
                    == "KX108_ONLY"
                ),

            "provider_no_authority":
                (
                    provider_valid
                    and provider_boundary.get(
                        "provider_authority"
                    )
                    is False
                ),

            "provider_no_execution_authority":
                (
                    provider_valid
                    and provider_boundary.get(
                        "execution_authority"
                    )
                    is False
                ),

            "provider_no_memory_write":
                (
                    provider_valid
                    and provider_boundary.get(
                        "memory_write"
                    )
                    is False
                ),

            "provider_no_kernel_mutation":
                (
                    provider_valid
                    and provider_boundary.get(
                        "kernel_mutation"
                    )
                    is False
                ),

            "provider_no_act":
                (
                    provider_valid
                    and provider_boundary.get(
                        "emits_act"
                    )
                    is False
                ),

            "security_result_object":
                isinstance(
                    security_result,
                    dict,
                ),

            "security_checks_valid":
                security_checks_valid,

            "security_kx108_only":
                (
                    isinstance(
                        security_result,
                        dict,
                    )
                    and security_result.get(
                        "decision_authority"
                    )
                    == "KX108_ONLY"
                ),

            "security_no_execution_authority":
                (
                    isinstance(
                        security_result,
                        dict,
                    )
                    and security_result.get(
                        "execution_authority"
                    )
                    is False
                ),

            "security_no_memory_write":
                (
                    isinstance(
                        security_result,
                        dict,
                    )
                    and security_result.get(
                        "memory_write"
                    )
                    is False
                ),

            "security_no_kernel_mutation":
                (
                    isinstance(
                        security_result,
                        dict,
                    )
                    and security_result.get(
                        "kernel_mutation"
                    )
                    is False
                ),

            "security_no_act":
                (
                    isinstance(
                        security_result,
                        dict,
                    )
                    and security_result.get(
                        "emits_act"
                    )
                    is False
                ),
        }

        valid = all(checks.values())

        return {
            "provider_security_runtime_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "checks":
                checks,

            "provider_id":
                (
                    provider_boundary.get(
                        "provider_id"
                    )
                    if provider_valid
                    else None
                ),

            "security_boundary":
                security_result,

            "secret_detected":
                (
                    security_result.get(
                        "secret_detected"
                    )
                    if isinstance(
                        security_result,
                        dict,
                    )
                    else None
                ),

            "security_authority":
                False,

            "provider_authority":
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
            "security_authority":
                self.security_authority,

            "provider_authority":
                self.provider_authority,

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
