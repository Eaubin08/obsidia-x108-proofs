"""
CG9 Canonical Runtime Receipt Flow V1
"""

from scripts.providers.canonical_execution_flow_v1 import (
    CanonicalExecutionFlow,
)

from scripts.providers.provider_runtime_receipt_v1 import (
    ProviderRuntimeReceipt,
)


class CanonicalRuntimeReceiptFlow:

    def __init__(self):

        self.flow = CanonicalExecutionFlow()

        self.decision_authority = False
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False


    def register_provider(
        self,
        provider_id: str,
        handler,
    ):

        self.flow.register_provider(
            provider_id,
            handler,
        )


    def run(
        self,
        mission_id: str,
        provider_id: str,
        capability: str,
        payload: dict,
    ):

        execution = self.flow.run(
            mission_id=mission_id,
            provider_id=provider_id,
            capability=capability,
            payload=payload,
        )

        envelope = execution["execution"]["envelope"]

        receipt = ProviderRuntimeReceipt(
            adapter_id=f"{provider_id}_runtime",
            provider_id=provider_id,
            invocation_id=mission_id,
            result_ref=envelope["runtime_id"],
        )

        return {
            "execution": execution,
            "receipt": receipt.to_dict(),
        }


    def status(self):

        return {
            "decision_authority": self.decision_authority,
            "execution_authority": self.execution_authority,
            "memory_write": self.memory_write,
            "kernel_mutation": self.kernel_mutation,
            "emits_act": self.emits_act,
        }
