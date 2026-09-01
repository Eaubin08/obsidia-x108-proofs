"""
CG9 Provider Cognitive Binder
Provider Flow Runner V0

Bounded provider execution pipeline.

No decision.
No authority escalation.
No mutation.
"""

from dataclasses import dataclass
from typing import Dict


class ProviderFlowRunnerError(Exception):
    pass


@dataclass
class ProviderFlowRunner:

    execution_authority: bool = False
    decision_authority: bool = False
    memory_write: bool = False
    kernel_mutation: bool = False
    emits_act: bool = False


    def run(
        self,
        envelope,
        session,
        adapter,
        result_binding,
    ) -> Dict:

        envelope.validate()

        if not adapter.supports(
            envelope.capability
        ):
            raise ProviderFlowRunnerError(
                "provider capability unavailable"
            )

        session.authorize()

        session.start()

        result = adapter.invoke(
            envelope.capability,
            {
                "input_ref": envelope.input_ref
            }
        )

        session.complete(
            result.get(
                "result_ref",
                "provider-result"
            )
        )

        result_binding.bind()

        session.close()

        return {
            "invocation_id": envelope.invocation_id,
            "provider_id": envelope.provider_id,
            "result": result,
            "result_bound": result_binding.bound,
            "session_state": session.state,
            "execution_authority": self.execution_authority,
            "decision_authority": self.decision_authority,
            "memory_write": self.memory_write,
            "kernel_mutation": self.kernel_mutation,
            "emits_act": self.emits_act,
        }
