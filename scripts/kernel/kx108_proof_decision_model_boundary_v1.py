"""
CG44 KX108 Proof Decision Model Boundary V1
"""

from scripts.kernel.canonical_decision_envelope_v1 import (
    CanonicalDecisionEnvelopeBuilder,
)


class KX108ProofDecisionModelBoundary:

    def __init__(self):
        self.builder = (
            CanonicalDecisionEnvelopeBuilder()
        )

        self.decision_authority = False
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def validate(self, guard_result):

        if not isinstance(guard_result, dict):

            return {
                "decision_model_boundary_status":
                    "REJECTED",

                "checks":
                    {
                        "guard_object":
                            False,
                    },

                "decision_model":
                    None,

                "decision_authority":
                    False,

                "execution_authority":
                    False,

                "memory_write":
                    False,

                "kernel_mutation":
                    False,

                "emits_act":
                    False,
            }

        envelope = self.builder.build(
            guard_result
        )

        builder_status = self.builder.status()

        checks = {
            "guard_object":
                True,

            "provider_identity":
                envelope.source_provider
                != "unknown",

            "runtime_identity":
                envelope.runtime_ref
                != "unknown",

            "guard_status_known":
                envelope.guard_status
                != "UNKNOWN",

            "candidate_only":
                envelope.decision_status
                == "CANDIDATE_ONLY",

            "no_decision_authority":
                builder_status[
                    "decision_authority"
                ]
                is False,

            "no_execution_authority":
                builder_status[
                    "execution_authority"
                ]
                is False,

            "no_kernel_mutation":
                builder_status[
                    "kernel_mutation"
                ]
                is False,

            "no_act":
                builder_status[
                    "emits_act"
                ]
                is False,
        }

        valid = all(checks.values())

        return {
            "decision_model_boundary_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "checks":
                checks,

            "decision_model":
                envelope.to_dict(),

            "decision_authority":
                False,

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
