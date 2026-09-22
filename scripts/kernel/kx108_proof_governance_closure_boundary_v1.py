"""
CG61 KX108 Proof Governance Closure Boundary V1.

Closes already-produced governance proof surfaces.

Closure means the upstream governance, integrity and canonical
authority boundaries agree on the same non-sovereign invariants.

It does not create a decision or authority.
"""


class KX108ProofGovernanceClosureBoundary:

    def __init__(self):
        self.decision_authority = "KX108_ONLY"
        self.closure_authority = False
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    @staticmethod
    def _safe_false(result, key):

        return (
            isinstance(result, dict)
            and result.get(key)
            is False
        )

    def close(
        self,
        governance_result,
        integrity_result,
        canonical_authority_result,
    ):

        inputs_valid = all(
            isinstance(result, dict)
            for result in (
                governance_result,
                integrity_result,
                canonical_authority_result,
            )
        )

        if not inputs_valid:

            return {
                "governance_closure_status":
                    "REJECTED",

                "checks":
                    {
                        "upstream_results":
                            False,
                    },

                "closure_authority":
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
            "upstream_results":
                True,

            "governance_validated":
                governance_result.get(
                    "governance_boundary_status"
                )
                == "VALIDATED",

            "integrity_governance_validated":
                integrity_result.get(
                    "integrity_governance_status"
                )
                == "VALIDATED",

            "canonical_authority_validated":
                canonical_authority_result.get(
                    "canonical_authority_status"
                )
                == "VALIDATED",

            "governance_kx108_only":
                governance_result.get(
                    "decision_authority"
                )
                == "KX108_ONLY",

            "integrity_kx108_only":
                integrity_result.get(
                    "decision_authority"
                )
                == "KX108_ONLY",

            "canonical_kx108_only":
                canonical_authority_result.get(
                    "decision_authority"
                )
                == "KX108_ONLY",

            "governance_no_execution_authority":
                self._safe_false(
                    governance_result,
                    "execution_authority",
                ),

            "integrity_no_execution_authority":
                self._safe_false(
                    integrity_result,
                    "execution_authority",
                ),

            "canonical_no_execution_authority":
                self._safe_false(
                    canonical_authority_result,
                    "execution_authority",
                ),

            "governance_no_memory_write":
                self._safe_false(
                    governance_result,
                    "memory_write",
                ),

            "integrity_no_memory_write":
                self._safe_false(
                    integrity_result,
                    "memory_write",
                ),

            "canonical_no_memory_write":
                self._safe_false(
                    canonical_authority_result,
                    "memory_write",
                ),

            "governance_no_kernel_mutation":
                self._safe_false(
                    governance_result,
                    "kernel_mutation",
                ),

            "integrity_no_kernel_mutation":
                self._safe_false(
                    integrity_result,
                    "kernel_mutation",
                ),

            "canonical_no_kernel_mutation":
                self._safe_false(
                    canonical_authority_result,
                    "kernel_mutation",
                ),

            "governance_no_act":
                self._safe_false(
                    governance_result,
                    "emits_act",
                ),

            "integrity_no_act":
                self._safe_false(
                    integrity_result,
                    "emits_act",
                ),

            "canonical_no_act":
                self._safe_false(
                    canonical_authority_result,
                    "emits_act",
                ),

            "canonical_source_is_kx108":
                (
                    canonical_authority_result
                    .get(
                        "decision_envelope",
                        {},
                    )
                    .get(
                        "source_authority"
                    )
                    == "KX108"
                ),

            "canonical_candidate_has_no_decision_payload":
                (
                    canonical_authority_result
                    .get(
                        "authority_result",
                        {},
                    )
                    .get(
                        "decision"
                    )
                    is None
                ),
        }

        closed = all(checks.values())

        return {
            "governance_closure_status":
                "CLOSED"
                if closed
                else "REJECTED",

            "checks":
                checks,

            "closed":
                closed,

            "new_authority_created":
                False,

            "decision_created":
                False,

            "act_created":
                False,

            "closure_authority":
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

            "closure_authority":
                self.closure_authority,

            "execution_authority":
                self.execution_authority,

            "memory_write":
                self.memory_write,

            "kernel_mutation":
                self.kernel_mutation,

            "emits_act":
                self.emits_act,
        }
