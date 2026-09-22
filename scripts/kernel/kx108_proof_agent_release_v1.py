"""
CG89 KX108 Proof Agent Release V1.

Combines validated agent proof surfaces with a proof-pack
release candidate.

This means AGENT RELEASE REVIEW CANDIDATE only.

It never means:
- release ready
- production ready
- deployment ready
- final freeze
"""


class KX108ProofAgentRelease:

    def __init__(self):

        self.release_authority = False
        self.agent_authority = False
        self.decision_authority = "KX108_ONLY"
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def evaluate(
        self,
        agent_validation,
        agent_governance,
        agent_security,
        release_candidate,
    ):

        inputs = (
            agent_validation,
            agent_governance,
            agent_security,
            release_candidate,
        )

        inputs_valid = all(
            isinstance(result, dict)
            for result in inputs
        )

        if not inputs_valid:

            return {
                "agent_release_status":
                    "REJECTED",

                "checks": {
                    "inputs_valid":
                        False,
                },

                "agent_release_candidate":
                    False,

                "release_authority":
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
            agent_validation.get("agent_id"),
            agent_governance.get("agent_id"),
            agent_security.get("agent_id"),
        )

        checks = {
            "inputs_valid":
                True,

            "agent_validation_validated":
                agent_validation.get(
                    "agent_validation_status"
                )
                == "VALIDATED",

            "agent_governance_validated":
                agent_governance.get(
                    "agent_governance_status"
                )
                == "VALIDATED",

            "agent_security_validated":
                agent_security.get(
                    "agent_security_status"
                )
                == "VALIDATED",

            "agent_ids_present":
                all(
                    bool(agent_id)
                    for agent_id in agent_ids
                ),

            "agent_identity_closed":
                len(set(agent_ids)) == 1,

            "proof_pack_release_candidate":
                release_candidate.get(
                    "release_candidate_status"
                )
                == "PROOF_PACK_RELEASE_CANDIDATE",

            "proof_pack_candidate_flag":
                release_candidate.get(
                    "proof_pack_release_candidate"
                )
                is True,

            "release_review_allowed":
                release_candidate.get(
                    "release_review_allowed"
                )
                is True,

            "not_production_ready":
                release_candidate.get(
                    "production_ready"
                )
                is False,

            "not_release_ready":
                release_candidate.get(
                    "release_ready"
                )
                is False,

            "not_deployment_ready":
                release_candidate.get(
                    "deployment_ready"
                )
                is False,

            "not_final_freeze":
                release_candidate.get(
                    "final_freeze"
                )
                is False,

            "validation_kx108_only":
                agent_validation.get(
                    "decision_authority"
                )
                == "KX108_ONLY",

            "governance_kx108_only":
                agent_governance.get(
                    "decision_authority"
                )
                == "KX108_ONLY",

            "security_kx108_only":
                agent_security.get(
                    "decision_authority"
                )
                == "KX108_ONLY",

            "candidate_kx108_only":
                release_candidate.get(
                    "decision_authority"
                )
                == "KX108_ONLY",

            "validation_no_execution_authority":
                agent_validation.get(
                    "execution_authority"
                )
                is False,

            "governance_no_execution_authority":
                agent_governance.get(
                    "execution_authority"
                )
                is False,

            "security_no_execution_authority":
                agent_security.get(
                    "execution_authority"
                )
                is False,

            "candidate_no_execution_authority":
                release_candidate.get(
                    "execution_authority"
                )
                is False,

            "validation_no_memory_write":
                agent_validation.get(
                    "memory_write"
                )
                is False,

            "governance_no_memory_write":
                agent_governance.get(
                    "memory_write"
                )
                is False,

            "security_no_memory_write":
                agent_security.get(
                    "memory_write"
                )
                is False,

            "candidate_no_memory_write":
                release_candidate.get(
                    "memory_write"
                )
                is False,

            "validation_no_kernel_mutation":
                agent_validation.get(
                    "kernel_mutation"
                )
                is False,

            "governance_no_kernel_mutation":
                agent_governance.get(
                    "kernel_mutation"
                )
                is False,

            "security_no_kernel_mutation":
                agent_security.get(
                    "kernel_mutation"
                )
                is False,

            "candidate_no_kernel_mutation":
                release_candidate.get(
                    "kernel_mutation"
                )
                is False,

            "validation_no_act":
                agent_validation.get(
                    "emits_act"
                )
                is False,

            "governance_no_act":
                agent_governance.get(
                    "emits_act"
                )
                is False,

            "security_no_act":
                agent_security.get(
                    "emits_act"
                )
                is False,

            "candidate_no_act":
                release_candidate.get(
                    "emits_act"
                )
                is False,
        }

        candidate = all(checks.values())

        return {
            "agent_release_status":
                "AGENT_RELEASE_CANDIDATE"
                if candidate
                else "REJECTED",

            "checks":
                checks,

            "agent_release_candidate":
                candidate,

            "agent_id":
                (
                    agent_ids[0]
                    if candidate
                    else None
                ),

            "release_review_allowed":
                candidate,

            "release_ready":
                False,

            "production_ready":
                False,

            "deployment_ready":
                False,

            "final_freeze":
                False,

            "new_authority_created":
                False,

            "release_authority":
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
