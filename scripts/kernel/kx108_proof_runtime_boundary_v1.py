"""
CG37 KX108 Proof Runtime Boundary V1
"""

from scripts.kernel.kx108_proof_runtime_validation_v1 import (
    KX108ProofRuntimeValidator,
)

from scripts.kernel.kx108_proof_execution_boundary_v1 import (
    KX108ProofExecutionBoundary,
)


class KX108ProofRuntimeBoundary:

    def __init__(self):
        self.runtime_validator = KX108ProofRuntimeValidator()
        self.execution_boundary = KX108ProofExecutionBoundary()

        self.authority = False
        self.decision_authority = False
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def validate(self, flow_output):

        runtime_result = self.runtime_validator.validate(
            flow_output
        )

        execution_output = (
            flow_output.get("execution")
            if isinstance(flow_output, dict)
            else None
        )

        execution_result = (
            self.execution_boundary.validate(
                execution_output
            )
        )

        refs_match = (
            runtime_result["runtime_ref"] is not None
            and
            runtime_result["runtime_ref"]
            == execution_result["runtime_ref"]
        )

        checks = {
            "runtime_validated":
                runtime_result["runtime_validation_status"]
                == "VALIDATED",

            "execution_validated":
                execution_result["execution_boundary_status"]
                == "VALIDATED",

            "runtime_refs_match":
                refs_match,

            "runtime_no_mutation":
                runtime_result["kernel_mutation"]
                is False,

            "execution_no_mutation":
                execution_result["kernel_mutation"]
                is False,
        }

        valid = all(checks.values())

        return {
            "runtime_boundary_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "checks":
                checks,

            "runtime_validation":
                runtime_result,

            "execution_validation":
                execution_result,

            "runtime_ref":
                runtime_result["runtime_ref"],

            "authority":
                False,

            "decision_authority":
                False,

            "execution_authority":
                False,

            "kernel_mutation":
                False,

            "emits_act":
                False,
        }

    def status(self):

        return {
            "authority": self.authority,
            "decision_authority": self.decision_authority,
            "execution_authority": self.execution_authority,
            "memory_write": self.memory_write,
            "kernel_mutation": self.kernel_mutation,
            "emits_act": self.emits_act,
        }
