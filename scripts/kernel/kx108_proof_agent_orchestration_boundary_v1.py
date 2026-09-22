"""
CG92 KX108 Proof Agent Orchestration Boundary V1.

Closes the agent composition surface against orchestration escalation.

The repository contains a workflow_governance_readonly orchestration branch,
while other orchestration surfaces are not treated here as canonical agent
runtime authority.

This layer invokes no orchestrator.
It permits only a readonly orchestration boundary declaration.
"""


class KX108ProofAgentOrchestrationBoundary:

    def __init__(self):
        self.orchestration_authority = False
        self.agent_authority = False
        self.decision_authority = "KX108_ONLY"
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def validate(
        self,
        agent_composition,
        readonly_orchestration=True,
        runtime_orchestrator_wired=False,
    ):
        composition_valid = isinstance(
            agent_composition,
            dict,
        )

        checks = {
            "composition_object":
                composition_valid,

            "composition_validated":
                (
                    composition_valid
                    and agent_composition.get(
                        "agent_composition_status"
                    ) == "COMPOSED"
                ),

            "agent_identities_present":
                (
                    composition_valid
                    and bool(
                        agent_composition.get(
                            "agent_ids"
                        )
                    )
                ),

            "composition_kx108_only":
                (
                    composition_valid
                    and agent_composition.get(
                        "decision_authority"
                    ) == "KX108_ONLY"
                ),

            "composition_no_authority_merge":
                (
                    composition_valid
                    and agent_composition.get(
                        "authority_merged"
                    ) is False
                ),

            "composition_no_authority_elevation":
                (
                    composition_valid
                    and agent_composition.get(
                        "authority_elevated"
                    ) is False
                ),

            "readonly_orchestration_only":
                readonly_orchestration is True,

            "runtime_orchestrator_not_wired_here":
                runtime_orchestrator_wired is False,

            "composition_no_execution_authority":
                (
                    composition_valid
                    and agent_composition.get(
                        "execution_authority"
                    ) is False
                ),

            "composition_no_memory_write":
                (
                    composition_valid
                    and agent_composition.get(
                        "memory_write"
                    ) is False
                ),

            "composition_no_kernel_mutation":
                (
                    composition_valid
                    and agent_composition.get(
                        "kernel_mutation"
                    ) is False
                ),

            "composition_no_act":
                (
                    composition_valid
                    and agent_composition.get(
                        "emits_act"
                    ) is False
                ),
        }

        valid = all(checks.values())

        return {
            "agent_orchestration_boundary_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "checks":
                checks,

            "agent_ids":
                (
                    agent_composition.get(
                        "agent_ids"
                    )
                    if valid
                    else ()
                ),

            "orchestration_mode":
                "READONLY_BOUNDARY_ONLY",

            "readonly_orchestration":
                True,

            "orchestrator_invoked_here":
                False,

            "runtime_orchestrator_wired":
                False,

            "orchestration_authority":
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
