"""
CG48 KX108 Proof Security Boundary V1.

Uses the existing Brody secret detection/scrubbing surface.
No IO, no write, no ACT and no authority transfer.
"""

import copy

from apps.obsidia_api.brody_secret_scrubber import (
    detect_secret_like,
    scrub_secret_like_deep,
)


def _contains_secret(obj):

    if isinstance(obj, str):
        return detect_secret_like(obj)

    if isinstance(obj, dict):
        return any(
            _contains_secret(value)
            for value in obj.values()
        )

    if isinstance(obj, (list, tuple)):
        return any(
            _contains_secret(value)
            for value in obj
        )

    return False


def _contains_redaction(obj):

    if isinstance(obj, str):
        return "[REDACTED_SECRET]" in obj

    if isinstance(obj, dict):
        return any(
            _contains_redaction(value)
            for value in obj.values()
        )

    if isinstance(obj, (list, tuple)):
        return any(
            _contains_redaction(value)
            for value in obj
        )

    return False


class KX108ProofSecurityBoundary:

    def __init__(self):
        self.decision_authority = "KX108_ONLY"
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def sanitize(self, payload):

        supported = isinstance(
            payload,
            (str, dict, list),
        )

        if not supported:

            return {
                "security_boundary_status":
                    "REJECTED",

                "checks":
                    {
                        "supported_payload":
                            False,
                    },

                "secret_detected":
                    False,

                "sanitized":
                    None,

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

        original_snapshot = copy.deepcopy(
            payload
        )

        secret_detected = _contains_secret(
            payload
        )

        sanitized = scrub_secret_like_deep(
            payload
        )

        redaction_present = (
            _contains_redaction(sanitized)
        )

        checks = {
            "supported_payload":
                True,

            "input_not_mutated":
                payload == original_snapshot,

            "secret_redacted_when_detected":
                (
                    not secret_detected
                    or redaction_present
                ),

            "clean_payload_preserved":
                (
                    secret_detected
                    or sanitized == payload
                ),
        }

        valid = all(checks.values())

        return {
            "security_boundary_status":
                (
                    "SANITIZED"
                    if valid and secret_detected
                    else (
                        "CLEAN"
                        if valid
                        else "REJECTED"
                    )
                ),

            "checks":
                checks,

            "secret_detected":
                secret_detected,

            "redaction_present":
                redaction_present,

            "sanitized":
                sanitized,

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

            "execution_authority":
                self.execution_authority,

            "memory_write":
                self.memory_write,

            "kernel_mutation":
                self.kernel_mutation,

            "emits_act":
                self.emits_act,
        }
