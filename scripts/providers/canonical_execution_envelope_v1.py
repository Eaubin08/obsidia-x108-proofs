"""
CG9 Canonical Execution Envelope V1
"""

from dataclasses import dataclass, field
import uuid


@dataclass
class CanonicalExecutionEnvelope:

    mission_id: str
    provider_id: str
    capability: str
    runtime_id: str

    envelope_id: str = field(
        default_factory=lambda: f"envelope-{uuid.uuid4().hex[:12]}"
    )

    status: str = "CREATED"

    decision_authority: bool = False
    execution_authority: bool = False
    memory_write: bool = False
    kernel_mutation: bool = False
    emits_act: bool = False


    def seal(self):

        self.status = "SEALED"

        return self.to_dict()


    def to_dict(self):

        return {
            "envelope_id": self.envelope_id,
            "mission_id": self.mission_id,
            "provider_id": self.provider_id,
            "capability": self.capability,
            "runtime_id": self.runtime_id,
            "status": self.status,
            "decision_authority": self.decision_authority,
            "execution_authority": self.execution_authority,
            "memory_write": self.memory_write,
            "kernel_mutation": self.kernel_mutation,
            "emits_act": self.emits_act,
        }
