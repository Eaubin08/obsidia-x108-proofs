"""
CG9 Brody Runtime Flow Adapter V1

Bridge between CG9 flow and Brody runtime engine.

No decision.
No authority.
No mutation.
"""

from scripts.providers.brody_runtime_contract_v1 import (
    BrodyRuntimeRequest,
)

from scripts.providers.brody_runtime_engine_v1 import (
    BrodyRuntimeEngine,
)


class BrodyRuntimeFlowAdapter:


    def __init__(self):

        self.provider_id = "brody"
        self.engine = BrodyRuntimeEngine()

        self.decision_authority = False
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False


    def execute_flow(
        self,
        mission_id: str,
        capability: str,
        payload: dict,
    ):

        request = BrodyRuntimeRequest(
            mission_id=mission_id,
            capability=capability,
            payload=payload,
        )

        result = self.engine.execute(
            request
        )

        return result.to_dict()


    def status(self):

        return {
            "provider_id": self.provider_id,
            "decision_authority": self.decision_authority,
            "execution_authority": self.execution_authority,
            "memory_write": self.memory_write,
            "kernel_mutation": self.kernel_mutation,
            "emits_act": self.emits_act,
        }
