# runtime_wiring/engine_bridge/bridge_types.py
# P10B — Bridge dataclasses. Stdlib only. No apps/periphery imports.
# All instances are PREVIEW_ONLY. No runtime activation. KX108_ONLY.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

# ── Safety invariants ─────────────────────────────────────────────────────────
_REQUIRED_FALSE = (
    "runtime_active",
    "emits_act",
    "proof_claim",
    "engine_mutation",
    "apps_mutation",
    "periphery_mutation",
    "memory_write",
    "graph_write",
)
_REQUIRED_TRUE = ("readonly",)
_REQUIRED_KX108 = "KX108_ONLY"


def _validate_safety(obj: Any, cls_name: str) -> None:
    for field_name in _REQUIRED_FALSE:
        val = getattr(obj, field_name, None)
        if val is not False:
            raise ValueError(
                f"FAIL_CLOSED [{cls_name}]: {field_name} must be False, got {val!r}"
            )
    for field_name in _REQUIRED_TRUE:
        val = getattr(obj, field_name, None)
        if val is not True:
            raise ValueError(
                f"FAIL_CLOSED [{cls_name}]: {field_name} must be True, got {val!r}"
            )
    da = getattr(obj, "decision_authority", None)
    if da is not None and da != _REQUIRED_KX108:
        raise ValueError(
            f"FAIL_CLOSED [{cls_name}]: decision_authority must be {_REQUIRED_KX108!r}, got {da!r}"
        )


# ── EngineBridgeInput ─────────────────────────────────────────────────────────

@dataclass
class EngineBridgeInput:
    """Represents the dry-run routing result entering the bridge."""

    source_pipeline: str
    registry_entries_count: int
    families: List[str]
    context_only_decision: str
    critical_action_decision: str
    # Safety flags — always False on construction
    runtime_active: bool = False
    readonly: bool = True
    emits_act: bool = False
    proof_claim: bool = False
    engine_mutation: bool = False
    apps_mutation: bool = False
    periphery_mutation: bool = False
    memory_write: bool = False
    graph_write: bool = False
    decision_authority: str = "KX108_ONLY"

    def __post_init__(self) -> None:
        _validate_safety(self, "EngineBridgeInput")
        if self.context_only_decision != "ALLOW_CONTEXT_ONLY":
            raise ValueError(
                f"FAIL_CLOSED: context_only_decision must be ALLOW_CONTEXT_ONLY, got {self.context_only_decision!r}"
            )
        if self.critical_action_decision != "HOLD":
            raise ValueError(
                f"FAIL_CLOSED: critical_action_decision must be HOLD, got {self.critical_action_decision!r}"
            )


# ── EngineBridgeSafetyStatus ──────────────────────────────────────────────────

@dataclass
class EngineBridgeSafetyStatus:
    """Collected safety proof for a bridge operation."""

    zip_extraction: bool = False
    source_pack_import: bool = False
    runtime_active: bool = False
    readonly: bool = True
    emits_act: bool = False
    proof_claim: bool = False
    engine_mutation: bool = False
    apps_mutation: bool = False
    periphery_mutation: bool = False
    memory_write: bool = False
    graph_write: bool = False
    world_action: bool = False
    packages_created: bool = False
    decision_authority: str = "KX108_ONLY"

    def __post_init__(self) -> None:
        _validate_safety(self, "EngineBridgeSafetyStatus")
        for extra in ("zip_extraction", "source_pack_import", "world_action", "packages_created"):
            if getattr(self, extra) is not False:
                raise ValueError(f"FAIL_CLOSED [EngineBridgeSafetyStatus]: {extra} must be False")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "zip_extraction": self.zip_extraction,
            "source_pack_import": self.source_pack_import,
            "runtime_active": self.runtime_active,
            "readonly": self.readonly,
            "emits_act": self.emits_act,
            "proof_claim": self.proof_claim,
            "engine_mutation": self.engine_mutation,
            "apps_mutation": self.apps_mutation,
            "periphery_mutation": self.periphery_mutation,
            "memory_write": self.memory_write,
            "graph_write": self.graph_write,
            "world_action": self.world_action,
            "packages_created": self.packages_created,
            "decision_authority": self.decision_authority,
        }


# ── EngineBridgeOutput ────────────────────────────────────────────────────────

@dataclass
class EngineBridgeOutput:
    """Preview output produced by the bridge. Never activates the engine."""

    bridge_status: str
    source_pipeline: str
    registry_entries_count: int
    input_family_count: int
    context_packets_count: int
    context_only_decision: str
    critical_action_decision: str
    safety: EngineBridgeSafetyStatus
    notes: List[str] = field(default_factory=list)
    # Safety flags — always False
    runtime_active: bool = False
    readonly: bool = True
    emits_act: bool = False
    proof_claim: bool = False
    engine_mutation: bool = False
    apps_mutation: bool = False
    periphery_mutation: bool = False
    memory_write: bool = False
    graph_write: bool = False
    decision_authority: str = "KX108_ONLY"

    def __post_init__(self) -> None:
        _validate_safety(self, "EngineBridgeOutput")
        if self.bridge_status != "ENGINE_BRIDGE_PREVIEW_ONLY":
            raise ValueError(
                f"FAIL_CLOSED: bridge_status must be ENGINE_BRIDGE_PREVIEW_ONLY, got {self.bridge_status!r}"
            )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bridge_status": self.bridge_status,
            "source_pipeline": self.source_pipeline,
            "registry_entries_count": self.registry_entries_count,
            "input_family_count": self.input_family_count,
            "context_packets_count": self.context_packets_count,
            "context_only_decision": self.context_only_decision,
            "critical_action_decision": self.critical_action_decision,
            "runtime_active": self.runtime_active,
            "readonly": self.readonly,
            "emits_act": self.emits_act,
            "proof_claim": self.proof_claim,
            "engine_mutation": self.engine_mutation,
            "apps_mutation": self.apps_mutation,
            "periphery_mutation": self.periphery_mutation,
            "memory_write": self.memory_write,
            "graph_write": self.graph_write,
            "decision_authority": self.decision_authority,
            "notes": self.notes,
            "safety": self.safety.to_dict(),
        }


# ── EngineBridgePreview ───────────────────────────────────────────────────────

@dataclass
class EngineBridgePreview:
    """Top-level container for a complete P10B bridge preview run."""

    bridge_input: EngineBridgeInput
    bridge_output: EngineBridgeOutput
    api_payload_preview: Dict[str, Any] = field(default_factory=dict)

    def is_safe(self) -> bool:
        try:
            _validate_safety(self.bridge_input, "EngineBridgeInput(check)")
            _validate_safety(self.bridge_output, "EngineBridgeOutput(check)")
            _validate_safety(self.bridge_output.safety, "EngineBridgeSafetyStatus(check)")
            return True
        except ValueError:
            return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bridge_input": {
                "source_pipeline": self.bridge_input.source_pipeline,
                "registry_entries_count": self.bridge_input.registry_entries_count,
                "families": self.bridge_input.families,
                "context_only_decision": self.bridge_input.context_only_decision,
                "critical_action_decision": self.bridge_input.critical_action_decision,
                "decision_authority": self.bridge_input.decision_authority,
            },
            "bridge_output": self.bridge_output.to_dict(),
            "api_payload_preview": self.api_payload_preview,
        }
