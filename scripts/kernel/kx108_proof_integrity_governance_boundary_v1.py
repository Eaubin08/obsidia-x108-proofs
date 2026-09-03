"""
CG51 KX108 Proof Integrity Governance Boundary V1.

Composes the existing ProofOfGovernance attestation surface
with the CG47 trust path.

Proof integrity is evidence.
It is never sovereign authority.
"""

from scripts.kernel.kx108_proof_trust_boundary_v1 import (
    KX108ProofTrustBoundary,
)


class KX108ProofIntegrityGovernanceBoundary:

    def __init__(self):
        self.trust_boundary = (
            KX108ProofTrustBoundary()
        )

        self.authority = False
        self.decision_authority = "KX108_ONLY"
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def validate(
        self,
        action_id,
        ticket,
        proof_of_governance_result,
    ):

        if (
            proof_of_governance_result is None
            or not hasattr(
                proof_of_governance_result,
                "to_dict",
            )
        ):

            return {
                "integrity_governance_status":
                    "REJECTED",

                "checks":
                    {
                        "pog_result":
                            False,
                    },

                "authority":
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

        pog = proof_of_governance_result.to_dict()

        trust = self.trust_boundary.validate(
            action_id,
            ticket,
            proof_of_governance_result,
        )

        checks = {
            "pog_result":
                True,

            "pog_valid":
                pog.get("pog_valid")
                is True,

            "ticket_integrity":
                pog.get("ticket_valid")
                is True,

            "lyapunov_stable":
                pog.get("lyapunov_stable")
                is True,

            "trust_path_complete":
                trust.get(
                    "trust_boundary_status"
                )
                == "TRUSTED",

            "runtime_not_bound":
                pog.get("runtime_bound")
                is False,

            "kx108_only":
                pog.get(
                    "decision_authority"
                )
                == "KX108_ONLY",

            "lean_does_not_decide":
                pog.get("lean_decides")
                is False,

            "attestation_only":
                pog.get("attestation_only")
                is True,
        }

        valid = all(checks.values())

        return {
            "integrity_governance_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "checks":
                checks,

            "proof_of_governance":
                pog,

            "trust":
                trust,

            "authority":
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
            "authority":
                self.authority,

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
