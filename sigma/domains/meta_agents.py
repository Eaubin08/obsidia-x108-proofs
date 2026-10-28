from __future__ import annotations

from ..base import BaseAgent
from ..contracts import AgentVote, Domain, DomainAggregate, Layer, Severity


class BaseMetaAgent(BaseAgent):
    def evaluate(self, aggregate: DomainAggregate) -> AgentVote:
        raise NotImplementedError


class UnknownsAgent(BaseMetaAgent):
    agent_id = "UnknownsAgent"
    def evaluate(self, aggregate: DomainAggregate) -> AgentVote:
        sev = Severity.S2 if aggregate.unknowns else Severity.S0
        unknowns_list = list(aggregate.unknowns)
        has_unknowns = bool(unknowns_list)
        return AgentVote(
            self.agent_id,
            Domain.META,
            Layer.CONTRADICTION,
            f"unknowns={len(unknowns_list)}",
            0.9 if has_unknowns else 0.3,
            sev,
            proposed_verdict="HOLD" if has_unknowns else aggregate.market_verdict,
            unknowns=unknowns_list,
            rule_id="RULE_META_UNKNOWNS",
            rule_version="1.0",
            observed_value={"unknowns": unknowns_list},
            measure_provenance="meta.unknowns",
            measure_age_s=0.0,
            measure_valid=True,
            predicate_violated=has_unknowns,
        )


class ConflictResolutionAgent(BaseMetaAgent):
    agent_id = "ConflictResolutionAgent"
    def evaluate(self, aggregate: DomainAggregate) -> AgentVote:
        sev = Severity.S3 if aggregate.contradictions else Severity.S0
        contra_list = list(aggregate.contradictions)
        has_contras = bool(contra_list)
        return AgentVote(
            self.agent_id,
            Domain.META,
            Layer.CONTRADICTION,
            f"contradictions={len(contra_list)}",
            0.95 if has_contras else 0.2,
            sev,
            proposed_verdict="HOLD" if has_contras else aggregate.market_verdict,
            contradictions=contra_list,
            rule_id="RULE_META_CONFLICT_RESOLUTION",
            rule_version="1.0",
            observed_value={"contradictions": contra_list},
            measure_provenance="meta.conflict_resolution",
            measure_age_s=0.0,
            measure_valid=True,
            predicate_violated=has_contras,
        )


class PolicyScopeAgent(BaseMetaAgent):
    agent_id = "PolicyScopeAgent"
    def evaluate(self, aggregate: DomainAggregate) -> AgentVote:
        blocked = any(flag in {"LIMIT_PRESSURE", "MERCHANT_POLICY_CONSTRAINT"} for flag in aggregate.risk_flags)
        return AgentVote(
            self.agent_id,
            Domain.META,
            Layer.CONTRADICTION,
            "policy scope validation",
            0.9 if blocked else 0.4,
            Severity.S4 if blocked else Severity.S1,
            proposed_verdict="BLOCK" if blocked else aggregate.market_verdict,
            rule_id="RULE_META_POLICY_SCOPE",
            rule_version="1.0",
            observed_value={"risk_flags": list(aggregate.risk_flags)},
            measure_provenance="meta.policy_scope",
            measure_age_s=0.0,
            measure_valid=True,
            predicate_violated=blocked,
        )


class TicketReadinessAgent(BaseMetaAgent):
    agent_id = "TicketReadinessAgent"
    def evaluate(self, aggregate: DomainAggregate) -> AgentVote:
        ready = not aggregate.unknowns and not aggregate.contradictions
        unknowns_out = [] if ready else ["TICKET_NOT_READY"]
        return AgentVote(
            self.agent_id,
            Domain.META,
            Layer.PROOF,
            "ticket readiness",
            0.9 if ready else 0.35,
            Severity.S0 if ready else Severity.S2,
            proposed_verdict=aggregate.market_verdict,
            unknowns=unknowns_out,
            rule_id="RULE_META_TICKET_READINESS",
            rule_version="1.0",
            observed_value={"unknowns": list(aggregate.unknowns), "contradictions": list(aggregate.contradictions)},
            measure_provenance="meta.ticket_readiness",
            measure_age_s=0.0,
            measure_valid=True,
            predicate_violated=not ready,
        )


class TraceIntegrityAgent(BaseMetaAgent):
    agent_id = "TraceIntegrityAgent"
    def evaluate(self, aggregate: DomainAggregate) -> AgentVote:
        vote_count = len(getattr(aggregate, "agent_votes", []))
        evidence_count = len(getattr(aggregate, "evidence_refs", []))
        ready = vote_count >= 3 and evidence_count >= 1
        unknowns_out = [] if ready else ["TRACE_INCOMPLETE"]
        return AgentVote(
            self.agent_id,
            Domain.META,
            Layer.PROOF,
            f"trace_evidence={evidence_count}",
            0.9 if ready else 0.4,
            Severity.S0 if ready else Severity.S2,
            proposed_verdict=aggregate.market_verdict,
            unknowns=unknowns_out,
            rule_id="RULE_META_TRACE_INTEGRITY",
            rule_version="1.0",
            observed_value={"vote_count": vote_count, "evidence_count": evidence_count},
            measure_provenance="meta.trace_integrity",
            measure_age_s=0.0,
            measure_valid=True,
            predicate_violated=not ready,
        )


