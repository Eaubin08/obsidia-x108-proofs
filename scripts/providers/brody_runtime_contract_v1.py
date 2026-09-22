"""
CG9 Brody Runtime Contract V1

Runtime boundary only.

Brody produces cognitive output.
KX108 keeps authority.
"""

from dataclasses import dataclass, field
import uuid


class BrodyRuntimeContractError(Exception):
    pass


@dataclass
class BrodyRuntimeRequest:

    mission_id: str
    capability: str
    payload: dict


@dataclass
class BrodyRuntimeResult:

    mission_id: str
    provider_id: str = "brody"

    runtime_id: str = field(
        default_factory=lambda: f"brody-runtime-{uuid.uuid4().hex[:12]}"
    )

    result: dict = field(
        default_factory=dict
    )

    decision_authority: bool = False
    execution_authority: bool = False
    memory_write: bool = False
    kernel_mutation: bool = False
    emits_act: bool = False


    def to_dict(self):

        return {
            "mission_id": self.mission_id,
            "provider_id": self.provider_id,
            "runtime_id": self.runtime_id,
            "result": self.result,
            "decision_authority": self.decision_authority,
            "execution_authority": self.execution_authority,
            "memory_write": self.memory_write,
            "kernel_mutation": self.kernel_mutation,
            "emits_act": self.emits_act,
        }


def validate_request(request):

    if not request.mission_id:
        raise BrodyRuntimeContractError(
            "missing mission_id"
        )

    if not request.capability:
        raise BrodyRuntimeContractError(
            "missing capability"
        )

    return True
