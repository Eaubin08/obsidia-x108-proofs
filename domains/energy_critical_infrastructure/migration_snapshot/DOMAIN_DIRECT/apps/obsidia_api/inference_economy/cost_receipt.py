"""OIE V0.1 — CostReceipt + DomainMetrics: typed, JSON-serialisable cost units."""
from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import List, Optional

# ── Security constants (immutable; OIE is non-sovereign) ──────────────────────
READONLY: bool = True
DECISION_AUTHORITY: str = "KX108_ONLY"
EMITS_ACT: bool = False
KERNEL_MUTATION: bool = False
MEMORY_WRITE: bool = False
GRAPHITI_WRITE: bool = False
NEO4J_WRITE: bool = False


@dataclass
class DomainMetrics:
    """Per-domain business metrics attached to a CostReceipt (optional in V0.1)."""

    domain_name: str = ""
    domain_action_type: str = ""
    domain_risk_level: str = ""
    domain_reversibility: str = ""

    # Cost / perf
    domain_cost_eur_per_1m: float = 0.0
    domain_latency_ms: float = 0.0
    domain_internal_units: float = 0.0

    # Tooling
    domain_tools_used: List[str] = field(default_factory=list)
    domain_tools_skipped: List[str] = field(default_factory=list)

    # Inference avoided
    external_api_calls_avoided: int = 0
    llm_calls_avoided: int = 0
    human_review_avoided_estimate: float = 0.0

    # Decision counters
    hold_count: int = 0
    block_count: int = 0
    act_count: int = 0          # always 0 — OIE never emits ACT
    unknowns_count: int = 0
    contradictions_count: int = 0

    # Proof / replay
    proof_available: bool = False
    replay_available: bool = False

    # Business cost avoided
    business_cost_avoided_label: str = ""
    business_cost_avoided_estimate_eur: float = 0.0

    # Advantage ratio vs baseline (filled by meter)
    domain_savings_ratio: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "DomainMetrics":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class CostReceipt:
    # ── Identity ──────────────────────────────────────────────────────────────
    receipt_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    # ── Routing ───────────────────────────────────────────────────────────────
    layer: str = ""
    route: str = ""
    domain: str = ""
    action_type: str = ""

    # ── Measurement ───────────────────────────────────────────────────────────
    elapsed_ms: float = 0.0
    internal_units: float = 0.0
    modules_activated: List[str] = field(default_factory=list)
    modules_skipped: List[str] = field(default_factory=list)

    # ── Cost ──────────────────────────────────────────────────────────────────
    obsidia_cost_eur_per_1m: float = 0.0
    baseline_label: str = ""
    baseline_cost_eur_per_1m: float = 0.0
    savings_ratio: float = 0.0
    avoided_cost_eur_per_1m: float = 0.0

    # ── Governance (fixed; never writable from outside) ───────────────────────
    kernel_status: str = "ACTIVE"
    proof_or_replay_available: bool = False
    readonly: bool = READONLY
    decision_authority: str = DECISION_AUTHORITY
    emits_act: bool = EMITS_ACT
    kernel_mutation: bool = KERNEL_MUTATION
    memory_write: bool = MEMORY_WRITE
    graphiti_write: bool = GRAPHITI_WRITE
    neo4j_write: bool = NEO4J_WRITE

    # ── Domain metrics (optional — V0.1) ──────────────────────────────────────
    domain_metrics: Optional[DomainMetrics] = field(default=None)

    # ── Post-init guard: governance flags are immutable ───────────────────────
    def __post_init__(self) -> None:
        object.__setattr__(self, "readonly", READONLY)
        object.__setattr__(self, "decision_authority", DECISION_AUTHORITY)
        object.__setattr__(self, "emits_act", EMITS_ACT)
        object.__setattr__(self, "kernel_mutation", KERNEL_MUTATION)
        object.__setattr__(self, "memory_write", MEMORY_WRITE)
        object.__setattr__(self, "graphiti_write", GRAPHITI_WRITE)
        object.__setattr__(self, "neo4j_write", NEO4J_WRITE)

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: dict) -> "CostReceipt":
        filtered = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        if "domain_metrics" in filtered and isinstance(filtered["domain_metrics"], dict):
            filtered["domain_metrics"] = DomainMetrics.from_dict(filtered["domain_metrics"])
        return cls(**filtered)
