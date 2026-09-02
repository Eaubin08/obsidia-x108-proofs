"""
CG10 X108 Guard Adapter V1
"""

from dataclasses import dataclass


@dataclass
class GuardResult:

    status: str
    validated_input: bool
    guard_passed: bool
    decision_candidate: dict | None


class X108GuardAdapter:

    def __init__(self):

        self.decision_authority = False
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False


    def evaluate(
        self,
        bridge_result: dict,
    ):

        valid = (
            bridge_result.get("status")
            == "VALIDATED"
        )

        if valid:

            return GuardResult(
                status="GUARD_PASSED",
                validated_input=True,
                guard_passed=True,
                decision_candidate={
                    "status": "CANDIDATE_ONLY",
                    "source": bridge_result,
                },
            )

        return GuardResult(
            status="GUARD_REJECTED",
            validated_input=False,
            guard_passed=False,
            decision_candidate=None,
        )


    def status(self):

        return {
            "decision_authority": self.decision_authority,
            "execution_authority": self.execution_authority,
            "memory_write": self.memory_write,
            "kernel_mutation": self.kernel_mutation,
            "emits_act": self.emits_act,
        }
