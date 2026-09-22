"""
CG71 KX108 Proof Provider Runtime V1.

Validates an already-produced canonical provider runtime output.

This layer observes execution envelope + runtime receipt.
It never invokes a provider itself.
"""

from scripts.kernel.kx108_proof_receipt_chain_v1 import (
    KX108ProofReceiptChain,
)


class KX108ProofProviderRuntime:

    def __init__(self):
        self.receipt_chain = (
            KX108ProofReceiptChain()
        )

        self.provider_runtime_authority = False
        self.decision_authority = "KX108_ONLY"
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def validate(self, canonical_output):

        if not isinstance(canonical_output, dict):

            return {
                "provider_runtime_status":
                    "REJECTED",

                "checks": {
                    "canonical_output":
                        False,
                },

                "provider_runtime_authority":
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

        flow = canonical_output.get(
            "execution"
        )

        receipt = canonical_output.get(
            "receipt"
        )

        execution_result = (
            flow.get("execution")
            if isinstance(flow, dict)
            else None
        )

        envelope = (
            execution_result.get("envelope")
            if isinstance(
                execution_result,
                dict,
            )
            else None
        )

        session = (
            execution_result.get("session")
            if isinstance(
                execution_result,
                dict,
            )
            else None
        )

        runtime_id = (
            envelope.get("runtime_id")
            if isinstance(envelope, dict)
            else None
        )

        invocation_id = (
            receipt.get("invocation_id")
            if isinstance(receipt, dict)
            else None
        )

        receipt_result = (
            self.receipt_chain.validate(
                receipt,
                expected_result_ref=runtime_id,
                expected_invocation_id=invocation_id,
            )
            if isinstance(receipt, dict)
            else {
                "receipt_chain_status":
                    "REJECTED"
            }
        )

        checks = {
            "canonical_output":
                True,

            "execution_flow_present":
                isinstance(flow, dict),

            "execution_flow_completed":
                (
                    isinstance(flow, dict)
                    and flow.get("flow_status")
                    == "COMPLETED"
                ),

            "execution_result_present":
                isinstance(
                    execution_result,
                    dict,
                ),

            "session_completed":
                (
                    isinstance(session, dict)
                    and session.get("status")
                    == "COMPLETED"
                ),

            "envelope_present":
                isinstance(envelope, dict),

            "envelope_sealed":
                (
                    isinstance(envelope, dict)
                    and envelope.get("status")
                    == "SEALED"
                ),

            "provider_identity":
                (
                    isinstance(envelope, dict)
                    and isinstance(receipt, dict)
                    and bool(
                        envelope.get("provider_id")
                    )
                    and envelope.get("provider_id")
                    == receipt.get("provider_id")
                ),

            "runtime_identity":
                bool(runtime_id),

            "receipt_chain_validated":
                receipt_result.get(
                    "receipt_chain_status"
                )
                == "VALIDATED",

            "envelope_no_decision_authority":
                (
                    isinstance(envelope, dict)
                    and envelope.get(
                        "decision_authority"
                    )
                    is False
                ),

            "envelope_no_execution_authority":
                (
                    isinstance(envelope, dict)
                    and envelope.get(
                        "execution_authority"
                    )
                    is False
                ),

            "envelope_no_memory_write":
                (
                    isinstance(envelope, dict)
                    and envelope.get(
                        "memory_write"
                    )
                    is False
                ),

            "envelope_no_kernel_mutation":
                (
                    isinstance(envelope, dict)
                    and envelope.get(
                        "kernel_mutation"
                    )
                    is False
                ),

            "envelope_no_act":
                (
                    isinstance(envelope, dict)
                    and envelope.get(
                        "emits_act"
                    )
                    is False
                ),
        }

        valid = all(checks.values())

        return {
            "provider_runtime_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "checks":
                checks,

            "provider_id":
                (
                    envelope.get("provider_id")
                    if isinstance(
                        envelope,
                        dict,
                    )
                    else None
                ),

            "runtime_id":
                runtime_id,

            "receipt_chain":
                receipt_result,

            "provider_invoked_here":
                False,

            "provider_runtime_authority":
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
            "provider_runtime_authority":
                self.provider_runtime_authority,

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
