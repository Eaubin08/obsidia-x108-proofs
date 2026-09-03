"""
CG93 KX108 Proof Agent Decision Flow V1.

Closes the current agent-to-decision boundary.

No canonical AgentResult -> ContextPacket adapter exists on this proof path,
therefore this layer MUST NOT fabricate direct X108 submission.

Agents do not decide.

Any future canonical adapter may only enter the existing X108 dry-run path,
whose observable decisions remain:
BLOCK, HOLD, ALLOW_CONTEXT_ONLY.
"""

_ALLOWED_X108_DRY_RUN_DECISIONS = (
    "BLOCK",
    "HOLD",
    "ALLOW_CONTEXT_ONLY",
)


class KX108ProofAgentDecisionFlow:

    def __init__(self):
        self.decision_flow_authority = False
        self.agent_authority = False
        self.decision_authority = "KX108_ONLY"
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def validate(
        self,
        orchestration_boundary,
        observed_x108_decision=None,
        canonical_agent_context_adapter=False,
    ):
        boundary_valid = isinstance(
            orchestration_boundary,
            dict,
        )

        decision_observed = (
            observed_x108_decision is not None
        )

        observed_decision_valid = (
            not decision_observed
            or observed_x108_decision
            in _ALLOWED_X108_DRY_RUN_DECISIONS
        )

        checks = {
            "orchestration_boundary_object":
                boundary_valid,

            "orchestration_boundary_validated":
                (
                    boundary_valid
                    and orchestration_boundary.get(
                        "agent_orchestration_boundary_status"
                    ) == "VALIDATED"
                ),

            "orchestration_kx108_only":
                (
                    boundary_valid
                    and orchestration_boundary.get(
                        "decision_authority"
                    ) == "KX108_ONLY"
                ),

            "orchestrator_not_invoked_here":
                (
                    boundary_valid
                    and orchestration_boundary.get(
                        "orchestrator_invoked_here"
                    ) is False
                ),

            "no_orchestration_authority":
                (
                    boundary_valid
                    and orchestration_boundary.get(
                        "orchestration_authority"
                    ) is False
                ),

            "no_agent_authority":
                (
                    boundary_valid
                    and orchestration_boundary.get(
                        "agent_authority"
                    ) is False
                ),

            "observed_decision_valid_if_present":
                observed_decision_valid,

            "no_fake_agent_context_adapter":
                canonical_agent_context_adapter
                is False,

            "no_execution_authority":
                (
                    boundary_valid
                    and orchestration_boundary.get(
                        "execution_authority"
                    ) is False
                ),

            "no_memory_write":
                (
                    boundary_valid
                    and orchestration_boundary.get(
                        "memory_write"
                    ) is False
                ),

            "no_kernel_mutation":
                (
                    boundary_valid
                    and orchestration_boundary.get(
                        "kernel_mutation"
                    ) is False
                ),

            "no_act":
                (
                    boundary_valid
                    and orchestration_boundary.get(
                        "emits_act"
                    ) is False
                ),
        }

        valid = all(checks.values())

        return {
            "agent_decision_flow_status":
                "BOUNDARY_VALIDATED"
                if valid
                else "REJECTED",

            "checks":
                checks,

            "direct_agent_decision_flow":
                False,

            "agent_decision_created":
                False,

            "context_packet_created_here":
                False,

            "x108_submitted_here":
                False,

            "requires_canonical_context_adapter":
                True,

            "canonical_agent_context_adapter_present":
                False,

            "observed_x108_decision":
                (
                    observed_x108_decision
                    if observed_decision_valid
                    else None
                ),

            "allowed_x108_dry_run_decisions":
                _ALLOWED_X108_DRY_RUN_DECISIONS,

            "decision_flow_authority":
                False,

            "agent_authority":
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
