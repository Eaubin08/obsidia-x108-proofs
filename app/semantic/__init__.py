"""Obsidia public semantic core (phase 2).

Lightweight, stdlib-only structures shared by bounded local solvers:
frames, constraint graphs, closure certificates and the human-needs
bounded domain. Non-sovereign by doctrine: this layer structures and
validates — it never decides, acts, writes memory or mutates the kernel.

decision_authority: KX108_ONLY
real_action: false
memory_write: false
kernel_mutation: false
emits_act: false
"""
from app.semantic.frame import (  # noqa: F401
    SemanticEntity,
    SemanticRelation,
    SemanticQuantity,
    SemanticConstraint,
    SemanticFrame,
    semantic_signature,
)
from app.semantic.constraints import ConstraintGraph  # noqa: F401
from app.semantic.closure import build_closure_certificate  # noqa: F401
