"""
CG22 KX108 Evidence Receipt V1
"""

from dataclasses import dataclass


@dataclass
class KX108EvidenceReceipt:

    receipt_id: str
    proof_status: str
    evidence_id: str
    provenance: str
    authority: bool
    decision_authority: bool
    kernel_mutation: bool


    def to_dict(self):

        return {

            "receipt_id":
                self.receipt_id,

            "proof_status":
                self.proof_status,

            "evidence_id":
                self.evidence_id,

            "provenance":
                self.provenance,

            "authority":
                self.authority,

            "decision_authority":
                self.decision_authority,

            "kernel_mutation":
                self.kernel_mutation,

        }



class KX108EvidenceReceiptBuilder:


    def __init__(self):

        self.memory_write = False
        self.kernel_mutation = False



    def create(
        self,
        proof_result: dict,
        evidence: dict,
    ):

        return KX108EvidenceReceipt(

            receipt_id=
                "kx108-evidence-proof-receipt-v1",

            proof_status=
                proof_result.get(
                    "proof_status",
                    "UNPROVEN",
                ),

            evidence_id=
                evidence.get(
                    "evidence_id"
                ),

            provenance=
                "kx108-evidence-proof",

            authority=False,

            decision_authority=False,

            kernel_mutation=False,

        )



    def status(self):

        return {

            "memory_write":
                self.memory_write,

            "kernel_mutation":
                self.kernel_mutation,

        }
