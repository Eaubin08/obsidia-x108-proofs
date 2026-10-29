from __future__ import annotations

from ..base import BaseAgent
from ..contracts import AgentVote, BankState, Domain, Layer, Severity


class TransactionContextAgent(BaseAgent):
    agent_id = "TransactionContextAgent"
    def evaluate(self, state: BankState) -> AgentVote:
        unknowns = ["UNKNOWN_CHANNEL"] if not state.channel else []
        return AgentVote(
            self.agent_id, Domain.BANK, Layer.OBSERVATION,
            f"type={state.transaction_type}, channel={state.channel}", 0.8, Severity.S1,
            proposed_verdict="ANALYZE", unknowns=unknowns,
            rule_id="RULE_BANK_CONTEXT_ADVISORY", rule_version="1.0",
            measure_provenance="bank.core.context", measure_age_s=0.0, measure_valid=True,
            observed_value=state.channel, predicate_violated=False
        )


class CounterpartyAgent(BaseAgent):
    agent_id = "CounterpartyAgent"
    def evaluate(self, state: BankState) -> AgentVote:
        known_valid = state.counterparty_known and state.counterparty_age_days > 30
        verdict = "AUTHORIZE" if known_valid else "ANALYZE"
        return AgentVote(
            self.agent_id, Domain.BANK, Layer.OBSERVATION,
            f"counterparty_known={state.counterparty_known}, age_days={state.counterparty_age_days}",
            0.75 if verdict=="AUTHORIZE" else 0.55, Severity.S1,
            proposed_verdict=verdict,
            rule_id="RULE_BANK_COUNTERPARTY", rule_version="1.0",
            measure_provenance="bank.kyc.registry", measure_age_s=0.0, measure_valid=True,
            observed_value=known_valid, predicate_violated=(not known_valid)
        )


class LiquidityExposureAgent(BaseAgent):
    agent_id = "LiquidityExposureAgent"
    def evaluate(self, state: BankState) -> AgentVote:
        pressure = 1.0 if state.account_balance <= 0 else state.amount / max(state.account_balance, 1e-9)
        verdict = "BLOCK" if pressure > 0.9 else "ANALYZE" if pressure > 0.5 else "AUTHORIZE"
        sev = Severity.S3 if verdict=="BLOCK" else Severity.S2 if verdict=="ANALYZE" else Severity.S1
        return AgentVote(
            self.agent_id, Domain.BANK, Layer.OBSERVATION,
            f"liquidity_pressure={pressure:.2f}", min(1.0, pressure), sev,
            proposed_verdict=verdict, risk_flags=["CASH_PRESSURE"] if pressure > 0.5 else [],
            rule_id="RULE_BANK_LIQUIDITY_EXPOSURE", rule_version="1.0",
            measure_provenance="bank.ledger.balance", measure_age_s=0.0, measure_valid=True,
            observed_value=pressure, predicate_violated=(pressure > 0.90)
        )


class BehaviorShiftAgent(BaseAgent):
    agent_id = "BehaviorShiftAgent"
    def evaluate(self, state: BankState) -> AgentVote:
        verdict = "ANALYZE" if state.behavior_shift_score > 0.5 else "AUTHORIZE"
        return AgentVote(
            self.agent_id, Domain.BANK, Layer.OBSERVATION,
            f"behavior_shift={state.behavior_shift_score:.2f}", state.behavior_shift_score,
            Severity.S2 if verdict=="ANALYZE" else Severity.S1, proposed_verdict=verdict,
            rule_id="RULE_BANK_BEHAVIOR_SHIFT", rule_version="1.0",
            measure_provenance="bank.ml.behavior", measure_age_s=0.0, measure_valid=True,
            observed_value=state.behavior_shift_score, predicate_violated=(state.behavior_shift_score > 0.50)
        )


