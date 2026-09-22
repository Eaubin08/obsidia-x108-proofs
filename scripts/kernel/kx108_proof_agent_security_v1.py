"""
CG88 KX108 Proof Agent Security V1.

Applies the existing KX108 security boundary to an explicit
security projection of a real AgentResult packet.

It does NOT create AgentResult -> ContextPacket conversion.
It does NOT submit anything to X108.
It does NOT invoke an agent.
"""

from copy import deepcopy

from periphery.agent_contracts import (
    AgentResult,
)

from scripts.kernel.kx108_proof_security_boundary_v1 import (
    KX108ProofSecurityBoundary,
)


class KX108ProofAgentSecurity:

    def __init__(self):

        self.security_boundary = (
            KX108ProofSecurityBoundary()
        )

        self.security_authority = False
        self.agent_authority = False
        self.decision_authority = "KX108_ONLY"
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    @staticmethod
    def _project(agent_result):

        packet = agent_result.packet

        return {
            "agent_id":
                agent_result.agent_id,

            "agent_layer":
                str(agent_result.layer),

            "action_id":
                packet.action_id,

            "domain":
                packet.domain,

            "extra_metrics":
                deepcopy(
                    packet.extra_metrics
                ),

            "unknowns":
                list(packet.unknowns),

            "risk_flags":
                list(packet.risk_flags),

            "contradictions":
                list(packet.contradictions),

            "evidence_refs":
                list(packet.evidence_refs),

            "recommended_gate":
                packet.recommended_gate,

            "can_emit_act":
                packet.can_emit_act,
        }

    def validate(
        self,
        agent_validation,
        agent_result,
    ):

        validation_valid = isinstance(
            agent_validation,
            dict,
        )

        result_valid = isinstance(
            agent_result,
            AgentResult,
        )

        packet_non_sovereign = False

        if result_valid:

            try:
                agent_result.assert_non_sovereign()
                packet_non_sovereign = True

            except AssertionError:
                packet_non_sovereign = False

        projected_payload = (
            self._project(agent_result)
            if result_valid
            else None
        )

        security_result = (
            self.security_boundary.sanitize(
                projected_payload
            )
            if projected_payload is not None
            else None
        )

        security_checks = (
            security_result.get("checks")
            if isinstance(
                security_result,
                dict,
            )
            else None
        )

        security_checks_valid = (
            isinstance(
                security_checks,
                dict,
            )
            and len(security_checks) > 0
            and all(
                security_checks.values()
            )
        )

        checks = {
            "agent_validation_object":
                validation_valid,

            "agent_validation_validated":
                (
                    validation_valid
                    and agent_validation.get(
                        "agent_validation_status"
                    )
                    == "VALIDATED"
                ),

            "agent_result_object":
                result_valid,

            "agent_identity_bound":
                (
                    validation_valid
                    and result_valid
                    and agent_validation.get(
                        "agent_id"
                    )
                    == agent_result.agent_id
                ),

            "packet_non_sovereign":
                packet_non_sovereign,

            "packet_cannot_emit_act":
                (
                    result_valid
                    and agent_result.packet.can_emit_act
                    is False
                ),

            "agent_kx108_only":
                (
                    validation_valid
                    and agent_validation.get(
                        "decision_authority"
                    )
                    == "KX108_ONLY"
                ),

            "agent_no_authority":
                (
                    validation_valid
                    and agent_validation.get(
                        "agent_authority"
                    )
                    is False
                ),

            "security_result_object":
                isinstance(
                    security_result,
                    dict,
                ),

            "security_checks_valid":
                security_checks_valid,

            "security_kx108_only":
                (
                    isinstance(
                        security_result,
                        dict,
                    )
                    and security_result.get(
                        "decision_authority"
                    )
                    == "KX108_ONLY"
                ),

            "security_no_execution_authority":
                (
                    isinstance(
                        security_result,
                        dict,
                    )
                    and security_result.get(
                        "execution_authority"
                    )
                    is False
                ),

            "security_no_memory_write":
                (
                    isinstance(
                        security_result,
                        dict,
                    )
                    and security_result.get(
                        "memory_write"
                    )
                    is False
                ),

            "security_no_kernel_mutation":
                (
                    isinstance(
                        security_result,
                        dict,
                    )
                    and security_result.get(
                        "kernel_mutation"
                    )
                    is False
                ),

            "security_no_act":
                (
                    isinstance(
                        security_result,
                        dict,
                    )
                    and security_result.get(
                        "emits_act"
                    )
                    is False
                ),
        }

        valid = all(checks.values())

        return {
            "agent_security_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "checks":
                checks,

            "agent_id":
                (
                    agent_result.agent_id
                    if valid
                    else None
                ),

            "security_projection":
                projected_payload,

            "sanitized_projection":
                (
                    security_result.get(
                        "sanitized"
                    )
                    if isinstance(
                        security_result,
                        dict,
                    )
                    else None
                ),

            "secret_detected":
                (
                    security_result.get(
                        "secret_detected"
                    )
                    if isinstance(
                        security_result,
                        dict,
                    )
                    else None
                ),

            "agent_invoked_here":
                False,

            "context_packet_created":
                False,

            "x108_submitted_here":
                False,

            "security_authority":
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
