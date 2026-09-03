"""
CG91 KX108 Proof Agent Composition V1.

Composes multiple already-validated CG90 agent proof-runtime surfaces.

Composition preserves agent identities and proof evidence.
It never merges or elevates authority.
"""


class KX108ProofAgentComposition:

    def __init__(self):
        self.composition_authority = False
        self.agent_authority = False
        self.decision_authority = "KX108_ONLY"
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def compose(self, agent_runtimes):

        if not isinstance(agent_runtimes, list) or not agent_runtimes:
            return self._rejected(
                {"nonempty_list": False}
            )

        objects_valid = all(
            isinstance(result, dict)
            for result in agent_runtimes
        )

        if not objects_valid:
            return self._rejected(
                {
                    "nonempty_list": True,
                    "objects_valid": False,
                }
            )

        agent_ids = [
            result.get("agent_id")
            for result in agent_runtimes
        ]

        checks = {
            "nonempty_list":
                True,

            "objects_valid":
                True,

            "all_complete_runtime_validated":
                all(
                    result.get(
                        "agent_complete_runtime_status"
                    ) == "VALIDATED"
                    for result in agent_runtimes
                ),

            "all_agent_ids_present":
                all(bool(agent_id) for agent_id in agent_ids),

            "agent_identities_unique":
                len(agent_ids) == len(set(agent_ids)),

            "all_kx108_only":
                all(
                    result.get("decision_authority")
                    == "KX108_ONLY"
                    for result in agent_runtimes
                ),

            "all_no_execution_authority":
                all(
                    result.get("execution_authority")
                    is False
                    for result in agent_runtimes
                ),

            "all_no_memory_write":
                all(
                    result.get("memory_write")
                    is False
                    for result in agent_runtimes
                ),

            "all_no_kernel_mutation":
                all(
                    result.get("kernel_mutation")
                    is False
                    for result in agent_runtimes
                ),

            "all_no_act":
                all(
                    result.get("emits_act")
                    is False
                    for result in agent_runtimes
                ),

            "all_not_global_runtime":
                all(
                    result.get(
                        "global_runtime_validated"
                    ) is False
                    for result in agent_runtimes
                ),
        }

        valid = all(checks.values())

        if not valid:
            return self._rejected(checks)

        return {
            "agent_composition_status":
                "COMPOSED",

            "checks":
                checks,

            "agent_ids":
                tuple(agent_ids),

            "agent_count":
                len(agent_ids),

            "authority_merged":
                False,

            "authority_elevated":
                False,

            "composition_authority":
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

    @staticmethod
    def _rejected(checks):
        return {
            "agent_composition_status":
                "REJECTED",

            "checks": checks,

            "agent_ids":
                (),

            "agent_count":
                0,

            "authority_merged":
                False,

            "authority_elevated":
                False,

            "composition_authority":
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
