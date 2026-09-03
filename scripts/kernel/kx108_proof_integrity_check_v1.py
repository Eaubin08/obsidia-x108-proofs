"""
CG30 KX108 Proof Integrity Check V1
"""

from scripts.kernel.kx108_proof_consistency_boundary_v1 import (
    KX108ProofConsistencyBoundary,
)
from scripts.kernel.kx108_proof_state_validation_v1 import (
    KX108ProofStateValidator,
)


class KX108ProofIntegrityCheck:

    def __init__(self):
        self.consistency = KX108ProofConsistencyBoundary()
        self.state_validator = KX108ProofStateValidator()

        self.authority = False
        self.decision_authority = False
        self.memory_write = False
        self.kernel_mutation = False

    def check(
        self,
        proof: dict,
        meta_states: list,
    ):

        proof_result = self.consistency.evaluate(
            proof
        )

        state_result = self.state_validator.validate(
            meta_states
        )

        checks = {
            "proof_consistent":
                proof_result["consistency_status"]
                == "CONSISTENT",

            "state_validated":
                state_result["state_validation_status"]
                == "VALIDATED",

            "proof_propagation_allowed":
                proof_result["propagation_allowed"]
                is True,

            "kernel_boundary_preserved":
                (
                    proof_result["kernel_mutation"]
                    is False
                    and
                    state_result["kernel_mutation"]
                    is False
                ),
        }

        intact = all(checks.values())

        return {
            "integrity_status":
                "INTACT"
                if intact
                else "REJECTED",

            "checks":
                checks,

            "proof":
                proof_result,

            "state":
                state_result,

            "authority":
                False,

            "decision_authority":
                False,

            "kernel_mutation":
                False,
        }

    def status(self):

        return {
            "authority": self.authority,
            "decision_authority": self.decision_authority,
            "memory_write": self.memory_write,
            "kernel_mutation": self.kernel_mutation,
        }
