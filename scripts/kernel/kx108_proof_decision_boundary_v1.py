"""
CG35 KX108 Proof Decision Boundary V1
"""

from scripts.kernel.canonical_decision_envelope_v1 import (
    CanonicalDecisionEnvelopeBuilder,
)

from scripts.kernel.kx108_decision_receipt_v1 import (
    KX108DecisionReceiptBuilder,
)


class KX108ProofDecisionBoundary:

    def __init__(self):
        self.envelope_builder = CanonicalDecisionEnvelopeBuilder()
        self.receipt_builder = KX108DecisionReceiptBuilder()

        self.authority = False
        self.decision_authority = False
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def validate(self, guard_result):

        is_dict = isinstance(guard_result, dict)

        envelope = (
            self.envelope_builder.build(guard_result)
            if is_dict
            else None
        )

        checks = {
            "guard_object":
                is_dict,

            "guard_passed":
                (
                    is_dict
                    and guard_result.get("status")
                    == "GUARD_PASSED"
                ),

            "provider_identity":
                (
                    envelope is not None
                    and envelope.source_provider != "unknown"
                ),

            "runtime_identity":
                (
                    envelope is not None
                    and envelope.runtime_ref != "unknown"
                ),

            "candidate_only":
                (
                    envelope is not None
                    and envelope.decision_status
                    == "CANDIDATE_ONLY"
                ),

            "no_decision_authority":
                (
                    self.envelope_builder
                    .status()["decision_authority"]
                    is False
                ),
        }

        valid = all(checks.values())

        receipt = (
            self.receipt_builder.create(
                {
                    "authority_status":
                        "CANDIDATE_ONLY",

                    "decision_status":
                        envelope.decision_status,
                }
            ).to_dict()
            if envelope is not None
            else None
        )

        return {
            "decision_boundary_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "checks":
                checks,

            "envelope":
                (
                    envelope.to_dict()
                    if envelope is not None
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
