"""
CG79 KX108 Proof Provider Governance Runtime V1.

Composes an already-validated provider runtime proof with an
already-closed governance proof.

Governance observes and constrains provider evidence.
It never makes the provider a decision authority.
"""


class KX108ProofProviderGovernanceRuntime:

    def __init__(self):

        self.governance_authority = False
        self.provider_authority = False
        self.decision_authority = "KX108_ONLY"
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def validate(
        self,
        provider_validation,
        governance_closure,
    ):

        inputs_valid = (
            isinstance(
                provider_validation,
                dict,
            )
            and isinstance(
                governance_closure,
                dict,
            )
        )

        if not inputs_valid:

            return {
                "provider_governance_runtime_status":
                    "REJECTED",

                "checks": {
                    "inputs_valid":
                        False,
                },

                "governance_authority":
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

        checks = {
            "inputs_valid":
                True,

            "provider_validation_validated":
                provider_validation.get(
                    "provider_validation_runtime_status"
                )
                == "VALIDATED",

            "governance_closed":
                governance_closure.get(
                    "governance_closure_status"
                )
                == "CLOSED",

            "provider_identity_present":
                bool(
                    provider_validation.get(
                        "provider_id"
                    )
                ),

            "provider_kx108_only":
                provider_validation.get(
                    "decision_authority"
                )
                == "KX108_ONLY",

            "governance_kx108_only":
                governance_closure.get(
                    "decision_authority"
                )
                == "KX108_ONLY",

            "provider_no_authority":
                provider_validation.get(
                    "provider_authority"
                )
                is False,

            "provider_no_execution_authority":
                provider_validation.get(
                    "execution_authority"
                )
                is False,

            "governance_no_execution_authority":
                governance_closure.get(
                    "execution_authority"
                )
                is False,

            "provider_no_memory_write":
                provider_validation.get(
                    "memory_write"
                )
                is False,

            "governance_no_memory_write":
                governance_closure.get(
                    "memory_write"
                )
                is False,

            "provider_no_kernel_mutation":
                provider_validation.get(
                    "kernel_mutation"
                )
                is False,

            "governance_no_kernel_mutation":
                governance_closure.get(
                    "kernel_mutation"
                )
                is False,

            "provider_no_act":
                provider_validation.get(
                    "emits_act"
                )
                is False,

            "governance_no_act":
                governance_closure.get(
                    "emits_act"
                )
                is False,

            "governance_created_no_authority":
                governance_closure.get(
                    "new_authority_created"
                )
                is False,
        }

        valid = all(checks.values())

        return {
            "provider_governance_runtime_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "checks":
                checks,

            "provider_id":
                provider_validation.get(
                    "provider_id"
                ),

            "provider_validation":
                provider_validation,

            "governance_closure":
                governance_closure,

            "provider_can_decide":
                False,

            "governance_authority":
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
            "governance_authority":
                self.governance_authority,

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
