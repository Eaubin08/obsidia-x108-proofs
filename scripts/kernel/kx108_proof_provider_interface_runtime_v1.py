"""
CG75 KX108 Proof Provider Interface Runtime V1.

Composes a validated provider boundary with the dry-run KX108
kernel interface.

Provider evidence may cross the interface.
Provider sovereignty may not.
"""

from scripts.kernel.kx108_proof_kernel_interface_v1 import (
    KX108ProofKernelInterface,
)


class KX108ProofProviderInterfaceRuntime:

    def __init__(self):

        self.kernel_interface = (
            KX108ProofKernelInterface()
        )

        self.provider_interface_authority = False
        self.decision_authority = "KX108_ONLY"
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def validate(
        self,
        provider_boundary,
        packet,
    ):

        provider_valid = isinstance(
            provider_boundary,
            dict,
        )

        kernel_result = (
            self.kernel_interface.validate(
                packet
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

            "provider_cannot_decide":
                (
                    provider_valid
                    and provider_boundary.get(
                        "provider_can_decide"
                    )
                    is False
                ),

            "provider_cannot_execute_by_authority":
                (
                    provider_valid
                    and provider_boundary.get(
                        "provider_can_execute_by_authority"
                    )
                    is False
                ),

            "provider_cannot_act":
                (
                    provider_valid
                    and provider_boundary.get(
                        "provider_can_act"
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

            "kernel_interface_validated":
                kernel_result.get(
                    "kernel_interface_status"
                )
                == "VALIDATED",

            "kernel_interface_kx108_only":
                kernel_result.get(
                    "decision_authority"
                )
                == "KX108_ONLY",

            "kernel_interface_no_authority":
                kernel_result.get(
                    "interface_authority"
                )
                is False,

            "kernel_interface_no_execution_authority":
                kernel_result.get(
                    "execution_authority"
                )
                is False,

            "kernel_interface_no_memory_write":
                kernel_result.get(
                    "memory_write"
                )
                is False,

            "kernel_interface_no_kernel_mutation":
                kernel_result.get(
                    "kernel_mutation"
                )
                is False,

            "kernel_interface_no_act":
                kernel_result.get(
                    "emits_act"
                )
                is False,

            "context_only":
                kernel_result.get(
                    "x108_decision"
                )
                == "ALLOW_CONTEXT_ONLY",
        }

        valid = all(checks.values())

        return {
            "provider_interface_runtime_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "checks":
                checks,

            "provider_boundary":
                provider_boundary,

            "kernel_interface":
                kernel_result,

            "provider_id":
                (
                    provider_boundary.get(
                        "provider_id"
                    )
                    if provider_valid
                    else None
                ),

            "provider_interface_authority":
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
            "provider_interface_authority":
                self.provider_interface_authority,

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
