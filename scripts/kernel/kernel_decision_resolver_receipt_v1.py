"""
CG10 Kernel Decision Resolver Receipt V1
"""

from dataclasses import dataclass


@dataclass
class DecisionResolverReceipt:

    receipt_id: str
    resolver_status: str
    decision_status: str
    source_gate: str


    def to_dict(self):

        return {
            "receipt_id": self.receipt_id,
            "resolver_status": self.resolver_status,
            "decision_status": self.decision_status,
            "source_gate": self.source_gate,
        }


class KernelDecisionResolverReceipt:

    def __init__(self):

        self.decision_authority = False
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False


    def create(
        self,
        resolver_result: dict,
    ):

        return DecisionResolverReceipt(
            receipt_id="resolver-receipt-v1",
            resolver_status=resolver_result.get(
                "resolver_status",
                "UNKNOWN",
            ),
            decision_status=resolver_result.get(
                "decision_status",
                "UNKNOWN",
            ),
            source_gate="OPEN_FOR_DECISION",
        )


    def status(self):

        return {
            "decision_authority": self.decision_authority,
            "execution_authority": self.execution_authority,
            "memory_write": self.memory_write,
            "kernel_mutation": self.kernel_mutation,
            "emits_act": self.emits_act,
        }
