# obsidia_kernel/contract.py
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional


class Decision(str, Enum):
    BLOCK = "BLOCK"
    HOLD  = "HOLD"
    ACT   = "ACT"


class IntentType(str, Enum):
    PROPOSE = "PROPOSE"
    ACTION  = "ACTION"


@dataclass
class Meta:
    request_id: str
    timestamp: str
    domain: str = "generic"   # generic|trading|bank|ecom|energy|agent
    mode: str = "proof"       # proof|simu|live
    agent_id: Optional[str] = None
    human_id: Optional[str] = None


@dataclass
class Intent:
    type: IntentType
    name: str
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Governance:
    irreversible: bool = False
    # internal knobs (optional)
    x108_enabled: bool = True
    x108_min_wait_s: int = 108
    x108_elapsed_s: int = 0
    theta_S: float = 0.25
    non_anticipation: bool = True


@dataclass
class Request:
    meta: Meta
    intent: Intent
    context: Dict[str, Any] = field(default_factory=dict)
    governance: Governance = field(default_factory=Governance)
    attachments: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HumanGate:
    required: bool = False
    type: Optional[str] = None
    prompt: Optional[str] = None
    deadline: Optional[str] = None


@dataclass
class Result:
    trace_id: str
    kernel_version: str
    decision: Decision
    reason_code: str
    reason_message: str
    artifacts_hash: str
    audit_path: List[str] = field(default_factory=list)

    required_human_gate: bool = False
    human_gate: Optional[HumanGate] = None

    metrics: Dict[str, Any] = field(default_factory=dict)

    # raw engine outputs (if available)
    ssr: Optional[str] = None
    engine_decision_raw: Optional[str] = None
    engine_registry_ok: Optional[bool] = None

    # enriched (internal spec, optional)
    acp_status: Optional[str] = None  # PASS | REFUSE_UNTIL_RESOLVED
    acp_ambiguity: Dict[str, Any] = field(default_factory=dict)
    hash_chain: List[str] = field(default_factory=list)
    replay_ref: Optional[str] = None
    artifact_files: List[str] = field(default_factory=list)


def result_to_dict(r: Result) -> Dict[str, Any]:
    d = asdict(r)
    d["decision"] = r.decision.value if isinstance(r.decision, Decision) else r.decision
    d["meta"] = {"trace_id": r.trace_id, "kernel_version": r.kernel_version, "artifacts_hash": r.artifacts_hash}
    # keep canonical top-level keys (avoid duplicating trace_id/kernel_version/artifacts_hash)
    d.pop("trace_id", None)
    d.pop("kernel_version", None)
    d.pop("artifacts_hash", None)
    return d
