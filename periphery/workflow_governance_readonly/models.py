from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
import hashlib
import json
import time

from .constants import DECISION_AUTHORITY, READONLY_FLAGS, PROOF_STATUS, MODULE_FAMILY


def stable_id(prefix: str, payload: Any) -> str:
    """Build deterministic-ish ids from canonical JSON payloads."""
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}_{digest}"


def now_ms() -> int:
    return int(time.time() * 1000)


@dataclass
class Boundary:
    """Readonly boundary block copied into every runtime artifact."""

    decision_authority: str = DECISION_AUTHORITY
    proof_status: str = PROOF_STATUS
    module_family: str = MODULE_FAMILY
    readonly: bool = True
    advisory_only: bool = True
    context_signal_only: bool = True
    allowed_to_decide: bool = False
    emits_act: bool = False
    emits_verdict: bool = False
    kernel_mutation: bool = False
    x108_mutation: bool = False
    workflow_decision: bool = False
    memory_decision: bool = False
    graphiti_decision: bool = False
    brody_decision: bool = False
    modules_execution: bool = False
    gates_execution: bool = False
    gates_decision: bool = False

    def as_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data.update(READONLY_FLAGS)
        data["decision_authority"] = DECISION_AUTHORITY
        data["proof_status"] = PROOF_STATUS
        data["module_family"] = MODULE_FAMILY
        return data


@dataclass
class WorkflowStep:
    step_id: str
    title: str
    description: str
    actor: str = "operator_or_agent"
    sequence_index: int = 0
    source_line: str = ""
    input_refs: List[str] = field(default_factory=list)
    output_refs: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    conditions: List[str] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)
    previous_steps: List[str] = field(default_factory=list)
    criticality: str = "low"
    criticality_score: float = 0.0
    risk_categories: List[str] = field(default_factory=list)
    irreversibility_signals: List[str] = field(default_factory=list)
    control_families: List[str] = field(default_factory=list)
    required_evidence: List[str] = field(default_factory=list)
    evidence_status: str = "requirements_only_missing_until_supplied"
    x108_review_required: bool = False
    candidate_only: bool = True
    boundary: Dict[str, Any] = field(default_factory=lambda: Boundary().as_dict())


@dataclass
class WorkflowEdge:
    source: str
    target: str
    edge_kind: str = "sequence"
    condition: str = "next_step"
    candidate_only: bool = True
    boundary: Dict[str, Any] = field(default_factory=lambda: Boundary().as_dict())


@dataclass
class WorkflowGraph:
    workflow_id: str
    title: str
    source_kind: str
    source_excerpt: str
    nodes: List[WorkflowStep]
    edges: List[WorkflowEdge]
    critical_steps: List[str]
    graph_kind: str = "workflow_graph_readonly_candidate"
    graph_version: str = "V5"
    graph_constraints: List[str] = field(default_factory=lambda: [
        "workflow_has_no_decision_authority",
        "workflow_has_no_runtime_execution_authority",
        "critical_candidates_require_external_x108_evaluation",
    ])
    boundary: Dict[str, Any] = field(default_factory=lambda: Boundary().as_dict())


@dataclass
class AgentSignal:
    agent_id: str
    signal_family: str
    status: str
    summary: str
    payload: Dict[str, Any]
    confidence: float = 0.0
    warnings: List[str] = field(default_factory=list)
    trace: List[str] = field(default_factory=list)
    role: str = "readonly_agent"
    cannot: List[str] = field(default_factory=lambda: [
        "decide",
        "execute",
        "mutate_kernel",
        "mutate_x108",
        "emit_verdict",
    ])
    boundary: Dict[str, Any] = field(default_factory=lambda: Boundary().as_dict())


@dataclass
class ObsidiaIR:
    ir_id: str
    source_workflow_id: str
    ir_kind: str
    intent: Dict[str, Any]
    steps: List[Dict[str, Any]]
    critical_action_candidates: List[Dict[str, Any]]
    required_evidence: List[str]
    os_projection: Dict[str, Any]
    authority: str = DECISION_AUTHORITY
    candidate_only: bool = True
    boundary: Dict[str, Any] = field(default_factory=lambda: Boundary().as_dict())


@dataclass
class ContextPacket:
    packet_id: str
    source_workflow_id: str
    source_ir_id: str
    packet_kind: str
    signals: List[Dict[str, Any]]
    workflow_graph: Dict[str, Any]
    obsidia_ir: Dict[str, Any]
    evidence_requirements: List[str]
    critical_action_summary: Dict[str, Any]
    trace_chain: List[str]
    replay_pointer: str
    packet_constraints: List[str] = field(default_factory=lambda: [
        "context_packet_is_not_a_decision",
        "context_packet_is_not_an_execution_request",
        "context_packet_is_for_x108_readonly_ingress_only",
    ])
    boundary: Dict[str, Any] = field(default_factory=lambda: Boundary().as_dict())


@dataclass
class X108ReadonlyIngressEnvelope:
    envelope_id: str
    source_packet_id: str
    ingress_kind: str
    purpose: str
    context_packet: Dict[str, Any]
    ingress_contract: Dict[str, Any]
    boundary: Dict[str, Any] = field(default_factory=lambda: Boundary().as_dict())
    x108_merge: bool = False
    x108_runtime_binding: bool = False
    kernel_binding: bool = False
    direct_runtime_call: bool = False
    candidate_only: bool = True


def to_dict(obj: Any) -> Dict[str, Any]:
    if hasattr(obj, "__dataclass_fields__"):
        return asdict(obj)
    if isinstance(obj, dict):
        return obj
    raise TypeError(f"Unsupported object type for to_dict: {type(obj)!r}")


def canonical_json(obj: Any) -> str:
    return json.dumps(to_dict(obj) if hasattr(obj, "__dataclass_fields__") else obj, ensure_ascii=False, sort_keys=True, indent=2)
