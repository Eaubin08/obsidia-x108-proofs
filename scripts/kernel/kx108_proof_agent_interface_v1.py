"""
CG85 KX108 Proof Agent Interface V1.

Validates the real periphery agent interface.

There is intentionally no implicit AgentResult -> ContextPacket conversion
here. That conversion is explicit and canonical, and lives in
periphery/context/agent_result_context_adapter.py; this interface proof
never performs it.

The agent remains a peripheral signal producer only.
"""


class KX108ProofAgentInterface:

    def __init__(self):

        self.interface_authority = False
        self.agent_authority = False
        self.decision_authority = "KX108_ONLY"
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def validate(
        self,
        agent_boundary,
        agent_result,
    ):

        from periphery.agent_contracts import (
            AgentResult,
        )

        boundary_valid = isinstance(
            agent_boundary,
            dict,
        )

        result_valid = isinstance(
            agent_result,
            AgentResult,
        )

        packet = (
            agent_result.packet
            if result_valid
            else None
        )

        packet_non_sovereign = False

        if result_valid:

            try:
                agent_result.assert_non_sovereign()
                packet_non_sovereign = True

            except AssertionError:
                packet_non_sovereign = False

        checks = {
            "agent_boundary_object":
                boundary_valid,

            "agent_boundary_validated":
                (
                    boundary_valid
                    and agent_boundary.get(
                        "agent_boundary_status"
                    )
                    == "VALIDATED"
                ),

            "agent_result_object":
                result_valid,

            "agent_identity_bound":
                (
                    boundary_valid
                    and result_valid
                    and agent_boundary.get(
                        "agent_id"
                    )
                    == agent_result.agent_id
                ),

            "packet_present":
                packet is not None,

            "packet_non_sovereign":
                packet_non_sovereign,

            "packet_cannot_emit_act":
                (
                    packet is not None
                    and getattr(
                        packet,
                        "can_emit_act",
                        None,
                    )
                    is False
                ),

            "agent_provenance_present":
                (
                    packet is not None
                    and f"agent:{agent_result.agent_id}"
                    in getattr(
                        packet,
                        "evidence_refs",
                        [],
                    )
                ),

            "boundary_kx108_only":
                (
                    boundary_valid
                    and agent_boundary.get(
                        "decision_authority"
                    )
                    == "KX108_ONLY"
                ),

            "boundary_no_agent_authority":
                (
                    boundary_valid
                    and agent_boundary.get(
                        "agent_authority"
                    )
                    is False
                ),

            "boundary_agent_cannot_decide":
                (
                    boundary_valid
                    and agent_boundary.get(
                        "agent_can_decide"
                    )
                    is False
                ),

            "boundary_agent_cannot_authorize":
                (
                    boundary_valid
                    and agent_boundary.get(
                        "agent_can_authorize"
                    )
                    is False
                ),

            "boundary_agent_cannot_act":
                (
                    boundary_valid
                    and agent_boundary.get(
                        "agent_can_act"
                    )
                    is False
                ),

            "boundary_no_execution_authority":
                (
                    boundary_valid
                    and agent_boundary.get(
                        "execution_authority"
                    )
                    is False
                ),

            "boundary_no_memory_write":
                (
                    boundary_valid
                    and agent_boundary.get(
                        "memory_write"
                    )
                    is False
                ),

            "boundary_no_kernel_mutation":
                (
                    boundary_valid
                    and agent_boundary.get(
                        "kernel_mutation"
                    )
                    is False
                ),

            "boundary_no_act":
                (
                    boundary_valid
                    and agent_boundary.get(
                        "emits_act"
                    )
                    is False
                ),
        }

        valid = all(checks.values())

        return {
            "agent_interface_status":
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

            "interface_mode":
                "PERIPHERAL_SIGNAL_ONLY",

            "requires_context_adapter":
                True,

            "context_adapter_invoked_here":
                False,

            "context_packet_created":
                False,

            "x108_submitted_here":
                False,

            "interface_authority":
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
