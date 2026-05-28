"""Obsidia Workflow Governance Primitive V4.

Readonly peripheral pack for transforming human SOPs into auditable workflow
context packets before any X108 evaluation.

Authority invariant:
    DECISION_AUTHORITY = KX108_ONLY

This package never binds to the X108 runtime, never mutates the kernel, never
emits a workflow verdict, and never executes a critical action. It prepares
structure, evidence requirements, replay traces, and ingress envelopes only.
"""

from .constants import DECISION_AUTHORITY, MODULE_FAMILY, MODE, READONLY_FLAGS

__all__ = ["DECISION_AUTHORITY", "MODULE_FAMILY", "MODE", "READONLY_FLAGS"]
