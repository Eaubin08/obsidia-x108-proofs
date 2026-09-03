"""
CG83 KX108 Proof Agent Runtime V1.

Validates an already-produced periphery AgentResult.

The proof layer does not invoke an agent itself.
Operational agents remain NON_SOVEREIGN peripheral signal producers.
"""

from periphery.agent_contracts import (
    AgentResult,
)

from periphery.agent_registry import (
    list_agents,
)


class KX108ProofAgentRuntime:

    def __init__(self):

        self.agent_runtime_authority = False
        self.decision_authority = "KX108_ONLY"
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def validate(self, agent_result):

        result_valid = isinstance(
            agent_result,
            AgentResult,
        )

        packet = (
            agent_result.packet
            if result_valid
            else None
        )

        agent_id = (
            agent_result.agent_id
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

        expected_evidence = (
            f"agent:{agent_id}"
            if agent_id
            else None
        )

        checks = {
            "agent_result_object":
                result_valid,

            "agent_id_present":
                bool(agent_id),

            "agent_registered":
                (
                    bool(agent_id)
                    and agent_id in set(
                        list_agents()
                    )
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

            "action_id_present":
                (
                    packet is not None
                    and bool(
                        getattr(
                            packet,
                            "action_id",
                            None,
                        )
                    )
                ),

            "domain_present":
                (
                    packet is not None
                    and bool(
                        getattr(
                            packet,
                            "domain",
                            None,
                        )
                    )
                ),

            "agent_provenance_bound":
                (
                    packet is not None
                    and expected_evidence
                    in getattr(
                        packet,
                        "evidence_refs",
                        [],
                    )
                ),
        }

        valid = all(checks.values())

        return {
            "agent_runtime_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "checks":
                checks,

            "agent_id":
                (
                    agent_id
                    if valid
                    else None
                ),

            "agent_layer":
                (
                    str(agent_result.layer)
                    if valid
                    else None
                ),

            "action_id":
                (
                    packet.action_id
                    if valid
                    else None
                ),

            "domain":
                (
                    packet.domain
                    if valid
                    else None
                ),

            "agent_invoked_here":
                False,

            "agent_runtime_authority":
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
