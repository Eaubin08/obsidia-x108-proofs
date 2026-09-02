"""
CG10 Kernel Decision Candidate Flow V1
"""

from scripts.kernel.x108_guard_adapter_v1 import (
    X108GuardAdapter,
)

from scripts.kernel.canonical_decision_envelope_v1 import (
    CanonicalDecisionEnvelopeBuilder,
)


class KernelDecisionCandidateFlow:

    def __init__(self):

        self.guard = X108GuardAdapter()
        self.builder = CanonicalDecisionEnvelopeBuilder()

        self.decision_authority = False
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False


    def process(
        self,
        bridge_result: dict,
    ):

        guard_result = self.guard.evaluate(
            bridge_result
        )

        if not guard_result.guard_passed:

            return {
                "status": "REJECTED",
                "candidate": None,
            }


        candidate = self.builder.build(
            {
                "provider_id": bridge_result.get(
                    "provider_id",
                    "unknown",
                ),
                "runtime_id": bridge_result.get(
                    "runtime_id",
                    "unknown",
                ),
                "status": guard_result.status,
            }
        )

        return {
            "status": "CANDIDATE_CREATED",
            "candidate": candidate.to_dict(),
        }


    def status(self):

        return {
            "decision_authority": self.decision_authority,
            "execution_authority": self.execution_authority,
            "memory_write": self.memory_write,
            "kernel_mutation": self.kernel_mutation,
            "emits_act": self.emits_act,
        }
