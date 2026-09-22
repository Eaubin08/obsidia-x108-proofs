"""
CG47 KX108 Proof Trust Boundary V1.

Trust is evidence continuity / traceability only.
It never grants decision or execution authority.
"""

from periphery.math_core.trust_path import (
    build_trust_path,
)


class KX108ProofTrustBoundary:

    def __init__(self):
        self.decision_authority = "KX108_ONLY"
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def validate(
        self,
        action_id,
        ticket,
        proof_of_governance_result,
    ):

        if not isinstance(action_id, str) or not action_id:

            return {
                "trust_boundary_status":
                    "REJECTED",

                "checks":
                    {
                        "action_identity":
                            False,
                    },

                "trust_path":
                    None,

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

        path = build_trust_path(
            action_id,
            ticket,
            proof_of_governance_result,
        )

        node_map = {
            node.step: node
            for node in path.nodes
        }

        checks = {
            "action_identity":
                path.action_id == action_id,

            "os3_input_trusted":
                (
                    "OS3_INPUT" in node_map
                    and node_map[
                        "OS3_INPUT"
                    ].trusted
                    is True
                ),

            "os3_trace_trusted":
                (
                    "OS3_TRACE" in node_map
                    and node_map[
                        "OS3_TRACE"
                    ].trusted
                    is True
                ),

            "lyapunov_trusted":
                (
                    "LYAPUNOV" in node_map
                    and node_map[
                        "LYAPUNOV"
                    ].trusted
                    is True
                ),

            "pog_trusted":
                (
                    "POG" in node_map
                    and node_map[
                        "POG"
                    ].trusted
                    is True
                ),

            "path_complete":
                path.is_complete is True,

            "not_broken":
                path.broken_at == "",
        }

        trusted = all(checks.values())

        return {
            "trust_boundary_status":
                "TRUSTED"
                if trusted
                else "REJECTED",

            "checks":
                checks,

            "trust_path":
                path.to_dict(),

            "broken_at":
                path.broken_at,

            "trust_is_authority":
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
