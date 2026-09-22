"""
CG67 KX108 Proof Provider Binding V1.

Validates provider/adapter/invocation/runtime-result identity binding.

Provider identity never grants KX108, execution, memory or ACT authority.
"""

from scripts.providers.provider_runtime_receipt_v1 import (
    ProviderRuntimeReceipt,
)

from scripts.providers.provider_runtime_receipt_binding_v1 import (
    ProviderRuntimeReceiptBinding,
)


class KX108ProofProviderBinding:

    def __init__(self):
        self.provider_authority = False
        self.decision_authority = "KX108_ONLY"
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def validate(
        self,
        receipt,
        binding,
        expected_provider_id=None,
        expected_adapter_id=None,
    ):

        canonical_objects = (
            isinstance(
                receipt,
                ProviderRuntimeReceipt,
            )
            and isinstance(
                binding,
                ProviderRuntimeReceiptBinding,
            )
        )

        if not canonical_objects:

            return {
                "provider_binding_status":
                    "REJECTED",

                "checks": {
                    "canonical_objects":
                        False,
                },

                "provider_authority":
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

        checks = {
            "canonical_objects":
                True,

            "provider_identity_present":
                bool(receipt.provider_id),

            "adapter_identity_present":
                bool(receipt.adapter_id),

            "invocation_identity_present":
                bool(receipt.invocation_id),

            "provider_matches_expected":
                (
                    expected_provider_id is None
                    or receipt.provider_id
                    == expected_provider_id
                ),

            "adapter_matches_expected":
                (
                    expected_adapter_id is None
                    or receipt.adapter_id
                    == expected_adapter_id
                ),

            "runtime_execution_binding":
                binding.runtime_execution_id
                == receipt.runtime_execution_id,

            "invocation_binding":
                binding.invocation_id
                == receipt.invocation_id,

            "result_binding":
                binding.result_ref
                == receipt.result_ref,

            "binding_complete":
                binding.bound
                is True,

            "receipt_no_decision_authority":
                receipt.decision_authority
                is False,

            "receipt_no_execution_authority":
                receipt.execution_authority
                is False,

            "binding_no_decision_authority":
                binding.decision_authority
                is False,

            "binding_no_execution_authority":
                binding.execution_authority
                is False,

            "no_memory_write":
                (
                    receipt.memory_write
                    is False
                    and binding.memory_write
                    is False
                ),

            "no_kernel_mutation":
                (
                    receipt.kernel_mutation
                    is False
                    and binding.kernel_mutation
                    is False
                ),

            "no_act":
                (
                    receipt.emits_act
                    is False
                    and binding.emits_act
                    is False
                ),
        }

        valid = all(checks.values())

        return {
            "provider_binding_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "checks":
                checks,

            "provider_id":
                receipt.provider_id,

            "adapter_id":
                receipt.adapter_id,

            "invocation_id":
                receipt.invocation_id,

            "runtime_execution_id":
                receipt.runtime_execution_id,

            "result_ref":
                receipt.result_ref,

            "provider_authority":
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
            "provider_authority":
                self.provider_authority,

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
