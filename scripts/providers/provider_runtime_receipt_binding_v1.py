"""
CG9 Provider Cognitive Binder
Provider Runtime Receipt Binding V1

Binds runtime execution trace to result proof.

No authority.
No decision.
No mutation.
"""

from dataclasses import dataclass, field
import uuid


class ProviderRuntimeReceiptBindingError(Exception):
    pass


@dataclass
class ProviderRuntimeReceiptBinding:

    runtime_execution_id: str
    invocation_id: str
    result_ref: str

    binding_ref: str = field(
        default_factory=lambda: f"binding-{uuid.uuid4().hex[:16]}"
    )

    bound: bool = False

    decision_authority: bool = False
    execution_authority: bool = False
    memory_write: bool = False
    kernel_mutation: bool = False
    emits_act: bool = False


    def bind(self):

        if not self.runtime_execution_id:
            raise ProviderRuntimeReceiptBindingError(
                "runtime_execution_id required"
            )

        if not self.invocation_id:
            raise ProviderRuntimeReceiptBindingError(
                "invocation_id required"
            )

        if not self.result_ref:
            raise ProviderRuntimeReceiptBindingError(
                "result_ref required"
            )

        self.bound = True

        return True


    def to_dict(self):

        return {
            "binding_ref": self.binding_ref,
            "runtime_execution_id": self.runtime_execution_id,
            "invocation_id": self.invocation_id,
            "result_ref": self.result_ref,
            "bound": self.bound,
            "decision_authority": self.decision_authority,
            "execution_authority": self.execution_authority,
            "memory_write": self.memory_write,
            "kernel_mutation": self.kernel_mutation,
            "emits_act": self.emits_act,
        }
