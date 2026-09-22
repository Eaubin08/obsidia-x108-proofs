"""
CG50 KX108 Proof Alignment Boundary V1.

Structural alignment means conformance with the canonical
non-sovereignty invariants.

Alignment never grants authority.
"""

from runtime_wiring.engine_bridge.bridge_types import (
    EngineBridgeInput,
)


class KX108ProofAlignmentBoundary:

    def __init__(self):
        self.authority = False
        self.decision_authority = "KX108_ONLY"
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def canonical_contract(self):

        baseline = EngineBridgeInput(
            source_pipeline="kx108_proof_alignment_boundary_v1",
            registry_entries_count=1,
            families=["ALIGNMENT"],
            context_only_decision="ALLOW_CONTEXT_ONLY",
            critical_action_decision="HOLD",
        )

        return {
            "decision_authority":
                baseline.decision_authority,

            "readonly":
                baseline.readonly,

            "runtime_active":
                baseline.runtime_active,

            "emits_act":
                baseline.emits_act,

            "memory_write":
                baseline.memory_write,

            "kernel_mutation":
                False,

            "allowed_to_decide":
                False,
        }

    def validate(self, snapshot):

        if not isinstance(snapshot, dict):

            return {
                "alignment_boundary_status":
                    "REJECTED",

                "checks":
                    {
                        "snapshot_object":
                            False,
                    },

                "authority":
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

        canonical = self.canonical_contract()

        checks = {
            "snapshot_object":
                True,

            "kx108_only":
                snapshot.get(
                    "decision_authority"
                )
                == canonical[
                    "decision_authority"
                ],

            "readonly":
                snapshot.get(
                    "readonly",
                    True,
                )
                is True,

            "runtime_inactive":
                snapshot.get(
                    "runtime_active",
                    False,
                )
                is False,

            "no_act":
                snapshot.get(
                    "emits_act",
                    False,
                )
                is False,

            "no_memory_write":
                snapshot.get(
                    "memory_write",
                    False,
                )
                is False,

            "no_kernel_mutation":
                snapshot.get(
                    "kernel_mutation",
                    False,
                )
                is False,

            "cannot_decide":
                snapshot.get(
                    "allowed_to_decide",
                    False,
                )
                is False,
        }

        aligned = all(checks.values())

        return {
            "alignment_boundary_status":
                "ALIGNED"
                if aligned
                else "REJECTED",

            "checks":
                checks,

            "canonical_contract":
                canonical,

            "authority":
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
            "authority":
                self.authority,

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
