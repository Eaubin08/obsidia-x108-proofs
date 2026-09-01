"""
CG9 Provider Cognitive Binder
Provider Runtime Receipt V1

Runtime execution trace.

No authority.
No decision.
No mutation.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


class ProviderRuntimeReceiptError(Exception):
    pass


@dataclass
class ProviderRuntimeReceipt:

    provider_id: str
    adapter_id: str
    invocation_id: str

    runtime_execution_id: str = field(
        default_factory=lambda: f"runtime-{uuid.uuid4().hex[:16]}"
    )

    started_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    completed_at: str = ""

    status: str = "STARTED"

    result_ref: str = ""

    decision_authority: bool = False
    execution_authority: bool = False
    memory_write: bool = False
    kernel_mutation: bool = False
    emits_act: bool = False


    def complete(
        self,
        result_ref: str
    ):

        if not result_ref:
            raise ProviderRuntimeReceiptError(
                "result_ref required"
            )

        self.result_ref = result_ref

        self.completed_at = datetime.now(
            timezone.utc
        ).isoformat()

        self.status = "COMPLETED"


    def fail(self):

        self.status = "FAILED"

        self.completed_at = datetime.now(
            timezone.utc
        ).isoformat()


    def to_dict(self):

        return {
            "runtime_execution_id": self.runtime_execution_id,
            "provider_id": self.provider_id,
            "adapter_id": self.adapter_id,
            "invocation_id": self.invocation_id,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "status": self.status,
            "result_ref": self.result_ref,
            "decision_authority": self.decision_authority,
            "execution_authority": self.execution_authority,
            "memory_write": self.memory_write,
            "kernel_mutation": self.kernel_mutation,
            "emits_act": self.emits_act,
        }
