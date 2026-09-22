"""
CG17 KX108 Multi Domain Audit V1
"""


class KX108MultiDomainAudit:


    def __init__(self):

        self.memory_write = False
        self.kernel_mutation = False


    def audit(
        self,
        receipt: dict,
    ):

        checks = {

            "receipt_valid":
                receipt.get("receipt_id")
                ==
                "kx108-canonical-domain-state-receipt-v1",


            "domain_count_valid":
                receipt.get("domain_count", 0)
                > 0,


            "domains_present":
                len(
                    receipt.get(
                        "domains",
                        []
                    )
                )
                > 0,


            "canonical_state_present":
                receipt.get(
                    "canonical_state"
                )
                is not None,


            "provenance_valid":
                receipt.get(
                    "provenance"
                )
                ==
                "multi-domain-aggregation",


            "kernel_protected":
                receipt.get(
                    "kernel_mutation"
                )
                is False,
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
