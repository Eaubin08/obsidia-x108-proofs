"""
CG23 KX108 Proof Provenance Chain Boundary V1
"""


class KX108ProofProvenanceChain:


    def __init__(self):

        self.memory_write = False
        self.kernel_mutation = False



    def create_chain(
        self,
        source,
        evidence,
        receipt,
        audit,
    ):

        valid = all(
            [
                source.get("source_id") is not None,
                evidence.get("evidence_id") is not None,
                receipt.get("receipt_id") is not None,
                audit.get("audit_status") == "PASSED",
            ]
        )


        return {

            "chain_status":
                "VALID"
                if valid
                else "INVALID",

            "provenance_chain":

                [

                    {
                        "stage":
                            "SOURCE",

                        "id":
                            source.get("source_id"),

                    },

                    {
                        "stage":
                            "EVIDENCE",

                        "id":
                            evidence.get("evidence_id"),

                    },

                    {
                        "stage":
                            "RECEIPT",

                        "id":
                            receipt.get("receipt_id"),

                    },

                    {
                        "stage":
                            "AUDIT",

                        "id":
                            "audit-proof-chain-v1",

                    },

                ],


            "authority":
                False,

            "decision_authority":
                False,

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
