"""
CG40 KX108 Proof Knowledge Boundary V1
"""

from periphery.agents.obsidure_math_memory_provider import (
    MISSING_CONTEXT,
    ObsidureMathMemoryProvider,
)


class KX108ProofKnowledgeBoundary:

    def __init__(self, provider=None):

        self.provider = (
            provider
            if provider is not None
            else ObsidureMathMemoryProvider()
        )

        self.decision_authority = "KX108_ONLY"
        self.allowed_to_decide = False
        self.allowed_to_act = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def inspect(self, knowledge_id):

        item = self.provider.get_pepite(
            knowledge_id
        )

        missing = (
            item == MISSING_CONTEXT
        )

        boundary = (
            self.provider.explain_boundary()
        )

        checks = {
            "context_known":
                missing is False,

            "readonly":
                boundary.get("readonly")
                is True,

            "kx108_only":
                boundary.get("decision_authority")
                == "KX108_ONLY",

            "no_act":
                boundary.get("emits_act")
                is False,

            "no_kernel_mutation":
                boundary.get("kernel_mutation")
                is False,

            "no_memory_write":
                boundary.get("memory_write")
                is False,

            "no_graphiti_write":
                boundary.get("graphiti_write")
                is False,

            "no_neo4j_write":
                boundary.get("neo4j_write")
                is False,
        }

        boundary_safe = all(
            value
            for key, value in checks.items()
            if key != "context_known"
        )

        available = (
            checks["context_known"]
            and boundary_safe
        )

        proof_eligible = (
            available
            and self.provider.can_use_for_proof(
                knowledge_id
            )
        )

        return {
            "knowledge_boundary_status":
                (
                    "AVAILABLE"
                    if available
                    else (
                        "MISSING_CONTEXT"
                        if missing
                        else "REJECTED"
                    )
                ),

            "checks":
                checks,

            "knowledge":
                (
                    item
                    if not missing
                    else None
                ),

            "proof_eligible":
                proof_eligible,

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
