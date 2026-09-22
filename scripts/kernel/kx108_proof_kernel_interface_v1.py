"""
CG68 KX108 Proof Kernel Interface V1.

Validates the dry-run interface into X108.

Peripheral/provider/context material can cross the interface only
as readonly/advisory context. The interface cannot mutate or replace
the kernel decision authority.
"""

import runtime_wiring

from runtime_wiring.x108_admission_stub import (
    evaluate_dry_run,
)


class KX108ProofKernelInterface:

    def __init__(self):
        self.interface_authority = False
        self.decision_authority = "KX108_ONLY"
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def validate(self, packet):

        if packet is None:

            return {
                "kernel_interface_status":
                    "REJECTED",

                "checks": {
                    "packet_present":
                        False,
                },

                "interface_authority":
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

        invariant_valid = True
        invariant_error = None

        try:
            packet.validate_invariants()
        except (AssertionError, ValueError) as exc:
            invariant_valid = False
            invariant_error = str(exc)

        ticket = evaluate_dry_run(
            packets=[packet],
            envelope=None,
            critical_action_requested=False,
        )

        checks = {
            "packet_present":
                True,

            "runtime_wiring_dry_run_only":
                getattr(
                    runtime_wiring,
                    "__status__",
                    None,
                )
                == "DRY_RUN_ONLY",

            "runtime_wiring_kx108_only":
                getattr(
                    runtime_wiring,
                    "__decision_authority__",
                    None,
                )
                == "KX108_ONLY",

            "runtime_wiring_no_act":
                getattr(
                    runtime_wiring,
                    "__emits_act__",
                    None,
                )
                is False,

            "packet_invariants":
                invariant_valid,

            "packet_kx108_only":
                getattr(
                    packet,
                    "decision_authority",
                    None,
                )
                == "KX108_ONLY",

            "packet_readonly":
                getattr(
                    packet,
                    "readonly",
                    None,
                )
                is True,

            "packet_advisory":
                getattr(
                    packet,
                    "advisory_only",
                    None,
                )
                is True,

            "packet_no_act":
                getattr(
                    packet,
                    "emits_act",
                    None,
                )
                is False,

            "packet_no_decision":
                getattr(
                    packet,
                    "emits_decision",
                    None,
                )
                is False,

            "runtime_not_activated":
                getattr(
                    packet,
                    "runtime_allowed_now",
                    None,
                )
                is False,

            "x108_context_only":
                ticket.decision
                == "ALLOW_CONTEXT_ONLY",

            "x108_interface_authority":
                ticket.decision_authority
                == "KX108_ONLY",
        }

        valid = all(checks.values())

        return {
            "kernel_interface_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "checks":
                checks,

            "invariant_error":
                invariant_error,

            "x108_decision":
                ticket.decision,

            "x108_gate_status":
                ticket.x108_gate_status,

            "interface_authority":
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
            "interface_authority":
                self.interface_authority,

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
