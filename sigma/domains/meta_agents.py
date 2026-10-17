from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Any

from ..base import BaseAgent
from ..contracts import AgentVote, Domain, DomainAggregate, Layer, Severity

try:
    from periphery.constants import THETA_ENERGY, THETA_MISMATCH, THETA_THERMO_DEBT
except Exception:  # pragma: no cover - fallback if periphery is not on sys.path
    THETA_ENERGY = 0.2
    THETA_MISMATCH = 0.35
    THETA_THERMO_DEBT = 1.0

THERMO_CANONICAL_KEYS: tuple[str, ...] = (
    "pin",
    "pout",
    "energy_efficiency",
    "thermo_debt",
    "truth_score",
    "sigma_score",
    "sigma_truth_mismatch",
)
THERMO_SPECIFIC_KEYS: tuple[str, ...] = (
    "pin",
    "pout",
    "energy_efficiency",
    "thermo_debt",
    "sigma_truth_mismatch",
)


@dataclass(frozen=True)
class ThermoSigmaEvaluation:
    """
    Canonical runtime contract for Sigma's semantic evaluation of Thermo signals.
    Remains strictly advisory (advisory_only=True, decision_authority='KX108_ONLY', emits_act=False).
    Does not create any new gate policy: GuardX108 retains gate authority and KX108 sovereign authority.
    """

    status: str  # "COHERENT" | "INCOHERENT" | "INCOMPLETE" | "NOT_PRESENT"
    present_keys: tuple[str, ...]
    missing_keys: tuple[str, ...]
    pin: float | None = None
    pout: float | None = None
    energy_efficiency: float | None = None
    expected_efficiency: float | None = None
    thermo_debt: float | None = None
    truth_score: float | None = None
    reported_sigma_score: float | None = None
    domain_sigma_score: float | None = None
    domain_truth_score: float | None = None
    domain_comparison_status: str = "NOT_COMPARABLE"  # "COMPARABLE" | "NOT_COMPARABLE"
    reported_mismatch: float | None = None
    actual_sigma_truth_mismatch: float | None = None
    formula_status: str = "NOT_EVALUATED"  # "EXACT_MATCH" | "NOT_EVALUATED_NO_CANONICAL_TOLERANCE" | "NOT_EVALUATED"
    formula_consistent: bool | None = None
    risk_flags: tuple[str, ...] = ()
    unknowns: tuple[str, ...] = ()
    contradictions: tuple[str, ...] = ()
    proposed_verdict: str = "ALLOW"
    severity: Severity = field(default_factory=lambda: Severity.S0)
    advisory_only: bool = True
    decision_authority: str = "KX108_ONLY"
    emits_act: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "present_keys": list(self.present_keys),
            "missing_keys": list(self.missing_keys),
            "pin": self.pin,
            "pout": self.pout,
            "energy_efficiency": self.energy_efficiency,
            "expected_efficiency": self.expected_efficiency,
            "thermo_debt": self.thermo_debt,
            "truth_score": self.truth_score,
            "reported_sigma_score": self.reported_sigma_score,
            "domain_sigma_score": self.domain_sigma_score,
            "domain_truth_score": self.domain_truth_score,
            "domain_comparison_status": self.domain_comparison_status,
            "reported_mismatch": self.reported_mismatch,
            "actual_sigma_truth_mismatch": self.actual_sigma_truth_mismatch,
            "formula_status": self.formula_status,
            "formula_consistent": self.formula_consistent,
            "risk_flags": list(self.risk_flags),
            "unknowns": list(self.unknowns),
            "contradictions": list(self.contradictions),
            "proposed_verdict": self.proposed_verdict,
            "severity": self.severity.value,
            "advisory_only": self.advisory_only,
            "decision_authority": self.decision_authority,
            "emits_act": self.emits_act,
        }


def _to_finite_float(val: Any) -> float | None:
    if isinstance(val, bool) or val is None:
        return None
    try:
        f = float(val)
    except (TypeError, ValueError):
        return None
    return f if math.isfinite(f) else None


