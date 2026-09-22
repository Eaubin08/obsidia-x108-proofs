"""
CG72 KX108 Proof Provider Boundary V1.

Composes provider runtime validation with provider identity binding.

A provider can produce bounded runtime evidence but cannot become
decision or execution authority.
"""


class KX108ProofProviderBoundary:

    def __init__(self):
        self.provider_authority = False
        self.decision_authority = "KX108_ONLY"
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def validate(
        self,
        provider_runtime,
        provider_binding,
    ):

        inputs_valid = (
            isinstance(
                provider_runtime,
                dict,
            )
            and isinstance(
                provider_binding,
                dict,
            )
        )

        if not inputs_valid:

            return {
                "provider_boundary_status":
                    "REJECTED",

                "checks": {
                    "inputs_valid":
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
            "inputs_valid":
                True,

            "provider_runtime_validated":
                provider_runtime.get(
                    "provider_runtime_status"
                )
                == "VALIDATED",

            "provider_binding_validated":
                provider_binding.get(
                    "provider_binding_status"
                )
                == "VALIDATED",

            "provider_identity_bound":
                (
                    provider_runtime.get(
                        "provider_id"
                    )
                    == provider_binding.get(
                        "provider_id"
                    )
                ),

            "runtime_kx108_only":
                provider_runtime.get(
                    "decision_authority"
                )
                == "KX108_ONLY",

            "binding_kx108_only":
                provider_binding.get(
                    "decision_authority"
                )
                == "KX108_ONLY",

            "runtime_no_execution_authority":
                provider_runtime.get(
                    "execution_authority"
                )
                is False,

            "binding_no_execution_authority":
                provider_binding.get(
                    "execution_authority"
                )
                is False,

            "runtime_no_memory_write":
                provider_runtime.get(
                    "memory_write"
                )
                is False,

            "binding_no_memory_write":
                provider_binding.get(
                    "memory_write"
                )
                is False,

            "runtime_no_kernel_mutation":
                provider_runtime.get(
                    "kernel_mutation"
                )
                is False,

            "binding_no_kernel_mutation":
                provider_binding.get(
                    "kernel_mutation"
                )
                is False,

            "runtime_no_act":
                provider_runtime.get(
                    "emits_act"
                )
                is False,

            "binding_no_act":
                provider_binding.get(
                    "emits_act"
                )
                is False,
        }

        valid = all(checks.values())

        return {
            "provider_boundary_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "checks":
                checks,

            "provider_id":
                provider_runtime.get(
                    "provider_id"
                ),

            "provider_authority":
                False,

            "provider_can_decide":
                False,

            "provider_can_execute_by_authority":
                False,

            "provider_can_act":
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
