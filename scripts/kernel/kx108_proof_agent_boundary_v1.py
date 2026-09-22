"""
CG84 KX108 Proof Agent Boundary V1.

Closes a validated CG83 agent runtime result against the
actual NonSovereignAgentSpec contract.

No agent may authorize, emit ACT, mutate the kernel or write memory.
"""

from periphery.agent_contracts import (
    NonSovereignAgentSpec,
)


class KX108ProofAgentBoundary:

    def __init__(self):

        self.agent_authority = False
        self.decision_authority = "KX108_ONLY"
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def validate(
        self,
        agent_runtime,
        spec,
    ):

        runtime_valid = isinstance(
            agent_runtime,
            dict,
        )

        spec_valid = isinstance(
            spec,
            NonSovereignAgentSpec,
        )

        spec_safe = False

        if spec_valid:

            try:
                spec.assert_safe()
                spec_safe = True

            except AssertionError:
                spec_safe = False

        checks = {
            "agent_runtime_object":
                runtime_valid,

            "agent_runtime_validated":
                (
                    runtime_valid
                    and agent_runtime.get(
                        "agent_runtime_status"
                    )
                    == "VALIDATED"
                ),

            "spec_object":
                spec_valid,

            "spec_safe":
                spec_safe,

            "agent_identity_bound":
                (
                    runtime_valid
                    and spec_valid
                    and agent_runtime.get(
                        "agent_id"
                    )
                    == spec.agent_id
                ),

            "spec_cannot_emit_act":
                (
                    spec_valid
                    and spec.can_emit_act
                    is False
                ),

            "spec_cannot_authorize":
                (
                    spec_valid
                    and spec.can_authorize
                    is False
                ),

            "spec_cannot_mutate_kernel":
                (
                    spec_valid
                    and spec.can_mutate_kernel
                    is False
                ),

            "spec_cannot_write_memory":
                (
                    spec_valid
                    and spec.can_write_memory
                    is False
                ),

            "runtime_kx108_only":
                (
                    runtime_valid
                    and agent_runtime.get(
                        "decision_authority"
                    )
                    == "KX108_ONLY"
                ),

            "runtime_no_execution_authority":
                (
                    runtime_valid
                    and agent_runtime.get(
                        "execution_authority"
                    )
                    is False
                ),

            "runtime_no_memory_write":
                (
                    runtime_valid
                    and agent_runtime.get(
                        "memory_write"
                    )
                    is False
                ),

            "runtime_no_kernel_mutation":
                (
                    runtime_valid
                    and agent_runtime.get(
                        "kernel_mutation"
                    )
                    is False
                ),

            "runtime_no_act":
                (
                    runtime_valid
                    and agent_runtime.get(
                        "emits_act"
                    )
                    is False
                ),
        }

        valid = all(checks.values())

        return {
            "agent_boundary_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "checks":
                checks,

            "agent_id":
                (
                    spec.agent_id
                    if valid
                    else None
                ),

            "agent_layer":
                (
                    str(spec.layer)
                    if valid
                    else None
                ),

            "agent_authority":
                False,

            "agent_can_decide":
                False,

            "agent_can_authorize":
                False,

            "agent_can_execute_by_authority":
                False,

            "agent_can_act":
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
