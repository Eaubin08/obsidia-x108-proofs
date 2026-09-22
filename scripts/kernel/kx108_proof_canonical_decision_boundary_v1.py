"""
CG62 KX108 Proof Canonical Decision Boundary V1.

Validates an already-rendered canonical KX108 decision record
through the existing CG53 decision-authority boundary.

No decision is recomputed.
No KX108 invocation occurs here.
"""

from scripts.kernel.kx108_proof_decision_authority_boundary_v1 import (
    KX108ProofDecisionAuthorityBoundary,
)


class KX108ProofCanonicalDecisionBoundary:

    def __init__(self):
        self.decision_boundary = (
            KX108ProofDecisionAuthorityBoundary()
        )

        self.decision_authority = "KX108_ONLY"
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def validate(self, record):

        decision_result = (
            self.decision_boundary.validate(record)
        )

        envelope = (
            record.get("canonical_envelope")
            if isinstance(record, dict)
            else None
        )

        checks = {
            "decision_record_validated":
                decision_result.get(
                    "decision_authority_boundary_status"
                )
                == "VALIDATED",

            "canonical_envelope_present":
                isinstance(envelope, dict),

            "kx108_only":
                decision_result.get(
                    "decision_authority"
                )
                == "KX108_ONLY",

            "gate_bound":
                (
                    isinstance(envelope, dict)
                    and envelope.get("x108_gate")
                    == decision_result.get(
                        "x108_gate"
                    )
                ),

            "decision_id_bound":
                (
                    isinstance(envelope, dict)
                    and envelope.get("decision_id")
                    == decision_result.get(
                        "decision_id"
                    )
                ),

            "trace_id_bound":
                (
                    isinstance(envelope, dict)
                    and envelope.get("trace_id")
                    == decision_result.get(
                        "trace_id"
                    )
                ),

            "no_redecision":
                decision_result.get(
                    "decision_recomputed"
                )
                is False,

            "no_kx108_reinvocation":
                decision_result.get(
                    "kx108_invoked"
                )
                is False,

            "no_execution_authority":
                decision_result.get(
                    "execution_authority"
                )
                is False,

            "no_memory_write":
                decision_result.get(
                    "memory_write"
                )
                is False,

            "no_kernel_mutation":
                decision_result.get(
                    "kernel_mutation"
                )
                is False,

            "no_act":
                decision_result.get(
                    "emits_act"
                )
                is False,
        }

        valid = all(checks.values())

        return {
            "canonical_decision_boundary_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "checks":
                checks,

            "decision_boundary":
                decision_result,

            "canonical_envelope":
                envelope,

            "decision_recomputed":
                False,

            "kx108_invoked":
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
