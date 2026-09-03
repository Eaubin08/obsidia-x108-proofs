"""
CG74 KX108 Proof Execution Boundary Runtime V1.

Composes the already-materialized execution-runtime proof with
the canonical execution boundary.

It validates coherence only.
It creates no execution authority.
"""

from scripts.kernel.kx108_proof_execution_runtime_v1 import (
    KX108ProofExecutionRuntime,
)

from scripts.kernel.kx108_proof_execution_boundary_v1 import (
    KX108ProofExecutionBoundary,
)


class KX108ProofExecutionBoundaryRuntime:

    def __init__(self):

        self.execution_runtime = (
            KX108ProofExecutionRuntime()
        )

        self.execution_boundary = (
            KX108ProofExecutionBoundary()
        )

        self.runtime_authority = False
        self.execution_authority = False
        self.decision_authority = "KX108_ONLY"
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def validate(self, flow_output):

        runtime_result = (
            self.execution_runtime.validate(
                flow_output
            )
        )

        execution_output = (
            flow_output.get("execution")
            if isinstance(flow_output, dict)
            else None
        )

        boundary_result = (
            self.execution_boundary.validate(
                execution_output
            )
        )

        runtime_ref = runtime_result.get(
            "runtime_ref"
        )

        boundary_ref = boundary_result.get(
            "runtime_ref"
        )

        checks = {
            "execution_runtime_validated":
                runtime_result.get(
                    "execution_runtime_status"
                )
                == "VALIDATED",

            "execution_boundary_validated":
                boundary_result.get(
                    "execution_boundary_status"
                )
                == "VALIDATED",

            "runtime_ref_present":
                bool(runtime_ref),

            "boundary_ref_present":
                bool(boundary_ref),

            "runtime_refs_match":
                runtime_ref == boundary_ref,

            "runtime_kx108_only":
                runtime_result.get(
                    "decision_authority"
                )
                == "KX108_ONLY",

            "boundary_has_no_decision_authority":
                boundary_result.get(
                    "decision_authority"
                )
                is False,

            "runtime_no_authority":
                runtime_result.get(
                    "runtime_authority"
                )
                is False,

            "runtime_no_execution_authority":
                runtime_result.get(
                    "execution_authority"
                )
                is False,

            "boundary_no_authority":
                boundary_result.get(
                    "authority"
                )
                is False,

            "boundary_no_execution_authority":
                boundary_result.get(
                    "execution_authority"
                )
                is False,

            "runtime_no_kernel_mutation":
                runtime_result.get(
                    "kernel_mutation"
                )
                is False,

            "boundary_no_kernel_mutation":
                boundary_result.get(
                    "kernel_mutation"
                )
                is False,

            "runtime_no_act":
                runtime_result.get(
                    "emits_act"
                )
                is False,

            "boundary_no_act":
                boundary_result.get(
                    "emits_act"
                )
                is False,
        }

        valid = all(checks.values())

        return {
            "execution_boundary_runtime_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "checks":
                checks,

            "execution_runtime":
                runtime_result,

            "execution_boundary":
                boundary_result,

            "runtime_ref":
                runtime_ref,

            "new_authority_created":
                False,

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
