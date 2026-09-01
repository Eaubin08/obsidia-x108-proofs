"""
CG9 Provider Cognitive Binder
Provider Performance Comparison V1

Performance comparison boundary only.

No decision.
No selection.
No authority.
"""

from dataclasses import dataclass, field
import uuid


class ProviderPerformanceComparisonError(Exception):
    pass


@dataclass
class ProviderPerformanceComparison:

    comparison_id: str = field(
        default_factory=lambda: f"perf-comparison-{uuid.uuid4().hex[:16]}"
    )

    decision_authority: bool = False
    execution_authority: bool = False
    memory_write: bool = False
    kernel_mutation: bool = False
    emits_act: bool = False


    def compare(self, receipts):

        if not receipts:
            raise ProviderPerformanceComparisonError(
                "performance receipts required"
            )

        return {
            "comparison_id": self.comparison_id,
            "providers_compared": len(receipts),
            "receipts": receipts,
            "comparison_only": True,
            "decision_authority": self.decision_authority,
            "execution_authority": self.execution_authority,
            "memory_write": self.memory_write,
            "kernel_mutation": self.kernel_mutation,
            "emits_act": self.emits_act,
        }
