"""
CG52 KX108 Proof Canonical Authority Boundary V1.

Uses the existing CG11 authority and decision-envelope chain.

The only canonical authority source observed here is KX108.
No ACT and no execution authority are emitted.
"""

from scripts.kernel.kx108_decision_authority_v1 import (
    KX108DecisionAuthority,
)

from scripts.kernel.kx108_decision_envelope_v1 import (
    KX108DecisionEnvelopeBuilder,
)


class KX108ProofCanonicalAuthorityBoundary:

    def __init__(self):
        self.authority = KX108DecisionAuthority()
        self.envelope_builder = (
            KX108DecisionEnvelopeBuilder()
        )

        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def validate(self, resolver_audit):

        if not isinstance(resolver_audit, dict):

            return {
                "canonical_authority_status":
                    "REJECTED",

                "checks":
                    {
                        "resolver_audit":
                            False,
                    },

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

        authority_result = self.authority.evaluate(
            resolver_audit
        )

        envelope = self.envelope_builder.build(
            authority_result
        )

        authority_status = self.authority.status()
        envelope_status = (
            self.envelope_builder.status()
        )

        checks = {
            "resolver_audit":
                True,

            "authority_enabled":
                authority_status.get(
                    "authority_enabled"
                )
                is True,

            "authorized_candidate":
                authority_result.get(
                    "authority_status"
                )
                == "AUTHORIZED_CANDIDATE",

            "decision_ready":
                authority_result.get(
                    "decision_status"
                )
                == "KX108_DECISION_READY",

            "canonical_source":
                envelope.source_authority
                == "KX108",

            "envelope_decision_ready":
                envelope.decision_status
                == "KX108_DECISION_READY",

            "no_decision_payload":
                authority_result.get(
                    "decision"
                )
                is None,

            "no_act":
                (
                    authority_result.get(
                        "act"
                    )
                    is False
                    and envelope.act
                    is False
                ),

            "no_execution_authority":
                (
                    authority_status.get(
                        "execution_authority"
                    )
                    is False
                    and envelope_status.get(
                        "execution_authority"
                    )
                    is False
                ),

            "no_memory_write":
                (
                    authority_status.get(
                        "memory_write"
                    )
                    is False
                    and envelope_status.get(
                        "memory_write"
                    )
                    is False
                ),

            "no_kernel_mutation":
                (
                    authority_status.get(
                        "kernel_mutation"
                    )
                    is False
                    and envelope_status.get(
                        "kernel_mutation"
                    )
                    is False
                ),
        }

        valid = all(checks.values())

        return {
            "canonical_authority_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "checks":
                checks,

            "authority_result":
                authority_result,

            "decision_envelope":
                envelope.to_dict(),

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
                "KX108_ONLY",

            "execution_authority":
                self.execution_authority,

            "memory_write":
                self.memory_write,

            "kernel_mutation":
                self.kernel_mutation,

            "emits_act":
                self.emits_act,
        }
