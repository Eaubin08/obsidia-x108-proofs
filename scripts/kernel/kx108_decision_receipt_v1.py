"""
CG11 KX108 Decision Receipt V1
"""

from dataclasses import dataclass


@dataclass
class KX108DecisionReceipt:

    receipt_id: str
    authority_status: str
    decision_status: str
    source_envelope: str


    def to_dict(self):

        return {
            "receipt_id": self.receipt_id,
            "authority_status": self.authority_status,
            "decision_status": self.decision_status,
            "source_envelope": self.source_envelope,
        }


class KX108DecisionReceiptBuilder:

    def __init__(self):

        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False


    def create(
        self,
        envelope: dict,
    ):

        return KX108DecisionReceipt(
            receipt_id="kx108-decision-receipt-v1",
            authority_status=envelope.get(
                "authority_status",
                "UNKNOWN",
            ),
            decision_status=envelope.get(
                "decision_status",
                "UNKNOWN",
            ),
            source_envelope="KX108_DECISION_ENVELOPE",
        )


    def status(self):

        return {
            "execution_authority": self.execution_authority,
            "memory_write": self.memory_write,
            "kernel_mutation": self.kernel_mutation,
            "emits_act": self.emits_act,
        }
