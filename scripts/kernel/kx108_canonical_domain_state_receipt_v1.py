"""
CG17 KX108 Canonical Domain State Receipt V1
"""


from dataclasses import dataclass


@dataclass
class KX108CanonicalDomainStateReceipt:

    receipt_id: str
    domain_count: int
    domains: list
    canonical_state: dict
    provenance: str
    kernel_mutation: bool


    def to_dict(self):

        return {
            "receipt_id":
                self.receipt_id,

            "domain_count":
                self.domain_count,

            "domains":
                self.domains,

            "canonical_state":
                self.canonical_state,

            "provenance":
                self.provenance,

            "kernel_mutation":
                self.kernel_mutation,
        }



class KX108CanonicalDomainStateReceiptBuilder:


    def __init__(self):

        self.memory_write = False
        self.kernel_mutation = False


    def create(
        self,
        aggregated_state: dict,
    ):

        domains = (
            aggregated_state
            .get(
                "canonical_domain_state",
                []
            )
        )


        return KX108CanonicalDomainStateReceipt(

            receipt_id=
                "kx108-canonical-domain-state-receipt-v1",

            domain_count=
                aggregated_state
                .get(
                    "domain_count",
                    0
                ),

            domains=
                domains,

            canonical_state={
                "domains":
                    domains
            },

            provenance=
                "multi-domain-aggregation",

            kernel_mutation=False,
        )


    def status(self):

        return {
            "memory_write":
                self.memory_write,

            "kernel_mutation":
                self.kernel_mutation,
        }
