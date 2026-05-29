"""
Bus signal input model — F56.

Defines the Pydantic model for POST /bus/signal.
Never decides. Never writes. Never mutates.
"""
from __future__ import annotations

from enum import Enum
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class SignalType(str, Enum):
    audit_request = "audit_request"
    monitoring_probe = "monitoring_probe"
    operator_check = "operator_check"
    ci_signal = "ci_signal"
    security_scan = "security_scan"
    graphiti_event = "graphiti_event"
    sigma_signal = "sigma_signal"
    brody_context_update = "brody_context_update"
    route_probe = "route_probe"
    proof_probe = "proof_probe"
    unknown_signal = "unknown_signal"


class RiskHint(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class SignalInput(BaseModel):
    # Required fields
    signal_type: SignalType
    signal_origin: str

    # Optional identification
    signal_id: Optional[str] = None
    signal_timestamp: Optional[str] = None
    correlation_id: Optional[str] = None
    session_id: Optional[str] = None

    # Optional content — accepts string or any JSON-serializable value
    signal_payload: Optional[Any] = Field(None, description="Signal content — sanitized before exposure")
    operator_context: Optional[str] = Field(None, max_length=1024)
    declared_intent: Optional[str] = None
    evidence_refs: Optional[List[str]] = None

    # Optional routing hints — advisory only, never binding
    source_layer: Optional[str] = None
    target_layer: Optional[str] = None
    risk_hint: Optional[RiskHint] = None
