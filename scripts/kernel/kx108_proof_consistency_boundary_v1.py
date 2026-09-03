"""
CG26 KX108 Proof Consistency Boundary V1
"""

from scripts.kernel.kx108_proof_verification_engine_v1 import (
    KX108ProofVerificationEngine,
)
from scripts.kernel.kx108_proof_contradiction_resolution_boundary_v1 import (
    KX108ProofContradictionResolver,
)


class KX108ProofConsistencyBoundary:

    def __init__(self):
        self.verifier = KX108ProofVerificationEngine()
        self.resolver = KX108ProofContradictionResolver()

        self.authority = False
        self.decision_authority = False
        self.memory_write = False
        self.kernel_mutation = False

    def evaluate(self, proof: dict):

        verification = self.verifier.verify(proof)
        resolution = self.resolver.resolve(proof)

        consistent = (
            verification["verification_status"] == "VERIFIED"
            and resolution["contradiction_detected"] is False
            and resolution["propagation_blocked"] is False
        )

        return {
            "consistency_status":
                "CONSISTENT"
                if consistent
                else "REJECTED",

            "verification":
                verification,

            "contradiction_resolution":
                resolution,

            "propagation_allowed":
                consistent,

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
