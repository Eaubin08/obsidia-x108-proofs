"""
CG18 KX108 Canonical Meta State Receipt V1
"""


from dataclasses import dataclass


@dataclass
class KX108CanonicalMetaStateReceipt:

    receipt_id: str
    aggregate_count: int
    aggregates: list
    canonical_meta_state: dict
    provenance: str
    decision_authority: bool
    kernel_mutation: bool


    def to_dict(self):

        return {

            "receipt_id":
                self.receipt_id,

            "aggregate_count":
                self.aggregate_count,

            "aggregates":
                self.aggregates,

            "canonical_meta_state":
                self.canonical_meta_state,

            "provenance":
                self.provenance,

            "decision_authority":
                self.decision_authority,

            "kernel_mutation":
                self.kernel_mutation,
        }



class KX108CanonicalMetaStateReceiptBuilder:


    def __init__(self):

        self.memory_write = False
        self.kernel_mutation = False


    def create(
        self,
        meta_state: dict,
    ):

        aggregates = (
            meta_state
            .get(
                "canonical_meta_state",
                {}
            )
            .get(
                "aggregates",
                []
            )
        )


        return KX108CanonicalMetaStateReceipt(

            receipt_id=
                "kx108-canonical-meta-state-receipt-v1",

            aggregate_count=
                meta_state
                .get(
                    "aggregate_count",
                    0
                ),

            aggregates=
                aggregates,

            canonical_meta_state=
                {
                    "aggregates":
                        aggregates
                },

            provenance=
                "meta-domain-coordination",

            decision_authority=False,

            kernel_mutation=False,
        )


    def status(self):

        return {

            "memory_write":
                self.memory_write,

            "kernel_mutation":
                self.kernel_mutation,
        }
