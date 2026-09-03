"""
CG99 KX108 Proof Release Preparation V1.

Combines:
- CG97 proof-E2E validation;
- CG98 proof security-surface audit;
- proof-pack release candidate;
- provider release candidate;
- agent release candidate.

This layer prepares a PROOF RELEASE REVIEW PACKAGE only.

It does NOT authorize:
- release;
- production;
- deployment;
- runtime activation;
- final system freeze.
"""


class KX108ProofReleasePreparation:

    def __init__(self):
        self.release_authority = False
        self.decision_authority = "KX108_ONLY"
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def validate(
        self,
        end_to_end_validation,
        security_audit,
        proof_release_candidate,
        provider_release_candidate,
        agent_release_candidate,
    ):
        surfaces = (
            end_to_end_validation,
            security_audit,
            proof_release_candidate,
            provider_release_candidate,
            agent_release_candidate,
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

            "proof_e2e_validated":
                end_to_end_validation.get(
                    "kx108_end_to_end_validation_status"
                )
                == "PROOF_E2E_VALIDATED",

            "security_proof_audited":
                security_audit.get(
                    "kx108_security_audit_status"
                )
                == "PROOF_SECURITY_SURFACES_AUDITED",

            "proof_pack_release_candidate":
                (
                    proof_release_candidate.get(
                        "release_candidate_status"
                    )
                    == "PROOF_PACK_RELEASE_CANDIDATE"
                    and proof_release_candidate.get(
                        "proof_pack_release_candidate"
                    )
                    is True
                ),

            "provider_release_candidate":
                (
                    provider_release_candidate.get(
                        "provider_release_runtime_status"
                    )
                    == "PROVIDER_RELEASE_CANDIDATE"
                    and provider_release_candidate.get(
                        "provider_release_candidate"
                    )
                    is True
                ),

            "agent_release_candidate":
                (
                    agent_release_candidate.get(
                        "agent_release_status"
                    )
                    == "AGENT_RELEASE_CANDIDATE"
                    and agent_release_candidate.get(
                        "agent_release_candidate"
                    )
                    is True
                ),

            "proof_review_allowed":
                proof_release_candidate.get(
                    "release_review_allowed"
                )
                is True,

            "provider_review_allowed":
                provider_release_candidate.get(
                    "release_review_allowed"
                )
                is True,

            "agent_review_allowed":
                agent_release_candidate.get(
                    "release_review_allowed"
                )
                is True,

            "runtime_not_globally_validated":
                end_to_end_validation.get(
                    "runtime_globally_validated"
                )
                is False,

            "runtime_not_end_to_end_validated":
                end_to_end_validation.get(
                    "runtime_end_to_end_validated"
                )
                is False,

            "all_not_release_ready":
                all(
                    surface.get(
                        "release_ready"
                    )
                    is False
                    for surface in (
                        end_to_end_validation,
                        security_audit,
                        proof_release_candidate,
                        provider_release_candidate,
                        agent_release_candidate,
                    )
                ),

            "all_not_production_ready":
                all(
                    surface.get(
                        "production_ready"
                    )
                    is False
                    for surface in (
                        end_to_end_validation,
                        security_audit,
                        proof_release_candidate,
                        provider_release_candidate,
                        agent_release_candidate,
                    )
                ),

            "all_not_deployment_ready":
                all(
                    surface.get(
                        "deployment_ready"
                    )
                    is False
                    for surface in (
                        end_to_end_validation,
                        security_audit,
                        proof_release_candidate,
                        provider_release_candidate,
                        agent_release_candidate,
                    )
                ),

            "all_not_final_freeze":
                all(
                    surface.get(
                        "final_freeze"
                    )
                    is False
                    for surface in (
                        end_to_end_validation,
                        security_audit,
                        proof_release_candidate,
                        provider_release_candidate,
                        agent_release_candidate,
                    )
                ),

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
            "kx108_release_preparation_status":
                "PROOF_RELEASE_REVIEW_PREPARED",

            "checks":
                checks,

            "proof_release_review_prepared":
                True,

            "release_review_allowed":
                True,

            "release_authorized":
                False,

            "runtime_activation_authorized":
                False,

            "runtime_globally_validated":
                False,

            "runtime_end_to_end_validated":
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

            "release_authority":
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
            "kx108_release_preparation_status":
                "REJECTED",

            "checks":
                checks,

            "proof_release_review_prepared":
                False,

            "release_review_allowed":
                False,

            "release_authorized":
                False,

            "runtime_activation_authorized":
                False,

            "runtime_globally_validated":
                False,

            "runtime_end_to_end_validated":
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

            "release_authority":
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
