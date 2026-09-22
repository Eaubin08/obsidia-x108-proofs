"""
CG96 KX108 Proof Global Runtime V1.

Aggregates already-produced proof-runtime surfaces:
- proof-pack global validation;
- execution-runtime proof;
- provider-validation runtime proof;
- mission-runtime proof;
- agent complete-runtime proof;
- agent canonical-envelope proof;
- agent receipt closure.

IMPORTANT:

The existing CG69 "global validation" is global to the proof pack only
and explicitly reports runtime_globally_validated=False.

Therefore this layer may validate global PROOF-RUNTIME SURFACES,
but it MUST NOT claim that the production runtime is globally validated.
"""


class KX108ProofGlobalRuntime:

    def __init__(self):
        self.global_runtime_authority = False
        self.decision_authority = "KX108_ONLY"
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def validate(
        self,
        proof_pack_global,
        execution_runtime,
        provider_validation,
        mission_runtime,
        agent_complete_runtime,
        agent_canonical_envelope,
        agent_receipt_closure,
    ):
        surfaces = (
            proof_pack_global,
            execution_runtime,
            provider_validation,
            mission_runtime,
            agent_complete_runtime,
            agent_canonical_envelope,
            agent_receipt_closure,
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

            "proof_pack_validated":
                (
                    proof_pack_global.get(
                        "global_validation_status"
                    )
                    == "PROOF_PACK_VALIDATED"
                    and proof_pack_global.get(
                        "proof_pack_validated"
                    )
                    is True
                ),

            "execution_runtime_validated":
                execution_runtime.get(
                    "execution_runtime_status"
                )
                == "VALIDATED",

            "provider_runtime_validated":
                provider_validation.get(
                    "provider_validation_runtime_status"
                )
                == "VALIDATED",

            "mission_runtime_validated":
                mission_runtime.get(
                    "mission_runtime_status"
                )
                == "VALIDATED",

            "agent_runtime_validated":
                (
                    agent_complete_runtime.get(
                        "agent_complete_runtime_status"
                    )
                    == "VALIDATED"
                    and agent_complete_runtime.get(
                        "agent_proof_runtime_complete"
                    )
                    is True
                ),

            "agent_envelope_validated":
                agent_canonical_envelope.get(
                    "agent_canonical_envelope_status"
                )
                == "VALIDATED",

            "agent_receipt_closure_validated":
                agent_receipt_closure.get(
                    "agent_receipt_closure_status"
                )
                == "VALIDATED",

            "proof_pack_not_runtime_global":
                proof_pack_global.get(
                    "runtime_globally_validated"
                )
                is False,

            "agent_pack_not_runtime_global":
                agent_complete_runtime.get(
                    "global_runtime_validated"
                )
                is False,

            "proof_pack_not_production_ready":
                proof_pack_global.get(
                    "production_ready"
                )
                is False,

            "proof_pack_not_release_ready":
                proof_pack_global.get(
                    "release_ready"
                )
                is False,

            "proof_pack_not_deployment_ready":
                proof_pack_global.get(
                    "deployment_ready"
                )
                is False,

            "proof_pack_not_final_freeze":
                proof_pack_global.get(
                    "final_freeze"
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
            "kx108_global_runtime_status":
                "PROOF_RUNTIME_SURFACES_VALIDATED",

            "checks":
                checks,

            "proof_runtime_surfaces_validated":
                True,

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

            "global_runtime_authority":
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
            "kx108_global_runtime_status":
                "REJECTED",

            "checks":
                checks,

            "proof_runtime_surfaces_validated":
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

            "global_runtime_authority":
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