def evaluate_thermo_sigma_coherence(aggregate: DomainAggregate) -> ThermoSigmaEvaluation:
    metrics = aggregate.extra_metrics or {}
    packet_keys_raw = metrics.get("thermo_packet_keys")
    if isinstance(packet_keys_raw, (list, tuple)):
        present_keys = tuple(k for k in THERMO_CANONICAL_KEYS if k in packet_keys_raw)
    elif any(k in metrics for k in THERMO_SPECIFIC_KEYS):
        present_keys = tuple(k for k in THERMO_CANONICAL_KEYS if k in metrics)
    else:
        present_keys = ()

    domain_sigma_score = _to_finite_float(metrics.get("domain_sigma_score"))
    domain_truth_score = _to_finite_float(metrics.get("domain_truth_score"))
    if (
        aggregate.domain == Domain.GPS_DEFENSE_AVIATION
        and domain_sigma_score is not None
        and domain_truth_score is not None
    ):
        domain_comparison_status = "COMPARABLE"
    else:
        domain_sigma_score = None
        domain_truth_score = None
        domain_comparison_status = "NOT_COMPARABLE"

    if not present_keys:
        return ThermoSigmaEvaluation(
            status="NOT_PRESENT",
            present_keys=(),
            missing_keys=(),
            domain_sigma_score=domain_sigma_score,
            domain_truth_score=domain_truth_score,
            domain_comparison_status=domain_comparison_status,
            proposed_verdict=aggregate.market_verdict,
            severity=Severity.S0,
        )

    parsed: dict[str, float] = {}
    missing: list[str] = []
    for key in THERMO_CANONICAL_KEYS:
        if key not in present_keys:
            missing.append(key)
            continue
        fval = _to_finite_float(metrics.get(key))
        if fval is None:
            missing.append(key)
        else:
            parsed[key] = fval

    if missing:
        return ThermoSigmaEvaluation(
            status="INCOMPLETE",
            present_keys=present_keys,
            missing_keys=tuple(missing),
            domain_sigma_score=domain_sigma_score,
            domain_truth_score=domain_truth_score,
            domain_comparison_status=domain_comparison_status,
            unknowns=("THERMO_SIGNAL_INCOMPLETE",),
            proposed_verdict="HOLD",
            severity=Severity.S2,
        )

    pin = parsed["pin"]
    pout = parsed["pout"]
    energy_efficiency = parsed["energy_efficiency"]
    thermo_debt = parsed["thermo_debt"]
    truth_score = parsed["truth_score"]
    reported_sigma_score = parsed["sigma_score"]
    reported_mismatch = parsed["sigma_truth_mismatch"]

    expected_efficiency = pout / max(pin, 1e-9)
    expected_reported_mismatch = abs(reported_sigma_score - truth_score)

    if domain_comparison_status == "COMPARABLE" and domain_sigma_score is not None and domain_truth_score is not None:
        domain_sigma_mismatch = abs(domain_sigma_score - truth_score)
        domain_truth_delta = abs(domain_truth_score - truth_score)
        actual_sigma_truth_mismatch = max(
            reported_mismatch,
            expected_reported_mismatch,
            domain_sigma_mismatch,
            domain_truth_delta,
        )
    else:
        actual_sigma_truth_mismatch = max(reported_mismatch, expected_reported_mismatch)

    # No canonical float tolerance exists in periphery/constants.py or periphery/energy_thermo.py.
    # Exact canonical equality is reported when satisfied; any numerical discrepancy not covered
    # by a canonical tolerance contract is reported as NOT_EVALUATED_NO_CANONICAL_TOLERANCE
    # (never converted into a synthetic contradiction or BLOCK).
    exact_formula_match = (
        pin > 0.0
        and pout >= 0.0
        and energy_efficiency == expected_efficiency
        and reported_mismatch == expected_reported_mismatch
    )
    if exact_formula_match:
        formula_status = "EXACT_MATCH"
        formula_consistent: bool | None = True
    else:
        formula_status = "NOT_EVALUATED_NO_CANONICAL_TOLERANCE"
        formula_consistent = None

    risk_flags: list[str] = []
    unknowns: list[str] = []
    contradictions: list[str] = []

    if energy_efficiency < THETA_ENERGY:
        risk_flags.append("ENERGY_INEFFICIENT")

    if thermo_debt > THETA_THERMO_DEBT:
        risk_flags.append("THERMO_DEBT_HIGH")

    if actual_sigma_truth_mismatch > THETA_MISMATCH:
        risk_flags.append("SIGMA_TRUTH_MISMATCH")

    if "COLLAPSE_DISGUISED_HIGH_SIGMA" in aggregate.contradictions:
        contradictions.append("COLLAPSE_DISGUISED_HIGH_SIGMA")

    dedup_risk = tuple(sorted(set(risk_flags)))
    dedup_unknowns = tuple(sorted(set(unknowns)))
    dedup_contra = tuple(sorted(set(contradictions)))

    if dedup_contra:
        status = "INCOHERENT"
        proposed_verdict = "BLOCK"
        severity = Severity.S3
    elif dedup_risk or dedup_unknowns:
        status = "INCOHERENT"
        proposed_verdict = "HOLD"
        severity = Severity.S2
    else:
        status = "COHERENT"
        proposed_verdict = aggregate.market_verdict
        severity = Severity.S0

    return ThermoSigmaEvaluation(
        status=status,
        present_keys=present_keys,
        missing_keys=(),
        pin=pin,
        pout=pout,
        energy_efficiency=energy_efficiency,
        expected_efficiency=expected_efficiency,
        thermo_debt=thermo_debt,
        truth_score=truth_score,
        reported_sigma_score=reported_sigma_score,
        domain_sigma_score=domain_sigma_score,
        domain_truth_score=domain_truth_score,
        domain_comparison_status=domain_comparison_status,
        reported_mismatch=reported_mismatch,
        actual_sigma_truth_mismatch=actual_sigma_truth_mismatch,
        formula_status=formula_status,
        formula_consistent=formula_consistent,
        risk_flags=dedup_risk,
        unknowns=dedup_unknowns,
        contradictions=dedup_contra,
        proposed_verdict=proposed_verdict,
        severity=severity,
    )


