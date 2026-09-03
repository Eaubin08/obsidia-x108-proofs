"""
CG87 KX108 Proof Agent Governance V1.

Composes an already-validated agent proof with an already-closed
governance proof.

Governance constrains agent evidence.
It never turns an agent into decision authority.
"""


class KX108ProofAgentGovernance:

    def __init__(self):

        self.governance_authority = False
        self.agent_authority = False
        self.decision_authority = "KX108_ONLY"
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def validate(
        self,
        agent_validation,
        governance_closure,
    ):

        inputs_valid = (
            isinstance(agent_validation, dict)
            and isinstance(governance_closure, dict)
        )

        if not inputs_valid:

            return {
                "agent_governance_status":
                    "REJECTED",

                "checks": {
                    "inputs_valid":
                        False,
                },

                "governance_authority":
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

        checks = {
            "inputs_valid":
                True,

            "agent_validation_validated":
                agent_validation.get(
                    "agent_validation_status"
                )
                == "VALIDATED",

            "agent_identity_present":
                bool(
                    agent_validation.get(
                        "agent_id"
                    )
                ),

            "governance_closed":
                governance_closure.get(
                    "governance_closure_status"
                )
                == "CLOSED",

            "agent_kx108_only":
                agent_validation.get(
                    "decision_authority"
                )
                == "KX108_ONLY",

            "governance_kx108_only":
                governance_closure.get(
                    "decision_authority"
                )
                == "KX108_ONLY",

            "agent_no_authority":
                agent_validation.get(
                    "agent_authority"
                )
                is False,

            "governance_created_no_authority":
                governance_closure.get(
                    "new_authority_created"
                )
                is False,

            "agent_no_execution_authority":
                agent_validation.get(
                    "execution_authority"
                )
                is False,

            "governance_no_execution_authority":
                governance_closure.get(
                    "execution_authority"
                )
                is False,

            "agent_no_memory_write":
                agent_validation.get(
                    "memory_write"
                )
                is False,

            "governance_no_memory_write":
                governance_closure.get(
                    "memory_write"
                )
                is False,

            "agent_no_kernel_mutation":
                agent_validation.get(
                    "kernel_mutation"
                )
                is False,

            "governance_no_kernel_mutation":
                governance_closure.get(
                    "kernel_mutation"
                )
                is False,

            "agent_no_act":
                agent_validation.get(
                    "emits_act"
                )
                is False,

            "governance_no_act":
                governance_closure.get(
                    "emits_act"
                )
                is False,
        }

        valid = all(checks.values())

        return {
            "agent_governance_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "checks":
                checks,

            "agent_id":
                (
                    agent_validation.get(
                        "agent_id"
                    )
                    if valid
                    else None
                ),

            "agent_validation":
                agent_validation,

            "governance_closure":
                governance_closure,

            "agent_can_decide":
                False,

            "governance_authority":
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
