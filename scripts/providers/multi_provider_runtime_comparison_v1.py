"""
CG9 Provider Cognitive Binder
Multi Provider Runtime Comparison V1

Comparison boundary only.

No selection.
No decision.
No authority.
"""

from dataclasses import dataclass, field
import uuid


class MultiProviderRuntimeComparisonError(Exception):
    pass


@dataclass
class MultiProviderRuntimeComparison:

    comparison_id: str = field(
        default_factory=lambda: f"comparison-{uuid.uuid4().hex[:16]}"
    )

    decision_authority: bool = False
    execution_authority: bool = False
    memory_write: bool = False
    kernel_mutation: bool = False
    emits_act: bool = False


    def compare(self, results):

        if not results:
            raise MultiProviderRuntimeComparisonError(
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
