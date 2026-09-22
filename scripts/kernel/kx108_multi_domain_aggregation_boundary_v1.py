"""
CG17 KX108 Multi Domain Aggregation Boundary V1
"""


class KX108MultiDomainAggregationBoundary:


    def __init__(self):

        self.memory_write = False
        self.kernel_mutation = False


    def aggregate(
        self,
        domain_states: list,
    ):

        return {
            "aggregation_status":
                "COMPLETED",

            "domain_count":
                len(domain_states),

            "canonical_domain_state":
                domain_states,

            "target":
                "KX108_EVALUATION",

            "kernel_mutation":
                False,
        }


    def accept_domain_states(
        self,
        domain_states: list,
    ):

        return {
            "domains_status":
                "ACCEPTED",

            "count":
                len(domain_states),

            "aggregation_allowed":
                True,

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
