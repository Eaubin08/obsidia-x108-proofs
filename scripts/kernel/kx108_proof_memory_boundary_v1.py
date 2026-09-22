"""
CG38 KX108 Proof Memory Boundary V1
"""

from periphery.memory.memory_source_registry import (
    MemorySourceEntry,
    get_source,
    list_sources,
)


class KX108ProofMemoryBoundary:

    def __init__(self):
        self.decision_authority = "KX108_ONLY"
        self.allowed_to_decide = False
        self.allowed_to_act = False
        self.memory_write = False
        self.kernel_mutation = False
        self.emits_act = False

    def validate_source(self, source):

        entry = (
            get_source(source)
            if isinstance(source, str)
            else source
        )

        is_entry = isinstance(
            entry,
            MemorySourceEntry,
        )

        checks = {
            "source_present":
                is_entry,

            "readonly":
                (
                    is_entry
                    and entry.readonly is True
                ),

            "write_forbidden":
                (
                    is_entry
                    and entry.write_allowed is False
                ),
        }

        valid = all(checks.values())

        return {
            "memory_boundary_status":
                "VALIDATED"
                if valid
                else "REJECTED",

            "checks":
                checks,

            "source":
                (
                    entry.to_dict()
                    if is_entry
                    else None
                ),

            "decision_authority":
                "KX108_ONLY",

            "allowed_to_decide":
                False,

            "allowed_to_act":
                False,

            "memory_write":
                False,

            "kernel_mutation":
                False,

            "emits_act":
                False,
        }

    def validate_registry(self):

        sources = list_sources()

        checks = {
            "registry_non_empty":
                len(sources) > 0,

            "all_readonly":
                all(
                    source.readonly is True
                    for source in sources
                ),

            "all_write_forbidden":
                all(
                    source.write_allowed is False
                    for source in sources
                ),
        }

        return {
            "memory_registry_status":
                "VALIDATED"
                if all(checks.values())
                else "REJECTED",

            "checks":
                checks,

            "source_count":
                len(sources),

            "decision_authority":
                "KX108_ONLY",

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

            "allowed_to_decide":
                self.allowed_to_decide,

            "allowed_to_act":
                self.allowed_to_act,

            "memory_write":
                self.memory_write,

            "kernel_mutation":
                self.kernel_mutation,

            "emits_act":
                self.emits_act,
        }
