"""
CG29 KX108 Proof State Validation V1
"""

from scripts.kernel.kx108_recursive_state_coordination_boundary_v1 import (
    KX108RecursiveStateCoordinationBoundary,
)


class KX108ProofStateValidator:

    def __init__(self):
        self.coordinator = (
            KX108RecursiveStateCoordinationBoundary()
        )

        self.authority = False
        self.decision_authority = False
        self.memory_write = False
        self.kernel_mutation = False

    def validate(self, meta_states):

        is_list = isinstance(meta_states, list)

        non_empty = (
            is_list
            and len(meta_states) > 0
        )

        well_formed = (
            non_empty
            and all(
                isinstance(state, dict)
                and state.get("meta_domain") is not None
                and state.get("state") is not None
                for state in meta_states
            )
        )

        all_validated = (
            well_formed
            and all(
                state.get("state") == "validated"
                for state in meta_states
            )
        )

        checks = {
            "state_list":
                is_list,

            "non_empty":
                non_empty,

            "well_formed":
                well_formed,

            "all_validated":
                all_validated,
        }

        valid = all(checks.values())

        coordination = (
            self.coordinator.coordinate(meta_states)
            if valid
            else None
        )

        return {
            "state_validation_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "checks":
                checks,

            "state_count":
                len(meta_states)
                if is_list
                else 0,

            "coordination":
                coordination,

            "authority":
                False,

            "decision_authority":
                False,

            "kernel_mutation":
                False,
        }

    def status(self):

        return {
            "authority": self.authority,
            "decision_authority": self.decision_authority,
            "memory_write": self.memory_write,
            "kernel_mutation": self.kernel_mutation,
        }
