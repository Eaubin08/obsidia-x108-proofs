"""
CG9 Brody Runtime Receipt Adapter V1

Connects Brody runtime execution
with CG9 runtime receipt tracing.

No decision.
No authority.
No mutation.
"""

from scripts.providers.brody_runtime_flow_adapter_v1 import (
    BrodyRuntimeFlowAdapter,
)

from scripts.providers.provider_runtime_receipt_v1 import (
    ProviderRuntimeReceipt,
)


class BrodyRuntimeReceiptAdapter:


    def __init__(self):

        self.provider_id = "brody"

        self.flow_adapter = BrodyRuntimeFlowAdapter()

        self.decision_authority = False
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False


    def execute_with_receipt(
        self,
        mission_id: str,
        capability: str,
        payload: dict,
    ):

        result = self.flow_adapter.execute_flow(
            mission_id=mission_id,
            capability=capability,
            payload=payload,
        )


        receipt = ProviderRuntimeReceipt(
            adapter_id="brody_runtime_flow_adapter_v1",
            provider_id="brody",
            invocation_id=mission_id,
            result_ref=result["runtime_id"],
        )


        return {
            "result": result,
            "receipt": receipt.to_dict(),
        }


    def status(self):

        return {
            "provider_id": self.provider_id,
            "decision_authority": self.decision_authority,
            "execution_authority": self.execution_authority,
            "memory_write": self.memory_write,
            "kernel_mutation": self.kernel_mutation,
            "emits_act": self.emits_act,
        }
