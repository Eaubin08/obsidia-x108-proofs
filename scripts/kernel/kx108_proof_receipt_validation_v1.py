"""
CG32 KX108 Proof Receipt Validation V1
"""

from scripts.providers.provider_runtime_receipt_binding_v1 import (
    ProviderRuntimeReceiptBinding,
    ProviderRuntimeReceiptBindingError,
)


class KX108ProofReceiptValidator:

    def __init__(self):
        self.authority = False
        self.decision_authority = False
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

        is_dict = isinstance(receipt, dict)

        runtime_execution_id = (
            receipt.get("runtime_execution_id")
            if is_dict
            else None
        )

        invocation_id = (
            receipt.get("invocation_id")
            if is_dict
            else None
        )

        result_ref = (
            receipt.get("result_ref")
            if is_dict
            else None
        )

        binding = None
        binding_valid = False

        if (
            runtime_execution_id
            and invocation_id
            and result_ref
        ):
            try:
                binding_object = ProviderRuntimeReceiptBinding(
                    runtime_execution_id=runtime_execution_id,
                    invocation_id=invocation_id,
                    result_ref=result_ref,
                )

                binding_valid = binding_object.bind()
                binding = binding_object.to_dict()

            except ProviderRuntimeReceiptBindingError:
                binding_valid = False

        authority_preserved = (
            is_dict
            and receipt.get("decision_authority") is False
            and receipt.get("execution_authority") is False
            and receipt.get("memory_write") is False
            and receipt.get("kernel_mutation") is False
            and receipt.get("emits_act") is False
        )

        checks = {
            "receipt_object":
                is_dict,

            "runtime_execution_identity":
                bool(runtime_execution_id),

            "provider_identity":
                (
                    is_dict
                    and bool(receipt.get("provider_id"))
                ),

            "invocation_identity":
                bool(invocation_id),

            "result_reference":
                bool(result_ref),

            "status_acceptable":
                (
                    is_dict
                    and receipt.get("status")
                    in {"STARTED", "COMPLETED"}
                ),

            "binding_valid":
                binding_valid is True,

            "result_ref_matches":
                (
                    expected_result_ref is None
                    or result_ref == expected_result_ref
                ),

            "invocation_matches":
                (
                    expected_invocation_id is None
                    or invocation_id == expected_invocation_id
                ),

            "authority_boundary_preserved":
                authority_preserved,
        }

        valid = all(checks.values())

        return {
            "receipt_validation_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "checks":
                checks,

            "binding":
                binding,

            "runtime_execution_id":
                runtime_execution_id,

            "result_ref":
                result_ref,

            "authority":
                False,

            "decision_authority":
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
            "decision_authority": self.decision_authority,
            "execution_authority": self.execution_authority,
            "memory_write": self.memory_write,
            "kernel_mutation": self.kernel_mutation,
            "emits_act": self.emits_act,
        }
