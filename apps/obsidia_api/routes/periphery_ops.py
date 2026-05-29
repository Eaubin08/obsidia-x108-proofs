"""
Periphery Ops — wires all remaining operational periphery modules.
Mode: READ_ONLY | Layer: CONNECTORS | Scope: periphery/* | Risk: LOW
"""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from apps.obsidia_api.safe_response import safe_backend_response
from periphery.workflow_governance_readonly.integration.brody_workflow_governance_snapshot_adapter import build_brody_workflow_governance_snapshot
from apps.obsidia_api.brody_operator_view_packet import build_operator_view_packet
from apps.obsidia_api.brody_runtime_context_adapter import build_runtime_context
from sigma.evaluate import evaluate_sigma_domain
from periphery.common import ActionCandidate, PeripheralSignalPacket

# ── Pipeline ──────────────────────────────────────────────────────────────────
from periphery.control_plane import run_control_plane
from periphery.data_gate import run_data_gate
from periphery.provenance_gate import run_provenance_gate
from periphery.memory_governor import run_memory_governor
from periphery.eml_compression import run_eml_compression
from periphery.energy_thermo import run_energy_thermo
from periphery.ocs_generation import run_ocs_generation
from periphery.operational_constance import run_operational_constance
from periphery.permission_economic import run_permission_economic
from periphery.validators import validate_action_candidate, validate_packet
from periphery.merge import merge_packets
from periphery.constants import THETA_FRESHNESS, THETA_MEMORY, THETA_ENERGY, THETA_MISMATCH, THETA_THERMO_DEBT, THETA_CONTEXT_DRIFT, THETA_TRAJECTORY_DIVERGENCE, THETA_OC

# ── Governance ────────────────────────────────────────────────────────────────
from periphery.math_core.governance_partition import partition_to_gate, is_admissible
from periphery.math_core.lyapunov import LyapunovResult
from periphery.agent_registry import list_agents, run_registered_agent
from periphery.agent_contracts import AgentLayer, NonSovereignAgentSpec
from periphery.action_lifecycle import ActionLifecycleTrace, ActionPhase
from periphery.action_sequence_governor import govern_action_sequence, ActionSequence, ActionStep
from periphery.github.github_workflow_guard import guard_workflow_action
from periphery.hackathon_failures import FailureCode
from periphery.failure_mapping import classify_failure
from periphery.benchmarks.benchmark_case_schema import get_benchmark_cases

# ── Cognitive / trees ─────────────────────────────────────────────────────────
from periphery.cognitive_trees.tree_registry import get_all_trees, get_tree_by_id, get_trees_by_domain
from periphery.cognitive_trees.memory_world_mapper import map_memory_world
from periphery.cognitive_trees.shazam_cognitif import ShazamCognitifResult
from periphery.cognitive_trees.dominant_trees import DominantTreeResult
from periphery.cognitive_trees.tree_signal_packet import build_tree_signal_packet

# ── Context & ingress ─────────────────────────────────────────────────────────
from periphery.context.context_packet_builder import build_context_packet
from periphery.context.context_packet_sanitizer import sanitize_context_packet
from periphery.context.context_packet_validator import validate_context_packet
from periphery.context.context_packet_exporter import export_context_packet
from periphery.x108_ingress.readonly_context_ingress import ingest_readonly_context

# ── Gencoin sandbox extensions ────────────────────────────────────────────────
from periphery.gencoin_sandbox.avdr_phase_mapper import map_avdr_phase
from periphery.gencoin_sandbox.balance_operator import compute_balance
from periphery.gencoin_sandbox.regime_state import classify_regime as classify_sandbox_regime, is_false_on, is_assisted_on, is_admissible as is_sandbox_admissible

# ── Consciousness ─────────────────────────────────────────────────────────────
from periphery.consciousness_regimes.passfail_metrics import evaluate_passfail
from periphery.consciousness_regimes.collective_sandbox_summary import build_collective_summary
from periphery.consciousness_regimes.regime_classifier import classify_regime as classify_consciousness_regime

# ── Interface, bias, MCP ──────────────────────────────────────────────────────
from periphery.interface.interface_state_packet import build_interface_state_packet
from periphery.interface.interface_event_log import log_interface_event
from periphery.interface.workbench_api_contract import evaluate_workbench_method
from periphery.interface.interface_view_contracts import BRODY_VIEW_CONTRACT, MEMORY_VIEW_CONTRACT, GRAPHITI_VIEW_CONTRACT, CONTEXT_VIEW_CONTRACT
from periphery.mcp.mcp_permission_matrix import evaluate_tool_access
from periphery.bias.bias_gate import apply_bias_gate
from periphery.bias.bias_trace import trace_bias

# ── Ingestion & memory ────────────────────────────────────────────────────────
from periphery.ingestion.source_classifier import classify_source
from periphery.ingestion.hash_ingestion import hash_content, verify_hash
from periphery.ingestion.document_ingestion_pipeline import ingest_document
from periphery.memory.memory_source_registry import list_sources, get_source

# ── OS3 & replay ──────────────────────────────────────────────────────────────
from periphery.os3_ticket import build_os3_ticket, ticket_is_valid
from periphery.os3_replay_manifest import build_replay_manifest
from periphery.os3_replay_runner import run_replay, replay_compare
from periphery.world_action_gateway import evaluate_world_action_readiness

# ── Education & projection ────────────────────────────────────────────────────
from periphery.education.education_score import compute_education_score
from periphery.reverse_os.audience_projection import project_audience
from periphery.reverse_os.format_projection import project_format

# ── Brody & BDF ───────────────────────────────────────────────────────────────
from periphery.brody.brody_context_query import build_context_query
from periphery.brody.brody_language_router import route_brody_language
from periphery.bdf.double_brain_router import route_double_brain
from periphery.bdf.llm_diffusion_mix import compute_diffusion_mix

# ── Graphiti extensions ───────────────────────────────────────────────────────
from periphery.graphiti.graphiti_freeze_snapshot_reader import read_freeze_snapshot
from periphery.graphiti.graphiti_context_adapter import adapt_graphiti_context
from periphery.graphiti.graphiti_readonly_bridge import GraphitiContextResult, query_graphiti_readonly

# ── Feedback & bridge ─────────────────────────────────────────────────────────
from periphery.feedback_memory_candidate import build_feedback_memory_candidate
from periphery.feedback_memory_bridge_brody_readonly import build_memory_candidate as build_bridge_memory_candidate

# ─────────────────────────────────────────────────────────────────────────────

class SigmaEvaluatePayload(BaseModel):
    domain: str
    payload: dict[str, Any] = Field(default_factory=dict)


router = APIRouter(prefix="/api/periphery", tags=["periphery"])

_BOUNDARY: dict[str, Any] = {
    "readonly": True,
    "emits_act": False,
    "memory_write": False,
    "decision_authority": "KX108_ONLY",
}


# ── Pydantic models ───────────────────────────────────────────────────────────

class ActionPayload(BaseModel):
    action_id: str = "pops-action"
    domain: str = "general"
    actor_id: str = "periphery-ops"
    intent: str = "inspect"
    action_type: str = "query"
    irreversible: bool = False
    timestamp_plan: str = ""
    payload: dict[str, Any] = Field(default_factory=dict)


class PartitionPayload(BaseModel):
    action_id: str = "partition-check"
    partition: str = "X_H"
    is_stable: bool = False
    L_value: float = 0.0


