"""
CG13 KX108 ACT Audit V1
"""


class KX108ACTAudit:

    def __init__(self):

        self.act_authority = False
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False


    def audit(
        self,
        act_boundary: dict,
        act_receipt: dict,
    ):

        checks = {

            "act_boundary_valid": (
                act_boundary.get(
                    "act_status"
                )
                in [
                    "ACT_BLOCKED",
                    "ACT_AUTHORIZED",
                ]
            ),

            "receipt_valid": (
                act_receipt.get(
                    "receipt_id"
                )
                == "kx108-act-receipt-v1"
            ),

            "boundary_binding": (
                act_receipt.get(
                    "source_boundary"
                )
                == "KX108_ACT_BOUNDARY"
            ),

            "act_consistency": (
                act_receipt.get(
                    "act"
                )
                == (
                    act_boundary.get(
                        "act",
                        False
                    )
                )
            ),
        }

        passed = all(checks.values())

        return {
            "audit_status": (
                "PASSED"
                if passed
                else "FAILED"
            ),
            "checks": checks,
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
