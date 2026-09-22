"""
CG34 KX108 Proof Execution Boundary V1
"""

from scripts.kernel.kx108_execution_receipt_v1 import (
    KX108ExecutionReceiptBuilder,
)


class KX108ProofExecutionBoundary:

    def __init__(self):
        self.receipt_builder = KX108ExecutionReceiptBuilder()

        self.authority = False
        self.decision_authority = False
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def validate(self, execution_output):

        is_dict = isinstance(execution_output, dict)

        session = (
            execution_output.get("session")
            if is_dict
            else None
        )

        envelope = (
            execution_output.get("envelope")
            if is_dict
            else None
        )

        boundary_preserved = (
            isinstance(envelope, dict)
            and envelope.get("decision_authority") is False
            and envelope.get("execution_authority") is False
            and envelope.get("memory_write") is False
            and envelope.get("kernel_mutation") is False
            and envelope.get("emits_act") is False
        )

        checks = {
            "execution_object":
                is_dict,

            "session_completed":
                (
                    isinstance(session, dict)
                    and session.get("status") == "COMPLETED"
                ),

            "envelope_present":
                isinstance(envelope, dict),

            "envelope_sealed":
                (
                    isinstance(envelope, dict)
                    and envelope.get("status") == "SEALED"
                ),

            "mission_identity":
                (
                    isinstance(envelope, dict)
                    and bool(envelope.get("mission_id"))
                ),

            "provider_identity":
                (
                    isinstance(envelope, dict)
                    and bool(envelope.get("provider_id"))
                ),

            "runtime_identity":
                (
                    isinstance(envelope, dict)
                    and bool(envelope.get("runtime_id"))
                ),

            "boundary_preserved":
                boundary_preserved,
        }

        valid = all(checks.values())

        receipt = self.receipt_builder.create(
            {
                "execution_status":
                    "EXECUTION_TRACE_VALIDATED"
                    if valid
                    else "EXECUTION_TRACE_REJECTED",
            }
        ).to_dict()

        return {
            "execution_boundary_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "checks":
                checks,

            "runtime_ref":
                (
                    envelope.get("runtime_id")
                    if isinstance(envelope, dict)
                    else None
                ),

            "receipt":
                receipt,

            "authority":
                False,

            "decision_authority":
                False,

            "execution_authority":
                False,

            "kernel_mutation":
                False,

            "emits_act":
                False,
        }

    def status(self):

        return {
            "authority": self.authority,
            "decision_authority": self.decision_authority,
            "execution_authority": self.execution_authority,
            "memory_write": self.memory_write,
            "kernel_mutation": self.kernel_mutation,
            "emits_act": self.emits_act,
        }