class FraudPatternAgent(BaseAgent):
    agent_id = "FraudPatternAgent"
    def evaluate(self, state: BankState) -> AgentVote:
        verdict = "BLOCK" if state.fraud_score > 0.75 else "ANALYZE" if state.fraud_score > 0.45 else "AUTHORIZE"
        sev = Severity.S4 if verdict=="BLOCK" else Severity.S2 if verdict=="ANALYZE" else Severity.S1
        return AgentVote(
            self.agent_id, Domain.BANK, Layer.INTERPRETATION,
            f"fraud_score={state.fraud_score:.2f}", state.fraud_score, sev,
            proposed_verdict=verdict, risk_flags=["FRAUD_PATTERN"] if verdict!="AUTHORIZE" else [],
            rule_id="RULE_BANK_FRAUD_PATTERN", rule_version="1.0",
            measure_provenance="bank.fraud.detector", measure_age_s=0.0, measure_valid=True,
            observed_value=state.fraud_score, predicate_violated=(state.fraud_score > 0.75)
        )


class LimitPolicyAgent(BaseAgent):
    agent_id = "LimitPolicyAgent"
    def evaluate(self, state: BankState) -> AgentVote:
        ratio = state.amount / max(state.policy_limit, 1e-9)
        verdict = "BLOCK" if ratio > 1.0 else "ANALYZE" if ratio > 0.8 else "AUTHORIZE"
        sev = Severity.S3 if verdict=="BLOCK" else Severity.S2 if verdict=="ANALYZE" else Severity.S1
        return AgentVote(
            self.agent_id, Domain.BANK, Layer.INTERPRETATION,
            f"limit_ratio={ratio:.2f}", min(1.0, ratio), sev,
            proposed_verdict=verdict, risk_flags=["LIMIT_PRESSURE"] if ratio > 0.8 else [],
            rule_id="RULE_BANK_LIMIT_POLICY", rule_version="1.0",
            measure_provenance="bank.policy.engine", measure_age_s=0.0, measure_valid=True,
            observed_value=ratio, predicate_violated=(ratio > 1.0)
        )


class AffordabilityAgent(BaseAgent):
    agent_id = "AffordabilityAgent"
    def evaluate(self, state: BankState) -> AgentVote:
        verdict = "AUTHORIZE" if state.affordability_score > 0.7 else "ANALYZE" if state.affordability_score > 0.4 else "BLOCK"
        sev = Severity.S3 if verdict=="BLOCK" else Severity.S2 if verdict=="ANALYZE" else Severity.S1
        return AgentVote(
            self.agent_id, Domain.BANK, Layer.INTERPRETATION,
            f"affordability={state.affordability_score:.2f}", state.affordability_score, sev,
            proposed_verdict=verdict,
            rule_id="RULE_BANK_AFFORDABILITY", rule_version="1.0",
            measure_provenance="bank.credit.scoring", measure_age_s=0.0, measure_valid=True,
            observed_value=state.affordability_score, predicate_violated=(state.affordability_score <= 0.40)
        )


class TemporalUrgencyAgent(BaseAgent):
    agent_id = "TemporalUrgencyAgent"
    def evaluate(self, state: BankState) -> AgentVote:
        verdict = "ANALYZE" if state.urgency_score > 0.75 else "AUTHORIZE"
        return AgentVote(
            self.agent_id, Domain.BANK, Layer.INTERPRETATION,
            f"urgency={state.urgency_score:.2f}", state.urgency_score,
            Severity.S2 if verdict=="ANALYZE" else Severity.S1, proposed_verdict=verdict,
            contradictions=["URGENT_BEHAVIOR"] if verdict=="ANALYZE" else [],
            rule_id="RULE_BANK_TEMPORAL_URGENCY", rule_version="1.0",
            measure_provenance="bank.session.urgency", measure_age_s=0.0, measure_valid=True,
            observed_value=state.urgency_score, predicate_violated=(state.urgency_score > 0.75)
        )


