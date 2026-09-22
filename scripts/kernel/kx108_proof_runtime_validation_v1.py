"""
CG31 KX108 Proof Runtime Validation V1
"""


class KX108ProofRuntimeValidator:

    def __init__(self):
        self.authority = False
        self.decision_authority = False
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def validate(self, runtime_output):

        is_dict = isinstance(runtime_output, dict)

        execution = (
            runtime_output.get("execution")
            if is_dict
            else None
        )

        envelope = (
            execution.get("envelope")
            if isinstance(execution, dict)
            else None
        )

        checks = {
            "runtime_output":
                is_dict,

            "flow_completed":
                (
                    is_dict
                    and runtime_output.get("flow_status")
                    == "COMPLETED"
                ),

            "execution_present":
                isinstance(execution, dict),

            "envelope_present":
                isinstance(envelope, dict),

            "envelope_sealed":
                (
                    isinstance(envelope, dict)
                    and envelope.get("status") == "SEALED"
                ),

            "runtime_identity":
                (
                    isinstance(envelope, dict)
                    and bool(envelope.get("runtime_id"))
                ),
        }

        valid = all(checks.values())

        return {
            "runtime_validation_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "checks":
                checks,

            "runtime_ref":
                (
                    envelope.get("runtime_id")
                    if isinstance(envelope, dict)
                    else None
                ),

            "authority":
                False,

            "decision_authority":
                False,

            "execution_authority":
                False,

            "kernel_mutation":
                False,

            "emits_act":
                False,
        }

    def status(self):

        return {
            "authority": self.authority,
            "decision_authority": self.decision_authority,
            "execution_authority": self.execution_authority,
            "memory_write": self.memory_write,
            "kernel_mutation": self.kernel_mutation,
            "emits_act": self.emits_act,
        }
