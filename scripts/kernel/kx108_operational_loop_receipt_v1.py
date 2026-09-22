"""
CG14 KX108 Operational Loop Receipt V1
"""

from dataclasses import dataclass


@dataclass
class KX108OperationalLoopReceipt:

    receipt_id: str
    previous_state: str
    transition: str
    next_state: str
    status: str


    def to_dict(self):

        return {
            "receipt_id": self.receipt_id,
            "previous_state": self.previous_state,
            "transition": self.transition,
            "next_state": self.next_state,
            "status": self.status,
        }


class KX108OperationalLoopReceiptBuilder:


    def __init__(self):

        self.memory_write = False
        self.kernel_mutation = False


    def create(
        self,
        transition_result: dict,
        previous_state: str,
        transition: str,
    ):

        return KX108OperationalLoopReceipt(
            receipt_id="kx108-operational-loop-receipt-v1",
            previous_state=previous_state,
            transition=transition,
            next_state=transition_result.get(
                "state",
                previous_state,
            ),
            status=transition_result.get(
                "transition_status",
                "UNKNOWN",
            ),
        )


    def status(self):

        return {
            "memory_write": self.memory_write,
            "kernel_mutation": self.kernel_mutation,
        }
