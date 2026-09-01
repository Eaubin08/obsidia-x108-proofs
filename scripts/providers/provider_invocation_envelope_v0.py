"""
CG9 Provider Cognitive Binder
Provider Invocation Envelope V0

Canonical bounded invocation transport.

No decision.
No authority.
No mutation.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict
import uuid


class ProviderInvocationEnvelopeError(Exception):
    pass


@dataclass
class ProviderInvocationEnvelope:

    mission_ref: str
    provider_id: str
    adapter_id: str
    capability: str
    authorization_ref: str
    execution_session_id: str
    input_ref: str

    invocation_id: str = field(
        default_factory=lambda: f"inv-{uuid.uuid4().hex[:16]}"
    )

    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    decision_authority: bool = False
    execution_authority: bool = False
    memory_write: bool = False
    kernel_mutation: bool = False
    emits_act: bool = False


    def validate(self):

        required = {
            "mission_ref": self.mission_ref,
            "provider_id": self.provider_id,
            "adapter_id": self.adapter_id,
            "capability": self.capability,
            "authorization_ref": self.authorization_ref,
            "execution_session_id": self.execution_session_id,
            "input_ref": self.input_ref,
        }

        missing = [
            key for key, value in required.items()
            if not value
        ]

        if missing:
            raise ProviderInvocationEnvelopeError(
                f"missing fields: {missing}"
            )

        return True


    def to_dict(self) -> Dict:
        return {
            "invocation_id": self.invocation_id,
            "mission_ref": self.mission_ref,
            "provider_id": self.provider_id,
            "adapter_id": self.adapter_id,
            "capability": self.capability,
            "authorization_ref": self.authorization_ref,
            "execution_session_id": self.execution_session_id,
            "input_ref": self.input_ref,
            "decision_authority": self.decision_authority,
            "execution_authority": self.execution_authority,
            "memory_write": self.memory_write,
            "kernel_mutation": self.kernel_mutation,
            "emits_act": self.emits_act,
        }
