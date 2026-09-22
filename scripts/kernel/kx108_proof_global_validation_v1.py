"""
CG69 KX108 Proof Global Validation V1.

Aggregates validation of the current proof-boundary pack.

GLOBAL means global to this proof pack only.
It does NOT claim:
- complete runtime validation,
- production readiness,
- release readiness,
- deployment readiness,
- final freeze.
"""


class KX108ProofGlobalValidation:

    REQUIRED = {
        "boundary_composition":
            (
                "boundary_composition_status",
                "COMPOSED",
            ),

        "final_boundary":
            (
                "final_boundary_status",
                "PROOF_BOUNDARY_CLOSED",
            ),

        "envelope_integrity":
            (
                "envelope_integrity_status",
                "INTACT",
            ),

        "receipt_chain":
            (
                "receipt_chain_status",
                "VALIDATED",
            ),

        "provider_binding":
            (
                "provider_binding_status",
                "VALIDATED",
            ),

        "kernel_interface":
            (
                "kernel_interface_status",
                "VALIDATED",
            ),
    }

    def __init__(self):
        self.global_authority = False
        self.decision_authority = "KX108_ONLY"
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def validate(self, proofs):

        if not isinstance(proofs, dict):

            return {
                "global_validation_status":
                    "REJECTED",

                "checks": {
                    "proof_map":
                        False,
                },

                "proof_pack_validated":
                    False,

                "global_authority":
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
            "proof_map":
                True,
        }

        for name, (
            status_key,
            expected_status,
        ) in self.REQUIRED.items():

            proof = proofs.get(name)

            checks[
                f"{name}_present"
            ] = isinstance(proof, dict)

            if not isinstance(proof, dict):
                continue

            checks[
                f"{name}_status"
            ] = (
                proof.get(status_key)
                == expected_status
            )

            checks[
                f"{name}_kx108_only"
            ] = (
                proof.get(
                    "decision_authority"
                )
                == "KX108_ONLY"
            )

            checks[
                f"{name}_no_execution_authority"
            ] = (
                proof.get(
                    "execution_authority"
                )
                is False
            )

            checks[
                f"{name}_no_memory_write"
            ] = (
                proof.get(
                    "memory_write"
                )
                is False
            )

            checks[
                f"{name}_no_kernel_mutation"
            ] = (
                proof.get(
                    "kernel_mutation"
                )
                is False
            )

            checks[
                f"{name}_no_act"
            ] = (
                proof.get(
                    "emits_act"
                )
                is False
            )

        validated = all(checks.values())

        return {
            "global_validation_status":
                "PROOF_PACK_VALIDATED"
                if validated
                else "REJECTED",

            "checks":
                checks,

            "proof_pack_validated":
                validated,

            "proof_count":
                len(self.REQUIRED),

            "runtime_globally_validated":
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

            "global_authority":
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

    def status(self):

        return {
            "global_authority":
                self.global_authority,

            "decision_authority":
                self.decision_authority,

            "execution_authority":
                self.execution_authority,

            "memory_write":
                self.memory_write,

            "kernel_mutation":
                self.kernel_mutation,

            "emits_act":
                self.emits_act,
        }
