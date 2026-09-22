"""
CG97 KX108 Proof End-To-End Validation V1.

Validates the current proof-level chain through:
- bounded agent decision flow;
- canonical-envelope separation;
- receipt closure;
- CG96 proof-runtime surface aggregation.

This is PROOF E2E validation only.

Post-CG100 the canonical AgentResult -> ContextPacket runtime link EXISTS
and is wired into the X108 dry-run admission path. That link alone does not
validate the runtime: every observable decision on this perimeter remains
BLOCK / HOLD / ALLOW_CONTEXT_ONLY and no real X108-gated execution path is
activated, therefore runtime_end_to_end_validated MUST remain False.

The reported adapter presence must match the detected repository fact --
claiming it absent when present, or present when absent, is rejected.

This layer MUST NOT claim:
- real global runtime validation;
- production readiness;
- release readiness;
- deployment readiness;
- final freeze.
"""


from scripts.kernel.kx108_runtime_link_facts_v1 import (
    MISSING_RUNTIME_LINK_REAL_EXECUTION,
    canonical_agent_context_adapter_present,
    missing_runtime_links,
)


class KX108ProofEndToEndValidation:

    # Kept for compatibility: the single blocker still standing in the way
    # of a real runtime end-to-end claim.
    MISSING_RUNTIME_LINK = MISSING_RUNTIME_LINK_REAL_EXECUTION

    def __init__(self):
        self.validation_authority = False
        self.decision_authority = "KX108_ONLY"
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def validate(
        self,
        global_runtime,
        agent_decision_flow,
        agent_canonical_envelope,
        agent_receipt_closure,
    ):
        surfaces = (
            global_runtime,
            agent_decision_flow,
            agent_canonical_envelope,
            agent_receipt_closure,
        )

        inputs_valid = all(
            isinstance(surface, dict)
            for surface in surfaces
        )

        if not inputs_valid:
            return self._rejected(
                {"inputs_valid": False}
            )

        checks = {
            "inputs_valid":
                True,

            "proof_runtime_surfaces_validated":
                (
                    global_runtime.get(
                        "kx108_global_runtime_status"
                    )
                    == "PROOF_RUNTIME_SURFACES_VALIDATED"
                    and global_runtime.get(
                        "proof_runtime_surfaces_validated"
                    )
                    is True
                ),

            "agent_decision_boundary_validated":
                agent_decision_flow.get(
                    "agent_decision_flow_status"
                )
                == "BOUNDARY_VALIDATED",

            "agent_envelope_validated":
                agent_canonical_envelope.get(
                    "agent_canonical_envelope_status"
                )
                == "VALIDATED",

            "agent_receipt_closure_validated":
                agent_receipt_closure.get(
                    "agent_receipt_closure_status"
                )
                == "VALIDATED",

            "agent_did_not_decide":
                agent_decision_flow.get(
                    "agent_decision_created"
                )
                is False,

            "agent_did_not_submit_x108_here":
                agent_decision_flow.get(
                    "x108_submitted_here"
                )
                is False,

            "canonical_context_adapter_still_required":
                agent_decision_flow.get(
                    "requires_canonical_context_adapter"
                )
                is True,

            "canonical_adapter_presence_is_factual":
                agent_decision_flow.get(
                    "canonical_agent_context_adapter_present"
                )
                is canonical_agent_context_adapter_present(),

            "envelope_not_created_by_agent":
                agent_canonical_envelope.get(
                    "agent_envelope_created_here"
                )
                is False,

            "agent_receipt_not_generated_here":
                agent_receipt_closure.get(
                    "agent_receipt_generated_here"
                )
                is False,

            "runtime_not_globally_validated":
                global_runtime.get(
                    "runtime_globally_validated"
                )
                is False,

            "runtime_not_end_to_end_validated":
                global_runtime.get(
                    "runtime_end_to_end_validated"
                )
                is False,

            "not_production_ready":
                global_runtime.get(
                    "production_ready"
                )
                is False,

            "not_release_ready":
                global_runtime.get(
                    "release_ready"
                )
                is False,

            "not_deployment_ready":
                global_runtime.get(
                    "deployment_ready"
                )
                is False,

            "not_final_freeze":
                global_runtime.get(
                    "final_freeze"
                )
                is False,

            "all_kx108_only":
                all(
                    surface.get(
                        "decision_authority"
                    )
                    == "KX108_ONLY"
                    for surface in surfaces
                ),

            "all_no_execution_authority":
                all(
                    surface.get(
                        "execution_authority"
                    )
                    is False
                    for surface in surfaces
                ),

            "all_no_memory_write":
                all(
                    surface.get(
                        "memory_write"
                    )
                    is False
                    for surface in surfaces
                ),

            "all_no_kernel_mutation":
                all(
                    surface.get(
                        "kernel_mutation"
                    )
                    is False
                    for surface in surfaces
                ),

            "all_no_act":
                all(
                    surface.get(
                        "emits_act"
                    )
                    is False
                    for surface in surfaces
                ),
        }

        valid = all(checks.values())

        if not valid:
            return self._rejected(checks)

        return {
            "kx108_end_to_end_validation_status":
                "PROOF_E2E_VALIDATED",

            "checks":
                checks,

            "proof_end_to_end_validated":
                True,

            "runtime_end_to_end_validated":
                False,

            "runtime_globally_validated":
                False,

            "missing_runtime_link":
                self.MISSING_RUNTIME_LINK,

            "missing_runtime_links":
                missing_runtime_links(),

            "canonical_agent_context_adapter_present":
                canonical_agent_context_adapter_present(),

            "production_ready":
                False,

            "release_ready":
                False,

            "deployment_ready":
                False,

            "final_freeze":
                False,

            "new_authority_created":
                False,

            "validation_authority":
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

    def _rejected(self, checks):
        return {
            "kx108_end_to_end_validation_status":
                "REJECTED",

            "checks":
                checks,

            "proof_end_to_end_validated":
                False,

            "runtime_end_to_end_validated":
                False,

            "runtime_globally_validated":
                False,

            "missing_runtime_link":
                self.MISSING_RUNTIME_LINK,

            "missing_runtime_links":
                missing_runtime_links(),

            "canonical_agent_context_adapter_present":
                canonical_agent_context_adapter_present(),

            "production_ready":
                False,

            "release_ready":
                False,

            "deployment_ready":
                False,

            "final_freeze":
                False,

            "new_authority_created":
                False,

            "validation_authority":
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
