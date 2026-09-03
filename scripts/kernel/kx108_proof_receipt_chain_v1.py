"""
CG66 KX108 Proof Receipt Chain V1.

Validates the existing provider runtime receipt -> binding -> result
reference chain.

Receipts are proof surfaces only. They never become authority.
"""

from scripts.kernel.kx108_proof_receipt_validation_v1 import (
    KX108ProofReceiptValidator,
)


class KX108ProofReceiptChain:

    def __init__(self):
        self.validator = KX108ProofReceiptValidator()

        self.authority = False
        self.decision_authority = "KX108_ONLY"
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def validate(
        self,
        receipt,
        expected_result_ref=None,
        expected_invocation_id=None,
    ):

        validation = self.validator.validate(
            receipt,
            expected_result_ref=expected_result_ref,
            expected_invocation_id=expected_invocation_id,
        )

        binding = validation.get("binding")

        checks = {
            "receipt_validated":
                validation.get(
                    "receipt_validation_status"
                )
                == "VALIDATED",

            "binding_present":
                isinstance(binding, dict),

            "binding_bound":
                (
                    isinstance(binding, dict)
                    and binding.get("bound")
                    is True
                ),

            "runtime_identity_bound":
                (
                    isinstance(binding, dict)
                    and binding.get(
                        "runtime_execution_id"
                    )
                    == receipt.get(
                        "runtime_execution_id"
                    )
                ),

            "invocation_identity_bound":
                (
                    isinstance(binding, dict)
                    and binding.get(
                        "invocation_id"
                    )
                    == receipt.get(
                        "invocation_id"
                    )
                ),

            "result_reference_bound":
                (
                    isinstance(binding, dict)
                    and binding.get(
                        "result_ref"
                    )
                    == receipt.get(
                        "result_ref"
                    )
                ),

            "receipt_no_decision_authority":
                receipt.get(
                    "decision_authority"
                )
                is False,

            "receipt_no_execution_authority":
                receipt.get(
                    "execution_authority"
                )
                is False,

            "receipt_no_memory_write":
                receipt.get(
                    "memory_write"
                )
                is False,

            "receipt_no_kernel_mutation":
                receipt.get(
                    "kernel_mutation"
                )
                is False,

            "receipt_no_act":
                receipt.get(
                    "emits_act"
                )
                is False,
        }

        valid = all(checks.values())

        return {
            "receipt_chain_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "checks":
                checks,

            "receipt_validation":
                validation,

            "binding":
                binding,

            "receipt_is_authority":
                False,

            "authority":
                False,

            "decision_authority":
                "KX108_ONLY",

            "execution_authority":
                False,

            "memory_write":
                False,

            "kernel_mutation":
                False,

            "emits_act":
                False,
        }

    def status(self):

        return {
            "authority":
                self.authority,

            "decision_authority":
                self.decision_authority,

            "execution_authority":
                self.execution_authority,

            "memory_write":
                self.memory_write,

            "kernel_mutation":
                self.kernel_mutation,

            "emits_act":
                self.emits_act,
        }
