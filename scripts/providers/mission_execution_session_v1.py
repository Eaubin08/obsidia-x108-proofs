"""
CG9 Mission Execution Session V1
"""

from dataclasses import dataclass, field
import uuid


@dataclass
class MissionExecutionSession:

    mission_id: str
    provider_id: str
    capability: str

    session_id: str = field(
        default_factory=lambda: f"session-{uuid.uuid4().hex[:12]}"
    )

    status: str = "CREATED"

    decision_authority: bool = False
    execution_authority: bool = False
    memory_write: bool = False
    kernel_mutation: bool = False
    emits_act: bool = False


    def start(self):

        self.status = "RUNNING"

        return self.to_dict()


    def complete(self):

        self.status = "COMPLETED"

        return self.to_dict()


    def to_dict(self):

        return {
            "session_id": self.session_id,
            "mission_id": self.mission_id,
            "provider_id": self.provider_id,
            "capability": self.capability,
            "status": self.status,
            "decision_authority": self.decision_authority,
            "execution_authority": self.execution_authority,
            "memory_write": self.memory_write,
            "kernel_mutation": self.kernel_mutation,
            "emits_act": self.emits_act,
        }
