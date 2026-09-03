"""
CG41 KX108 Proof Semantic Boundary V1
"""

from apps.obsidia_api.brody_semantic_query_router import (
    build_semantic_query,
)


class KX108ProofSemanticBoundary:

    def __init__(self):
        self.decision_authority = "KX108_ONLY"
        self.allowed_to_decide = False
        self.allowed_to_act = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def route(self, user_message):

        valid_input = (
            isinstance(user_message, str)
            and bool(user_message.strip())
        )

        semantic = (
            build_semantic_query(user_message)
            if valid_input
            else None
        )

        checks = {
            "valid_input":
                valid_input,

            "semantic_object":
                isinstance(semantic, dict),

            "topic_present":
                (
                    isinstance(semantic, dict)
                    and bool(semantic.get("topic"))
                ),

            "semantic_query_present":
                (
                    isinstance(semantic, dict)
                    and bool(
                        semantic.get(
                            "semantic_query"
                        )
                    )
                ),

            "primary_query_present":
                (
                    isinstance(semantic, dict)
                    and bool(
                        semantic.get(
                            "primary_query"
                        )
                    )
                ),

            "fallback_queries_list":
                (
                    isinstance(semantic, dict)
                    and isinstance(
                        semantic.get(
                            "fallback_queries"
                        ),
                        list,
                    )
                ),
        }

        valid = all(checks.values())

        return {
            "semantic_boundary_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "checks":
                checks,

            "semantic":
                semantic,

            "advisory_only":
                True,

            "decision_authority":
                "KX108_ONLY",

            "allowed_to_decide":
                False,

            "allowed_to_act":
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

            "allowed_to_decide":
                self.allowed_to_decide,

            "allowed_to_act":
                self.allowed_to_act,

            "memory_write":
                self.memory_write,

            "kernel_mutation":
                self.kernel_mutation,

            "emits_act":
                self.emits_act,
        }
