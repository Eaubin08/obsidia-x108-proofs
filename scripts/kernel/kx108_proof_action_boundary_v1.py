"""
CG36 KX108 Proof Action Boundary V1
"""

from scripts.kernel.kx108_act_receipt_v1 import (
    KX108ACTReceiptBuilder,
)


class KX108ProofActionBoundary:

    def __init__(self):
        self.receipt_builder = KX108ACTReceiptBuilder()

        self.authority = False
        self.act_authority = False
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def validate(self, act_result):

        is_dict = isinstance(act_result, dict)

        receipt = (
            self.receipt_builder.create(act_result)
            if is_dict
            else None
        )

        checks = {
            "act_object":
                is_dict,

            "act_status_present":
                (
                    receipt is not None
                    and receipt.act_status != "UNKNOWN"
                ),

            "act_flag_boolean":
                (
                    receipt is not None
                    and isinstance(receipt.act, bool)
                ),

            "canonical_source":
                (
                    receipt is not None
                    and receipt.source_boundary
                    == "KX108_ACT_BOUNDARY"
                ),

            "receipt_identity":
                (
                    receipt is not None
                    and receipt.receipt_id
                    == "kx108-act-receipt-v1"
                ),

            "no_act_authority":
                (
                    self.receipt_builder
                    .status()["act_authority"]
                    is False
                ),
        }

        valid = all(checks.values())

        return {
            "action_boundary_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "checks":
                checks,

            "receipt":
                (
                    receipt.to_dict()
                    if receipt is not None
                    else None
                ),

            "act_observed":
                (
                    receipt.act
                    if receipt is not None
                    else False
                ),

            "authorizes_act":
                False,

            "authority":
                False,

            "act_authority":
                False,

            "execution_authority":
                False,

            "kernel_mutation":
                False,

            "emits_act":
                False,
        }

    def status(self):

        return {
            "authority": self.authority,
            "act_authority": self.act_authority,
            "execution_authority": self.execution_authority,
            "memory_write": self.memory_write,
            "kernel_mutation": self.kernel_mutation,
            "emits_act": self.emits_act,
        }
