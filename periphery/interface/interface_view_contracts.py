"""
Interface View Contracts — defines read-only view contracts for all interface components.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class InterfaceViewContract:
    component: str
    readonly: bool = True
    mutable: bool = False
    can_emit_act: bool = False
    can_write_memory: bool = False
    decision_authority: str = "KX108_ONLY"

    def validate(self) -> None:
        assert self.readonly is True
        assert self.mutable is False
        assert self.can_emit_act is False
        assert self.can_write_memory is False

    def to_dict(self) -> dict[str, Any]:
        return {
            "component": self.component,
            "readonly": self.readonly,
            "mutable": self.mutable,
            "can_emit_act": self.can_emit_act,
            "can_write_memory": self.can_write_memory,
            "decision_authority": self.decision_authority,
        }


BRODY_VIEW_CONTRACT = InterfaceViewContract("brody_view")
MEMORY_VIEW_CONTRACT = InterfaceViewContract("memory_view")
GRAPHITI_VIEW_CONTRACT = InterfaceViewContract("graphiti_view")
CONTEXT_VIEW_CONTRACT = InterfaceViewContract("context_view")