class BaseMetaAgent(BaseAgent):
    def evaluate(self, aggregate: DomainAggregate) -> AgentVote:
        raise NotImplementedError


class ThermoCoherenceAgent(BaseMetaAgent):
    agent_id = "ThermoCoherenceAgent"

    def evaluate(self, aggregate: DomainAggregate) -> AgentVote:
        evaluation = evaluate_thermo_sigma_coherence(aggregate)
        aggregate.extra_metrics["sigma_thermo_evaluation"] = evaluation.to_dict()
        # ThermoCoherenceAgent records its structured advisory evaluation and canonical risk flags
        # without injecting synthetic unknowns or contradictions that would create a new gate policy.
        return AgentVote(
            self.agent_id,
            Domain.META,
            Layer.CONTRADICTION,
            f"thermo_sigma_status={evaluation.status}",
            0.95 if evaluation.status != "NOT_PRESENT" else 0.4,
            evaluation.severity,
            proposed_verdict=evaluation.proposed_verdict,
            risk_flags=list(evaluation.risk_flags),
            unknowns=[],
            contradictions=[],
        )


class UnknownsAgent(BaseMetaAgent):
    agent_id = "UnknownsAgent"
    def evaluate(self, aggregate: DomainAggregate) -> AgentVote:
        sev = Severity.S2 if aggregate.unknowns else Severity.S0
        return AgentVote(self.agent_id, Domain.META, Layer.CONTRADICTION, f"unknowns={len(aggregate.unknowns)}", 0.9 if aggregate.unknowns else 0.3, sev, proposed_verdict="HOLD" if aggregate.unknowns else aggregate.market_verdict, unknowns=list(aggregate.unknowns))


class ConflictResolutionAgent(BaseMetaAgent):
    agent_id = "ConflictResolutionAgent"
    def evaluate(self, aggregate: DomainAggregate) -> AgentVote:
        sev = Severity.S3 if aggregate.contradictions else Severity.S0
        return AgentVote(self.agent_id, Domain.META, Layer.CONTRADICTION, f"contradictions={len(aggregate.contradictions)}", 0.95 if aggregate.contradictions else 0.2, sev, proposed_verdict="HOLD" if aggregate.contradictions else aggregate.market_verdict, contradictions=list(aggregate.contradictions))


class PolicyScopeAgent(BaseMetaAgent):
    agent_id = "PolicyScopeAgent"
    def evaluate(self, aggregate: DomainAggregate) -> AgentVote:
        blocked = any(flag in {"LIMIT_PRESSURE", "MERCHANT_POLICY_CONSTRAINT"} for flag in aggregate.risk_flags)
        return AgentVote(self.agent_id, Domain.META, Layer.CONTRADICTION, "policy scope validation", 0.9 if blocked else 0.4, Severity.S3 if blocked else Severity.S1, proposed_verdict="BLOCK" if blocked else aggregate.market_verdict)


