"""
CG80 KX108 Proof Provider Release Runtime V1.

Combines provider validation with a proof-pack release candidate.

This means candidate for review only.
It does NOT mean release ready, production ready or final freeze.
"""


class KX108ProofProviderReleaseRuntime:

    def __init__(self):

        self.release_authority = False
        self.provider_authority = False
        self.decision_authority = "KX108_ONLY"
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def evaluate(
        self,
        provider_validation,
        release_candidate,
    ):

        inputs_valid = (
            isinstance(
                provider_validation,
                dict,
            )
            and isinstance(
                release_candidate,
                dict,
            )
        )

        if not inputs_valid:

            return {
                "provider_release_runtime_status":
                    "REJECTED",

                "checks": {
                    "inputs_valid":
                        False,
                },

                "provider_release_candidate":
                    False,

                "release_authority":
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

            "provider_identity_present":
                bool(
                    provider_validation.get(
                        "provider_id"
                    )
                ),

            "proof_pack_release_candidate":
                release_candidate.get(
                    "release_candidate_status"
                )
                == "PROOF_PACK_RELEASE_CANDIDATE",

            "proof_pack_candidate_flag":
                release_candidate.get(
                    "proof_pack_release_candidate"
                )
                is True,

            "review_allowed":
                release_candidate.get(
                    "release_review_allowed"
                )
                is True,

            "not_release_ready":
                release_candidate.get(
                    "release_ready"
                )
                is False,

            "not_production_ready":
                release_candidate.get(
                    "production_ready"
                )
                is False,

            "not_deployment_ready":
                release_candidate.get(
                    "deployment_ready"
                )
                is False,

            "not_final_freeze":
                release_candidate.get(
                    "final_freeze"
                )
                is False,

            "provider_kx108_only":
                provider_validation.get(
                    "decision_authority"
                )
                == "KX108_ONLY",

            "candidate_kx108_only":
                release_candidate.get(
                    "decision_authority"
                )
                == "KX108_ONLY",

            "provider_no_execution_authority":
                provider_validation.get(
                    "execution_authority"
                )
                is False,

            "candidate_no_execution_authority":
                release_candidate.get(
                    "execution_authority"
                )
                is False,

            "provider_no_memory_write":
                provider_validation.get(
                    "memory_write"
                )
                is False,

            "candidate_no_memory_write":
                release_candidate.get(
                    "memory_write"
                )
                is False,

            "provider_no_kernel_mutation":
                provider_validation.get(
                    "kernel_mutation"
                )
                is False,

            "candidate_no_kernel_mutation":
                release_candidate.get(
                    "kernel_mutation"
                )
                is False,

            "provider_no_act":
                provider_validation.get(
                    "emits_act"
                )
                is False,

            "candidate_no_act":
                release_candidate.get(
                    "emits_act"
                )
                is False,
        }

        candidate = all(checks.values())

        return {
            "provider_release_runtime_status":
                "PROVIDER_RELEASE_CANDIDATE"
                if candidate
                else "REJECTED",

            "checks":
                checks,

            "provider_release_candidate":
                candidate,

            "provider_id":
                (
                    provider_validation.get(
                        "provider_id"
                    )
                    if candidate
                    else None
                ),

            "release_review_allowed":
                candidate,

            "release_ready":
                False,

            "production_ready":
                False,

            "deployment_ready":
                False,

            "final_freeze":
                False,

            "new_authority_created":
                False,

            "release_authority":
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
            "release_authority":
                self.release_authority,

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
