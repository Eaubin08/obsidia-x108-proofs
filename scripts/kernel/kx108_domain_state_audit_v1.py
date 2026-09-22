"""
CG16 KX108 Domain State Audit V1
"""


class KX108DomainStateAudit:


    def __init__(self):

        self.memory_write = False
        self.kernel_mutation = False


    def audit(
        self,
        receipt: dict,
    ):

        checks = {

            "receipt_valid": (
                receipt.get("receipt_id")
                == "kx108-domain-state-receipt-v1"
            ),

            "domain_present": (
                receipt.get("domain")
                is not None
            ),

            "state_hash_present": (
                receipt.get("state_hash")
                is not None
            ),

            "confidence_valid": (
                receipt.get("confidence", 0)
                >= 0
            ),

            "provenance_present": (
                receipt.get("provenance")
                is not None
            ),

            "kernel_protected": (
                receipt.get("kernel_mutation")
                is False
            ),
        }

        passed = all(
            checks.values()
        )

        return {
            "audit_status":
                "PASSED"
                if passed
                else "FAILED",

            "checks":
                checks,

            "kernel_mutation":
                False,
        }


    def status(self):

        return {
            "memory_write":
                self.memory_write,

            "kernel_mutation":
                self.kernel_mutation,
        }
