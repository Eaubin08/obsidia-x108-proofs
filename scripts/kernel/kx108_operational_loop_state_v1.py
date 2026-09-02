"""
CG14 KX108 Operational Loop State V1
"""


class KX108OperationalLoopState:

    VALID_TRANSITIONS = {

        "OBSERVATION": [
            "DECISION_PENDING",
        ],

        "DECISION_PENDING": [
            "DECISION_VALIDATED",
        ],

        "DECISION_VALIDATED": [
            "EXECUTION_AUTHORIZED",
        ],

        "EXECUTION_AUTHORIZED": [
            "ACT_EVALUATED",
        ],

        "ACT_EVALUATED": [
            "FEEDBACK_RECEIVED",
        ],

        "FEEDBACK_RECEIVED": [
            "CONTEXT_UPDATED",
        ],

        "CONTEXT_UPDATED": [
            "OBSERVATION",
        ],
    }


    def __init__(self):

        self.current_state = "OBSERVATION"

        self.memory_write = False
        self.kernel_mutation = False


    def transition(
        self,
        next_state: str,
    ):

        allowed = self.VALID_TRANSITIONS.get(
            self.current_state,
            [],
        )

        if next_state in allowed:

            self.current_state = next_state

            return {
                "transition_status": "ACCEPTED",
                "state": self.current_state,
            }

        return {
            "transition_status": "BLOCKED",
            "state": self.current_state,
        }


    def status(self):

        return {
            "state": self.current_state,
            "memory_write": self.memory_write,
            "kernel_mutation": self.kernel_mutation,
        }
