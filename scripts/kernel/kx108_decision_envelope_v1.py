"""
CG11 KX108 Decision Envelope V1
"""

from dataclasses import dataclass


@dataclass
class KX108DecisionEnvelope:

    authority_status: str
    decision_status: str
    source_authority: str
    act: bool


    def to_dict(self):

        return {
            "authority_status": self.authority_status,
            "decision_status": self.decision_status,
            "source_authority": self.source_authority,
            "act": self.act,
        }


class KX108DecisionEnvelopeBuilder:

    def __init__(self):

        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False


    def build(
        self,
        authority_result: dict,
    ):

        authorized = (
            authority_result.get("authority_status")
            == "AUTHORIZED_CANDIDATE"
        )

        if authorized:

            return KX108DecisionEnvelope(
                authority_status="AUTHORIZED_CANDIDATE",
                decision_status="KX108_DECISION_READY",
                source_authority="KX108",
                act=False,
            )

        return KX108DecisionEnvelope(
            authority_status="REJECTED",
            decision_status="NONE",
            source_authority="KX108",
            act=False,
        )


    def status(self):

        return {
            "execution_authority": self.execution_authority,
            "memory_write": self.memory_write,
            "kernel_mutation": self.kernel_mutation,
            "emits_act": self.emits_act,
        }
