"""
CG9 Provider Cognitive Binder
Provider Result Binding V0

Binds provider results to an authorized execution context.

No authority.
No decision.
No mutation.
"""

from dataclasses import dataclass
from typing import Dict


class ProviderResultBindingError(Exception):
    pass


@dataclass
class ProviderResultBinding:
    execution_session_id: str
    invocation_id: str
    provider_id: str
    result_ref: str

    bound: bool = False

    execution_authority: bool = False
    decision_authority: bool = False
    memory_write: bool = False
    kernel_mutation: bool = False
    emits_act: bool = False


    def bind(self):
        if not self.execution_session_id:
            raise ProviderResultBindingError(
                "execution_session_id required"
            )

        if not self.invocation_id:
            raise ProviderResultBindingError(
                "invocation_id required"
            )

        if not self.provider_id:
            raise ProviderResultBindingError(
                "provider_id required"
            )

        if not self.result_ref:
            raise ProviderResultBindingError(
                "result_ref required"
            )

        self.bound = True


    def to_dict(self) -> Dict:
        return {
            "execution_session_id": self.execution_session_id,
            "invocation_id": self.invocation_id,
            "provider_id": self.provider_id,
            "result_ref": self.result_ref,
            "bound": self.bound,
            "execution_authority": self.execution_authority,
            "decision_authority": self.decision_authority,
            "memory_write": self.memory_write,
            "kernel_mutation": self.kernel_mutation,
            "emits_act": self.emits_act,
        }
