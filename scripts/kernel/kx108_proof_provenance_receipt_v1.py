"""
CG23 KX108 Proof Provenance Receipt V1
"""


from dataclasses import dataclass



@dataclass
class KX108ProofProvenanceReceipt:


    chain_id: str

    chain_status: str

    provenance_depth: int

    authority: bool

    decision_authority: bool

    kernel_mutation: bool



    def to_dict(self):

        return {

            "chain_id":
                self.chain_id,

            "chain_status":
                self.chain_status,

            "provenance_depth":
                self.provenance_depth,

            "authority":
                self.authority,

            "decision_authority":
                self.decision_authority,

            "kernel_mutation":
                self.kernel_mutation,

        }



class KX108ProofProvenanceReceiptBuilder:



    def __init__(self):

        self.memory_write = False
        self.kernel_mutation = False



    def create(self, chain):

        return KX108ProofProvenanceReceipt(

            chain_id=
                "kx108-proof-provenance-chain-v1",

            chain_status=
                chain.get(
                    "chain_status"
                ),

            provenance_depth=
                len(
                    chain.get(
                        "provenance_chain",
                        []
                    )
                ),

            authority=False,

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
