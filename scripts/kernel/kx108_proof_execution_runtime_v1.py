"""
CG73 KX108 Proof Execution Runtime V1.

Delegates to the already-materialized runtime boundary.

It verifies coherence between the canonical execution result and
runtime proof. It does not create execution authority.
"""

from scripts.kernel.kx108_proof_runtime_boundary_v1 import (
    KX108ProofRuntimeBoundary,
)


class KX108ProofExecutionRuntime:

    def __init__(self):
        self.runtime_boundary = (
            KX108ProofRuntimeBoundary()
        )

        self.runtime_authority = False
        self.execution_authority = False
        self.decision_authority = "KX108_ONLY"
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def validate(self, flow_output):

        runtime_result = (
            self.runtime_boundary.validate(
                flow_output
            )
        )

        execution_result = (
            runtime_result.get(
                "execution_validation"
            )
        )

        checks = {
            "runtime_boundary_validated":
                runtime_result.get(
                    "runtime_boundary_status"
                )
                == "VALIDATED",

            "execution_validation_present":
                isinstance(
                    execution_result,
                    dict,
                ),

            "execution_boundary_validated":
                (
                    isinstance(
                        execution_result,
                        dict,
                    )
                    and execution_result.get(
                        "execution_boundary_status"
                    )
                    == "VALIDATED"
                ),

            "runtime_ref_present":
                bool(
                    runtime_result.get(
                        "runtime_ref"
                    )
                ),

            "runtime_no_authority":
                runtime_result.get(
                    "authority"
                )
                is False,

            "runtime_no_execution_authority":
                runtime_result.get(
                    "execution_authority"
                )
                is False,

            "runtime_no_kernel_mutation":
                runtime_result.get(
                    "kernel_mutation"
                )
                is False,

            "runtime_no_act":
                runtime_result.get(
                    "emits_act"
                )
                is False,

            "execution_no_authority":
                (
                    isinstance(
                        execution_result,
                        dict,
                    )
                    and execution_result.get(
                        "authority"
                    )
                    is False
                ),

            "execution_no_execution_authority":
                (
                    isinstance(
                        execution_result,
                        dict,
                    )
                    and execution_result.get(
                        "execution_authority"
                    )
                    is False
                ),

            "execution_no_kernel_mutation":
                (
                    isinstance(
                        execution_result,
                        dict,
                    )
                    and execution_result.get(
                        "kernel_mutation"
                    )
                    is False
                ),

            "execution_no_act":
                (
                    isinstance(
                        execution_result,
                        dict,
                    )
                    and execution_result.get(
                        "emits_act"
                    )
                    is False
                ),
        }

        valid = all(checks.values())

        return {
            "execution_runtime_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "checks":
                checks,

            "runtime_boundary":
                runtime_result,

            "execution_boundary":
                execution_result,

            "runtime_ref":
                runtime_result.get(
                    "runtime_ref"
                ),

            "runtime_authority":
                False,

            "execution_authority":
                False,

            "decision_authority":
                "KX108_ONLY",

            "memory_write":
                False,

            "kernel_mutation":
                False,

            "emits_act":
                False,
        }

    def status(self):

        return {
            "runtime_authority":
                self.runtime_authority,

            "execution_authority":
                self.execution_authority,

            "decision_authority":
                self.decision_authority,

            "memory_write":
                self.memory_write,

            "kernel_mutation":
                self.kernel_mutation,

            "emits_act":
                self.emits_act,
        }
