"""
CG33 KX108 Proof Canonical Receipt Flow V1
"""

from scripts.providers.canonical_runtime_receipt_flow_v1 import (
    CanonicalRuntimeReceiptFlow,
)

from scripts.kernel.kx108_proof_runtime_validation_v1 import (
    KX108ProofRuntimeValidator,
)

from scripts.kernel.kx108_proof_receipt_validation_v1 import (
    KX108ProofReceiptValidator,
)


class KX108ProofCanonicalReceiptFlow:

    def __init__(self):
        self.flow = CanonicalRuntimeReceiptFlow()
        self.runtime_validator = KX108ProofRuntimeValidator()
        self.receipt_validator = KX108ProofReceiptValidator()

        self.authority = False
        self.decision_authority = False
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def register_provider(
        self,
        provider_id,
        handler,
    ):

        self.flow.register_provider(
            provider_id,
            handler,
        )

    def run(
        self,
        mission_id,
        provider_id,
        capability,
        payload,
    ):

        canonical_output = self.flow.run(
            mission_id=mission_id,
            provider_id=provider_id,
            capability=capability,
            payload=payload,
        )

        execution = canonical_output["execution"]

        envelope = execution["execution"]["envelope"]

        runtime_validation = (
            self.runtime_validator.validate(
                execution
            )
        )

        receipt_validation = (
            self.receipt_validator.validate(
                canonical_output["receipt"],
                expected_result_ref=envelope["runtime_id"],
                expected_invocation_id=mission_id,
            )
        )

        valid = (
            runtime_validation["runtime_validation_status"]
            == "VALIDATED"
            and
            receipt_validation["receipt_validation_status"]
            == "VALIDATED"
        )

        return {
            "canonical_receipt_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "runtime_validation":
                runtime_validation,

            "receipt_validation":
                receipt_validation,

            "execution":
                canonical_output,

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
