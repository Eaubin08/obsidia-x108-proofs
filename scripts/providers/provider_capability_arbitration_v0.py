"""
CG9 Provider Cognitive Binder
Provider Capability Arbitration V0

Capability comparison only.

No provider selection.
No decision authority.
No execution authority.
"""

from dataclasses import dataclass
from typing import List, Dict


class ProviderCapabilityArbitrationError(Exception):
    pass


@dataclass
class ProviderCapabilityArbitration:

    comparison_id: str

    decision_authority: bool = False
    execution_authority: bool = False
    memory_write: bool = False
    kernel_mutation: bool = False
    emits_act: bool = False


    def compare_capabilities(
        self,
        capability: str,
        providers: List[Dict]
    ) -> Dict:

        if not capability:
            raise ProviderCapabilityArbitrationError(
                "capability required"
            )

        if not providers:
            raise ProviderCapabilityArbitrationError(
                "providers required"
            )

        compatible = []

        for provider in providers:
            capabilities = provider.get(
                "capabilities",
                []
            )

            if capability in capabilities:
                compatible.append(provider)


        return {
            "comparison_id": self.comparison_id,
            "requested_capability": capability,
            "providers_checked": len(providers),
            "compatible_providers": compatible,
            "comparison_only": True,
            "decision_authority": self.decision_authority,
            "execution_authority": self.execution_authority,
            "memory_write": self.memory_write,
            "kernel_mutation": self.kernel_mutation,
            "emits_act": self.emits_act,
        }
