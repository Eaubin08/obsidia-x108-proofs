"""
CG81 KX108 Proof Mission Runtime V1.

Validates mission identity coherence between:
- an already-produced canonical execution flow,
- its execution session/envelope,
- bounded mission-authority evidence.

Mission authority evidence remains NON_SOVEREIGN.
It is never KX108 authority and never runtime/execution authority.
"""


class KX108ProofMissionRuntime:

    def __init__(self):

        self.mission_authority = False
        self.runtime_authority = False
        self.decision_authority = "KX108_ONLY"
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def validate(
        self,
        flow_output,
        mission_authority,
    ):

        flow_valid = isinstance(
            flow_output,
            dict,
        )

        authority_valid = isinstance(
            mission_authority,
            dict,
        )

        execution = (
            flow_output.get("execution")
            if flow_valid
            else None
        )

        session = (
            execution.get("session")
            if isinstance(
                execution,
                dict,
            )
            else None
        )

        envelope = (
            execution.get("envelope")
            if isinstance(
                execution,
                dict,
            )
            else None
        )

        session_mission_id = (
            session.get("mission_id")
            if isinstance(
                session,
                dict,
            )
            else None
        )

        envelope_mission_id = (
            envelope.get("mission_id")
            if isinstance(
                envelope,
                dict,
            )
            else None
        )

        authority_mission_id = (
            mission_authority.get(
                "mission_id"
            )
            if authority_valid
            else None
        )

        checks = {
            "flow_object":
                flow_valid,

            "flow_completed":
                (
                    flow_valid
                    and flow_output.get(
                        "flow_status"
                    )
                    == "COMPLETED"
                ),

            "execution_present":
                isinstance(
                    execution,
                    dict,
                ),

            "session_present":
                isinstance(
                    session,
                    dict,
                ),

            "session_completed":
                (
                    isinstance(
                        session,
                        dict,
                    )
                    and session.get(
                        "status"
                    )
                    == "COMPLETED"
                ),

            "envelope_present":
                isinstance(
                    envelope,
                    dict,
                ),

            "envelope_sealed":
                (
                    isinstance(
                        envelope,
                        dict,
                    )
                    and envelope.get(
                        "status"
                    )
                    == "SEALED"
                ),

            "mission_ids_present":
                (
                    bool(
                        session_mission_id
                    )
                    and bool(
                        envelope_mission_id
                    )
                    and bool(
                        authority_mission_id
                    )
                ),

            "mission_identity_closed":
                (
                    session_mission_id
                    == envelope_mission_id
                    == authority_mission_id
                ),

            "authority_evidence_present":
                authority_valid,

            "mission_authority_non_sovereign":
                (
                    authority_valid
                    and mission_authority.get(
                        "authority"
                    )
                    == "NON_SOVEREIGN"
                ),

            "runtime_authority_inactive":
                (
                    authority_valid
                    and mission_authority.get(
                        "runtime_authority_active"
                    )
                    is False
                ),

            "not_kx_authority":
                (
                    authority_valid
                    and mission_authority.get(
                        "is_kx_authority"
                    )
                    is False
                ),

            "plan_not_execution_authority":
                (
                    authority_valid
                    and mission_authority.get(
                        "plan_is_execution_authority"
                    )
                    is False
                ),

            "session_no_decision_authority":
                (
                    isinstance(
                        session,
                        dict,
                    )
                    and session.get(
                        "decision_authority"
                    )
                    is False
                ),

            "session_no_execution_authority":
                (
                    isinstance(
                        session,
                        dict,
                    )
                    and session.get(
                        "execution_authority"
                    )
                    is False
                ),

            "session_no_memory_write":
                (
                    isinstance(
                        session,
                        dict,
                    )
                    and session.get(
                        "memory_write"
                    )
                    is False
                ),

            "session_no_kernel_mutation":
                (
                    isinstance(
                        session,
                        dict,
                    )
                    and session.get(
                        "kernel_mutation"
                    )
                    is False
                ),

            "session_no_act":
                (
                    isinstance(
                        session,
                        dict,
                    )
                    and session.get(
                        "emits_act"
                    )
                    is False
                ),

            "envelope_no_decision_authority":
                (
                    isinstance(
                        envelope,
                        dict,
                    )
                    and envelope.get(
                        "decision_authority"
                    )
                    is False
                ),

            "envelope_no_execution_authority":
                (
                    isinstance(
                        envelope,
                        dict,
                    )
                    and envelope.get(
                        "execution_authority"
                    )
                    is False
                ),

            "envelope_no_memory_write":
                (
                    isinstance(
                        envelope,
                        dict,
                    )
                    and envelope.get(
                        "memory_write"
                    )
                    is False
                ),

            "envelope_no_kernel_mutation":
                (
                    isinstance(
                        envelope,
                        dict,
                    )
                    and envelope.get(
                        "kernel_mutation"
                    )
                    is False
                ),

            "envelope_no_act":
                (
                    isinstance(
                        envelope,
                        dict,
                    )
                    and envelope.get(
                        "emits_act"
                    )
                    is False
                ),
        }

        valid = all(checks.values())

        return {
            "mission_runtime_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "checks":
                checks,

            "mission_id":
                (
                    session_mission_id
                    if valid
                    else None
                ),

            "mission_authority_evidence":
                mission_authority,

            "runtime_authority_active":
                False,

            "mission_authority":
                False,

            "runtime_authority":
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
            "mission_authority":
                self.mission_authority,

            "runtime_authority":
                self.runtime_authority,

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