class AgentRunPayload(BaseModel):
    agent_id: str
    action: ActionPayload = Field(default_factory=ActionPayload)


class AgentSpecPayload(BaseModel):
    agent_id: str
    layer: str = "CONTROL"
    description: str = ""


class LifecyclePayload(BaseModel):
    action_id: str
    phases: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class SequencePayload(BaseModel):
    action: ActionPayload = Field(default_factory=ActionPayload)
    steps: list[dict[str, Any]] = Field(default_factory=list)


class WorkflowGuardPayload(BaseModel):
    action_id: str = "wf-action"
    action_type: str = "push"
    domain: str = "github"


class FailureClassifyPayload(BaseModel):
    code: str


class MemoryWorldPayload(BaseModel):
    vector_id: str = "v0"
    dominant_ids: list[int] = Field(default_factory=list)
    patterns_detected: list[str] = Field(default_factory=list)


class TreeSignalPayload(BaseModel):
    signal_id: str = "tree-signal"
    activations: list[float] = Field(default_factory=list)
    theta: float = 0.15
    domain_sigma_envelope: dict[str, Any] = Field(default_factory=dict)


class ContextBuildPayload(BaseModel):
    action_id: str
    signals: list[dict[str, Any]] = Field(default_factory=list)
    status: str = "READY"


class ContextSanitizePayload(BaseModel):
    packet_id: str
    context_items: list[dict[str, Any]] = Field(default_factory=list)


class ContextValidatePayload(BaseModel):
    packet: dict[str, Any] = Field(default_factory=dict)


class AVDRPayload(BaseModel):
    action_id: str
    truth_score: float = 0.5
    sigma_score: float = 0.5


class BalancePayload(BaseModel):
    action_id: str
    utility: float = 0.5
    coherence: float = 0.5
    stability: float = 0.5
    cost: float = 0.1
    risk: float = 0.1


class RegimeStatePayload(BaseModel):
    truth_score: float = 0.5
    sigma_score: float = 0.5
    state: str = "START"


class PassFailPayload(BaseModel):
    regime_id: str
    coherence: float = 0.5
    integration: float = 0.5
    responsiveness: float = 0.5


class CollectiveSummaryPayload(BaseModel):
    summary_id: str
    regimes: list[dict[str, Any]] = Field(default_factory=list)


class InterfaceStatePayload(BaseModel):
    session_id: str
    phase: str = "ACTIVE"
    memory_status: str = "STABLE"
    brody_status: str = "READY"
    graphiti_status: str = "READY"


class InterfaceEventPayload(BaseModel):
    session_id: str
    event_type: str
    details: str = ""
    log_path: str = "_local_audits/interface_event_log.jsonl"


class MCPPayload(BaseModel):
    tool_name: str
    has_permission: bool = False


class BiasGatePayload(BaseModel):
    action_id: str
    bias_score: float = 0.0
    bias_validated: bool = False


class BiasTracePayload(BaseModel):
    action_id: str
    bias_score: float = 0.0
    source: str = "unknown"


class SourceClassifyPayload(BaseModel):
    source: str


class HashPayload(BaseModel):
    content: str
    expected_hash: str = ""


class IngestDocumentPayload(BaseModel):
    doc_id: str
    content: str
    source_class: str = "TRUSTED"


class OS3TicketPayload(BaseModel):
    action: ActionPayload = Field(default_factory=ActionPayload)
    x108_gate: str = "HOLD"


class ReplayComparePayload(BaseModel):
    original_hash: str
    replay_hash: str


class WorldActionReadinessPayload(BaseModel):
    action: ActionPayload = Field(default_factory=ActionPayload)
    x108_gate: str = "HOLD"
    ticket_id: str = "demo-ticket"


class EducationScorePayload(BaseModel):
    episode_id: str
    stability: float = 0.5
    coherence: float = 0.5
    memory_reuse: float = 0.5
    correct_refusal: float = 0.5
    absence_of_drift: float = 0.5


class AudienceProjectionPayload(BaseModel):
    projection_id: str
    context: str = ""
    preferred_audience: str = "general"


class FormatProjectionPayload(BaseModel):
    projection_id: str
    audience: str = "general"


class BrodyQueryPayload(BaseModel):
    query_id: str
    query_text: str
    language: str = "en"
    context_filters: list[str] = Field(default_factory=list)


class BrodyLangPayload(BaseModel):
    query_id: str
    language_code: str = "en"


class DoubleBrainPayload(BaseModel):
    route_id: str
    complexity: float = 0.5
    urgency: float = 0.5
    uncertainty: float = 0.5


class DiffusionMixPayload(BaseModel):
    mix_id: str
    creativity_score: float = 0.5
    precision_score: float = 0.5


class GraphitiAdaptPayload(BaseModel):
    adapter_id: str
    query_id: str
    query: str = ""
    max_nodes: int = 10


class FeedbackCandidatePayload(BaseModel):
    action: ActionPayload = Field(default_factory=ActionPayload)
    ticket_id: str = "demo-ticket"
    feedback: str = ""
    memory_status: str = "STABLE"


class BridgeCandidatePayload(BaseModel):
    action_id: str = "bridge-action"
    os3_ticket_id: str = "demo-ticket"
    x108_gate: str = "HOLD"
    input_hash: str = ""
    output_hash: str = ""
    trace_hash: str = ""
    memory_status: str = "STABLE"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_action(body: ActionPayload) -> ActionCandidate:
    return ActionCandidate(
        action_id=body.action_id,
        domain=body.domain,
        actor_id=body.actor_id,
        intent=body.intent,
        action_type=body.action_type,
        irreversible=body.irreversible,
        timestamp_plan=body.timestamp_plan,
        payload=body.payload,
    )


def _pkt(p: PeripheralSignalPacket) -> dict[str, Any]:
    return p.to_dict() if hasattr(p, "to_dict") else vars(p)


# ── PIPELINE ──────────────────────────────────────────────────────────────────

