"""
CG9 Canonical Execution Orchestrator V1
"""

from scripts.providers.mission_execution_router_v1 import (
    MissionExecutionRouter,
)

from scripts.providers.canonical_execution_envelope_v1 import (
    CanonicalExecutionEnvelope,
)


class CanonicalExecutionOrchestrator:

    def __init__(self):

        self.router = MissionExecutionRouter()

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

        self.router.register_provider(
            provider_id,
            handler,
        )


    def execute(
        self,
        mission_id: str,
        provider_id: str,
        capability: str,
        payload: dict,
    ):

        output = self.router.execute(
            mission_id=mission_id,
            provider_id=provider_id,
            capability=capability,
            payload=payload,
        )

        result = output["result"]

        envelope = CanonicalExecutionEnvelope(
            mission_id=mission_id,
            provider_id=provider_id,
            capability=capability,
            runtime_id=result.get(
                "runtime_id",
                "runtime-unknown",
            ),
        )

        envelope.seal()

        return {
            "session": output["session"],
            "result": result,
            "envelope": envelope.to_dict(),
        }


    def status(self):

        return {
            "decision_authority": self.decision_authority,
            "execution_authority": self.execution_authority,
            "memory_write": self.memory_write,
            "kernel_mutation": self.kernel_mutation,
            "emits_act": self.emits_act,
        }
