"""
CG9 Mission Sequencer V1
"""

from scripts.providers.mission_execution_session_v1 import (
    MissionExecutionSession,
)


class MissionSequencer:

    def __init__(self):

        self.sessions = []

        self.decision_authority = False
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False


    def create_session(
        self,
        mission_id: str,
        provider_id: str,
        capability: str,
    ):

        session = MissionExecutionSession(
            mission_id=mission_id,
            provider_id=provider_id,
            capability=capability,
        )

        self.sessions.append(session)

        return session


    def start_mission(
        self,
        mission_id: str,
        provider_id: str,
        capability: str,
    ):

        session = self.create_session(
            mission_id,
            provider_id,
            capability,
        )

        return session.start()


    def status(self):

        return {
            "sessions": len(self.sessions),
            "decision_authority": self.decision_authority,
            "execution_authority": self.execution_authority,
            "memory_write": self.memory_write,
            "kernel_mutation": self.kernel_mutation,
            "emits_act": self.emits_act,
        }
