"""
Pydantic contracts for Obsidia API.
All responses carry readonly=True and decision_authority=KX108_ONLY.
"""
from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


# ── Shared base ──────────────────────────────────────────────────────────────

class SovereignBase(BaseModel):
    readonly: bool = True
    emits_act: bool = False
    memory_write: bool = False
    kernel_mutation: bool = False
    decision_authority: str = "KX108_ONLY"
    source: str = "REAL_BACKEND"


# ── Status ───────────────────────────────────────────────────────────────────

class StatusResponse(SovereignBase):
    status: str = "ok"
    version: str = "V5B"
    timestamp: str = ""
    tests_passing: int = 397
    kernel_status: str = "ACTIVE"
    periphery_loaded: bool = True


class X108StatusResponse(SovereignBase):
    kernel_id: str = "X108"
    kernel_status: str = "ACTIVE"
    mode: str = "READONLY"
    tests_passing: int = 397
    invariants: dict[str, Any] = Field(default_factory=dict)
    protected_files_intact: bool = True
    decision_authority: str = "KX108_ONLY"


# ── Brody ────────────────────────────────────────────────────────────────────

class BrodyChatRequest(BaseModel):
    message: str
    language: str = "fr"
    session_id: str = ""
    context_refs: list[str] = Field(default_factory=list)


class TranslationTraceData(BaseModel):
    trace_id: str = ""
    user_input: str = ""
    detected_language: str = "fr"
    response_language: str = "fr"
    os_trad_status: str = "PARSED"
    alphabet_units: list[dict[str, Any]] = Field(default_factory=list)
    ir_candidate: dict[str, Any] = Field(default_factory=dict)
    context_packet_id: str = ""
    os_reverse_projection: str = ""
    x108_boundary_status: str = "READONLY"
    readonly: bool = True
    allowed_to_decide: bool = False
    allowed_to_act: bool = False
    memory_write: bool = False
    kernel_mutation: bool = False


class ContextPacketData(BaseModel):
    packet_id: str = ""
    action_id: str = ""
    status: str = "READY"
    content_hash: str = ""
    signals: list[str] = Field(default_factory=list)
    can_decide: bool = False


class AuditEventData(BaseModel):
    event_id: str = ""
    type: str = "brody_response"
    timestamp: str = ""
    readonly: bool = True
    emits_act: bool = False


class BrodyChatResponse(SovereignBase):
    response_id: str = ""
    response_text: str = ""
    language: str = "fr"
    confidence: float = 0.7
    translation_trace: TranslationTraceData = Field(default_factory=TranslationTraceData)
    context_packet: ContextPacketData = Field(default_factory=ContextPacketData)
    x108_boundary: str = "READONLY"
    audit_event: AuditEventData = Field(default_factory=AuditEventData)


# ── Translation ───────────────────────────────────────────────────────────────

class TranslationRequest(BaseModel):
    text: str
    session_language: str = "fr"


class AlphabetUnit(BaseModel):
    symbol: str
    label: str
    role: str
    confidence: float
    source_span: str


class IRCandidateData(BaseModel):
    ir_id: str = ""
    intent_type: str = "general_query"
    entities: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)
    contradictions: list[str] = Field(default_factory=list)
    allowed_to_decide: bool = False
    allowed_to_act: bool = False
    memory_write: bool = False
    kernel_mutation: bool = False
    decision_authority: str = "KX108_ONLY"


class TranslationTraceResponse(SovereignBase):
    trace_id: str = ""
    user_input: str = ""
    detected_language: str = "fr"
    response_language: str = "fr"
    os_trad_status: str = "PARSED"
    alphabet_units: list[AlphabetUnit] = Field(default_factory=list)
    ir_candidate: IRCandidateData = Field(default_factory=IRCandidateData)
    context_packet_id: str = ""
    os_reverse_projection: str = ""
    x108_boundary_status: str = "READONLY"
    mode: str = "REAL_BACKEND"


# ── Context ──────────────────────────────────────────────────────────────────

class ContextFromMessageRequest(BaseModel):
    message: str
    language: str = "fr"
    session_id: str = ""


class ContextPacketResponse(SovereignBase):
    packet_id: str = ""
    action_id: str = ""
    status: str = "READY"
    content_hash: str = ""
    signals: list[str] = Field(default_factory=list)
    can_decide: bool = False
    query: str = ""
    context_items: list[str] = Field(default_factory=list)


# ── Memory ───────────────────────────────────────────────────────────────────

class MemoryCandidateItem(BaseModel):
    candidate_id: str
    source_id: str
    source_type: str
    content_hash: str
    content_summary: str
    status: str
    memory_write_allowed: bool = False
    auto_promotion_allowed: bool = False
    created_at: str = ""
    risk_flags: list[str] = Field(default_factory=list)


class MemoryResponse(SovereignBase):
    candidates: list[MemoryCandidateItem] = Field(default_factory=list)
    total: int = 0
    mode: str = "CANDIDATE_ONLY"
    auto_promotion: bool = False
    graphiti_write: bool = False


# ── Gencoin ──────────────────────────────────────────────────────────────────

class GencoinEntry(BaseModel):
    ledger_id: str = ""
    os3_ticket_id: str = ""
    gencoin_candidate: float = 0.0
    mint_allowed: bool = False
    timestamp: str = ""
    is_real_token: bool = False


class GencoinResponse(SovereignBase):
    entries: list[GencoinEntry] = Field(default_factory=list)
    total: int = 0
    is_real_token: bool = False
    post_proof_only: bool = True
    ledger_only: bool = True


# ── Blockchain ───────────────────────────────────────────────────────────────

class BlockchainStatusResponse(SovereignBase):
    gate_status: str = "READ_ONLY"
    real_chain_action_allowed: bool = False
    wallet_connected: bool = False
    dry_run_only: bool = True
    classified_actions: list[dict[str, Any]] = Field(default_factory=list)


# ── WorldCalls ───────────────────────────────────────────────────────────────

class WorldCallItem(BaseModel):
    action_id: str = ""
    dry_run_only: bool = True
    world_action_allowed: bool = False
    reason: str = "BACKEND_STUB"


class WorldCallsResponse(SovereignBase):
    calls: list[WorldCallItem] = Field(default_factory=list)
    dry_run_only: bool = True
    mode: str = "BACKEND_STUB"


# ── OS3 ──────────────────────────────────────────────────────────────────────

class OS3TicketItem(BaseModel):
    ticket_id: str = ""
    domain: str = "governance"
    x108_gate: str = "UNKNOWN"
    replay_status: str = "NOT_RUN"
    proof_valid: bool = False


class OS3Response(SovereignBase):
    tickets: list[OS3TicketItem] = Field(default_factory=list)
    mode: str = "BACKEND_STUB"
    proof_engine: str = "OS3_V1"


# ── Audit ────────────────────────────────────────────────────────────────────

class AuditItem(BaseModel):
    event_id: str = ""
    type: str = "governance_check"
    description: str = ""
    result: str = "OK"
    timestamp: str = ""


class AuditResponse(SovereignBase):
    events: list[AuditItem] = Field(default_factory=list)
    total: int = 0
    mode: str = "BACKEND_STUB"


# ── Graphiti proxy ────────────────────────────────────────────────────────────

class GraphitiStatusProxy(SovereignBase):
    graphiti_status: str = "FROZEN_READONLY"
    version: str = "v20"
    entity_count: int = 0
    run_id: str = ""
    proxy_source: str = "BACKEND_STUB"
