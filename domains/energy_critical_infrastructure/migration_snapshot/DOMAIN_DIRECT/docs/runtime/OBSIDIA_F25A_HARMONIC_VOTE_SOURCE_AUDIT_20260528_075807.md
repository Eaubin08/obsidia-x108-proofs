# OBSIDIA F25A — HARMONIC VOTE SOURCE AUDIT

Date: 20260528_075807
Mode: READ_ONLY_AUDIT
Patch: NO
Commit: NO

## Git

- HEAD: 9ea9a5e
- TAG: BRODY_F23A_F27_REFLEX_AUTOMATION_PROTOCOL_AUDIT_20260528
```text
## main...origin/main
?? scripts/f25a_harmonic_vote_source_audit.py
```

## Findings

- agent_vote_present: True
- readiness_packet_class_present: False
- readiness_structure_present: True
- compute_governance_confidence_present: True
- compute_readiness_confidence_present: True
- calculate_immutable_vote_present: False
- sigma_aggregation_present: True

## Gap confirmed: True

`calculate_immutable_vote()` is missing while AgentVote / ReadinessPacket / governance confidence functions exist.

## Allowed F25B patch boundary

- allowed patch file: `sigma/contracts.py`
- allowed test file: `tests/sigma/test_f25b_immutable_vote_minimal.py`
- no Brody route wiring
- no runtime restart
- no dependency install
- no Graphiti / Neo4j / memory / kernel mutation

## Required F25B invariants

- function: calculate_immutable_vote
- type: pure_advisory_function
- side_effects: False
- decision_authority: KX108_ONLY
- readonly: True
- emits_act: False
- emits_verdict: False
- memory_write: False
- graphiti_write: False
- kernel_mutation: False
- x108_mutation: False
- score_range: [-1.0, 1.0]
- x108_gate_preserved: True
- advisory_verdict_never_runtime_decision: True

## Required tests

- test_all_allow_votes_positive_score
- test_all_block_votes_negative_score
- test_all_hold_votes_neutral_score
- test_mixed_votes_weighted
- test_empty_votes_returns_hold
- test_output_is_readonly
- test_decision_authority_kx108_only
- test_emits_act_false
- test_emits_verdict_false
- test_immutable_flag
- test_x108_gate_preserved
- test_advisory_does_not_override_x108_block
- test_confidence_clamped
- test_score_clamped_to_minus_one_one

## Target snippets

