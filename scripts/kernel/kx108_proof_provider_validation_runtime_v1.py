"""
CG76 KX108 Proof Provider Validation Runtime V1.

Aggregates already-produced provider runtime, binding and boundary
proofs.

It does not invoke a provider.
It does not create provider authority.
"""


class KX108ProofProviderValidationRuntime:

    def __init__(self):

        self.validation_authority = False
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
        provider_boundary,
    ):

        inputs_valid = all(
            isinstance(result, dict)
            for result in (
                provider_runtime,
                provider_binding,
                provider_boundary,
            )
        )

        if not inputs_valid:

            return {
                "provider_validation_runtime_status":
                    "REJECTED",

                "checks": {
                    "inputs_valid":
                        False,
                },

                "provider_invoked_here":
                    False,

                "validation_authority":
                    False,

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

        provider_ids = (
            provider_runtime.get(
                "provider_id"
            ),
            provider_binding.get(
                "provider_id"
            ),
            provider_boundary.get(
                "provider_id"
            ),
        )

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

            "provider_boundary_validated":
                provider_boundary.get(
                    "provider_boundary_status"
                )
                == "VALIDATED",

            "provider_identity_present":
                all(
                    bool(provider_id)
                    for provider_id
                    in provider_ids
                ),

            "provider_identity_closed":
                (
                    len(set(provider_ids))
                    == 1
                ),

            "runtime_did_not_invoke_provider":
                provider_runtime.get(
                    "provider_invoked_here"
                )
                is False,

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

            "boundary_kx108_only":
                provider_boundary.get(
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

            "boundary_no_execution_authority":
                provider_boundary.get(
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

            "boundary_no_memory_write":
                provider_boundary.get(
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

            "boundary_no_kernel_mutation":
                provider_boundary.get(
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

            "boundary_no_act":
                provider_boundary.get(
                    "emits_act"
                )
                is False,
        }

        valid = all(checks.values())

        return {
            "provider_validation_runtime_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "checks":
                checks,

            "provider_id":
                (
                    provider_ids[0]
                    if valid
                    else None
                ),

            "provider_invoked_here":
                False,

            "validation_authority":
                False,

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
            "validation_authority":
                self.validation_authority,

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
