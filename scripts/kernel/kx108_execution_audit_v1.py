"""
CG12 KX108 Execution Audit V1
"""


class KX108ExecutionAudit:

    def __init__(self):

        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False


    def audit(
        self,
        boundary: dict,
        receipt: dict,
    ):

        checks = {

            "execution_authorized": (
                boundary.get(
                    "execution_status"
                )
                == "EXECUTION_AUTHORIZED"
            ),

            "receipt_valid": (
                receipt.get(
                    "receipt_id"
                )
                == "kx108-execution-receipt-v1"
            ),

            "boundary_binding": (
                receipt.get(
                    "source_boundary"
                )
                == "KX108_EXECUTION_BOUNDARY"
            ),

            "act_disabled": (
                receipt.get(
                    "act"
                )
                is False
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
            "execution": False,
            "act": False,
        }


    def status(self):

        return {
            "execution_authority": self.execution_authority,
            "memory_write": self.memory_write,
            "kernel_mutation": self.kernel_mutation,
            "emits_act": self.emits_act,
        }
