"""
CG10 Kernel Decision Candidate Receipt V1
"""

from dataclasses import dataclass


@dataclass
class DecisionCandidateReceipt:

    receipt_id: str
    source_provider: str
    runtime_ref: str
    candidate_status: str


    def to_dict(self):

        return {
            "receipt_id": self.receipt_id,
            "source_provider": self.source_provider,
            "runtime_ref": self.runtime_ref,
            "candidate_status": self.candidate_status,
        }


class KernelDecisionCandidateReceipt:

    def __init__(self):

        self.decision_authority = False
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False


    def create(
        self,
        candidate: dict,
    ):

        return DecisionCandidateReceipt(
            receipt_id="candidate-receipt-v1",
            source_provider=candidate.get(
                "source_provider",
                "unknown",
            ),
            runtime_ref=candidate.get(
                "runtime_ref",
                "unknown",
            ),
            candidate_status=candidate.get(
                "decision_status",
                "UNKNOWN",
            ),
        )


    def status(self):

        return {
            "decision_authority": self.decision_authority,
            "execution_authority": self.execution_authority,
            "memory_write": self.memory_write,
            "kernel_mutation": self.kernel_mutation,
            "emits_act": self.emits_act,
        }
