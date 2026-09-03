"""
CG98 KX108 Proof Security Audit V1.

Aggregates already-produced proof security surfaces:
- canonical KX108 security boundary;
- provider security runtime proof;
- agent security proof;
- CG97 proof-E2E validation.

This is a SECURITY PROOF-SURFACE AUDIT only.

It is NOT:
- a complete application security audit;
- penetration testing;
- infrastructure security certification;
- production security approval.
"""


class KX108ProofSecurityAudit:

    def __init__(self):
        self.audit_authority = False
        self.security_authority = False
        self.decision_authority = "KX108_ONLY"
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def validate(
        self,
        security_boundary,
        provider_security,
        agent_security,
        end_to_end_validation,
    ):
        surfaces = (
            security_boundary,
            provider_security,
            agent_security,
            end_to_end_validation,
        )

        inputs_valid = all(
            isinstance(surface, dict)
            for surface in surfaces
        )

        if not inputs_valid:
            return self._rejected(
                {"inputs_valid": False}
            )

        boundary_checks = security_boundary.get(
            "checks"
        )

        checks = {
            "inputs_valid":
                True,

            "security_boundary_checks_present":
                (
                    isinstance(boundary_checks, dict)
                    and len(boundary_checks) > 0
                ),

            "security_boundary_checks_valid":
                (
                    isinstance(boundary_checks, dict)
                    and len(boundary_checks) > 0
                    and all(boundary_checks.values())
                ),

            "provider_security_validated":
                provider_security.get(
                    "provider_security_runtime_status"
                )
                == "VALIDATED",

            "agent_security_validated":
                agent_security.get(
                    "agent_security_status"
                )
                == "VALIDATED",

            "proof_e2e_validated":
                end_to_end_validation.get(
                    "kx108_end_to_end_validation_status"
                )
                == "PROOF_E2E_VALIDATED",

            "runtime_e2e_still_false":
                end_to_end_validation.get(
                    "runtime_end_to_end_validated"
                )
                is False,

            "runtime_global_still_false":
                end_to_end_validation.get(
                    "runtime_globally_validated"
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
            "kx108_security_audit_status":
                "PROOF_SECURITY_SURFACES_AUDITED",

            "checks":
                checks,

            "proof_security_surfaces_audited":
                True,

            "complete_system_security_audit":
                False,

            "penetration_test_completed":
                False,

            "infrastructure_security_certified":
                False,

            "production_security_approved":
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

            "audit_authority":
                False,

            "security_authority":
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
            "kx108_security_audit_status":
                "REJECTED",

            "checks":
                checks,

            "proof_security_surfaces_audited":
                False,

            "complete_system_security_audit":
                False,

            "penetration_test_completed":
                False,

            "infrastructure_security_certified":
                False,

            "production_security_approved":
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

            "audit_authority":
                False,

            "security_authority":
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
