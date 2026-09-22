"""
CG9 Obsidure Runtime Contract V1

Formal proof runtime boundary.

Obsidure produces verified results.
KX108 keeps decision authority.
"""

from dataclasses import dataclass, field
import uuid


class ObsidureRuntimeContractError(Exception):
    pass


@dataclass
class ObsidureRuntimeRequest:

    mission_id: str
    capability: str
    proof_target: str
    payload: dict


@dataclass
class ObsidureRuntimeResult:

    mission_id: str

    provider_id: str = "obsidure"

    runtime_id: str = field(
        default_factory=lambda: f"obsidure-runtime-{uuid.uuid4().hex[:12]}"
    )

    proof: dict = field(
        default_factory=dict
    )

    verified: bool = True

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
            "proof": self.proof,
            "verified": self.verified,
            "decision_authority": self.decision_authority,
            "execution_authority": self.execution_authority,
            "memory_write": self.memory_write,
            "kernel_mutation": self.kernel_mutation,
            "emits_act": self.emits_act,
        }


def validate_request(request):

    if not request.mission_id:
        raise ObsidureRuntimeContractError(
            "missing mission_id"
        )

    if not request.capability:
        raise ObsidureRuntimeContractError(
            "missing capability"
        )

    if not request.proof_target:
        raise ObsidureRuntimeContractError(
            "missing proof_target"
        )

    return True