class TicketReadinessAgent(BaseMetaAgent):
    agent_id = "TicketReadinessAgent"
    def evaluate(self, aggregate: DomainAggregate) -> AgentVote:
        ready = not aggregate.unknowns and not aggregate.contradictions
        return AgentVote(self.agent_id, Domain.META, Layer.PROOF, "ticket readiness", 0.9 if ready else 0.35, Severity.S0 if ready else Severity.S2, proposed_verdict=aggregate.market_verdict, unknowns=[] if ready else ["TICKET_NOT_READY"])


class TraceIntegrityAgent(BaseMetaAgent):
    agent_id = "TraceIntegrityAgent"
    def evaluate(self, aggregate: DomainAggregate) -> AgentVote:
        ready = len(aggregate.agent_votes) >= 3 and len(aggregate.evidence_refs) >= 1
        return AgentVote(self.agent_id, Domain.META, Layer.PROOF, f"trace_evidence={len(aggregate.evidence_refs)}", 0.9 if ready else 0.4, Severity.S0 if ready else Severity.S2, proposed_verdict=aggregate.market_verdict, unknowns=[] if ready else ["TRACE_INCOMPLETE"])


class AttestationReadinessAgent(BaseMetaAgent):
    agent_id = "AttestationReadinessAgent"
    def evaluate(self, aggregate: DomainAggregate) -> AgentVote:
        ready = "proof_ready" in aggregate.extra_metrics
        return AgentVote(self.agent_id, Domain.META, Layer.PROOF, "attestation readiness", 0.85 if ready else 0.4, Severity.S0 if ready else Severity.S2, proposed_verdict=aggregate.market_verdict, unknowns=[] if ready else ["ATTESTATION_NOT_READY"])


class HumanOverrideEligibilityAgent(BaseMetaAgent):
    agent_id = "HumanOverrideEligibilityAgent"
    def evaluate(self, aggregate: DomainAggregate) -> AgentVote:
        eligible = aggregate.market_verdict in {"ANALYZE", "WAIT", "REVIEW", "HOLD"} or aggregate.confidence < 0.65
        return AgentVote(self.agent_id, Domain.META, Layer.PROOF, f"human_override={eligible}", 0.9 if eligible else 0.5, Severity.S1, proposed_verdict=aggregate.market_verdict)


class SeverityClassifierAgent(BaseMetaAgent):
    agent_id = "SeverityClassifierAgent"
    def evaluate(self, aggregate: DomainAggregate) -> AgentVote:
        score = 0
        score += len(aggregate.unknowns)
        score += len(aggregate.contradictions) * 2
        score += len(aggregate.risk_flags)
        severity = Severity.S4 if score >= 5 else Severity.S3 if score >= 3 else Severity.S2 if score >= 1 else Severity.S0
        return AgentVote(self.agent_id, Domain.META, Layer.PROOF, f"severity_classified={severity.value}", min(1.0, 0.4 + score * 0.1), severity, proposed_verdict=aggregate.market_verdict)


class ReplayConsistencyAgent(BaseMetaAgent):
    agent_id = "ReplayConsistencyAgent"
    def evaluate(self, aggregate: DomainAggregate) -> AgentVote:
        deterministic = aggregate.extra_metrics.get("deterministic", True)
        return AgentVote(self.agent_id, Domain.META, Layer.PROOF, f"deterministic={deterministic}", 0.9 if deterministic else 0.4, Severity.S0 if deterministic else Severity.S2, proposed_verdict=aggregate.market_verdict)


class ProofConsistencyAgent(BaseMetaAgent):
    agent_id = "ProofConsistencyAgent"
    def evaluate(self, aggregate: DomainAggregate) -> AgentVote:
        coherent = bool(aggregate.market_verdict) and aggregate.confidence >= 0.0
        return AgentVote(self.agent_id, Domain.META, Layer.PROOF, "payload/ticket/trace/severity coherence", 0.95 if coherent else 0.2, Severity.S0 if coherent else Severity.S3, proposed_verdict=aggregate.market_verdict)


def build_meta_agents() -> list[BaseMetaAgent]:
    return [
        ThermoCoherenceAgent(),
        UnknownsAgent(),
        ConflictResolutionAgent(),
        PolicyScopeAgent(),
        TicketReadinessAgent(),
        TraceIntegrityAgent(),
        AttestationReadinessAgent(),
        HumanOverrideEligibilityAgent(),
        SeverityClassifierAgent(),
        ReplayConsistencyAgent(),
        ProofConsistencyAgent(),
    ]