### sigma/contracts.py
- L31 [HOLD]     ALLOW = "ALLOW"; HOLD = "HOLD"; BLOCK = "BLOCK"
- L80 [AgentVote] class AgentVote(UniversalBase):
- L82 [HOLD]     vote: str = "HOLD"
- L83 [HOLD]     proposed_verdict: str = "HOLD"
- L84 [confidence]     confidence: float = 0.0
- L96 [confidence]             field_order = ["agent_id", "domain", "layer", "claim", "confidence", "severity_hint"]
- L100 [confidence]             field_order = ["agent_id", "vote", "proposed_verdict", "confidence", "domain", "layer", "claim", "contradictions", "unknowns", "risk_flags", "evidence_refs", "severity_hint"]
- L108 [confidence]         self.confidence = kwargs.pop("confidence", 0.0)
- L111 [HOLD]         if not self.proposed_verdict: self.proposed_verdict = self.vote or "HOLD"
- L112 [HOLD]         if not self.vote: self.vote = self.proposed_verdict or "HOLD"
- L123 [confidence]         try: self.confidence = float(self.confidence)
- L124 [confidence]         except: self.confidence = 0.0
- L129 [HOLD]     market_verdict: str = "HOLD"
- L130 [confidence]     confidence: float = 0.0
- L135 [AgentVote]     agent_votes: List[AgentVote] = field(default_factory=list)
- L140 [HOLD]         self.domain = "unknown"; self.market_verdict = "HOLD"; self.confidence = 0.0
- L147 [AgentVote]             self.agent_votes = [AgentVote(**item) if isinstance(item, dict) else item for item in v]
- L153 [HOLD]         verdict = str(getattr(self, "market_verdict", "HOLD")).upper()
- L156 [confidence]             # DomainAggregate owns only raw integrity confidence.
- L159 [normalize_confidence]             self.confidence = normalize_confidence(getattr(self, "confidence", 0.50))
- L161 [BLOCK]             if verdict in ("BLOCK", "ABORT_TRAJECTORY", "REFUSE", "DENY"):
- L167 [ALLOW]             elif verdict in ("AUTHORIZE", "ALLOW", "ACT", "VALID", "PASS", "TRAJECTORY_VALID", "PAY"):
- L171 [confidence]         obsidia_log(f"Aggregate Audit for {self.domain} | Verdict: {verdict} | Integrity: {self.confidence} | Severity: {self.severity}")
- L174 [normalize_confidence] def normalize_confidence(value, fallback=0.50):
- L175 [confidence]     """Normalize a confidence value without inventing score."""
- L187 [compute_governance_confidence] def compute_governance_confidence(
- L190 [x108_gate]     x108_gate,
- L196 [confidence]     Confidence in the sovereign X-108 governance decision.
- L199 [confidence]     This is not prediction confidence.
- L201 [HOLD]     BLOCK / HOLD / ACT / ANALYZE under known risk signals.
- L203 [normalize_confidence]     integrity = normalize_confidence(integrity)
- L206 [x108_gate]     x108_gate = str(x108_gate or "").upper()
- L214 [ALLOW]         "ALLOW",
- L223 [HOLD]         "HOLD",
- L228 [BLOCK]     # Robust refusal: the motor knows why it blocks.
- L229 [BLOCK]     if x108_gate == "BLOCK":
- L237 [HOLD]     if x108_gate == "HOLD" or verdict in review_verdicts:
- L252 [compute_readiness_confidence] def compute_readiness_confidence(integrity, governance):
- L256 [harmonic]     Harmonic mean:
- L261 [normalize_confidence]     integrity = normalize_confidence(integrity)
- L262 [normalize_confidence]     governance = normalize_confidence(governance)
- L274 [HOLD]     market_verdict: str = "HOLD"
- L275 [confidence]     confidence: float = 0.0
- L276 [confidence]     confidence_integrity: float = 0.0
- L277 [confidence]     confidence_governance: float = 0.0
- L278 [confidence]     confidence_readiness: float = 0.0
- L279 [confidence]     confidence_scope: str = "integrity"
- L281 [readiness_scope]     readiness_scope: str = "harmonic_integrity_governance"
- L285 [HOLD]     x108_gate: str = "HOLD"
- L306 [confidence]         # Final triple confidence architecture.
- L307 [x108_gate]         # At envelope level, x108_gate is already known.
- L308 [normalize_confidence]         self.confidence_integrity = normalize_confidence(getattr(self, "confidence", 0.50))
- L309 [confidence]         self.confidence = self.confidence_integrity
- L310 [confidence]         self.confidence_scope = "integrity"
- L312 [compute_governance_confidence]         self.confidence_governance = compute_governance_confidence(
- L313 [confidence]             self.confidence_integrity,
- L314 [HOLD]             getattr(self, "market_verdict", "HOLD"),
- L315 [x108_gate]             getattr(self, "x108_gate", ""),
- L322 [compute_readiness_confidence]         self.confidence_readiness = compute_readiness_confidence(
- L323 [confidence]             self.confidence_integrity,

### sigma/aggregation.py
- L7 [AgentVote] from .contracts import AgentVote, Domain, DomainAggregate
- L14 [AgentVote] def _common(votes: list[AgentVote]):
- L27 [AgentVote] def aggregate_trading(votes: Iterable[AgentVote]) -> DomainAggregate:
- L31 [confidence]         scores[v.proposed_verdict] += v.confidence
- L34 [HOLD]     hold = scores.get("HOLD", 0.0)
- L35 [HOLD]     market_verdict = "EXECUTE_LONG" if buy > max(sell, hold) else "EXECUTE_SHORT" if sell > max(buy, hold) else "REVIEW"
- L36 [HOLD]     confidence = round(min(0.98, max(buy, sell, hold) if sum(scores.values()) > 0 else 0.5), 2)
- L38 [HOLD]     extra_metrics = {"buy_score": buy, "sell_score": sell, "hold_score": hold, "proof_ready": True, "deterministic": True}
- L39 [confidence]     return DomainAggregate(Domain.TRADING, market_verdict, confidence, contradictions, unknowns, risk_flags, evidence_refs, agent_votes=votes, extra_metrics=extra_metrics)
- L42 [AgentVote] def aggregate_bank(votes: Iterable[AgentVote]) -> DomainAggregate:
- L46 [confidence]         scores[v.proposed_verdict] += v.confidence
- L49 [BLOCK]     block = scores.get("BLOCK", 0.0)
- L50 [BLOCK]     market_verdict = "BLOCK" if block > max(auth, analyze) else "AUTHORIZE" if auth > analyze else "ANALYZE"
- L51 [BLOCK]     confidence = round(min(0.98, max(auth, analyze, block) if sum(scores.values()) > 0 else 0.5), 2)
- L53 [BLOCK]     extra_metrics = {"authorize_score": auth, "analyze_score": analyze, "block_score": block, "proof_ready": True, "deterministic": True}
- L54 [confidence]     return DomainAggregate(Domain.BANK, market_verdict, confidence, contradictions, unknowns, risk_flags, evidence_refs, agent_votes=votes, extra_metrics=extra_metrics)
- L57 [AgentVote] def aggregate_ecom(votes: Iterable[AgentVote]) -> DomainAggregate:
- L61 [confidence]         scores[v.proposed_verdict] += v.confidence
- L66 [confidence]     confidence = round(min(0.98, max(pay, wait, refuse) if sum(scores.values()) > 0 else 0.5), 2)
- L69 [confidence]     return DomainAggregate(Domain.ECOM, market_verdict, confidence, contradictions, unknowns, risk_flags, evidence_refs, agent_votes=votes, extra_metrics=extra_metrics)
- L72 [AgentVote] def aggregate_gps_defense_aviation(votes: Iterable[AgentVote]) -> DomainAggregate:
- L76 [confidence]         scores[v.proposed_verdict] += v.confidence
- L83 [confidence]     confidence = round(min(0.98, max(valid, recalc, degraded, abort) if sum(scores.values()) > 0 else 0.5), 2)
- L98 [confidence]     sigma_score = confidence
- L99 [confidence]     truth_score = max(0.0, min(1.0, confidence - truth_penalty))
- L132 [confidence]         confidence,

## Status

F25A_HARMONIC_VOTE_SOURCE_AUDIT_PASS
NEXT=F25B_IMMUTABLE_VOTE_MINIMAL_PATCH