"""
CG13 KX108 ACT Boundary V1
"""


class KX108ACTBoundary:

    def __init__(self):

        self.act_authority = False
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False


    def evaluate(
        self,
        execution_audit: dict,
    ):

        valid = (
            execution_audit.get("audit_status")
            == "PASSED"
        )

        if valid and self.act_authority:

            return {
                "act_status": "ACT_AUTHORIZED",
                "act": True,
            }

        return {
            "act_status": "ACT_BLOCKED",
            "act": False,
        }


    def status(self):

        return {
            "act_authority": self.act_authority,
            "execution_authority": self.execution_authority,
            "memory_write": self.memory_write,
            "kernel_mutation": self.kernel_mutation,
            "emits_act": self.emits_act,
        }
