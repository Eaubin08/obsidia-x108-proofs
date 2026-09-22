"""
CG16 KX108 Domain State Receipt V1
"""

from dataclasses import dataclass


@dataclass
class KX108DomainStateReceipt:

    receipt_id: str
    domain: str
    state_hash: str
    confidence: float
    provenance: str
    kernel_mutation: bool


    def to_dict(self):

        return {
            "receipt_id": self.receipt_id,
            "domain": self.domain,
            "state_hash": self.state_hash,
            "confidence": self.confidence,
            "provenance": self.provenance,
            "kernel_mutation": self.kernel_mutation,
        }


class KX108DomainStateReceiptBuilder:


    def __init__(self):

        self.memory_write = False
        self.kernel_mutation = False


    def create(
        self,
        domain_state: dict,
    ):

        return KX108DomainStateReceipt(

            receipt_id=
                "kx108-domain-state-receipt-v1",

            domain=
                domain_state.get(
                    "domain",
                    "unknown",
                ),

            state_hash=
                domain_state.get(
                    "state_hash",
                    "undefined",
                ),

            confidence=
                domain_state.get(
                    "confidence",
                    0.0,
                ),

            provenance=
                domain_state.get(
                    "provenance",
                    "domain-adapter",
                ),

            kernel_mutation=False,
        )


    def status(self):

        return {
            "memory_write": self.memory_write,
            "kernel_mutation": self.kernel_mutation,
        }
