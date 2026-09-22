"""
CG9 Provider Cognitive Binder
Provider Performance Receipt V1

Execution metrics trace only.

No decision.
No authority.
No mutation.
"""

from dataclasses import dataclass, field
import uuid


class ProviderPerformanceReceiptError(Exception):
    pass


@dataclass
class ProviderPerformanceReceipt:

    provider_id: str
    adapter_id: str
    execution_id: str

    performance_id: str = field(
        default_factory=lambda: f"perf-{uuid.uuid4().hex[:16]}"
    )

    latency_ms: float = 0.0
    token_cost: float = 0.0
    compute_cost: float = 0.0
    resource_usage: dict = field(
        default_factory=dict
    )

    status: str = "RECORDED"

    decision_authority: bool = False
    execution_authority: bool = False
    memory_write: bool = False
    kernel_mutation: bool = False
    emits_act: bool = False


    def record(
        self,
        latency_ms: float,
        token_cost: float,
        compute_cost: float,
        resource_usage: dict,
    ):

        if latency_ms < 0:
            raise ProviderPerformanceReceiptError(
                "invalid latency"
            )

        if token_cost < 0:
            raise ProviderPerformanceReceiptError(
                "invalid token cost"
            )

        if compute_cost < 0:
            raise ProviderPerformanceReceiptError(
                "invalid compute cost"
            )

        self.latency_ms = latency_ms
        self.token_cost = token_cost
        self.compute_cost = compute_cost
        self.resource_usage = resource_usage

        return True


    def to_dict(self):

        return {
            "performance_id": self.performance_id,
            "provider_id": self.provider_id,
            "adapter_id": self.adapter_id,
            "execution_id": self.execution_id,
            "latency_ms": self.latency_ms,
            "token_cost": self.token_cost,
            "compute_cost": self.compute_cost,
            "resource_usage": self.resource_usage,
            "status": self.status,
            "decision_authority": self.decision_authority,
            "execution_authority": self.execution_authority,
            "memory_write": self.memory_write,
            "kernel_mutation": self.kernel_mutation,
            "emits_act": self.emits_act,
        }
