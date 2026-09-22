"""
CG10 Canonical Decision Envelope V1
"""

from dataclasses import dataclass


@dataclass
class CanonicalDecisionEnvelope:

    envelope_id: str
    source_provider: str
    runtime_ref: str
    guard_status: str
    decision_status: str


    def to_dict(self):

        return {
            "envelope_id": self.envelope_id,
            "source_provider": self.source_provider,
            "runtime_ref": self.runtime_ref,
            "guard_status": self.guard_status,
            "decision_status": self.decision_status,
        }


class CanonicalDecisionEnvelopeBuilder:

    def __init__(self):

        self.decision_authority = False
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False


    def build(
        self,
        guard_result: dict,
    ):

        return CanonicalDecisionEnvelope(
            envelope_id="decision-envelope-v1",
            source_provider=guard_result.get(
                "provider_id",
                "unknown",
            ),
            runtime_ref=guard_result.get(
                "runtime_id",
                "unknown",
            ),
            guard_status=guard_result.get(
                "status",
                "UNKNOWN",
            ),
            decision_status="CANDIDATE_ONLY",
        )


    def status(self):

        return {
            "decision_authority": self.decision_authority,
            "execution_authority": self.execution_authority,
            "memory_write": self.memory_write,
            "kernel_mutation": self.kernel_mutation,
            "emits_act": self.emits_act,
        }
