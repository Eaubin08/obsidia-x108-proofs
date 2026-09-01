"""
CG9 Provider Cognitive Binder
Brody Runtime Adapter V1

Runtime callable boundary.

No decision.
No authority.
No mutation.
"""

from dataclasses import dataclass
from typing import Callable, Dict, Any


class BrodyRuntimeAdapterError(Exception):
    pass


@dataclass
class BrodyRuntimeAdapter:

    runtime: Callable[[Dict[str, Any]], Any]

    provider_id: str = "brody"
    adapter_id: str = "brody-runtime-v1"

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
    ) -> Dict:

        if not self.supports(capability):
            raise BrodyRuntimeAdapterError(
                f"Unsupported capability: {capability}"
            )

        if not callable(self.runtime):
            raise BrodyRuntimeAdapterError(
                "runtime unavailable"
            )

        output = self.runtime(payload)

        return {
            "provider_id": self.provider_id,
            "adapter_id": self.adapter_id,
            "capability": capability,
            "status": "PRODUCED",
            "output": output,
            "execution_authority": self.execution_authority,
            "decision_authority": self.decision_authority,
            "memory_write": self.memory_write,
            "kernel_mutation": self.kernel_mutation,
            "emits_act": self.emits_act,
        }