class IdentityMismatchAgent(BaseAgent):
    agent_id = "IdentityMismatchAgent"
    def evaluate(self, state: BankState) -> AgentVote:
        combined = max(state.identity_mismatch_score, 1 - state.device_trust_score)
        verdict = "BLOCK" if combined > 0.75 else "ANALYZE" if combined > 0.4 else "AUTHORIZE"
        sev = Severity.S4 if verdict=="BLOCK" else Severity.S2 if verdict=="ANALYZE" else Severity.S1
        return AgentVote(
            self.agent_id, Domain.BANK, Layer.CONTRADICTION,
            f"identity_mismatch={combined:.2f}", combined, sev,
            proposed_verdict=verdict,
            contradictions=["IDENTITY_CONTEXT_MISMATCH"] if combined > 0.4 else [],
            rule_id="RULE_BANK_IDENTITY_MISMATCH", rule_version="1.0",
            measure_provenance="bank.device.identity", measure_age_s=0.0, measure_valid=True,
            observed_value=combined, predicate_violated=(combined > 0.75)
        )


class NarrativeConflictAgent(BaseAgent):
    agent_id = "NarrativeConflictAgent"
    def evaluate(self, state: BankState) -> AgentVote:
        verdict = "ANALYZE" if state.narrative_conflict_score > 0.45 else "AUTHORIZE"
        return AgentVote(
            self.agent_id, Domain.BANK, Layer.CONTRADICTION,
            f"narrative_conflict={state.narrative_conflict_score:.2f}", state.narrative_conflict_score,
            Severity.S2 if verdict=="ANALYZE" else Severity.S1, proposed_verdict=verdict,
            contradictions=["NARRATIVE_CONFLICT"] if verdict=="ANALYZE" else [],
            rule_id="RULE_BANK_NARRATIVE_CONFLICT", rule_version="1.0",
            measure_provenance="bank.nlp.intent", measure_age_s=0.0, measure_valid=True,
            observed_value=state.narrative_conflict_score, predicate_violated=(state.narrative_conflict_score > 0.45)
        )


class RecoveryPathAgent(BaseAgent):
    agent_id = "RecoveryPathAgent"
    def evaluate(self, state: BankState) -> AgentVote:
        claim = "manual confirmation / delayed verification path available"
        return AgentVote(
            self.agent_id, Domain.BANK, Layer.PROOF,
            claim, 0.85, Severity.S1, proposed_verdict="ANALYZE",
            rule_id="RULE_BANK_RECOVERY_PATH", rule_version="1.0",
            measure_provenance="bank.ops.recovery", measure_age_s=0.0, measure_valid=True,
            observed_value=claim, predicate_violated=False
        )


class BankProofAgent(BaseAgent):
    agent_id = "BankProofAgent"
    def evaluate(self, state: BankState) -> AgentVote:
        unknowns = []
        if state.elapsed_s < state.min_required_elapsed_s:
            unknowns.append("TEMPORAL_LOCK_NOT_MATURE")
        if state.recent_failed_attempts > 0:
            unknowns.append("RECENT_FAILED_ATTEMPTS")
        verdict = "ANALYZE" if unknowns else "AUTHORIZE"
        obs = {"elapsed_s": state.elapsed_s, "failed": state.recent_failed_attempts}
        return AgentVote(
            self.agent_id, Domain.BANK, Layer.PROOF,
            "bank proof readiness", 0.9 if not unknowns else 0.45,
            Severity.S2 if unknowns else Severity.S0, proposed_verdict=verdict, unknowns=unknowns,
            rule_id="RULE_BANK_PROOF", rule_version="1.0",
            measure_provenance="bank.audit.proofkit", measure_age_s=0.0, measure_valid=True,
            observed_value=obs, predicate_violated=bool(unknowns)
        )


def build_bank_agents() -> list[BaseAgent]:
    return [
        TransactionContextAgent(),
        CounterpartyAgent(),
        LiquidityExposureAgent(),
        BehaviorShiftAgent(),
        FraudPatternAgent(),
        LimitPolicyAgent(),
        AffordabilityAgent(),
        TemporalUrgencyAgent(),
        IdentityMismatchAgent(),
        NarrativeConflictAgent(),
        RecoveryPathAgent(),
        BankProofAgent(),
    ]
