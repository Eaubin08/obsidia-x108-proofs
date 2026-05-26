"""
Governance Partition: X_B (block), X_H (hold), X_A (allow/admissible).
P_partition(x) = BLOCK if x ∈ X_B, HOLD if x ∈ X_H, ALLOW if x ∈ X_A.
"""
from __future__ import annotations

from .lyapunov import LyapunovResult


def partition_to_gate(lyapunov: LyapunovResult) -> str:
    if lyapunov.partition == "X_B":
        return "BLOCK"
    if lyapunov.partition == "X_H":
        return "HOLD"
    if lyapunov.partition == "X_A":
        return "ALLOW"
    return "HOLD"


def is_admissible(lyapunov: LyapunovResult) -> bool:
    return lyapunov.partition == "X_A" and lyapunov.is_stable
