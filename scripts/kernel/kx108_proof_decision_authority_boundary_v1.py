"""
CG53 KX108 Proof Decision Authority Boundary V1.

Validates an already-rendered immutable KX108 decision record.

It does NOT invoke KX108.
It does NOT recompute a decision.
It only delegates cryptographic/authority verification to the
existing canonical decision store verifier.
"""

import importlib
import sys
from pathlib import Path


def _load_decision_store():

    scripts_dir = str(
        Path(__file__).resolve().parents[1]
    )

    inserted = False

    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
        inserted = True

    try:
        return importlib.import_module(
            "obsidia_kx108_decision_store"
        )
    finally:
        if inserted:
            try:
                sys.path.remove(scripts_dir)
            except ValueError:
                pass


class KX108ProofDecisionAuthorityBoundary:

    def __init__(self):
        self.decision_authority = "KX108_ONLY"
        self.execution_authority = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def validate(self, record):

        if not isinstance(record, dict):

            return {
                "decision_authority_boundary_status":
                    "REJECTED",

                "checks":
                    {
                        "record_object":
                            False,
                    },

                "verification_reason":
                    "DECISION_RECORD_MISSING",

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

        store = _load_decision_store()

        verified, reason = (
            store.verify_kx108_decision_record(
                record
            )
        )

        envelope = record.get(
            "canonical_envelope"
        )

        checks = {
            "record_object":
                True,

            "canonical_verifier_passed":
                verified is True,

            "kx108_only":
                record.get(
                    "decision_authority"
                )
                == store.DECISION_AUTHORITY
                == "KX108_ONLY",

            "gate_valid":
                record.get(
                    "x108_gate"
                )
                in {
                    "ALLOW",
                    "HOLD",
                    "BLOCK",
                },

            "canonical_envelope":
                isinstance(
                    envelope,
                    dict,
                ),

            "gate_binding":
                (
                    isinstance(
                        envelope,
                        dict,
                    )
                    and envelope.get(
                        "x108_gate"
                    )
                    == record.get(
                        "x108_gate"
                    )
                ),

            "decision_identity_binding":
                (
                    isinstance(
                        envelope,
                        dict,
                    )
                    and envelope.get(
                        "decision_id"
                    )
                    == record.get(
                        "decision_id"
                    )
                ),

            "trace_identity_binding":
                (
                    isinstance(
                        envelope,
                        dict,
                    )
                    and envelope.get(
                        "trace_id"
                    )
                    == record.get(
                        "trace_id"
                    )
                ),

            "record_hash_present":
                isinstance(
                    record.get(
                        "decision_record_hash"
                    ),
                    str,
                )
                and len(
                    record.get(
                        "decision_record_hash",
                    )
                )
                == 64,
        }

        valid = all(checks.values())

        return {
            "decision_authority_boundary_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "checks":
                checks,

            "verification_reason":
                reason,

            "decision_record_id":
                record.get(
                    "decision_record_id"
                ),

            "x108_gate":
                record.get(
                    "x108_gate"
                ),

            "decision_id":
                record.get(
                    "decision_id"
                ),

            "trace_id":
                record.get(
                    "trace_id"
                ),

            "decision_recomputed":
                False,

            "kx108_invoked":
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

            "execution_authority":
                self.execution_authority,

            "memory_write":
                self.memory_write,

            "kernel_mutation":
                self.kernel_mutation,

            "emits_act":
                self.emits_act,
        }
