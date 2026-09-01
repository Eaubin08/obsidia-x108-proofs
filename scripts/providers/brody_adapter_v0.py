"""
CG9 Provider Cognitive Binder
Brody Adapter V0

Adapter boundary for Brody provider.

No authority.
No decision.
No memory mutation.
"""

from dataclasses import dataclass
from typing import Dict, Any


class BrodyAdapterError(Exception):
    pass


@dataclass
class BrodyAdapter:
    provider_id: str = "brody"
    adapter_id: str = "brody-adapter-v0"

    capabilities: tuple = (
        "reasoning",
        "analysis",
        "generation",
    )

    execution_authority: bool = False
    decision_authority: bool = False
    memory_write: bool = False
    kernel_mutation: bool = False
    emits_act: bool = False


    def supports(self, capability: str) -> bool:
        return capability in self.capabilities


    def invoke(
        self,
        capability: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:

        if not self.supports(capability):
            raise BrodyAdapterError(
                f"Unsupported capability: {capability}"
            )

        return {
            "provider_id": self.provider_id,
            "adapter_id": self.adapter_id,
            "capability": capability,
            "status": "PRODUCED",
            "payload": payload,
            "execution_authority": self.execution_authority,
            "decision_authority": self.decision_authority,
            "memory_write": self.memory_write,
            "kernel_mutation": self.kernel_mutation,
            "emits_act": self.emits_act,
        }


    def metadata(self):
        return {
            "provider_id": self.provider_id,
            "adapter_id": self.adapter_id,
            "capabilities": list(self.capabilities),
        }
