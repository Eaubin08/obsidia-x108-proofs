"""
CG54 KX108 Proof Action Authority Boundary V1.

Action candidates remain governed by X108 admission.
This boundary never emits or authorizes ACT.
"""

from runtime_wiring.x108_admission_stub import (
    evaluate_dry_run,
)


class KX108ProofActionAuthorityBoundary:

    def __init__(self):
        self.decision_authority = "KX108_ONLY"
        self.action_authority = False
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def evaluate(self, packet):

        if packet is None:

            return {
                "action_authority_boundary_status": "REJECTED",
                "checks": {
                    "packet_present": False,
                },
                "decision": None,
                "authorizes_act": False,
                "decision_authority": "KX108_ONLY",
                "action_authority": False,
                "execution_authority": False,
                "memory_write": False,
                "kernel_mutation": False,
                "emits_act": False,
            }

        ticket = evaluate_dry_run(
            packets=[packet],
            envelope=None,
            critical_action_requested=True,
        )

        checks = {
            "packet_present":
                True,

            "kx108_only":
                getattr(
                    packet,
                    "decision_authority",
                    None,
                )
                == "KX108_ONLY",

            "action_never_allowed_directly":
                ticket.decision
                in {
                    "HOLD",
                    "BLOCK",
                },

            "no_direct_act_authority":
                True,

            "no_execution_authority":
                True,
        }

        valid = all(checks.values())

        return {
            "action_authority_boundary_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "checks":
                checks,

            "decision":
                ticket.decision,

            "x108_gate_status":
                ticket.x108_gate_status,

            "reason_codes":
                list(
                    ticket.reason_codes
                ),

            "authorizes_act":
                False,

            "decision_authority":
                "KX108_ONLY",

            "action_authority":
                False,

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

            "action_authority":
                self.action_authority,

            "execution_authority":
                self.execution_authority,

            "memory_write":
                self.memory_write,

            "kernel_mutation":
                self.kernel_mutation,

            "emits_act":
                self.emits_act,
        }
