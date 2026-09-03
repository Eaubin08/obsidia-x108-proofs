"""
CG82 KX108 Proof Mission Boundary V1.

Closes an already-validated CG81 mission runtime result.

Mission evidence remains NON_SOVEREIGN.
It cannot become KX108, runtime or execution authority.
"""


class KX108ProofMissionBoundary:

    def __init__(self):

        self.mission_boundary_authority = False
        self.runtime_authority = False
        self.decision_authority = "KX108_ONLY"
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def validate(self, mission_runtime):

        runtime_valid = isinstance(
            mission_runtime,
            dict,
        )

        evidence = (
            mission_runtime.get(
                "mission_authority_evidence"
            )
            if runtime_valid
            else None
        )

        evidence_valid = isinstance(
            evidence,
            dict,
        )

        checks = {
            "mission_runtime_object":
                runtime_valid,

            "mission_runtime_validated":
                (
                    runtime_valid
                    and mission_runtime.get(
                        "mission_runtime_status"
                    )
                    == "VALIDATED"
                ),

            "mission_id_present":
                (
                    runtime_valid
                    and bool(
                        mission_runtime.get(
                            "mission_id"
                        )
                    )
                ),

            "authority_evidence_present":
                evidence_valid,

            "authority_non_sovereign":
                (
                    evidence_valid
                    and evidence.get(
                        "authority"
                    )
                    == "NON_SOVEREIGN"
                ),

            "not_kx_authority":
                (
                    evidence_valid
                    and evidence.get(
                        "is_kx_authority"
                    )
                    is False
                ),

            "plan_not_execution_authority":
                (
                    evidence_valid
                    and evidence.get(
                        "plan_is_execution_authority"
                    )
                    is False
                ),

            "runtime_authority_inactive":
                (
                    runtime_valid
                    and mission_runtime.get(
                        "runtime_authority_active"
                    )
                    is False
                ),

            "mission_runtime_no_authority":
                (
                    runtime_valid
                    and mission_runtime.get(
                        "mission_authority"
                    )
                    is False
                ),

            "runtime_no_authority":
                (
                    runtime_valid
                    and mission_runtime.get(
                        "runtime_authority"
                    )
                    is False
                ),

            "kx108_only":
                (
                    runtime_valid
                    and mission_runtime.get(
                        "decision_authority"
                    )
                    == "KX108_ONLY"
                ),

            "no_execution_authority":
                (
                    runtime_valid
                    and mission_runtime.get(
                        "execution_authority"
                    )
                    is False
                ),

            "no_memory_write":
                (
                    runtime_valid
                    and mission_runtime.get(
                        "memory_write"
                    )
                    is False
                ),

            "no_kernel_mutation":
                (
                    runtime_valid
                    and mission_runtime.get(
                        "kernel_mutation"
                    )
                    is False
                ),

            "no_act":
                (
                    runtime_valid
                    and mission_runtime.get(
                        "emits_act"
                    )
                    is False
                ),
        }

        valid = all(checks.values())

        return {
            "mission_boundary_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "checks":
                checks,

            "mission_id":
                (
                    mission_runtime.get(
                        "mission_id"
                    )
                    if valid
                    else None
                ),

            "mission_boundary_authority":
                False,

            "runtime_authority":
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
