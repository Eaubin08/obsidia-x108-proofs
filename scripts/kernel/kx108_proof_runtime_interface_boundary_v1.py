"""
CG77 KX108 Proof Runtime Interface Boundary V1.

Closes the dry-run kernel interface with the runtime-authority
boundary.

Context may cross the interface.
Runtime activation, decision authority and ACT remain forbidden.
"""

from scripts.kernel.kx108_proof_kernel_interface_v1 import (
    KX108ProofKernelInterface,
)

from scripts.kernel.kx108_proof_runtime_authority_boundary_v1 import (
    KX108ProofRuntimeAuthorityBoundary,
)


class KX108ProofRuntimeInterfaceBoundary:

    def __init__(self):

        self.kernel_interface = (
            KX108ProofKernelInterface()
        )

        self.runtime_authority_boundary = (
            KX108ProofRuntimeAuthorityBoundary()
        )

        self.interface_authority = False
        self.runtime_authority = False
        self.decision_authority = "KX108_ONLY"
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def validate(self, packet):

        kernel_result = (
            self.kernel_interface.validate(
                packet
            )
        )

        runtime_result = (
            self.runtime_authority_boundary.validate(
                packet
            )
        )

        checks = {
            "kernel_interface_validated":
                kernel_result.get(
                    "kernel_interface_status"
                )
                == "VALIDATED",

            "runtime_authority_validated":
                runtime_result.get(
                    "runtime_authority_boundary_status"
                )
                == "VALIDATED",

            "kernel_kx108_only":
                kernel_result.get(
                    "decision_authority"
                )
                == "KX108_ONLY",

            "runtime_kx108_only":
                runtime_result.get(
                    "decision_authority"
                )
                == "KX108_ONLY",

            "kernel_interface_no_authority":
                kernel_result.get(
                    "interface_authority"
                )
                is False,

            "runtime_no_authority":
                runtime_result.get(
                    "runtime_authority"
                )
                is False,

            "runtime_not_authorized":
                runtime_result.get(
                    "authorizes_runtime"
                )
                is False,

            "runtime_disabled":
                runtime_result.get(
                    "runtime_allowed_now"
                )
                is False,

            "kernel_no_execution_authority":
                kernel_result.get(
                    "execution_authority"
                )
                is False,

            "runtime_no_execution_authority":
                runtime_result.get(
                    "execution_authority"
                )
                is False,

            "kernel_no_memory_write":
                kernel_result.get(
                    "memory_write"
                )
                is False,

            "runtime_no_memory_write":
                runtime_result.get(
                    "memory_write"
                )
                is False,

            "kernel_no_kernel_mutation":
                kernel_result.get(
                    "kernel_mutation"
                )
                is False,

            "runtime_no_kernel_mutation":
                runtime_result.get(
                    "kernel_mutation"
                )
                is False,

            "kernel_no_act":
                kernel_result.get(
                    "emits_act"
                )
                is False,

            "runtime_no_act":
                runtime_result.get(
                    "emits_act"
                )
                is False,
        }

        valid = all(checks.values())

        return {
            "runtime_interface_boundary_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "checks":
                checks,

            "kernel_interface":
                kernel_result,

            "runtime_authority_boundary":
                runtime_result,

            "runtime_activated":
                False,

            "interface_authority":
                False,

            "runtime_authority":
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
            "interface_authority":
                self.interface_authority,

            "runtime_authority":
                self.runtime_authority,

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
