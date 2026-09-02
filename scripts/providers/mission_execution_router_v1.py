"""
CG9 Mission Execution Router V1
"""

from scripts.providers.mission_sequencer_v1 import (
    MissionSequencer,
)


class MissionExecutionRouter:

    def __init__(self):

        self.sequencer = MissionSequencer()

        self.routes = {}

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

        self.routes[provider_id] = handler


    def execute(
        self,
        mission_id: str,
        provider_id: str,
        capability: str,
        payload: dict,
    ):

        session = self.sequencer.create_session(
            mission_id,
            provider_id,
            capability,
        )

        session.start()

        provider = self.routes[provider_id]

        result = provider(
            mission_id=mission_id,
            capability=capability,
            payload=payload,
        )

        session.complete()

        return {
            "session": session.to_dict(),
            "result": result,
        }


    def status(self):

        return {
            "routes": list(self.routes.keys()),
            "decision_authority": self.decision_authority,
            "execution_authority": self.execution_authority,
            "memory_write": self.memory_write,
            "kernel_mutation": self.kernel_mutation,
            "emits_act": self.emits_act,
        }
