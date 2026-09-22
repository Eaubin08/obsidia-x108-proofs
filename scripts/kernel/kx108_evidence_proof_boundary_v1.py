"""
CG22 KX108 Evidence Proof Boundary V1

Evidence is attached to validated states.
Evidence does not create authority.
Evidence does not mutate Kernel.
"""


class KX108EvidenceProofBoundary:

    def __init__(self):

        self.memory_write = False
        self.kernel_mutation = False


    def attach_evidence(
        self,
        validation_state: dict,
        evidence: dict,
    ):

        validation_ok = (
            validation_state.get(
                "validation_status"
            )
            ==
            "VALIDATED"
        )

        evidence_present = (
            evidence.get(
                "evidence_id"
            )
            is not None
        )

        valid = (
            validation_ok
            and evidence_present
        )

        return {

            "proof_status":
                "PROVEN"
                if valid
                else "UNPROVEN",

            "evidence_attached":
                valid,

            "authority":
                False,

            "decision_authority":
                False,

            "kernel_mutation":
                False,
        }


    def status(self):

        return {

            "memory_write":
                self.memory_write,

            "kernel_mutation":
                self.kernel_mutation,

        }
