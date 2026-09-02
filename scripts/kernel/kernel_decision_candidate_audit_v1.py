"""
CG10 Kernel Decision Candidate Audit V1
"""


class KernelDecisionCandidateAudit:

    def __init__(self):

        self.decision_authority = False
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False


    def audit(
        self,
        candidate_flow: dict,
        receipt: dict,
    ):

        checks = {
            "candidate_present": candidate_flow.get(
                "candidate"
            ) is not None,

            "receipt_present": receipt.get(
                "receipt_id"
            ) is not None,

            "candidate_only": (
                candidate_flow
                .get("candidate", {})
                .get("decision_status")
                == "CANDIDATE_ONLY"
            ),

            "provider_trace": receipt.get(
                "source_provider"
            ) is not None,

            "runtime_trace": receipt.get(
                "runtime_ref"
            ) is not None,
        }

        passed = all(checks.values())

        return {
            "audit_status": (
                "PASSED"
                if passed
                else "FAILED"
            ),
            "checks": checks,
            "decision": None,
        }


    def status(self):

        return {
            "decision_authority": self.decision_authority,
            "execution_authority": self.execution_authority,
            "memory_write": self.memory_write,
            "kernel_mutation": self.kernel_mutation,
            "emits_act": self.emits_act,
        }
