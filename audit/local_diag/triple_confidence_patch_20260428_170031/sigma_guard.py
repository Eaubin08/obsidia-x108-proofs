from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass

from .contracts import CanonicalDecisionEnvelope, DomainAggregate, Severity, X108Gate, SourceTag


@dataclass
class GuardConfig:
    min_confidence_allow: float = 0.72
    hold_confidence_floor: float = 0.45
    max_unknowns_before_hold: int = 1
    max_contradictions_before_block: int = 2


class GuardX108:
    def __init__(self, config: GuardConfig | None = None) -> None:
        self.config = config or GuardConfig()

    def decide(self, aggregate: DomainAggregate) -> CanonicalDecisionEnvelope:
        contradiction_count = len(aggregate.contradictions)
        unknown_count = len(aggregate.unknowns)
        risk_count = len(aggregate.risk_flags)

        if contradiction_count >= self.config.max_contradictions_before_block or "FRAUD_PATTERN" in aggregate.risk_flags:
            gate = X108Gate.BLOCK
            reason = "CONTRADICTION_THRESHOLD_REACHED"
            severity = Severity.S4
        elif unknown_count > self.config.max_unknowns_before_hold or aggregate.confidence < self.config.hold_confidence_floor:
            gate = X108Gate.HOLD
            reason = "UNKNOWNS_OR_CONFIDENCE_LOW"
            severity = Severity.S2
        elif risk_count >= 2 and aggregate.confidence < self.config.min_confidence_allow:
            gate = X108Gate.HOLD
            reason = "RISK_FLAGS_REQUIRE_DELAY"
            severity = Severity.S2
        else:
            gate = X108Gate.ALLOW
            reason = "GUARD_ALLOW"
            severity = Severity.S0 if aggregate.confidence >= self.config.min_confidence_allow else Severity.S1

        decision_id = f"{aggregate.domain.value}-{uuid.uuid4().hex[:12]}"
        trace_id = str(uuid.uuid4())
        ticket_required = gate == X108Gate.ALLOW
        ticket_id = uuid.uuid4().hex[:16] if ticket_required else None
        attestation_ref = hashlib.sha256("|".join(aggregate.evidence_refs).encode("utf-8")).hexdigest()[:24] if aggregate.evidence_refs else None

        return CanonicalDecisionEnvelope(
            domain=aggregate.domain.value,
            market_verdict=aggregate.market_verdict,
            confidence=aggregate.confidence,
            contradictions=aggregate.contradictions,
            unknowns=aggregate.unknowns,
            risk_flags=aggregate.risk_flags,
            x108_gate=gate.value,
            reason_code=reason,
            severity=severity.value,
            decision_id=decision_id,
            trace_id=trace_id,
            ticket_required=ticket_required,
            ticket_id=ticket_id,
            attestation_ref=attestation_ref,
            source=SourceTag.CANONICAL_FRAMEWORK.value,
            evidence_refs=aggregate.evidence_refs,
            metrics=aggregate.extra_metrics,
            raw_engine={
                "domain": aggregate.domain.value,
                "agent_votes": [v.agent_id for v in aggregate.agent_votes],
                "vote_count": len(aggregate.agent_votes),
            },
        )
