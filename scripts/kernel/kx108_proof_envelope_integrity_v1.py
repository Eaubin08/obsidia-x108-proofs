"""
CG65 KX108 Proof Envelope Integrity V1.

Structural integrity verification across:
- canonical decision candidate envelope,
- KX108 authority envelope,
- canonical execution envelope.

No cryptographic hash is invented where the source envelope
contract does not define one.
"""

from scripts.kernel.canonical_decision_envelope_v1 import (
    CanonicalDecisionEnvelope,
)

from scripts.kernel.kx108_decision_envelope_v1 import (
    KX108DecisionEnvelope,
)

from scripts.providers.canonical_execution_envelope_v1 import (
    CanonicalExecutionEnvelope,
)


class KX108ProofEnvelopeIntegrity:

    def __init__(self):
        self.decision_authority = "KX108_ONLY"
        self.integrity_authority = False
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def validate(
        self,
        decision_candidate,
        kx108_envelope,
        execution_envelope,
    ):

        objects_valid = (
            isinstance(
                decision_candidate,
                CanonicalDecisionEnvelope,
            )
            and isinstance(
                kx108_envelope,
                KX108DecisionEnvelope,
            )
            and isinstance(
                execution_envelope,
                CanonicalExecutionEnvelope,
            )
        )

        if not objects_valid:

            return {
                "envelope_integrity_status":
                    "REJECTED",

                "checks": {
                    "canonical_envelope_objects":
                        False,
                },

                "integrity_authority":
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
            "canonical_envelope_objects":
                True,

            "decision_envelope_identity":
                decision_candidate.envelope_id
                == "decision-envelope-v1",

            "decision_candidate_only":
                decision_candidate.decision_status
                == "CANDIDATE_ONLY",

            "decision_source_present":
                bool(
                    decision_candidate.source_provider
                ),

            "decision_runtime_present":
                bool(
                    decision_candidate.runtime_ref
                ),

            "runtime_binding":
                decision_candidate.runtime_ref
                == execution_envelope.runtime_id,

            "kx108_authorized_candidate":
                kx108_envelope.authority_status
                == "AUTHORIZED_CANDIDATE",

            "kx108_decision_ready":
                kx108_envelope.decision_status
                == "KX108_DECISION_READY",

            "kx108_source":
                kx108_envelope.source_authority
                == "KX108",

            "kx108_no_act":
                kx108_envelope.act
                is False,

            "execution_envelope_sealed":
                execution_envelope.status
                == "SEALED",

            "execution_runtime_present":
                bool(
                    execution_envelope.runtime_id
                ),

            "execution_no_decision_authority":
                execution_envelope.decision_authority
                is False,

            "execution_no_execution_authority":
                execution_envelope.execution_authority
                is False,

            "execution_no_memory_write":
                execution_envelope.memory_write
                is False,

            "execution_no_kernel_mutation":
                execution_envelope.kernel_mutation
                is False,

            "execution_no_act":
                execution_envelope.emits_act
                is False,
        }

        valid = all(checks.values())

        return {
            "envelope_integrity_status":
                "INTACT"
                if valid
                else "REJECTED",

            "checks":
                checks,

            "decision_candidate":
                decision_candidate.to_dict(),

            "kx108_envelope":
                kx108_envelope.to_dict(),

            "execution_envelope":
                execution_envelope.to_dict(),

            "cryptographic_hash_claimed":
                False,

            "integrity_authority":
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
            "decision_authority":
                self.decision_authority,

            "integrity_authority":
                self.integrity_authority,

            "execution_authority":
                self.execution_authority,

            "memory_write":
                self.memory_write,

            "kernel_mutation":
                self.kernel_mutation,

            "emits_act":
                self.emits_act,
        }
