"""
CG57 KX108 Proof Memory Authority Boundary V1.

Memory sources remain readonly/non-sovereign.
Promotion policy may mark a candidate eligible for manual review,
but never grants automatic promotion or decision authority.
"""

from periphery.memory.memory_source_registry import (
    MemorySourceEntry,
)

from periphery.memory.memory_promotion_policy import (
    evaluate_promotion_policy,
)


class KX108ProofMemoryAuthorityBoundary:

    def __init__(self):
        self.decision_authority = "KX108_ONLY"
        self.memory_authority = False
        self.memory_write = False
        self.auto_promotion = False
        self.execution_authority = False
        self.kernel_mutation = False
        self.emits_act = False

    def validate_source(self, entry):

        if not isinstance(
            entry,
            MemorySourceEntry,
        ):

            return {
                "memory_source_boundary_status":
                    "REJECTED",

                "checks":
                    {
                        "memory_source_entry":
                            False,
                    },

                "memory_authority":
                    False,

                "memory_write":
                    False,

                "decision_authority":
                    "KX108_ONLY",

                "execution_authority":
                    False,

                "kernel_mutation":
                    False,

                "emits_act":
                    False,
            }

        checks = {
            "memory_source_entry":
                True,

            "readonly":
                entry.readonly
                is True,

            "write_forbidden":
                entry.write_allowed
                is False,
        }

        valid = all(checks.values())

        return {
            "memory_source_boundary_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "checks":
                checks,

            "source":
                entry.to_dict(),

            "memory_authority":
                False,

            "memory_write":
                False,

            "decision_authority":
                "KX108_ONLY",

            "execution_authority":
                False,

            "kernel_mutation":
                False,

            "emits_act":
                False,
        }

    def evaluate_candidate(
        self,
        candidate,
    ):

        decision = evaluate_promotion_policy(
            candidate
        )

        checks = {
            "human_review_required":
                decision.requires_human_review
                is True,

            "auto_promotion_blocked":
                decision.auto_promotion_blocked
                is True,

            "no_automatic_memory_write":
                True,
        }

        valid = all(checks.values())

        return {
            "memory_promotion_boundary_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "checks":
                checks,

            "promotion":
                decision.to_dict(),

            "manual_promotion_eligibility":
                decision.promotion_allowed,

            "automatic_promotion_authority":
                False,

            "memory_authority":
                False,

            "memory_write":
                False,

            "decision_authority":
                "KX108_ONLY",

            "execution_authority":
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

            "memory_authority":
                self.memory_authority,

            "memory_write":
                self.memory_write,

            "auto_promotion":
                self.auto_promotion,

            "execution_authority":
                self.execution_authority,

            "kernel_mutation":
                self.kernel_mutation,

            "emits_act":
                self.emits_act,
        }
