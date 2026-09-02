"""
CG12 KX108 Execution Receipt V1
"""

from dataclasses import dataclass


@dataclass
class KX108ExecutionReceipt:

    receipt_id: str
    execution_status: str
    source_boundary: str
    act: bool


    def to_dict(self):

        return {
            "receipt_id": self.receipt_id,
            "execution_status": self.execution_status,
            "source_boundary": self.source_boundary,
            "act": self.act,
        }


class KX108ExecutionReceiptBuilder:

    def __init__(self):

        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False


    def create(
        self,
        execution_result: dict,
    ):

        return KX108ExecutionReceipt(
            receipt_id="kx108-execution-receipt-v1",
            execution_status=execution_result.get(
                "execution_status",
                "UNKNOWN",
            ),
            source_boundary="KX108_EXECUTION_BOUNDARY",
            act=False,
        )


    def status(self):

        return {
            "execution_authority": self.execution_authority,
            "memory_write": self.memory_write,
            "kernel_mutation": self.kernel_mutation,
            "emits_act": self.emits_act,
        }
