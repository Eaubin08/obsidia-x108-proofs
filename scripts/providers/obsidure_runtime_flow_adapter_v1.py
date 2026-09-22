"""
CG9 Obsidure Runtime Flow Adapter V1
"""

from scripts.providers.obsidure_runtime_contract_v1 import (
    ObsidureRuntimeRequest,
)

from scripts.providers.obsidure_runtime_engine_v1 import (
    ObsidureRuntimeEngine,
)


class ObsidureRuntimeFlowAdapter:

    def __init__(self):

        self.provider_id = "obsidure"
        self.engine = ObsidureRuntimeEngine()

        self.decision_authority = False
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False


    def execute_flow(
        self,
        mission_id: str,
        capability: str,
        proof_target: str,
        payload: dict,
    ):

        request = ObsidureRuntimeRequest(
            mission_id=mission_id,
            capability=capability,
            proof_target=proof_target,
            payload=payload,
        )

        result = self.engine.execute(request)

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
