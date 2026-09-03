"""
CG90 KX108 Proof Agent Complete Runtime V1.

Closes the current agent proof pack:
CG86 validation + CG87 governance + CG88 security + CG89 release review.

"Complete runtime" here means complete agent proof-runtime surface only.
It does NOT mean global runtime, production, deployment or final freeze.
"""


class KX108ProofAgentCompleteRuntime:

    def __init__(self):
        self.agent_authority = False
        self.runtime_authority = False
        self.decision_authority = "KX108_ONLY"
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def validate(
        self,
        agent_validation,
        agent_governance,
        agent_security,
        agent_release,
    ):
        results = (
            agent_validation,
            agent_governance,
            agent_security,
            agent_release,
        )

        inputs_valid = all(
            isinstance(result, dict)
            for result in results
        )

        if not inputs_valid:
            return self._rejected(
                {"inputs_valid": False}
            )

        agent_ids = (
            agent_validation.get("agent_id"),
            agent_governance.get("agent_id"),
            agent_security.get("agent_id"),
            agent_release.get("agent_id"),
        )

        checks = {
            "inputs_valid": True,

            "validation_validated":
                agent_validation.get(
                    "agent_validation_status"
                ) == "VALIDATED",

            "governance_validated":
                agent_governance.get(
                    "agent_governance_status"
                ) == "VALIDATED",

            "security_validated":
                agent_security.get(
                    "agent_security_status"
                ) == "VALIDATED",

            "release_candidate_validated":
                agent_release.get(
                    "agent_release_status"
                ) == "AGENT_RELEASE_CANDIDATE",

            "release_candidate_flag":
                agent_release.get(
                    "agent_release_candidate"
                ) is True,

            "agent_ids_present":
                all(bool(agent_id) for agent_id in agent_ids),

            "agent_identity_closed":
                len(set(agent_ids)) == 1,

            "all_kx108_only":
                all(
                    result.get("decision_authority")
                    == "KX108_ONLY"
                    for result in results
                ),

            "all_no_execution_authority":
                all(
                    result.get("execution_authority")
                    is False
                    for result in results
                ),

            "all_no_memory_write":
                all(
                    result.get("memory_write")
                    is False
                    for result in results
                ),

            "all_no_kernel_mutation":
                all(
                    result.get("kernel_mutation")
                    is False
                    for result in results
                ),

            "all_no_act":
                all(
                    result.get("emits_act")
                    is False
                    for result in results
                ),

            "not_release_ready":
                agent_release.get(
                    "release_ready"
                ) is False,

            "not_production_ready":
                agent_release.get(
                    "production_ready"
                ) is False,

            "not_deployment_ready":
                agent_release.get(
                    "deployment_ready"
                ) is False,

            "not_final_freeze":
                agent_release.get(
                    "final_freeze"
                ) is False,
        }

        valid = all(checks.values())

        if not valid:
            return self._rejected(checks)

        return {
            "agent_complete_runtime_status":
                "VALIDATED",

            "checks": checks,

            "agent_id": agent_ids[0],

            "agent_proof_runtime_complete":
                True,

            "global_runtime_validated":
                False,

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

            "agent_authority":
                False,

            "runtime_authority":
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
            "agent_complete_runtime_status":
                "REJECTED",

            "checks": checks,

            "agent_id":
                None,

            "agent_proof_runtime_complete":
                False,

            "global_runtime_validated":
                False,

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

            "agent_authority":
                False,

            "runtime_authority":
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