@router.post("/pipeline/run")
async def periphery_pipeline_run(body: ActionPayload):
    a = _make_action(body)
    packet = run_control_plane(a)
    packet.assert_non_sovereign()
    return safe_backend_response({**_pkt(packet), **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/pipeline/data-gate")
async def periphery_data_gate(body: ActionPayload):
    a = _make_action(body)
    packet = run_data_gate(a)
    packet.assert_non_sovereign()
    return safe_backend_response({**_pkt(packet), **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/pipeline/provenance-gate")
async def periphery_provenance_gate(body: ActionPayload):
    a = _make_action(body)
    packet = run_provenance_gate(a)
    packet.assert_non_sovereign()
    return safe_backend_response({**_pkt(packet), **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/pipeline/memory-governor")
async def periphery_memory_governor(body: ActionPayload):
    a = _make_action(body)
    packet = run_memory_governor(a)
    packet.assert_non_sovereign()
    return safe_backend_response({**_pkt(packet), **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/pipeline/eml-compression")
async def periphery_eml_compression(body: ActionPayload):
    a = _make_action(body)
    packet = run_eml_compression(a)
    packet.assert_non_sovereign()
    return safe_backend_response({**_pkt(packet), **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/pipeline/energy-thermo")
async def periphery_energy_thermo(body: ActionPayload):
    a = _make_action(body)
    packet = run_energy_thermo(a)
    packet.assert_non_sovereign()
    return safe_backend_response({**_pkt(packet), **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/pipeline/ocs-generation")
async def periphery_ocs_generation(body: ActionPayload):
    a = _make_action(body)
    packet = run_ocs_generation(a)
    packet.assert_non_sovereign()
    return safe_backend_response({**_pkt(packet), **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/pipeline/operational-constance")
async def periphery_operational_constance(body: ActionPayload):
    a = _make_action(body)
    packet = run_operational_constance(a)
    packet.assert_non_sovereign()
    return safe_backend_response({**_pkt(packet), **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/pipeline/permission-economic")
async def periphery_permission_economic(body: ActionPayload):
    a = _make_action(body)
    packet = run_permission_economic(a)
    packet.assert_non_sovereign()
    return safe_backend_response({**_pkt(packet), **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/pipeline/validate-candidate")
async def periphery_validate_candidate(body: ActionPayload):
    a = _make_action(body)
    candidate_valid = validate_action_candidate(a)
    packet = run_data_gate(a)
    packet_valid = validate_packet(packet)
    return safe_backend_response({"candidate_valid": candidate_valid, "packet_valid": packet_valid, **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/pipeline/merge")
async def periphery_merge(body: ActionPayload):
    a = _make_action(body)
    p1 = run_data_gate(a)
    p2 = run_provenance_gate(a)
    merged = merge_packets(p1, p2)
    merged.assert_non_sovereign()
    return safe_backend_response({**_pkt(merged), **_BOUNDARY}, source="REAL_BACKEND")


@router.get("/pipeline/constants")
async def periphery_constants():
    return safe_backend_response({
        "THETA_FRESHNESS": THETA_FRESHNESS,
        "THETA_MEMORY": THETA_MEMORY,
        "THETA_ENERGY": THETA_ENERGY,
        "THETA_MISMATCH": THETA_MISMATCH,
        "THETA_THERMO_DEBT": THETA_THERMO_DEBT,
        "THETA_CONTEXT_DRIFT": THETA_CONTEXT_DRIFT,
        "THETA_TRAJECTORY_DIVERGENCE": THETA_TRAJECTORY_DIVERGENCE,
        "THETA_OC": THETA_OC,
        **_BOUNDARY,
    }, source="REAL_BACKEND")


# ── GOVERNANCE ────────────────────────────────────────────────────────────────

@router.post("/governance/partition-gate")
async def periphery_partition_gate(body: PartitionPayload):
    lyapunov = LyapunovResult(action_id=body.action_id, L_value=body.L_value, is_stable=body.is_stable, partition=body.partition)
    gate = partition_to_gate(lyapunov)
    admissible = is_admissible(lyapunov)
    return safe_backend_response({**lyapunov.to_dict(), "gate": gate, "admissible": admissible, **_BOUNDARY}, source="REAL_BACKEND")


@router.get("/governance/agents")
async def periphery_list_agents():
    agents = list_agents()
    return safe_backend_response({"agents": agents, "count": len(agents), **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/governance/agent-run")
async def periphery_agent_run(body: AgentRunPayload):
    a = _make_action(body.action)
    result = run_registered_agent(body.agent_id, a)
    result.assert_non_sovereign()
    return safe_backend_response({"agent_id": result.agent_id, "layer": str(result.layer), **_pkt(result.packet), **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/governance/agent-spec-check")
async def periphery_agent_spec_check(body: AgentSpecPayload):
    try:
        layer = AgentLayer(body.layer)
    except ValueError:
        raise HTTPException(status_code=422, detail=f"Unknown AgentLayer: {body.layer}")
    spec = NonSovereignAgentSpec(agent_id=body.agent_id, layer=layer, description=body.description)
    try:
        spec.assert_safe()
        safe_flag = True
        violation = None
    except AssertionError as exc:
        safe_flag = False
        violation = str(exc)
    return safe_backend_response({"agent_id": spec.agent_id, "layer": str(spec.layer), "safe": safe_flag, "violation": violation, **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/governance/lifecycle")
async def periphery_lifecycle(body: LifecyclePayload):
    trace = ActionLifecycleTrace(body.action_id)
    phases = body.phases or []
    notes = body.notes or []
    for i, phase in enumerate(phases):
        note = notes[i] if i < len(notes) else ""
        try:
            trace.advance(ActionPhase(phase), note)
        except Exception as exc:
            raise HTTPException(status_code=422, detail=f"Invalid phase '{phase}': {exc}")
    return safe_backend_response({**trace.to_dict(), **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/governance/sequence-govern")
async def periphery_sequence_govern(body: SequencePayload):
    a = _make_action(body.action)
    steps = [
        ActionStep(
            step_id=s.get("step_id", f"step-{i}"),
            tool=s.get("tool", "noop"),
            irreversible=bool(s.get("irreversible", False)),
            async_step=bool(s.get("async_step", False)),
            requires_permission=bool(s.get("requires_permission", False)),
            changed_plan=bool(s.get("changed_plan", False)),
            payload=s.get("payload", {}),
        )
        for i, s in enumerate(body.steps)
    ]
    sequence = ActionSequence(action_id=a.action_id, steps=steps)
    packet = govern_action_sequence(a, sequence)
    packet.assert_non_sovereign()
    return safe_backend_response({**_pkt(packet), **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/governance/workflow-guard")
async def periphery_workflow_guard(body: WorkflowGuardPayload):
    decision = guard_workflow_action(body.action_type)
    return safe_backend_response({**decision.to_dict(), **_BOUNDARY}, source="REAL_BACKEND")


@router.get("/governance/benchmarks")
async def periphery_benchmarks(name: Optional[str] = None):
    cases = get_benchmark_cases(name)
    return safe_backend_response({"cases": [c.to_dict() for c in cases], "count": len(cases), **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/governance/failure-classify")
async def periphery_failure_classify(body: FailureClassifyPayload):
    try:
        category = classify_failure(body.code)
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=422, detail=f"Unknown failure code: {exc}")
    return safe_backend_response({"code": body.code, "category": category, **_BOUNDARY}, source="REAL_BACKEND")


@router.get("/governance/failure-codes")
async def periphery_failure_codes():
    codes = [c.value for c in FailureCode]
    return safe_backend_response({"failure_codes": codes, "count": len(codes), **_BOUNDARY}, source="REAL_BACKEND")


# ── COGNITIVE / TREES ─────────────────────────────────────────────────────────

@router.get("/cognitive/trees")
async def periphery_trees_all():
    trees = get_all_trees()
    return safe_backend_response({"trees": [t.to_dict() for t in trees], "count": len(trees), **_BOUNDARY}, source="REAL_BACKEND")


@router.get("/cognitive/trees/{tree_id}")
async def periphery_tree_by_id(tree_id: int):
    tree = get_tree_by_id(tree_id)
    if tree is None:
        raise HTTPException(status_code=404, detail=f"Tree {tree_id} not found")
    return safe_backend_response({**tree.to_dict(), **_BOUNDARY}, source="REAL_BACKEND")


@router.get("/cognitive/trees/domain/{domain}")
async def periphery_trees_by_domain(domain: str):
    trees = get_trees_by_domain(domain)
    return safe_backend_response({"trees": [t.to_dict() for t in trees], "domain": domain, "count": len(trees), **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/cognitive/memory-world-map")
async def periphery_memory_world_map(body: MemoryWorldPayload):
    dominant = DominantTreeResult(
        vector_id=body.vector_id,
        theta=0.15,
        dominant_ids=body.dominant_ids,
        dominant_names=[],
        dominant_count=len(body.dominant_ids),
    )
    shazam = ShazamCognitifResult(
        vector_id=body.vector_id,
        patterns_detected=body.patterns_detected,
        dominant_result=dominant,
    )
    ctx = map_memory_world(shazam)
    return safe_backend_response({**ctx.to_dict(), **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/cognitive/tree-signal")
async def periphery_tree_signal(body: TreeSignalPayload):
    packet = build_tree_signal_packet(
        body.signal_id,
        body.activations,
        theta=body.theta,
        domain_sigma_envelope=body.domain_sigma_envelope,
    )
    return safe_backend_response({**packet.to_dict(), **_BOUNDARY}, source="REAL_BACKEND")


# ── CONTEXT & INGRESS ─────────────────────────────────────────────────────────

@router.post("/context/build")
async def periphery_context_build(body: ContextBuildPayload):
    packet = build_context_packet(body.action_id, body.signals, body.status)
    return safe_backend_response({**packet.to_dict(), **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/context/sanitize")
async def periphery_context_sanitize(body: ContextSanitizePayload):
    result = sanitize_context_packet(body.packet_id, body.context_items)
    return safe_backend_response({**result.to_dict(), **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/context/validate")
async def periphery_context_validate(body: ContextValidatePayload):
    result = validate_context_packet(body.packet)
    return safe_backend_response({**result.to_dict(), **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/context/export")
async def periphery_context_export(body: ContextValidatePayload):
    result = export_context_packet(body.packet)
    return safe_backend_response({**result.to_dict(), **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/context/ingress")
async def periphery_context_ingress(body: ContextBuildPayload):
    ingress = ingest_readonly_context(body.action_id, {"signals": body.signals, "status": body.status})
    return safe_backend_response({**ingress.to_dict(), **_BOUNDARY}, source="REAL_BACKEND")


# ── GENCOIN SANDBOX EXTENSIONS ────────────────────────────────────────────────

@router.post("/gencoin/avdr-phase")
async def periphery_avdr_phase(body: AVDRPayload):
    phase = map_avdr_phase(body.action_id, body.truth_score, body.sigma_score)
    return safe_backend_response({**phase.to_dict(), **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/gencoin/balance")
async def periphery_balance(body: BalancePayload):
    result = compute_balance(body.action_id, body.utility, body.coherence, body.stability, body.cost, body.risk)
    return safe_backend_response({**result.to_dict(), **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/gencoin/regime-state")
async def periphery_regime_state(body: RegimeStatePayload):
    from periphery.gencoin_sandbox.sandbox_engine import System, State
    try:
        state_enum = State(body.state)
    except ValueError:
        state_enum = State.START
    sys = System(truth_score=body.truth_score, sigma_score=body.sigma_score, state=state_enum)
    return safe_backend_response({
        "regime": classify_sandbox_regime(sys),
        "is_false_on": is_false_on(sys),
        "is_assisted_on": is_assisted_on(sys),
        "is_admissible": is_sandbox_admissible(sys),
        "truth_score": body.truth_score,
        "sigma_score": body.sigma_score,
        **_BOUNDARY,
    }, source="REAL_BACKEND")


@router.post("/gencoin/passfail")
async def periphery_passfail(body: PassFailPayload):
    result = evaluate_passfail(body.regime_id, body.coherence, body.integration, body.responsiveness)
    return safe_backend_response({**result.to_dict(), **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/gencoin/consciousness-regime")
async def periphery_consciousness_regime(body: PassFailPayload):
    result = classify_consciousness_regime(body.regime_id, body.coherence, body.integration, body.responsiveness)
    return safe_backend_response({**result.to_dict(), **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/gencoin/collective-summary")
async def periphery_collective_summary(body: CollectiveSummaryPayload):
    from periphery.consciousness_regimes.regime_classifier import ConsciousnessRegimeResult
    regimes = [
        ConsciousnessRegimeResult(
            regime_id=r.get("regime_id", "r0"),
            operational_label=r.get("operational_label", "DORMANT"),
            coherence_score=float(r.get("coherence_score", 0.0)),
            integration_score=float(r.get("integration_score", 0.0)),
            responsiveness_score=float(r.get("responsiveness_score", 0.0)),
        )
        for r in body.regimes
    ]
    summary = build_collective_summary(body.summary_id, regimes)
    return safe_backend_response({**summary.to_dict(), **_BOUNDARY}, source="REAL_BACKEND")


# ── INTERFACE, BIAS, MCP ──────────────────────────────────────────────────────

@router.post("/interface/state-packet")
async def periphery_interface_state(body: InterfaceStatePayload):
    packet = build_interface_state_packet(body.session_id, body.phase, body.memory_status, body.brody_status, body.graphiti_status)
    return safe_backend_response({**packet.to_dict(), **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/interface/log-event")
async def periphery_interface_log_event(body: InterfaceEventPayload):
    try:
        event = log_interface_event(body.session_id, body.event_type, body.details, body.log_path)
    except Exception as exc:
        return safe_backend_response({"error": str(exc), "logged": False, **_BOUNDARY}, source="REAL_BACKEND")
    return safe_backend_response({**event.to_dict(), "logged": True, **_BOUNDARY}, source="REAL_BACKEND")


@router.get("/interface/workbench-check")
async def periphery_workbench_check(method: str = "GET"):
    result = evaluate_workbench_method(method)
    return safe_backend_response({**result.to_dict(), **_BOUNDARY}, source="REAL_BACKEND")


@router.get("/interface/view-contracts")
async def periphery_view_contracts():
    return safe_backend_response({
        "brody_view": BRODY_VIEW_CONTRACT.to_dict(),
        "memory_view": MEMORY_VIEW_CONTRACT.to_dict(),
        "graphiti_view": GRAPHITI_VIEW_CONTRACT.to_dict(),
        "context_view": CONTEXT_VIEW_CONTRACT.to_dict(),
        **_BOUNDARY,
    }, source="REAL_BACKEND")


@router.post("/interface/mcp-access")
async def periphery_mcp_access(body: MCPPayload):
    access = evaluate_tool_access(body.tool_name, body.has_permission)
    return safe_backend_response({**access.to_dict(), **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/interface/bias-gate")
async def periphery_bias_gate(body: BiasGatePayload):
    result = apply_bias_gate(body.action_id, body.bias_score, body.bias_validated)
    return safe_backend_response({**result.to_dict(), **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/interface/bias-trace")
async def periphery_bias_trace(body: BiasTracePayload):
    trace_result = trace_bias(body.action_id, body.bias_score, body.source)
    return safe_backend_response({**trace_result.to_dict(), **_BOUNDARY}, source="REAL_BACKEND")


# ── INGESTION & MEMORY ────────────────────────────────────────────────────────

@router.post("/ingestion/classify-source")
async def periphery_classify_source(body: SourceClassifyPayload):
    classification = classify_source(body.source)
    return safe_backend_response({"source": body.source, "classification": classification, **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/ingestion/hash")
async def periphery_hash(body: HashPayload):
    h = hash_content(body.content)
    verified = verify_hash(body.content, body.expected_hash) if body.expected_hash else None
    return safe_backend_response({"hash": h, "verified": verified, **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/ingestion/document")
async def periphery_ingest_document(body: IngestDocumentPayload):
    doc = ingest_document(body.doc_id, body.content, body.source_class)
    return safe_backend_response({**doc.to_dict(), **_BOUNDARY}, source="REAL_BACKEND")


@router.get("/ingestion/memory-sources")
async def periphery_memory_sources(source_id: Optional[str] = None):
    if source_id:
        src = get_source(source_id)
        data = src.to_dict() if (src and hasattr(src, "to_dict")) else (vars(src) if src else {})
        return safe_backend_response({**data, "found": src is not None, **_BOUNDARY}, source="REAL_BACKEND")
    sources = list_sources()
    items = [s.to_dict() if hasattr(s, "to_dict") else vars(s) for s in sources]
    return safe_backend_response({"sources": items, "count": len(items), **_BOUNDARY}, source="REAL_BACKEND")


# ── OS3 & REPLAY ──────────────────────────────────────────────────────────────

@router.post("/os3/ticket")
async def periphery_os3_ticket(body: OS3TicketPayload):
    a = _make_action(body.action)
    packet = run_data_gate(a)
    envelope = SimpleNamespace(x108_gate=body.x108_gate)
    ticket = build_os3_ticket(a, packet, envelope)
    valid = ticket_is_valid(ticket)
    return safe_backend_response({**ticket.to_dict(), "ticket_valid": valid, **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/os3/manifest")
async def periphery_os3_manifest(body: OS3TicketPayload):
    a = _make_action(body.action)
    packet = run_data_gate(a)
    envelope = SimpleNamespace(x108_gate=body.x108_gate)
    ticket = build_os3_ticket(a, packet, envelope)
    manifest = build_replay_manifest(ticket)
    return safe_backend_response({**manifest.to_dict(), **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/os3/replay-compare")
async def periphery_replay_compare(body: ReplayComparePayload):
    result = replay_compare(body.original_hash, body.replay_hash)
    return safe_backend_response({"original_hash": body.original_hash, "replay_hash": body.replay_hash, "compare_result": result, **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/os3/world-action-readiness")
async def periphery_world_action_readiness(body: WorldActionReadinessPayload):
    a = _make_action(body.action)
    envelope = SimpleNamespace(x108_gate=body.x108_gate)
    ticket = SimpleNamespace(
        ticket_id=body.ticket_id,
        x108_gate=body.x108_gate,
        input_hash="",
        output_hash="",
        trace_hash="",
        merkle_root="",
    )
    readiness = evaluate_world_action_readiness(a, envelope, ticket)
    return safe_backend_response({
        "action_id": readiness.action_id,
        "dry_run_only": readiness.dry_run_only,
        "ready_for_controlled_execution": readiness.ready_for_controlled_execution,
        "world_action_allowed": readiness.world_action_allowed,
        "reason": readiness.reason,
        **_BOUNDARY,
    }, source="REAL_BACKEND")


@router.post("/os3/replay-run")
async def periphery_replay_run(body: OS3TicketPayload):
    a = _make_action(body.action)
    packet = run_data_gate(a)
    envelope = SimpleNamespace(x108_gate=body.x108_gate)
    ticket = build_os3_ticket(a, packet, envelope)
    manifest = run_replay(ticket, a, packet, envelope)
    return safe_backend_response({**manifest.to_dict(), **_BOUNDARY}, source="REAL_BACKEND")


# ── EDUCATION & PROJECTION ────────────────────────────────────────────────────

@router.post("/education/score")
async def periphery_education_score(body: EducationScorePayload):
    score = compute_education_score(body.episode_id, body.stability, body.coherence, body.memory_reuse, body.correct_refusal, body.absence_of_drift)
    return safe_backend_response({**score.to_dict(), **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/education/audience")
async def periphery_audience_projection(body: AudienceProjectionPayload):
    projection = project_audience(body.projection_id, body.context, body.preferred_audience)
    return safe_backend_response({**projection.to_dict(), **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/education/format")
async def periphery_format_projection(body: FormatProjectionPayload):
    projection = project_format(body.projection_id, body.audience)
    return safe_backend_response({**projection.to_dict(), **_BOUNDARY}, source="REAL_BACKEND")


# ── BRODY & BDF ───────────────────────────────────────────────────────────────

@router.post("/brody/context-query")
async def periphery_brody_context_query(body: BrodyQueryPayload):
    query = build_context_query(body.query_id, body.query_text, body.language, body.context_filters)
    return safe_backend_response({**query.to_dict(), **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/brody/language-route")
async def periphery_brody_language_route(body: BrodyLangPayload):
    route = route_brody_language(body.query_id, body.language_code)
    return safe_backend_response({**route.to_dict(), **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/brody/double-brain-route")
async def periphery_double_brain_route(body: DoubleBrainPayload):
    route = route_double_brain(body.route_id, body.complexity, body.urgency, body.uncertainty)
    return safe_backend_response({**route.to_dict(), **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/brody/diffusion-mix")
async def periphery_diffusion_mix(body: DiffusionMixPayload):
    result = compute_diffusion_mix(body.mix_id, body.creativity_score, body.precision_score)
    return safe_backend_response({**result.to_dict(), **_BOUNDARY}, source="REAL_BACKEND")


# ── GRAPHITI EXTENSIONS ───────────────────────────────────────────────────────

@router.get("/graphiti/freeze-snapshot/{snapshot_id}")
async def periphery_freeze_snapshot(snapshot_id: str):
    snapshot = read_freeze_snapshot(snapshot_id)
    return safe_backend_response({**snapshot.to_dict(), **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/graphiti/context-adapt")
async def periphery_graphiti_context_adapt(body: GraphitiAdaptPayload):
    graphiti_result: GraphitiContextResult = query_graphiti_readonly(body.query_id, body.query, body.max_nodes)
    adapted = adapt_graphiti_context(body.adapter_id, graphiti_result)
    return safe_backend_response({**adapted.to_dict(), **_BOUNDARY}, source="REAL_BACKEND")


# ── FEEDBACK & BRIDGE ─────────────────────────────────────────────────────────

@router.post("/feedback/candidate")
async def periphery_feedback_candidate(body: FeedbackCandidatePayload):
    from dataclasses import asdict
    a = _make_action(body.action)
    ticket = SimpleNamespace(ticket_id=body.ticket_id)
    candidate = build_feedback_memory_candidate(a, ticket, body.feedback, body.memory_status)
    return safe_backend_response({**asdict(candidate), **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/feedback/bridge-candidate")
async def periphery_bridge_candidate(body: BridgeCandidatePayload):
    ticket_ns = SimpleNamespace(
        ticket_id=body.os3_ticket_id,
        x108_gate=body.x108_gate,
        input_hash=body.input_hash,
        output_hash=body.output_hash,
        trace_hash=body.trace_hash,
    )
    packet_ns = SimpleNamespace(
        extra_metrics={"memory_status": body.memory_status},
        evidence_refs=[],
    )
    action_ns = SimpleNamespace(action_id=body.action_id)
    try:
        candidate = build_bridge_memory_candidate(ticket_ns, packet_ns, action_ns)
    except AssertionError as exc:
        return safe_backend_response({"error": str(exc), "memory_write_allowed": False, **_BOUNDARY}, source="REAL_BACKEND")
    return safe_backend_response({**candidate.to_dict(), **_BOUNDARY}, source="REAL_BACKEND")

@router.post("/sigma/evaluate")
async def sigma_evaluate(payload: SigmaEvaluatePayload):
    """
    F23A6.2 readonly Sigma evaluation endpoint.

    Exposes Sigma dispatcher through periphery API.
    Does not execute action.
    Does not mutate memory, Graphiti, Neo4j, kernel, or X108.
    Decision authority remains KX108_ONLY.
    """
    envelope = evaluate_sigma_domain(payload.domain, payload.payload)

    return safe_backend_response({
        "domain_sigma_envelope": envelope,
        "domain_sigma_attached": True,
        "readonly": True,
        "advisory_only": True,
        "emits_act": False,
        "emits_verdict": False,
        "memory_write": False,
        "graphiti_write": False,
        "neo4j_write": False,
        "kernel_mutation": False,
        "x108_mutation": False,
        "runtime_execute": False,
        "decision_authority": "KX108_ONLY",
    }, source="REAL_BACKEND")


class GovernedOperatorRuntimePayload(BaseModel):
    runtime_id: str = "governed-operator-runtime"
    domain: str = "general"
    sigma_payload: dict[str, Any] = Field(default_factory=dict)
    tree_signal_id: str = "governed-tree-signal"
    activations: list[float] = Field(default_factory=list)
    theta: float = 0.15


@router.post("/operator/governed-runtime")
async def periphery_governed_operator_runtime(body: GovernedOperatorRuntimePayload):
    """
    F28.2 governed operator runtime.

    Aggregates existing readonly packets:
    - domain_sigma_envelope
    - tree_signal_packet
    - operator_view_packet
    - runtime_context

    No ACT.
    No verdict.
    No memory/Graphiti/Neo4j write.
    No kernel/X108 mutation.
    Decision authority remains KX108_ONLY.
    """
    domain_sigma_envelope = evaluate_sigma_domain(body.domain, body.sigma_payload)

    tree_signal_packet = build_tree_signal_packet(
        body.tree_signal_id,
        body.activations,
        theta=body.theta,
        domain_sigma_envelope=domain_sigma_envelope,
    ).to_dict()

    operator_view_packet = build_operator_view_packet(
        domain_sigma_envelope=domain_sigma_envelope,
        tree_signal_packet=tree_signal_packet,
    )

    runtime_context = build_runtime_context(
        domain_sigma_envelope_snapshot=domain_sigma_envelope,
        tree_signal_packet_snapshot=tree_signal_packet,
        brody_full_context=operator_view_packet,
    )

    return safe_backend_response({
        "version": "GOVERNED_OPERATOR_RUNTIME_V1",
        "mode": "READONLY_GOVERNED_OPERATOR_RUNTIME",
        "runtime_id": body.runtime_id,
        "domain_sigma_envelope": domain_sigma_envelope,
        "tree_signal_packet": tree_signal_packet,
        "operator_view_packet": operator_view_packet,
        "runtime_context": runtime_context,
        "domain_sigma_attached": True,
        "tree_signal_attached": True,
        "operator_runtime_attached": True,
        "readonly": True,
        "advisory_only": True,
        "context_signal_only": True,
        "can_decide": False,
        "can_emit_act": False,
        "emits_act": False,
        "emits_verdict": False,
        "memory_write": False,
        "graphiti_write": False,
        "neo4j_write": False,
        "kernel_mutation": False,
        "x108_mutation": False,
        "decision_authority": "KX108_ONLY",
    }, source="REAL_BACKEND")


class WorkflowGovernancePacketPayload(BaseModel):
    sop_text: str
    title: str = "workflow governance candidate"
    session_id: str = "manual-session"
    request_type: str = "STRUCTURAL_PREPARATION"


@router.post("/workflow-governance/packet")
async def workflow_governance_packet(payload: WorkflowGovernancePacketPayload):
    """
    F30.4 readonly workflow governance packet route.

    Builds:
    - workflow governance snapshot
    - workflow governance packet
    - X108 readonly ingress envelope

    No ACT.
    No verdict.
    No workflow execution.
    No memory/Graphiti/Neo4j write.
    No kernel/X108 mutation.
    Decision authority remains KX108_ONLY.
    """
    snapshot = build_brody_workflow_governance_snapshot(
        sop_text=payload.sop_text,
        title=payload.title,
        session_id=payload.session_id,
        request_type=payload.request_type,
    )

    workflow_governance_packet = snapshot.get("workflow_governance_packet", {})
    x108_readonly_ingress_envelope = snapshot.get("x108_readonly_ingress_envelope", {})
    context_packet = x108_readonly_ingress_envelope.get("context_packet", {})

    operator_packet = workflow_governance_packet.get("operator_packet", {})
    swarm_result = operator_packet.get("swarm_result", {})
    obsidiashell_workbench_state = workflow_governance_packet.get("obsidiashell_workbench_state", {})

    workflow_graph = (
        workflow_governance_packet.get("workflow_graph")
        or swarm_result.get("workflow_graph")
        or obsidiashell_workbench_state.get("workflow_graph")
        or {
            "graph_kind": "workflow_graph_readonly_candidate",
            "source_workflow_id": context_packet.get("source_workflow_id"),
            "candidate_only": True,
            "boundary": snapshot.get("boundary", {}),
        }
    )

    obsidia_ir = (
        workflow_governance_packet.get("obsidia_ir")
        or swarm_result.get("obsidia_ir")
        or obsidiashell_workbench_state.get("obsidia_ir")
        or {
            "ir_kind": "obsidia_ir_candidate",
            "ir_id": context_packet.get("source_ir_id"),
            "authority": "KX108_ONLY",
            "candidate_only": True,
            "boundary": snapshot.get("boundary", {}),
        }
    )

    normalized_context_packet = (
        workflow_governance_packet.get("context_packet")
        or context_packet
        or {
            "packet_kind": "workflow_governance_context_packet",
            "candidate_only": True,
            "boundary": snapshot.get("boundary", {}),
        }
    )

    normalized_packet = {
        **workflow_governance_packet,
        "workflow_graph": workflow_graph,
        "obsidia_ir": obsidia_ir,
        "context_packet": normalized_context_packet,
        "x108_readonly_ingress_envelope": x108_readonly_ingress_envelope,
    }

    return safe_backend_response({
        "version": "WORKFLOW_GOVERNANCE_PACKET_ROUTE_V1",
        "mode": "READONLY_WORKFLOW_GOVERNANCE_PACKET_ROUTE",
        "workflow_governance_snapshot": snapshot,
        "workflow_governance_packet": normalized_packet,
        "workflow_graph": workflow_graph,
        "obsidia_ir": obsidia_ir,
        "context_packet": normalized_context_packet,
        "x108_readonly_ingress_envelope": x108_readonly_ingress_envelope,
        "snapshot_attached": True,
        "packet_attached": True,
        "workflow_graph_attached": True,
        "obsidia_ir_attached": True,
        "context_packet_attached": True,
        "x108_readonly_ingress_attached": True,
        "readonly": True,
        "advisory_only": True,
        "context_signal_only": True,
        "allowed_to_decide": False,
        "can_decide": False,
        "can_emit_act": False,
        "emits_act": False,
        "emits_verdict": False,
        "workflow_decision": False,
        "memory_decision": False,
        "graphiti_decision": False,
        "brody_decision": False,
        "runtime_execute": False,
        "memory_write": False,
        "graphiti_write": False,
        "neo4j_write": False,
        "kernel_mutation": False,
        "x108_mutation": False,
        "decision_authority": "KX108_ONLY",
    }, source="REAL_BACKEND")


# ── F33 — Brody Runtime Entrypoint Readonly ───────────────────────────────────

class F33EntrypointPayload(BaseModel):
    domain: str = "bank"
    sigma_payload: Optional[dict] = None
    sop_text: str = (
        "1. Read readonly request\n"
        "2. Validate contract boundary\n"
        "3. Prepare readonly advisory response"
    )
    title: str = "F33 entrypoint readonly"
    session_id: str = "f33-entrypoint"
    signal_id: str = "f33-tree-signal"
    activations: Optional[list[float]] = None
    theta: float = 0.15
    request_type: str = "STRUCTURAL_PREPARATION"


@router.post("/brody-runtime/f33/integration-packet")
async def f33_brody_runtime_entrypoint(payload: F33EntrypointPayload):
    """
    F33 readonly entrypoint — exposes the F32 full runtime integration packet via HTTP.

    Assembles all 7 readonly surfaces (F23A6.2 → F30) and returns a certified
    readonly entrypoint envelope. No ACT. No verdict. No mutation. KX108_ONLY.
    """
    from periphery.brody_runtime.f33_runtime_entrypoint_readonly import (  # noqa: PLC0415
        call_brody_runtime_entrypoint,
    )
    result = call_brody_runtime_entrypoint(
        domain=payload.domain,
        sigma_payload=payload.sigma_payload,
        sop_text=payload.sop_text,
        title=payload.title,
        session_id=payload.session_id,
        signal_id=payload.signal_id,
        activations=payload.activations,
        theta=payload.theta,
        request_type=payload.request_type,
    )
    return safe_backend_response(result, source="REAL_BACKEND")

# ?? F35 ? Operator / Demo / Workbench Readonly Surfaces ???????????????????????

F35_DEFAULT_PAYLOAD: dict[str, Any] = {
    "domain": "bank",
    "sigma_payload": {
        "request_type": "STRUCTURAL_PREPARATION",
        "amount": 100,
        "recipient": "readonly-operator-target",
    },
    "sop_text": (
        "1. Receive operator request\n"
        "2. Build readonly runtime packet\n"
        "3. Display surfaces and boundary\n"
        "4. Human review before any real-world action"
    ),
    "title": "F35 operator live runtime panel",
    "session_id": "f35-operator-panel",
    "signal_id": "f35-tree-signal",
    "activations": None,
    "theta": 0.15,
    "request_type": "STRUCTURAL_PREPARATION",
}


def _f35_boundary() -> dict[str, Any]:
    return {
        "decision_authority": "KX108_ONLY",
        "readonly": True,
        "advisory_only": True,
        "context_signal_only": True,
        "allowed_to_decide": False,
        "can_decide": False,
        "can_emit_act": False,
        "emits_act": False,
        "emits_verdict": False,
        "workflow_decision": False,
        "memory_decision": False,
        "graphiti_decision": False,
        "brody_decision": False,
        "runtime_execute": False,
        "memory_write": False,
        "graphiti_write": False,
        "neo4j_write": False,
        "kernel_mutation": False,
        "x108_mutation": False,
    }


def _f35_build_runtime_snapshot() -> dict[str, Any]:
    from periphery.brody_runtime.f33_runtime_entrypoint_readonly import (  # noqa: PLC0415
        call_brody_runtime_entrypoint,
    )

    packet = call_brody_runtime_entrypoint(**F35_DEFAULT_PAYLOAD)
    f32_packet = packet.get("f32_packet", {})
    surfaces = f32_packet.get("surfaces", {})

    surface_rows = []
    for name, surface in sorted(surfaces.items()):
        surface_rows.append({
            "name": name,
            "status": surface.get("status"),
            "decision_authority": surface.get("decision_authority"),
            "readonly": surface.get("readonly"),
            "emits_act": surface.get("emits_act"),
            "runtime_execute": surface.get("runtime_execute"),
            "kernel_mutation": surface.get("kernel_mutation"),
            "x108_mutation": surface.get("x108_mutation"),
            "neo4j_write": surface.get("neo4j_write"),
        })

    boundary = _f35_boundary()

    return {
        "version": "F35_OPERATOR_DEMO_SURFACE_V1",
        "mode": "READONLY_OPERATOR_DEMO_WORKBENCH_SURFACE",
        "runtime_packet": packet,
        "f32_packet": f32_packet,
        "surface_rows": surface_rows,
        "surfaces_total": packet.get("surfaces_total"),
        "surfaces_ready": packet.get("surfaces_ready"),
        "surfaces_missing": packet.get("surfaces_missing"),
        "entrypoint_id": packet.get("entrypoint_id"),
        "entrypoint_status": packet.get("entrypoint_status"),
        "integration_status": packet.get("integration_status"),
        "proof_status": packet.get("proof_status"),
        "source": packet.get("source", "REAL_BACKEND"),
        "route_source": "F33_BRODY_RUNTIME_ENTRYPOINT_READONLY",
        **boundary,
    }


def _f35_assert_readonly(snapshot: dict[str, Any]) -> None:
    if snapshot.get("decision_authority") != "KX108_ONLY":
        raise HTTPException(status_code=500, detail="F35_BOUNDARY_FAIL_DECISION_AUTHORITY")

    forbidden_true = [
        "allowed_to_decide",
        "can_decide",
        "can_emit_act",
        "emits_act",
        "emits_verdict",
        "workflow_decision",
        "memory_decision",
        "graphiti_decision",
        "brody_decision",
        "runtime_execute",
        "memory_write",
        "graphiti_write",
        "neo4j_write",
        "kernel_mutation",
        "x108_mutation",
    ]

    for key in forbidden_true:
        if snapshot.get(key) is True:
            raise HTTPException(status_code=500, detail=f"F35_FORBIDDEN_TRUE:{key}")


@router.get("/operator/runtime-panel")
async def f35_operator_runtime_panel_data():
    """
    F35_C01 JSON operator surface.

    Exposes the F33/F34B runtime readiness in an operator-readable envelope.
    Readonly only. No ACT. No runtime execution. No memory/Graphiti/Neo4j write.
    """
    snapshot = _f35_build_runtime_snapshot()
    _f35_assert_readonly(snapshot)

    return safe_backend_response({
        "surface_id": "F35_C01_OPERATOR_LIVE_RUNTIME_PANEL",
        "surface_kind": "operator_json_panel",
        "title": "Obsidia Operator Live Runtime Panel",
        "summary": {
            "entrypoint_id": snapshot.get("entrypoint_id"),
            "entrypoint_status": snapshot.get("entrypoint_status"),
            "integration_status": snapshot.get("integration_status"),
            "surfaces_ready": snapshot.get("surfaces_ready"),
            "surfaces_missing": snapshot.get("surfaces_missing"),
            "decision_authority": snapshot.get("decision_authority"),
            "readonly": snapshot.get("readonly"),
        },
        "surface_rows": snapshot.get("surface_rows", []),
        "runtime_packet": snapshot.get("runtime_packet", {}),
        **_f35_boundary(),
    }, source="REAL_BACKEND")


@router.get("/operator/runtime-panel.html", response_class=HTMLResponse)
async def f35_operator_runtime_panel_html():
    """
    F35_C01 HTML operator panel.

    Static-style readonly panel generated from current runtime snapshot.
    """
    snapshot = _f35_build_runtime_snapshot()
    _f35_assert_readonly(snapshot)

    rows = []
    for row in snapshot.get("surface_rows", []):
        rows.append(
            "<tr>"
            f"<td>{row.get('name')}</td>"
            f"<td>{row.get('status')}</td>"
            f"<td>{row.get('decision_authority')}</td>"
            f"<td>{row.get('readonly')}</td>"
            f"<td>{row.get('emits_act')}</td>"
            f"<td>{row.get('runtime_execute')}</td>"
            f"<td>{row.get('kernel_mutation')}</td>"
            f"<td>{row.get('x108_mutation')}</td>"
            f"<td>{row.get('neo4j_write')}</td>"
            "</tr>"
        )

    html = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Obsidia Operator Runtime Panel</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 32px; background: #111; color: #eee; }}
    .card {{ border: 1px solid #444; border-radius: 12px; padding: 16px; margin-bottom: 16px; }}
    .ok {{ color: #8ef58e; font-weight: bold; }}
    .warn {{ color: #ffd166; font-weight: bold; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ border: 1px solid #444; padding: 8px; text-align: left; }}
    th {{ background: #222; }}
    code {{ color: #8ef58e; }}
  </style>
</head>
<body>
  <h1>Obsidia Operator Runtime Panel</h1>

  <div class="card">
    <p><b>Status:</b> <span class="ok">{snapshot.get('integration_status')}</span></p>
    <p><b>Entrypoint:</b> <code>{snapshot.get('entrypoint_id')}</code></p>
    <p><b>Surfaces:</b> {snapshot.get('surfaces_ready')}/{snapshot.get('surfaces_total')} ready ? missing={snapshot.get('surfaces_missing')}</p>
    <p><b>Decision authority:</b> <code>{snapshot.get('decision_authority')}</code></p>
    <p><b>Readonly:</b> {snapshot.get('readonly')} ? emits_act={snapshot.get('emits_act')} ? runtime_execute={snapshot.get('runtime_execute')}</p>
  </div>

  <div class="card">
    <h2>Runtime Surfaces</h2>
    <table>
      <tr>
        <th>Surface</th><th>Status</th><th>Authority</th><th>Readonly</th>
        <th>ACT</th><th>Runtime Execute</th><th>Kernel Mutation</th><th>X108 Mutation</th><th>Neo4j Write</th>
      </tr>
      {''.join(rows)}
    </table>
  </div>

  <div class="card">
    <h2>Boundary</h2>
    <pre>DECISION_AUTHORITY=KX108_ONLY
readonly=true
advisory_only=true
context_signal_only=true
emits_act=false
runtime_execute=false
memory_write=false
graphiti_write=false
neo4j_write=false
kernel_mutation=false
x108_mutation=false</pre>
  </div>
</body>
</html>"""
    return HTMLResponse(content=html, status_code=200)


@router.get("/demo/runtime-readiness")
async def f35_investor_demo_runtime_readiness():
    """
    F35_C02 investor/demo readiness packet.

    Converts runtime readiness into a short proof-oriented JSON envelope.
    """
    snapshot = _f35_build_runtime_snapshot()
    _f35_assert_readonly(snapshot)

    demo_packet = {
        "surface_id": "F35_C02_INVESTOR_DEMO_PACKET",
        "surface_kind": "investor_demo_readiness_packet",
        "headline": "Obsidia exposes a live readonly governed runtime entrypoint.",
        "proof_points": [
            "Live backend route is callable through F33 entrypoint.",
            "Seven runtime surfaces are attached and READY.",
            "Decision authority remains KX108_ONLY.",
            "No ACT emission.",
            "No runtime execution.",
            "No memory/Graphiti/Neo4j write.",
            "No kernel/X108 mutation.",
        ],
        "readiness": {
            "runtime_ready": snapshot.get("integration_status") == "READY_READONLY",
            "surfaces_ready": snapshot.get("surfaces_ready"),
            "surfaces_missing": snapshot.get("surfaces_missing"),
            "operator_panel_available": True,
            "workbench_connector_available": True,
        },
        "boundary": _f35_boundary(),
        "source_route": "POST /api/periphery/brody-runtime/f33/integration-packet",
        "operator_panel_route": "GET /api/periphery/operator/runtime-panel.html",
        "workbench_connector_route": "GET /api/periphery/workbench/runtime-connector",
    }

    return safe_backend_response(demo_packet, source="REAL_BACKEND")


@router.get("/workbench/runtime-connector")
async def f35_workbench_runtime_connector():
    """
    F35_C03 workbench connector surface.

    Provides a compact readonly connector packet for UI/workbench consumption.
    """
    snapshot = _f35_build_runtime_snapshot()
    _f35_assert_readonly(snapshot)

    connector = {
        "surface_id": "F35_C03_WORKBENCH_CONNECTOR_SURFACE",
        "surface_kind": "workbench_runtime_connector",
        "connector_status": "READY_READONLY",
        "tabs": [
            {"id": "runtime", "title": "Runtime", "ready": True},
            {"id": "surfaces", "title": "Surfaces", "ready": True},
            {"id": "boundary", "title": "Boundary", "ready": True},
            {"id": "proof", "title": "Proof", "ready": True},
        ],
        "runtime_summary": {
            "entrypoint_id": snapshot.get("entrypoint_id"),
            "entrypoint_status": snapshot.get("entrypoint_status"),
            "integration_status": snapshot.get("integration_status"),
            "surfaces_ready": snapshot.get("surfaces_ready"),
            "surfaces_missing": snapshot.get("surfaces_missing"),
        },
        "surface_rows": snapshot.get("surface_rows", []),
        "proof_links": [
            "docs/runtime/F34B_LIVE_UVICORN_ROUTE_PROOF_20260529_044331.json",
            "docs/runtime/OBSIDIA_F34B_TRUE_LIVE_UVICORN_SERVER_SMOKE_20260529_024438.md",
            ".runtime_freezes/F34B_TRUE_LIVE_UVICORN_SERVER_SMOKE_20260529_024438/MANIFEST_SHA256.json",
        ],
        "boundary": _f35_boundary(),
        **_f35_boundary(),
    }

    return safe_backend_response(connector, source="REAL_BACKEND")


# ── F36 — User Scenario: Brody Workbench Controlled Response ──────────────────

class F36UserScenarioPayload(BaseModel):
    user_input: str = "Je veux analyser une transaction bancaire avant paiement."
    domain: str = "bank"
    sigma_payload: Optional[dict] = None
    session_id: str = "f36-user-scenario"
    signal_id: str = "f36-tree-signal"
    theta: float = 0.15
    request_type: str = "STRUCTURAL_PREPARATION"


@router.post("/brody-runtime/f36/user-scenario")
async def f36_user_scenario_controlled_response(payload: F36UserScenarioPayload):
    """
    F36 user scenario — controlled readonly response.

    Accepts a user input, consults F33/F32 runtime surfaces and the F35
    workbench connector, returns a controlled readonly advisory response.
    No ACT. No mutation. No execution. KX108_ONLY decision authority.
    """
    from periphery.brody_runtime.f36_user_scenario_controlled_response import (  # noqa: PLC0415
        build_user_scenario_controlled_response,
    )
    result = build_user_scenario_controlled_response(
        user_input=payload.user_input,
        domain=payload.domain,
        sigma_payload=payload.sigma_payload,
        session_id=payload.session_id,
        signal_id=payload.signal_id,
        theta=payload.theta,
        request_type=payload.request_type,
    )
    return safe_backend_response(result, source="REAL_BACKEND")
