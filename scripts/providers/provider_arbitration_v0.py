"""
CG9 Provider Cognitive Binder
Provider Arbitration V0

Comparison layer only.

No decision.
No authority.
No ACT.
"""

from dataclasses import dataclass
from typing import List, Dict


class ProviderArbitrationError(Exception):
    pass


@dataclass
class ProviderArbitration:
    comparison_id: str

    decision_authority: bool = False
    execution_authority: bool = False
    memory_write: bool = False
    kernel_mutation: bool = False
    emits_act: bool = False


    def compare(
        self,
        results: List[Dict]
    ) -> Dict:

        if not results:
            raise ProviderArbitrationError(
                "results required"
            )

        return {
            "comparison_id": self.comparison_id,
            "providers_compared": len(results),
            "results": results,
            "comparison_only": True,
            "decision_authority": self.decision_authority,
            "execution_authority": self.execution_authority,
            "memory_write": self.memory_write,
            "kernel_mutation": self.kernel_mutation,
            "emits_act": self.emits_act,
        }
