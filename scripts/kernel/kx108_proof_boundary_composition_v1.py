"""
CG64 KX108 Proof Boundary Composition V1.

Composes already-evaluated proof boundaries.

Composition preserves boundaries; it does not merge or elevate
their authority.
"""


class KX108ProofBoundaryComposition:

    REQUIRED = {
        "context":
            (
                "context_authority_boundary_status",
                "VALIDATED",
            ),

        "semantic":
            (
                "semantic_authority_boundary_status",
                "VALIDATED",
            ),

        "cognition":
            (
                "cognition_authority_boundary_status",
                "VALIDATED",
            ),

        "governance_closure":
            (
                "governance_closure_status",
                "CLOSED",
            ),

        "canonical_decision":
            (
                "canonical_decision_boundary_status",
                "VALIDATED",
            ),

        "final_boundary":
            (
                "final_boundary_status",
                "PROOF_BOUNDARY_CLOSED",
            ),
    }

    def __init__(self):
        self.decision_authority = "KX108_ONLY"
        self.composition_authority = False
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def compose(self, boundaries):

        if not isinstance(boundaries, dict):

            return {
                "boundary_composition_status":
                    "REJECTED",

                "checks": {
                    "boundary_map":
                        False,
                },

                "composition_authority":
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
            "boundary_map":
                True,
        }

        for name, (
            status_key,
            expected_status,
        ) in self.REQUIRED.items():

            result = boundaries.get(name)

            checks[
                f"{name}_present"
            ] = isinstance(result, dict)

            if not isinstance(result, dict):
                continue

            checks[
                f"{name}_status"
            ] = (
                result.get(status_key)
                == expected_status
            )

            checks[
                f"{name}_kx108_only"
            ] = (
                result.get(
                    "decision_authority"
                )
                == "KX108_ONLY"
            )

            checks[
                f"{name}_no_execution_authority"
            ] = (
                result.get(
                    "execution_authority"
                )
                is False
            )

            checks[
                f"{name}_no_memory_write"
            ] = (
                result.get(
                    "memory_write"
                )
                is False
            )

            checks[
                f"{name}_no_kernel_mutation"
            ] = (
                result.get(
                    "kernel_mutation"
                )
                is False
            )

            checks[
                f"{name}_no_act"
            ] = (
                result.get(
                    "emits_act"
                )
                is False
            )

        composed = all(checks.values())

        return {
            "boundary_composition_status":
                "COMPOSED"
                if composed
                else "REJECTED",

            "checks":
                checks,

            "boundary_count":
                len(self.REQUIRED),

            "required_boundaries":
                list(self.REQUIRED.keys()),

            "authority_merged":
                False,

            "authority_elevated":
                False,

            "composition_authority":
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

            "composition_authority":
                self.composition_authority,

            "execution_authority":
                self.execution_authority,

            "memory_write":
                self.memory_write,

            "kernel_mutation":
                self.kernel_mutation,

            "emits_act":
                self.emits_act,
        }
