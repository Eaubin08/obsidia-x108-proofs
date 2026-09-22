"""
CG59 KX108 Proof Semantic Authority Boundary V1.

Semantic routing classifies/query-normalizes user text.
Classification is advisory metadata and never decision authority.
"""

from apps.obsidia_api.brody_semantic_query_router import (
    build_semantic_query,
)


class KX108ProofSemanticAuthorityBoundary:

    def __init__(self):
        self.decision_authority = "KX108_ONLY"
        self.semantic_authority = False
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def evaluate(self, user_message):

        if (
            not isinstance(user_message, str)
            or not user_message.strip()
        ):

            return {
                "semantic_authority_boundary_status":
                    "REJECTED",

                "checks":
                    {
                        "message_present":
                            False,
                    },

                "semantic_result":
                    None,

                "semantic_authority":
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

        semantic = build_semantic_query(
            user_message
        )

        checks = {
            "message_present":
                True,

            "semantic_result_object":
                isinstance(
                    semantic,
                    dict,
                ),

            "topic_present":
                bool(
                    semantic.get("topic")
                ),

            "semantic_query_present":
                bool(
                    semantic.get(
                        "semantic_query"
                    )
                ),

            "primary_query_present":
                bool(
                    semantic.get(
                        "primary_query"
                    )
                ),

            "classification_not_authority":
                True,
        }

        valid = all(checks.values())

        return {
            "semantic_authority_boundary_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "checks":
                checks,

            "semantic_result":
                semantic,

            "classification_only":
                True,

            "authorizes_decision":
                False,

            "authorizes_act":
                False,

            "semantic_authority":
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

            "semantic_authority":
                self.semantic_authority,

            "execution_authority":
                self.execution_authority,

            "memory_write":
                self.memory_write,

            "kernel_mutation":
                self.kernel_mutation,

            "emits_act":
                self.emits_act,
        }
