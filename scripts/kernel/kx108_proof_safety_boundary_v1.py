"""
CG49 KX108 Proof Safety Boundary V1.

Composes existing EngineBridge fail-closed invariants with
the X108 dry-run admission boundary.

BLOCK > HOLD > ALLOW_CONTEXT_ONLY.
Never ACT.
"""

from runtime_wiring.engine_bridge.bridge_types import (
    EngineBridgeInput,
)

from runtime_wiring.x108_admission_stub import (
    evaluate_dry_run,
)


class KX108ProofSafetyBoundary:

    def __init__(self):
        self.decision_authority = "KX108_ONLY"
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def validate_bridge(
        self,
        overrides=None,
    ):

        values = {
            "source_pipeline":
                "kx108_proof_safety_boundary_v1",

            "registry_entries_count":
                1,

            "families":
                ["COGNITIVE"],

            "context_only_decision":
                "ALLOW_CONTEXT_ONLY",

            "critical_action_decision":
                "HOLD",
        }

        if isinstance(overrides, dict):
            values.update(overrides)

        try:

            bridge_input = EngineBridgeInput(
                **values
            )

        except ValueError as exc:

            return {
                "safety_bridge_status":
                    "REJECTED",

                "fail_closed":
                    True,

                "reason":
                    str(exc),

                "bridge_input":
                    None,

                "authorizes_act":
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

        return {
            "safety_bridge_status":
                "VALIDATED",

            "fail_closed":
                False,

            "reason":
                None,

            "bridge_input":
                {
                    "source_pipeline":
                        bridge_input.source_pipeline,

                    "context_only_decision":
                        bridge_input.context_only_decision,

                    "critical_action_decision":
                        bridge_input.critical_action_decision,

                    "readonly":
                        bridge_input.readonly,

                    "runtime_active":
                        bridge_input.runtime_active,

                    "emits_act":
                        bridge_input.emits_act,

                    "memory_write":
                        bridge_input.memory_write,

                    "decision_authority":
                        bridge_input.decision_authority,
                },

            "authorizes_act":
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

    def evaluate_packet(
        self,
        packet,
        *,
        critical_action_requested=False,
    ):

        ticket = evaluate_dry_run(
            packets=[packet],
            envelope=None,
            critical_action_requested=(
                critical_action_requested
            ),
        )

        allowed_outcomes = {
            "BLOCK",
            "HOLD",
            "ALLOW_CONTEXT_ONLY",
        }

        valid = (
            ticket.decision
            in allowed_outcomes
        )

        return {
            "safety_boundary_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "decision":
                ticket.decision,

            "x108_gate_status":
                ticket.x108_gate_status,

            "reason_codes":
                list(ticket.reason_codes),

            "authorizes_act":
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
