"""
CG86 KX108 Proof Agent Validation V1.

Composes the already-produced CG83 agent-runtime,
CG84 agent-boundary and CG85 agent-interface proofs.

Validation observes proof surfaces only.
It invokes no agent and creates no authority.
"""


class KX108ProofAgentValidation:

    def __init__(self):

        self.validation_authority = False
        self.agent_authority = False
        self.decision_authority = "KX108_ONLY"
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def validate(
        self,
        agent_runtime,
        agent_boundary,
        agent_interface,
    ):

        inputs_valid = all(
            isinstance(result, dict)
            for result in (
                agent_runtime,
                agent_boundary,
                agent_interface,
            )
        )

        if not inputs_valid:

            return {
                "agent_validation_status":
                    "REJECTED",

                "checks": {
                    "inputs_valid":
                        False,
                },

                "agent_invoked_here":
                    False,

                "validation_authority":
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

        agent_ids = (
            agent_runtime.get("agent_id"),
            agent_boundary.get("agent_id"),
            agent_interface.get("agent_id"),
        )

        checks = {
            "inputs_valid":
                True,

            "agent_runtime_validated":
                agent_runtime.get(
                    "agent_runtime_status"
                )
                == "VALIDATED",

            "agent_boundary_validated":
                agent_boundary.get(
                    "agent_boundary_status"
                )
                == "VALIDATED",

            "agent_interface_validated":
                agent_interface.get(
                    "agent_interface_status"
                )
                == "VALIDATED",

            "agent_ids_present":
                all(
                    bool(agent_id)
                    for agent_id in agent_ids
                ),

            "agent_identity_closed":
                len(set(agent_ids)) == 1,

            "interface_peripheral_only":
                agent_interface.get(
                    "interface_mode"
                )
                == "PERIPHERAL_SIGNAL_ONLY",

            "no_context_adapter_invoked":
                agent_interface.get(
                    "context_adapter_invoked_here"
                )
                is False,

            "no_context_packet_created":
                agent_interface.get(
                    "context_packet_created"
                )
                is False,

            "not_submitted_to_x108_here":
                agent_interface.get(
                    "x108_submitted_here"
                )
                is False,

            "runtime_kx108_only":
                agent_runtime.get(
                    "decision_authority"
                )
                == "KX108_ONLY",

            "boundary_kx108_only":
                agent_boundary.get(
                    "decision_authority"
                )
                == "KX108_ONLY",

            "interface_kx108_only":
                agent_interface.get(
                    "decision_authority"
                )
                == "KX108_ONLY",

            "boundary_agent_no_authority":
                agent_boundary.get(
                    "agent_authority"
                )
                is False,

            "interface_agent_no_authority":
                agent_interface.get(
                    "agent_authority"
                )
                is False,

            "agent_cannot_decide":
                agent_boundary.get(
                    "agent_can_decide"
                )
                is False,

            "agent_cannot_authorize":
                agent_boundary.get(
                    "agent_can_authorize"
                )
                is False,

            "agent_cannot_act":
                agent_boundary.get(
                    "agent_can_act"
                )
                is False,

            "runtime_no_execution_authority":
                agent_runtime.get(
                    "execution_authority"
                )
                is False,

            "boundary_no_execution_authority":
                agent_boundary.get(
                    "execution_authority"
                )
                is False,

            "interface_no_execution_authority":
                agent_interface.get(
                    "execution_authority"
                )
                is False,

            "runtime_no_memory_write":
                agent_runtime.get(
                    "memory_write"
                )
                is False,

            "boundary_no_memory_write":
                agent_boundary.get(
                    "memory_write"
                )
                is False,

            "interface_no_memory_write":
                agent_interface.get(
                    "memory_write"
                )
                is False,

            "runtime_no_kernel_mutation":
                agent_runtime.get(
                    "kernel_mutation"
                )
                is False,

            "boundary_no_kernel_mutation":
                agent_boundary.get(
                    "kernel_mutation"
                )
                is False,

            "interface_no_kernel_mutation":
                agent_interface.get(
                    "kernel_mutation"
                )
                is False,

            "runtime_no_act":
                agent_runtime.get(
                    "emits_act"
                )
                is False,

            "boundary_no_act":
                agent_boundary.get(
                    "emits_act"
                )
                is False,

            "interface_no_act":
                agent_interface.get(
                    "emits_act"
                )
                is False,
        }

        valid = all(checks.values())

        return {
            "agent_validation_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "checks":
                checks,

            "agent_id":
                (
                    agent_ids[0]
                    if valid
                    else None
                ),

            "agent_runtime":
                agent_runtime,

            "agent_boundary":
                agent_boundary,

            "agent_interface":
                agent_interface,

            "agent_invoked_here":
                False,

            "validation_authority":
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
