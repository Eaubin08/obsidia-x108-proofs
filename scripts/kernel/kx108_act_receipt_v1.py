"""
CG13 KX108 ACT Receipt V1
"""

from dataclasses import dataclass


@dataclass
class KX108ACTReceipt:

    receipt_id: str
    act_status: str
    source_boundary: str
    act: bool


    def to_dict(self):

        return {
            "receipt_id": self.receipt_id,
            "act_status": self.act_status,
            "source_boundary": self.source_boundary,
            "act": self.act,
        }


class KX108ACTReceiptBuilder:

    def __init__(self):

        self.act_authority = False
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False


    def create(
        self,
        act_result: dict,
    ):

        return KX108ACTReceipt(
            receipt_id="kx108-act-receipt-v1",
            act_status=act_result.get(
                "act_status",
                "UNKNOWN",
            ),
            source_boundary="KX108_ACT_BOUNDARY",
            act=act_result.get(
                "act",
                False,
            ),
        )


    def status(self):

        return {
            "act_authority": self.act_authority,
            "execution_authority": self.execution_authority,
            "memory_write": self.memory_write,
            "kernel_mutation": self.kernel_mutation,
            "emits_act": self.emits_act,
        }