class AttestationReadinessAgent(BaseMetaAgent):
    agent_id = "AttestationReadinessAgent"
    def evaluate(self, aggregate: DomainAggregate) -> AgentVote:
        proof_ready = "proof_ready" in aggregate.extra_metrics
        unknowns_out = [] if proof_ready else ["ATTESTATION_NOT_READY"]
        return AgentVote(
            self.agent_id,
            Domain.META,
            Layer.PROOF,
            "attestation readiness",
            0.85 if proof_ready else 0.4,
            Severity.S0 if proof_ready else Severity.S2,
            proposed_verdict=aggregate.market_verdict,
            unknowns=unknowns_out,
            rule_id="RULE_META_ATTESTATION_READINESS",
            rule_version="1.0",
            observed_value={"proof_ready": proof_ready},
            measure_provenance="meta.attestation_readiness",
            measure_age_s=0.0,
            measure_valid=True,
            predicate_violated=not proof_ready,
        )


class HumanOverrideEligibilityAgent(BaseMetaAgent):
    agent_id = "HumanOverrideEligibilityAgent"
    def evaluate(self, aggregate: DomainAggregate) -> AgentVote:
        eligible = aggregate.market_verdict in {"ANALYZE", "WAIT", "REVIEW", "HOLD"} or aggregate.confidence < 0.65
        return AgentVote(
            self.agent_id,
            Domain.META,
            Layer.PROOF,
            f"human_override={eligible}",
            0.9 if eligible else 0.5,
            Severity.S1,
            proposed_verdict=aggregate.market_verdict,
            rule_id="RULE_META_HUMAN_OVERRIDE",
            rule_version="1.0",
            observed_value={"eligible": eligible},
            measure_provenance="meta.human_override",
            measure_age_s=0.0,
            measure_valid=True,
            predicate_violated=False,
        )


class SeverityClassifierAgent(BaseMetaAgent):
    agent_id = "SeverityClassifierAgent"
    def evaluate(self, aggregate: DomainAggregate) -> AgentVote:
        score = 0
        score += len(aggregate.unknowns)
        score += len(aggregate.contradictions) * 2
        score += len(aggregate.risk_flags)
        severity = Severity.S4 if score >= 5 else Severity.S3 if score >= 3 else Severity.S2 if score >= 1 else Severity.S0
        return AgentVote(
            self.agent_id,
            Domain.META,
            Layer.PROOF,
            f"severity_classified={severity.value}",
            min(1.0, 0.4 + score * 0.1),
            severity,
            proposed_verdict=aggregate.market_verdict,
            rule_id="RULE_META_SEVERITY_CLASSIFIER",
            rule_version="1.0",
            observed_value={"score": score, "severity": severity.value},
            measure_provenance="meta.severity_classifier",
            measure_age_s=0.0,
            measure_valid=True,
            predicate_violated=False,
        )


class ReplayConsistencyAgent(BaseMetaAgent):
    agent_id = "ReplayConsistencyAgent"
    def evaluate(self, aggregate: DomainAggregate) -> AgentVote:
        deterministic = aggregate.extra_metrics.get("deterministic", True)
        return AgentVote(
            self.agent_id,
            Domain.META,
            Layer.PROOF,
            f"deterministic={deterministic}",
            0.9 if deterministic else 0.4,
            Severity.S0 if deterministic else Severity.S2,
            proposed_verdict=aggregate.market_verdict,
            rule_id="RULE_META_REPLAY_CONSISTENCY",
            rule_version="1.0",
            observed_value={"deterministic": deterministic},
            measure_provenance="meta.replay_consistency",
            measure_age_s=0.0,
            measure_valid=True,
            predicate_violated=not deterministic,
        )


class ProofConsistencyAgent(BaseMetaAgent):
    agent_id = "ProofConsistencyAgent"
    def evaluate(self, aggregate: DomainAggregate) -> AgentVote:
        coherent = bool(aggregate.market_verdict) and aggregate.confidence >= 0.0
        return AgentVote(
            self.agent_id,
            Domain.META,
            Layer.PROOF,
            "payload/ticket/trace/severity coherence",
            0.95 if coherent else 0.2,
            Severity.S0 if coherent else Severity.S4,
            proposed_verdict=aggregate.market_verdict if coherent else "BLOCK",
            rule_id="RULE_META_PROOF_CONSISTENCY",
            rule_version="1.0",
            observed_value={"market_verdict": aggregate.market_verdict, "confidence": aggregate.confidence},
            measure_provenance="meta.proof_consistency",
            measure_age_s=0.0,
            measure_valid=True,
            predicate_violated=not coherent,
        )


def build_meta_agents() -> list[BaseMetaAgent]:
    return [
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
