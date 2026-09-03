"""
CG55 KX108 Proof Execution Authority Boundary V1.

Validates canonical execution trace/binding surfaces.

Completion of an execution trace does not itself confer
execution authority.
"""

from scripts.providers.canonical_execution_envelope_v1 import (
    CanonicalExecutionEnvelope,
)

from scripts.providers.provider_runtime_receipt_v1 import (
    ProviderRuntimeReceipt,
)

from scripts.providers.provider_runtime_receipt_binding_v1 import (
    ProviderRuntimeReceiptBinding,
)


class KX108ProofExecutionAuthorityBoundary:

    def __init__(self):
        self.decision_authority = "KX108_ONLY"
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def validate(
        self,
        envelope,
        receipt,
        binding,
    ):

        objects_valid = (
            isinstance(
                envelope,
                CanonicalExecutionEnvelope,
            )
            and isinstance(
                receipt,
                ProviderRuntimeReceipt,
            )
            and isinstance(
                binding,
                ProviderRuntimeReceiptBinding,
            )
        )

        if not objects_valid:

            return {
                "execution_authority_boundary_status":
                    "REJECTED",

                "checks":
                    {
                        "canonical_objects":
                            False,
                    },

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

            "envelope_sealed":
                envelope.status
                == "SEALED",

            "provider_binding":
                envelope.provider_id
                == receipt.provider_id,

            "result_binding":
                receipt.result_ref
                == envelope.runtime_id
                == binding.result_ref,

            "runtime_receipt_binding":
                binding.runtime_execution_id
                == receipt.runtime_execution_id,

            "invocation_binding":
                binding.invocation_id
                == receipt.invocation_id,

            "binding_complete":
                binding.bound
                is True,

            "envelope_no_execution_authority":
                envelope.execution_authority
                is False,

            "receipt_no_execution_authority":
                receipt.execution_authority
                is False,

            "binding_no_execution_authority":
                binding.execution_authority
                is False,

            "no_act":
                (
                    envelope.emits_act
                    is False
                    and receipt.emits_act
                    is False
                    and binding.emits_act
                    is False
                ),

            "no_memory_write":
                (
                    envelope.memory_write
                    is False
                    and receipt.memory_write
                    is False
                    and binding.memory_write
                    is False
                ),
        }

        valid = all(checks.values())

        return {
            "execution_authority_boundary_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "checks":
                checks,

            "envelope":
                envelope.to_dict(),

            "receipt":
                receipt.to_dict(),

            "binding":
                binding.to_dict(),

            "authorizes_execution":
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
