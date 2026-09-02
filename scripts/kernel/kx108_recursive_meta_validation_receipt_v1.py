"""
CG21 KX108 Recursive Meta Validation Receipt V1
"""

from dataclasses import dataclass


@dataclass
class KX108RecursiveMetaValidationReceipt:

    receipt_id: str
    validation_status: str
    provenance: str
    validation_authority: bool
    decision_authority: bool
    kernel_mutation: bool

    def to_dict(self):
        return {
            "receipt_id": self.receipt_id,
            "validation_status": self.validation_status,
            "provenance": self.provenance,
            "validation_authority": self.validation_authority,
            "decision_authority": self.decision_authority,
            "kernel_mutation": self.kernel_mutation,
        }


class KX108RecursiveMetaValidationReceiptBuilder:

    def __init__(self):
        self.memory_write = False
        self.kernel_mutation = False

    def create(self, validation_result: dict):

        return KX108RecursiveMetaValidationReceipt(
            receipt_id=
                "kx108-recursive-meta-validation-receipt-v1",

            validation_status=
                validation_result.get(
                    "validation_status",
                    "REJECTED",
                ),

            provenance=
                "recursive-meta-validation",

            validation_authority=False,
            decision_authority=False,
            kernel_mutation=False,
        )

    def status(self):
        return {
            "memory_write": self.memory_write,
            "kernel_mutation": self.kernel_mutation,
        }
