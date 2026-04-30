# SCORING REGRESSION AUDIT — 20260428_155357

## 1. Current git status
```text
 M connectors/bank_normal_flow.py
 M merkle_seal.json
 M server.kernel.sealed.cjs
 M sigma/contracts.py
 M sigma/utils/__pycache__/__init__.cpython-313.pyc
 M sigma/utils/__pycache__/indicators.cpython-313.pyc
?? audit/local_diag/
?? audit/local_rescue/
```

## 2. Current scoring/confidence scan
```text
sigma/README.md:47:- `severity = "S4"`
sigma/aggregation.py:7:from .contracts import AgentVote, Domain, DomainAggregate
sigma/aggregation.py:17:    risk_flags = []
sigma/aggregation.py:22:        risk_flags.extend(v.risk_flags)
sigma/aggregation.py:24:    return contradictions, unknowns, risk_flags, evidence_refs
sigma/aggregation.py:27:def aggregate_trading(votes: Iterable[AgentVote]) -> DomainAggregate:
sigma/aggregation.py:31:        scores[v.proposed_verdict] += v.confidence
sigma/aggregation.py:36:    confidence = max(buy, sell, hold) / max(1.0, sum(scores.values()))
sigma/aggregation.py:37:    contradictions, unknowns, risk_flags, evidence_refs = _common(votes)
sigma/aggregation.py:39:    return DomainAggregate(Domain.TRADING, market_verdict, confidence, contradictions, unknowns, risk_flags, evidence_refs, agent_votes=votes, extra_metrics=extra_metrics)
sigma/aggregation.py:42:def aggregate_bank(votes: Iterable[AgentVote]) -> DomainAggregate:
sigma/aggregation.py:46:        scores[v.proposed_verdict] += v.confidence
sigma/aggregation.py:51:    confidence = max(auth, analyze, block) / max(1.0, sum(scores.values()))
sigma/aggregation.py:52:    contradictions, unknowns, risk_flags, evidence_refs = _common(votes)
sigma/aggregation.py:53:    extra_metrics = {"authorize_score": auth, "analyze_score": analyze, "block_score": block, "proof_ready": True, "deterministic": True}
sigma/aggregation.py:54:    return DomainAggregate(Domain.BANK, market_verdict, confidence, contradictions, unknowns, risk_flags, evidence_refs, agent_votes=votes, extra_metrics=extra_metrics)
sigma/aggregation.py:57:def aggregate_ecom(votes: Iterable[AgentVote]) -> DomainAggregate:
sigma/aggregation.py:61:        scores[v.proposed_verdict] += v.confidence
sigma/aggregation.py:66:    confidence = max(pay, wait, refuse) / max(1.0, sum(scores.values()))
sigma/aggregation.py:67:    contradictions, unknowns, risk_flags, evidence_refs = _common(votes)
sigma/aggregation.py:69:    return DomainAggregate(Domain.ECOM, market_verdict, confidence, contradictions, unknowns, risk_flags, evidence_refs, agent_votes=votes, extra_metrics=extra_metrics)
sigma/aggregation.py:72:def aggregate_gps_defense_aviation(votes: Iterable[AgentVote]) -> DomainAggregate:
sigma/aggregation.py:76:        scores[v.proposed_verdict] += v.confidence
sigma/aggregation.py:83:    confidence = max(valid, recalc, degraded, abort) / max(1.0, sum(scores.values()))
sigma/aggregation.py:84:    contradictions, unknowns, risk_flags, evidence_refs = _common(votes)
sigma/aggregation.py:98:    sigma_score = confidence
sigma/aggregation.py:99:    truth_score = max(0.0, min(1.0, confidence - truth_penalty))
sigma/aggregation.py:104:    elif "BROWNOUT" in risk_flags or "BROWNOUT_ACTIVE" in unknowns or "POWER_STATE_UNCERTAIN" in unknowns:
sigma/aggregation.py:107:        "TIME_SKEW" in risk_flags
sigma/aggregation.py:129:    return DomainAggregate(
sigma/aggregation.py:132:        confidence,
sigma/aggregation.py:135:        risk_flags,
sigma/batches/bank_truth_proxy_pack.json:1210:      "affordability_score": 0.54,
sigma/batches/bank_truth_proxy_pack.json:1237:      "fraud_score": 0.52,
sigma/batches/bank_truth_proxy_pack.json:1265:      "behavior_shift_score": 0.56,
sigma/batches/bank_truth_proxy_pack.json:1266:      "fraud_score": 0.57,
sigma/batches/bank_truth_proxy_pack.json:1269:      "urgency_score": 0.54,
sigma/batches/bank_truth_proxy_pack.json:1270:      "identity_mismatch_score": 0.52,
sigma/batches/bank_truth_proxy_pack.json:1271:      "narrative_conflict_score": 0.5,
sigma/batches/bank_truth_proxy_pack.json:1300:      "narrative_conflict_score": 0.58,
sigma/batches/bank_truth_proxy_pack.json:1326:      "affordability_score": 0.54,
sigma/batches/bank_truth_proxy_pack.json:1381:      "behavior_shift_score": 0.56,
sigma/batches/bank_truth_proxy_pack.json:1382:      "fraud_score": 0.52,
sigma/batches/bank_truth_proxy_pack.json:1385:      "urgency_score": 0.54,
sigma/batches/bank_truth_proxy_pack.json:1411:      "fraud_score": 0.57,
sigma/batches/bank_truth_proxy_pack.json:1415:      "identity_mismatch_score": 0.52,
sigma/batches/bank_truth_proxy_pack.json:1416:      "narrative_conflict_score": 0.5,
sigma/batches/bank_truth_proxy_pack.json:1442:      "affordability_score": 0.54,
sigma/batches/bank_truth_proxy_pack.json:1445:      "narrative_conflict_score": 0.58,
sigma/batches/bank_truth_proxy_pack.json:1497:      "behavior_shift_score": 0.56,
sigma/batches/bank_truth_proxy_pack.json:1501:      "urgency_score": 0.54,
sigma/batches/bank_truth_proxy_pack.json:1527:      "fraud_score": 0.52,
sigma/batches/bank_truth_proxy_pack.json:1556:      "fraud_score": 0.57,
sigma/batches/bank_truth_proxy_pack.json:1558:      "affordability_score": 0.54,
sigma/batches/bank_truth_proxy_pack.json:1560:      "identity_mismatch_score": 0.52,
sigma/batches/bank_truth_proxy_pack.json:1561:      "narrative_conflict_score": 0.5,
sigma/batches/bank_truth_proxy_pack.json:1590:      "narrative_conflict_score": 0.58,
sigma/batches/bank_truth_proxy_pack.json:1613:      "behavior_shift_score": 0.56,
sigma/batches/bank_truth_proxy_pack.json:1617:      "urgency_score": 0.54,
sigma/batches/bank_truth_proxy_pack.json:1672:      "fraud_score": 0.52,
sigma/batches/bank_truth_proxy_pack.json:1674:      "affordability_score": 0.54,
sigma/batches/bank_truth_proxy_pack.json:1701:      "fraud_score": 0.57,
sigma/batches/bank_truth_proxy_pack.json:1705:      "identity_mismatch_score": 0.52,
sigma/batches/bank_truth_proxy_pack.json:1706:      "narrative_conflict_score": 0.5,
sigma/batches/bank_truth_proxy_pack.json:1729:      "behavior_shift_score": 0.56,
sigma/batches/bank_truth_proxy_pack.json:1733:      "urgency_score": 0.54,
sigma/batches/bank_truth_proxy_pack.json:1735:      "narrative_conflict_score": 0.58,
sigma/batches/bank_truth_proxy_pack.json:1790:      "affordability_score": 0.54,
sigma/batches/bank_truth_proxy_pack.json:1817:      "fraud_score": 0.52,
sigma/batches/bank_truth_proxy_pack.json:1845:      "behavior_shift_score": 0.56,
sigma/batches/bank_truth_proxy_pack.json:1846:      "fraud_score": 0.57,
sigma/batches/bank_truth_proxy_pack.json:1849:      "urgency_score": 0.54,
sigma/batches/bank_truth_proxy_pack.json:1850:      "identity_mismatch_score": 0.52,
sigma/batches/bank_truth_proxy_pack.json:1851:      "narrative_conflict_score": 0.5,
sigma/batches/bank_truth_proxy_pack.json:1880:      "narrative_conflict_score": 0.58,
sigma/batches/bank_truth_proxy_pack.json:1906:      "affordability_score": 0.54,
sigma/batches/bank_truth_proxy_pack.json:1961:      "behavior_shift_score": 0.56,
sigma/batches/bank_truth_proxy_pack.json:1962:      "fraud_score": 0.52,
sigma/batches/bank_truth_proxy_pack.json:1965:      "urgency_score": 0.54,
sigma/batches/bank_truth_proxy_pack.json:1991:      "fraud_score": 0.57,
sigma/batches/bank_truth_proxy_pack.json:1995:      "identity_mismatch_score": 0.52,
sigma/batches/bank_truth_proxy_pack.json:1996:      "narrative_conflict_score": 0.5,
sigma/batches/bank_truth_proxy_pack.json:2022:      "affordability_score": 0.54,
sigma/batches/bank_truth_proxy_pack.json:2025:      "narrative_conflict_score": 0.58,
sigma/contracts.broken-ragnarok.py:56:class DomainAggregate(UniversalBase):
sigma/contracts.broken-ragnarok.py:59:    confidence: float = 0.0
sigma/contracts.broken-ragnarok.py:69:class DomainAggregate(UniversalBase):
sigma/contracts.broken-ragnarok.py:70:    domain: str = "unknown"; agent_votes: List[AgentVote] = field(default_factory=list); confidence: float = 0.0
sigma/contracts.broken-ragnarok.py:84:    position_confidence: float = 1.0
sigma/contracts.broken-ragnarok.py:97:class CanonicalDecisionEnvelope(UniversalBase):
sigma/contracts.py:84:    confidence: float = 0.0
sigma/contracts.py:90:    risk_flags: List[str] = field(default_factory=list)
sigma/contracts.py:92:    severity_hint: Severity = field(default_factory=lambda: Severity.S0)
sigma/contracts.py:96:            field_order = ["agent_id", "domain", "layer", "claim", "confidence", "severity_hint"]
sigma/contracts.py:100:            field_order = ["agent_id", "vote", "proposed_verdict", "confidence", "domain", "layer", "claim", "contradictions", "unknowns", "risk_flags", "evidence_refs", "severity_hint"]
sigma/contracts.py:108:        self.confidence = kwargs.pop("confidence", 0.0)
sigma/contracts.py:115:        self.risk_flags = list(kwargs.pop("risk_flags", []) or [])
sigma/contracts.py:118:        severity = kwargs.pop("severity_hint", Severity.S0)
sigma/contracts.py:119:        try: self.severity_hint = severity if isinstance(severity, Severity) else Severity(severity)
sigma/contracts.py:120:        except: self.severity_hint = Severity.S0
sigma/contracts.py:123:        try: self.confidence = float(self.confidence)
sigma/contracts.py:124:        except: self.confidence = 0.0
sigma/contracts.py:127:class DomainAggregate(UniversalBase):
sigma/contracts.py:130:    confidence: float = 0.0
sigma/contracts.py:133:    risk_flags: List[str] = field(default_factory=list)
sigma/contracts.py:137:    severity: Severity = field(default_factory=lambda: Severity.S0)
sigma/contracts.py:140:        self.domain = "unknown"; self.market_verdict = "HOLD"; self.confidence = 0.0
sigma/contracts.py:141:        self.contradictions = []; self.unknowns = []; self.risk_flags = []
sigma/contracts.py:143:        self.severity = Severity.S0
sigma/contracts.py:151:            self.risk_flags.extend(list(getattr(av, "risk_flags", []) or []))
sigma/contracts.py:158:                if not self.contradictions and not self.unknowns and not self.risk_flags:
sigma/contracts.py:159:                    self.confidence = 0.98; self.severity = Severity.S0
sigma/contracts.py:161:                    self.confidence = 0.85; self.severity = Severity.S1
sigma/contracts.py:163:                self.confidence = 1.0; self.severity = Severity.S4
sigma/contracts.py:166:                self.confidence = 0.85; self.severity = Severity.S2
sigma/contracts.py:168:        obsidia_log(f"Sovereign Audit for {self.domain} | Verdict: {verdict} | Conf: {self.confidence} | Severity: {self.severity}")
sigma/contracts.py:171:class CanonicalDecisionEnvelope(UniversalBase):
sigma/contracts.py:174:    confidence: float = 0.0
sigma/contracts.py:177:    risk_flags: List[str] = field(default_factory=list)
sigma/contracts.py:180:    severity: str = "S0"
sigma/contracts.py:192:        if hasattr(self, "severity"):
sigma/contracts.py:193:            if isinstance(self.severity, int) and not isinstance(self.severity, str):
sigma/contracts.py:194:                self.severity = f"S{self.severity}"
sigma/contracts.py:195:            elif hasattr(self.severity, "name"):
sigma/contracts.py:196:                self.severity = str(self.severity.name)
sigma/domains/bank_agents.py:18:        return AgentVote(self.agent_id, Domain.BANK, Layer.OBSERVATION, f"counterparty_known={state.counterparty_known}, age_days={state.counterparty_age_days}", 0.75 if verdict=="AUTHORIZE" else 0.55, Severity.S1, proposed_verdict=verdict)
sigma/domains/bank_agents.py:25:        verdict = "BLOCK" if pressure > 0.9 else "ANALYZE" if pressure > 0.5 else "AUTHORIZE"
sigma/domains/bank_agents.py:27:        return AgentVote(self.agent_id, Domain.BANK, Layer.OBSERVATION, f"liquidity_pressure={pressure:.2f}", min(1.0, pressure), sev, proposed_verdict=verdict, risk_flags=["CASH_PRESSURE"] if pressure > 0.5 else [])
sigma/domains/bank_agents.py:33:        verdict = "ANALYZE" if state.behavior_shift_score > 0.5 else "AUTHORIZE"
sigma/domains/bank_agents.py:42:        return AgentVote(self.agent_id, Domain.BANK, Layer.INTERPRETATION, f"fraud_score={state.fraud_score:.2f}", state.fraud_score, sev, proposed_verdict=verdict, risk_flags=["FRAUD_PATTERN"] if verdict!="AUTHORIZE" else [])
sigma/domains/bank_agents.py:51:        return AgentVote(self.agent_id, Domain.BANK, Layer.INTERPRETATION, f"limit_ratio={ratio:.2f}", min(1.0, ratio), sev, proposed_verdict=verdict, risk_flags=["LIMIT_PRESSURE"] if ratio > 0.8 else [])
sigma/domains/ecom_agents.py:49:        return AgentVote(self.agent_id, Domain.ECOM, Layer.INTERPRETATION, f"margin_rate={state.margin_rate:.2f}", min(1.0, max(0.0, 1-state.margin_rate)), sev, proposed_verdict=verdict, risk_flags=["LOW_MARGIN"] if verdict!="PAY" else [])
sigma/domains/ecom_agents.py:57:        return AgentVote(self.agent_id, Domain.ECOM, Layer.INTERPRETATION, f"roas={state.roas:.2f}", min(1.0, state.roas/4), sev, proposed_verdict=verdict, risk_flags=["LOW_ROAS"] if verdict=="REFUSE" else [])
sigma/domains/ecom_agents.py:87:        verdict = "REFUSE" if state.merchant_policy_score < 0.2 else "WAIT" if state.merchant_policy_score < 0.5 else "PAY"
sigma/domains/ecom_agents.py:89:        return AgentVote(self.agent_id, Domain.ECOM, Layer.CONTRADICTION, f"merchant_policy={state.merchant_policy_score:.2f}", 1-state.merchant_policy_score, sev, proposed_verdict=verdict, risk_flags=["MERCHANT_POLICY_CONSTRAINT"] if verdict!="PAY" else [])
sigma/domains/gps_defense_aviation_agents.py:21:            confidence=0.95 if not missing else 0.35,
sigma/domains/gps_defense_aviation_agents.py:22:            severity_hint=Severity.S0 if not missing else Severity.S3,
sigma/domains/gps_defense_aviation_agents.py:40:            risk_flags=risk,
sigma/domains/gps_defense_aviation_agents.py:48:        contradictions = ["SOURCE_CONFLICT"] if conflict >= 0.5 else []
sigma/domains/gps_defense_aviation_agents.py:49:        verdict = "ABORT_TRAJECTORY" if conflict >= 0.8 else "RECALC_TRAJECTORY" if conflict >= 0.5 else "TRAJECTORY_VALID"
sigma/domains/gps_defense_aviation_agents.py:56:            Severity.S4 if conflict >= 0.8 else Severity.S2 if conflict >= 0.5 else Severity.S0,
sigma/domains/gps_defense_aviation_agents.py:65:        risk = ["TIME_SKEW"] if skew >= 0.5 else []
sigma/domains/gps_defense_aviation_agents.py:67:        verdict = "ABORT_TRAJECTORY" if skew >= 0.9 else "RECALC_TRAJECTORY" if skew >= 0.5 else "TRAJECTORY_VALID"
sigma/domains/gps_defense_aviation_agents.py:74:            Severity.S4 if skew >= 0.9 else Severity.S3 if skew >= 0.8 else Severity.S2 if skew >= 0.5 else Severity.S0,
sigma/domains/gps_defense_aviation_agents.py:75:            risk_flags=risk,
sigma/domains/gps_defense_aviation_agents.py:84:        risk = ["BROWNOUT"] if b >= 0.5 else []
sigma/domains/gps_defense_aviation_agents.py:86:        verdict = "ABORT_TRAJECTORY" if b >= 0.9 else "DEGRADED_NAVIGATION" if b >= 0.5 else "TRAJECTORY_VALID"
sigma/domains/gps_defense_aviation_agents.py:93:            Severity.S4 if b >= 0.9 else Severity.S3 if b >= 0.8 else Severity.S2 if b >= 0.5 else Severity.S0,
sigma/domains/gps_defense_aviation_agents.py:94:            risk_flags=risk,
sigma/domains/meta_agents.py:4:from ..contracts import AgentVote, Domain, DomainAggregate, Layer, Severity
sigma/domains/meta_agents.py:8:    def evaluate(self, aggregate: DomainAggregate) -> AgentVote:
sigma/domains/meta_agents.py:14:    def evaluate(self, aggregate: DomainAggregate) -> AgentVote:
sigma/domains/meta_agents.py:21:    def evaluate(self, aggregate: DomainAggregate) -> AgentVote:
sigma/domains/meta_agents.py:28:    def evaluate(self, aggregate: DomainAggregate) -> AgentVote:
sigma/domains/meta_agents.py:29:        blocked = any(flag in {"LIMIT_PRESSURE", "MERCHANT_POLICY_CONSTRAINT"} for flag in aggregate.risk_flags)
sigma/domains/meta_agents.py:35:    def evaluate(self, aggregate: DomainAggregate) -> AgentVote:
sigma/domains/meta_agents.py:42:    def evaluate(self, aggregate: DomainAggregate) -> AgentVote:
sigma/domains/meta_agents.py:49:    def evaluate(self, aggregate: DomainAggregate) -> AgentVote:
sigma/domains/meta_agents.py:56:    def evaluate(self, aggregate: DomainAggregate) -> AgentVote:
sigma/domains/meta_agents.py:57:        eligible = aggregate.market_verdict in {"ANALYZE", "WAIT", "REVIEW", "HOLD"} or aggregate.confidence < 0.65
sigma/domains/meta_agents.py:58:        return AgentVote(self.agent_id, Domain.META, Layer.PROOF, f"human_override={eligible}", 0.9 if eligible else 0.5, Severity.S1, proposed_verdict=aggregate.market_verdict)
sigma/domains/meta_agents.py:63:    def evaluate(self, aggregate: DomainAggregate) -> AgentVote:
sigma/domains/meta_agents.py:67:        score += len(aggregate.risk_flags)
sigma/domains/meta_agents.py:68:        severity = Severity.S4 if score >= 5 else Severity.S3 if score >= 3 else Severity.S2 if score >= 1 else Severity.S0
sigma/domains/meta_agents.py:69:        return AgentVote(self.agent_id, Domain.META, Layer.PROOF, f"severity_classified={severity.value}", min(1.0, 0.4 + score * 0.1), severity, proposed_verdict=aggregate.market_verdict)
sigma/domains/meta_agents.py:74:    def evaluate(self, aggregate: DomainAggregate) -> AgentVote:
sigma/domains/meta_agents.py:81:    def evaluate(self, aggregate: DomainAggregate) -> AgentVote:
sigma/domains/meta_agents.py:82:        coherent = bool(aggregate.market_verdict) and aggregate.confidence >= 0.0
sigma/domains/meta_agents.py:83:        return AgentVote(self.agent_id, Domain.META, Layer.PROOF, "payload/ticket/trace/severity coherence", 0.95 if coherent else 0.2, Severity.S0 if coherent else Severity.S3, proposed_verdict=aggregate.market_verdict)
sigma/domains/trading_agents.py:31:        return AgentVote(self.agent_id, Domain.TRADING, Layer.OBSERVATION, f"spread_bps={spread:.2f}, avg_vol={avg_vol:.2f}", 0.7 if liquid else 0.5, Severity.S1, proposed_verdict=verdict)
sigma/domains/trading_agents.py:41:        return AgentVote(self.agent_id, Domain.TRADING, Layer.OBSERVATION, f"rv20={rv20:.4f}, rv60={rv60:.4f}", conf, Severity.S2 if verdict=="SELL" else Severity.S1, proposed_verdict=verdict, risk_flags=["HIGH_VOLATILITY"] if verdict=="SELL" else [])
sigma/domains/trading_agents.py:47:        risk = state.event_risk_scores[-1] if state.event_risk_scores else 0.5
sigma/domains/trading_agents.py:49:        return AgentVote(self.agent_id, Domain.TRADING, Layer.OBSERVATION, f"event_risk={risk:.2f}", min(1.0, abs(risk-0.5)*2), Severity.S2 if risk > 0.7 else Severity.S1, proposed_verdict=verdict)
sigma/domains/trading_agents.py:132:        return AgentVote(self.agent_id, Domain.TRADING, Layer.INTERPRETATION, f"composite_risk={composite:.2f}", min(1.0, abs(composite-0.5)*2), Severity.S2 if composite > 0.70 else Severity.S1, proposed_verdict=verdict)
sigma/domains/trading_agents.py:147:        return AgentVote(self.agent_id, Domain.TRADING, Layer.CONTRADICTION, f"execution_cost_score={cost_score:.3f}", min(1.0, cost_score*3), Severity.S2 if verdict=="SELL" else Severity.S1, proposed_verdict=verdict, risk_flags=["POOR_EXECUTION"] if verdict=="SELL" else [])
sigma/domains/trading_agents.py:166:        return AgentVote(self.agent_id, Domain.TRADING, Layer.CONTRADICTION, f"portfolio_stress={stress:.2f}", stress, Severity.S3 if verdict=="SELL" else Severity.S1, proposed_verdict=verdict, risk_flags=["PORTFOLIO_STRESS"] if verdict=="SELL" else [])
sigma/examples/ecom_normal.json:1:´╗┐{"domain":"ecom","case_id":"ecom_normal","cart_total":89.90,"risk_flags":[],"expected_decision":"ALLOW"}
sigma/examples/gps_brownout.json:8:  "position_confidence": 0.68,
sigma/examples/gps_brownout.json:13:  "environment_risk_score": 0.50,
sigma/examples/gps_no_source.json:8:  "position_confidence": 0.10,
sigma/examples/gps_nominal.json:8:  "position_confidence": 0.94,
sigma/examples/gps_omega_chaos.json:11:    "position_confidence": 0.1,
sigma/examples/gps_source_conflict.json:8:  "position_confidence": 0.62,
sigma/examples/gps_time_skew.json:8:  "position_confidence": 0.70,
sigma/examples/ragnarok_full_attack.json:4:    "confidence": 0.85,
sigma/examples/ragnarok_full_attack.json:9:        "confidence": 0.9
sigma/examples/ragnarok_full_attack.json:14:        "confidence": 0.7
sigma/examples/trading_normal.json:1:´╗┐{"domain":"trading","case_id":"trading_normal","instrument":"AAPL","risk_flags":[],"expected_decision":"ALLOW"}
sigma/guard.py:7:from .contracts import CanonicalDecisionEnvelope, DomainAggregate, Severity, X108Gate, SourceTag
sigma/guard.py:12:    min_confidence_allow: float = 0.72
sigma/guard.py:13:    hold_confidence_floor: float = 0.45
sigma/guard.py:18:class GuardX108:
sigma/guard.py:22:    def decide(self, aggregate: DomainAggregate) -> CanonicalDecisionEnvelope:
sigma/guard.py:25:        risk_count = len(aggregate.risk_flags)
sigma/guard.py:27:        if contradiction_count >= self.config.max_contradictions_before_block or "FRAUD_PATTERN" in aggregate.risk_flags:
sigma/guard.py:30:            severity = Severity.S4
sigma/guard.py:31:        elif unknown_count > self.config.max_unknowns_before_hold or aggregate.confidence < self.config.hold_confidence_floor:
sigma/guard.py:34:            severity = Severity.S2
sigma/guard.py:35:        elif risk_count >= 2 and aggregate.confidence < self.config.min_confidence_allow:
sigma/guard.py:38:            severity = Severity.S2
sigma/guard.py:42:            severity = Severity.S0 if aggregate.confidence >= self.config.min_confidence_allow else Severity.S1
sigma/guard.py:50:        return CanonicalDecisionEnvelope(
sigma/guard.py:53:            confidence=aggregate.confidence,
sigma/guard.py:56:            risk_flags=aggregate.risk_flags,
sigma/guard.py:59:            severity=severity.value,
sigma/obsidia_sigma_v130.py:17:    monitor.evaluate_step(severity, risks, contras)
sigma/obsidia_sigma_v130.py:29:SEVERITY_MAP = {"S0": 0.0, "S1": 0.25, "S2": 0.5, "S3": 0.75, "S4": 1.0}
sigma/obsidia_sigma_v130.py:106:    def _to_vector(self, severity: str, risk_count: int, contra_count: int) -> float:
sigma/obsidia_sigma_v130.py:107:        base = SEVERITY_MAP.get(severity, 0.0)
sigma/obsidia_sigma_v130.py:116:        severity: str,
sigma/obsidia_sigma_v130.py:125:        z_t = self._to_vector(severity, len(risks), len(contras))
sigma/obsidia_sigma_v130.py:130:            "severity": severity,
sigma/protocols.py:4:from .contracts import BankState, CanonicalDecisionEnvelope, EcomState, TradingState, GpsDefenseAviationState
sigma/protocols.py:10:from .guard import GuardX108
sigma/protocols.py:23:        aggregate.risk_flags.extend(meta_vote.risk_flags)
sigma/protocols.py:28:def run_trading_pipeline(state: TradingState) -> CanonicalDecisionEnvelope:
sigma/protocols.py:31:    return GuardX108().decide(aggregate)
sigma/protocols.py:34:def run_bank_pipeline(state: BankState) -> CanonicalDecisionEnvelope:
sigma/protocols.py:37:    return GuardX108().decide(aggregate)
sigma/protocols.py:40:def run_ecom_pipeline(state: EcomState) -> CanonicalDecisionEnvelope:
sigma/protocols.py:43:    return GuardX108().decide(aggregate)
sigma/protocols.py:45:def run_gps_defense_aviation_pipeline(state: GpsDefenseAviationState) -> CanonicalDecisionEnvelope:
sigma/protocols.py:50:    return GuardX108().decide(aggregate)
sigma/run_pipeline.py:65:        severity=result_dict.get("severity", "S0"),
sigma/run_pipeline.py:66:        risks=result_dict.get("risk_flags", []),
sigma/run_pipeline.py:74:        result_dict["severity"] = "S4"
sigma/stress_test_results.json:11:          "severity": "S0",
sigma/stress_test_results.json:18:          "severity": "S1",
sigma/stress_test_results.json:27:          "severity": "S2",
sigma/stress_test_results.json:37:          "severity": "S3",
sigma/stress_test_results.json:47:          "severity": "S4",
sigma/stress_test_results.json:138:          "delay_s": 0.5,
sigma/stress_test_results.json:139:          "mean_velocity": 0.599733,
sigma/tests/test_bank_adversarial_pack.py:56:    severities = {d["severity"] for d in outputs}
sigma/tests/test_bank_adversarial_pack.py:60:    # bank_normal is sovereignly stable as HOLD when confidence/proof maturity is insufficient.
sigma/tests/test_bank_adversarial_pack.py:105:    ladder = [0.99, 0.80, 0.50, 0.20, 0.02]
sigma/tests/test_bank_adversarial_pack.py:111:        p["counterparty_known"] = trust >= 0.5
sigma/tests/test_bank_adversarial_pack.py:112:        p["counterparty_age_days"] = 240 if trust >= 0.5 else 0
sigma/tests/test_bank_adversarial_pack.py:163:            p["counterparty_known"] = trust >= 0.5
sigma/tests/test_bank_adversarial_pack.py:164:            p["counterparty_age_days"] = 240 if trust >= 0.5 else 0
sigma/tests/test_bank_market_pack.py:61:    assert blocked["severity"] == "S4", blocked
sigma/tests/test_bank_market_pack.py:155:                payload["counterparty_known"] = device_trust_score >= 0.5
sigma/tests/test_bank_robo_scenario_benchmark.py:55:        assert "severity" in row
sigma/tests/test_bank_world.py:43:    assert d["severity"] == "S4", d
sigma/tests/test_sigma_smoke.py:60:    assert "severity" in data
sigma/tools/run_bank_confusion_matrix_pack.py:74:            "severity": r.get("severity"),
sigma/tools/run_bank_confusion_matrix_pack.py:101:            "severity": r.get("severity"),
sigma/tools/run_bank_confusion_matrix_pack.py:128:            "severity": r.get("severity"),
sigma/tools/run_bank_confusion_matrix_pack.py:199:                "severity","reason_code","reason_family","gap_status","ok","expected_positive","predicted_positive",
sigma/tools/run_bank_enterprise_pack.py:53:        "severity": data.get("severity"),
sigma/tools/run_bank_enterprise_pack.py:92:                "x108_gate", "severity", "reason_code", "decision_id", "trace_id", "attestation_ref"
sigma/tools/run_bank_fuzz_scale_pack.py:80:for fraud in [0.20, 0.50, 0.90]:
sigma/tools/run_bank_fuzz_scale_pack.py:263:                "x108_gate_observed","reason_code","severity","elapsed_ms",
sigma/tools/run_bank_regulatory_proxy_pack.py:127:        "severity": out.get("severity"),
sigma/tools/run_bank_regulatory_proxy_pack.py:167:                "observed_reason_family","reason_family_match","x108_gate_observed","severity","reason_code",
sigma/tools/run_bank_replay_pack.py:120:        "severity": out.get("severity"),
sigma/tools/run_bank_replay_pack.py:195:    verdict_match = first_stable.get("severity") == second_stable.get("severity")
sigma/tools/run_bank_replay_pack.py:210:        "first_severity": first_stable.get("severity"),
sigma/tools/run_bank_replay_pack.py:211:        "second_severity": second_stable.get("severity"),
sigma/tools/run_bank_replay_pack.py:283:                "first_severity","second_severity",
sigma/tools/run_bank_robo_scenario_benchmark.py:90:    payload["channel"] = "mobile" if sensors["timeOfDay"] >= 0.5 else "web"
sigma/tools/run_bank_robo_scenario_benchmark.py:108:    payload["counterparty_known"] = (expected == "AUTORISER" and sensors["location"] < 0.5 and sensors["accountAge"] > 0.5)
sigma/tools/run_bank_robo_scenario_benchmark.py:162:                "severity": out.get("severity"),
sigma/tools/run_bank_robo_scenario_benchmark.py:177:                "severity": "ERROR",
sigma/tools/run_bank_robo_scenario_benchmark.py:210:                "severity",
sigma/tools/run_bank_scale_pack.py:178:        "severity": out.get("severity"),
sigma/tools/run_bank_scale_pack.py:233:                "severity","reason_code","gap_status","sigma_ok","floor_ok","ok","elapsed_ms",
sigma/tools/run_bank_security_fuzz_extended_pack.py:72:        "severity": None,
sigma/tools/run_bank_security_fuzz_extended_pack.py:93:    row["severity"] = out.get("severity")
sigma/tools/run_bank_security_fuzz_extended_pack.py:214:        "severity": None,
sigma/tools/run_bank_security_fuzz_extended_pack.py:220:    for fraud in [0.20, 0.50, 0.90]:
sigma/tools/run_bank_security_fuzz_extended_pack.py:247:                "x108_gate_observed","reason_code","severity","stdout","stderr","detail"
sigma/tools/run_bank_security_fuzz_pack.py:75:        "severity": None,
sigma/tools/run_bank_security_fuzz_pack.py:96:    row["severity"] = out.get("severity")
sigma/tools/run_bank_security_fuzz_pack.py:210:        "severity": None,
sigma/tools/run_bank_security_fuzz_pack.py:231:                "x108_gate_observed","reason_code","severity","stdout","stderr","detail"
sigma/tools/run_bank_truth_proxy_pack.py:97:        "severity": data.get("severity"),
sigma/tools/run_bank_truth_proxy_pack.py:143:                "observed_reason_family","reason_family_match","x108_gate_observed","severity","reason_code",
```

## 3. Suspect hardcoded fallback scan
```text
```

## 4. Dataclass / envelope definitions
```text

  sigma\aggregation.py:14:def _common(votes: list[AgentVote]):
  sigma\aggregation.py:15:    contradictions = []
  sigma\aggregation.py:16:    unknowns = []
> sigma\aggregation.py:17:    risk_flags = []
  sigma\aggregation.py:18:    evidence_refs = []
  sigma\aggregation.py:19:    for v in votes:
  sigma\aggregation.py:20:        contradictions.extend(v.contradictions)
  sigma\aggregation.py:21:        unknowns.extend(v.unknowns)
> sigma\aggregation.py:22:        risk_flags.extend(v.risk_flags)
  sigma\aggregation.py:23:        
evidence_refs.append(_hash_ref(f"{v.agent_id}:{v.claim}:{v.proposed_verdict}"))
> sigma\aggregation.py:24:    return contradictions, unknowns, risk_flags, evidence_refs
  sigma\aggregation.py:25:
  sigma\aggregation.py:26:
  sigma\aggregation.py:27:def aggregate_trading(votes: Iterable[AgentVote]) -> DomainAggregate:
  sigma\aggregation.py:28:    votes = list(votes)
  sigma\aggregation.py:29:    scores = defaultdict(float)
  sigma\aggregation.py:30:    for v in votes:
> sigma\aggregation.py:31:        scores[v.proposed_verdict] += v.confidence
  sigma\aggregation.py:32:    buy = scores.get("BUY", 0.0)
  sigma\aggregation.py:33:    sell = scores.get("SELL", 0.0)
  sigma\aggregation.py:34:    hold = scores.get("HOLD", 0.0)
  sigma\aggregation.py:35:    market_verdict = "EXECUTE_LONG" if buy > max(sell, hold) else "EXECUTE_SHORT" if 
sell > max(buy, hold) else "REVIEW"
> sigma\aggregation.py:36:    confidence = max(buy, sell, hold) / max(1.0, sum(scores.values()))
> sigma\aggregation.py:37:    contradictions, unknowns, risk_flags, evidence_refs = _common(votes)
  sigma\aggregation.py:38:    extra_metrics = {"buy_score": buy, "sell_score": sell, "hold_score": hold, 
"proof_ready": True, "deterministic": True}
> sigma\aggregation.py:39:    return DomainAggregate(Domain.TRADING, market_verdict, confidence, 
contradictions, unknowns, risk_flags, evidence_refs, agent_votes=votes, extra_metrics=extra_metrics)
  sigma\aggregation.py:40:
  sigma\aggregation.py:41:
  sigma\aggregation.py:42:def aggregate_bank(votes: Iterable[AgentVote]) -> DomainAggregate:
  sigma\aggregation.py:43:    votes = list(votes)
  sigma\aggregation.py:44:    scores = defaultdict(float)
  sigma\aggregation.py:45:    for v in votes:
> sigma\aggregation.py:46:        scores[v.proposed_verdict] += v.confidence
  sigma\aggregation.py:47:    auth = scores.get("AUTHORIZE", 0.0)
  sigma\aggregation.py:48:    analyze = scores.get("ANALYZE", 0.0)
  sigma\aggregation.py:49:    block = scores.get("BLOCK", 0.0)
  sigma\aggregation.py:50:    market_verdict = "BLOCK" if block > max(auth, analyze) else "AUTHORIZE" if auth > 
analyze else "ANALYZE"
> sigma\aggregation.py:51:    confidence = max(auth, analyze, block) / max(1.0, sum(scores.values()))
> sigma\aggregation.py:52:    contradictions, unknowns, risk_flags, evidence_refs = _common(votes)
> sigma\aggregation.py:53:    extra_metrics = {"authorize_score": auth, "analyze_score": analyze, 
"block_score": block, "proof_ready": True, "deterministic": True}
> sigma\aggregation.py:54:    return DomainAggregate(Domain.BANK, market_verdict, confidence, contradictions, 
unknowns, risk_flags, evidence_refs, agent_votes=votes, extra_metrics=extra_metrics)
  sigma\aggregation.py:55:
  sigma\aggregation.py:56:
  sigma\aggregation.py:57:def aggregate_ecom(votes: Iterable[AgentVote]) -> DomainAggregate:
  sigma\aggregation.py:58:    votes = list(votes)
  sigma\aggregation.py:59:    scores = defaultdict(float)
  sigma\aggregation.py:60:    for v in votes:
> sigma\aggregation.py:61:        scores[v.proposed_verdict] += v.confidence
  sigma\aggregation.py:62:    pay = scores.get("PAY", 0.0)
  sigma\aggregation.py:63:    wait = scores.get("WAIT", 0.0)
  sigma\aggregation.py:64:    refuse = scores.get("REFUSE", 0.0)
  sigma\aggregation.py:65:    market_verdict = "REFUSE" if refuse > max(pay, wait) else "PAY" if pay > wait 
else "WAIT"
> sigma\aggregation.py:66:    confidence = max(pay, wait, refuse) / max(1.0, sum(scores.values()))
> sigma\aggregation.py:67:    contradictions, unknowns, risk_flags, evidence_refs = _common(votes)
  sigma\aggregation.py:68:    extra_metrics = {"pay_score": pay, "wait_score": wait, "refuse_score": refuse, 
"proof_ready": True, "deterministic": True}
> sigma\aggregation.py:69:    return DomainAggregate(Domain.ECOM, market_verdict, confidence, contradictions, 
unknowns, risk_flags, evidence_refs, agent_votes=votes, extra_metrics=extra_metrics)
  sigma\aggregation.py:70:
  sigma\aggregation.py:71:
  sigma\aggregation.py:72:def aggregate_gps_defense_aviation(votes: Iterable[AgentVote]) -> DomainAggregate:
  sigma\aggregation.py:73:    votes = list(votes)
  sigma\aggregation.py:74:    scores = defaultdict(float)
  sigma\aggregation.py:75:    for v in votes:
> sigma\aggregation.py:76:        scores[v.proposed_verdict] += v.confidence
  sigma\aggregation.py:77:
  sigma\aggregation.py:78:    valid = scores.get("TRAJECTORY_VALID", 0.0)
  sigma\aggregation.py:79:    recalc = scores.get("RECALC_TRAJECTORY", 0.0)
  sigma\aggregation.py:80:    degraded = scores.get("DEGRADED_NAVIGATION", 0.0)
  sigma\aggregation.py:81:    abort = scores.get("ABORT_TRAJECTORY", 0.0)
  sigma\aggregation.py:82:
> sigma\aggregation.py:83:    confidence = max(valid, recalc, degraded, abort) / max(1.0, sum(scores.values()))
> sigma\aggregation.py:84:    contradictions, unknowns, risk_flags, evidence_refs = _common(votes)
  sigma\aggregation.py:85:
  sigma\aggregation.py:86:    truth_penalty = 0.0
  sigma\aggregation.py:87:    if any(u in unknowns for u in ["GPS_MISSING", "INERTIAL_MISSING", 
"RADIO_MISSING"]):
  sigma\aggregation.py:88:        truth_penalty += 0.35
  sigma\aggregation.py:89:    if "TIME_SKEW_ACTIVE" in unknowns or "TEMPORAL_ALIGNMENT_UNCERTAIN" in unknowns:
  sigma\aggregation.py:90:        truth_penalty += 0.22
  sigma\aggregation.py:95:    if "ATTESTATION_NOT_READY" in unknowns:
  sigma\aggregation.py:96:        truth_penalty += 0.10
  sigma\aggregation.py:97:
> sigma\aggregation.py:98:    sigma_score = confidence
> sigma\aggregation.py:99:    truth_score = max(0.0, min(1.0, confidence - truth_penalty))
  sigma\aggregation.py:100:    mismatch_gap = abs(sigma_score - truth_score)
  sigma\aggregation.py:101:
  sigma\aggregation.py:102:    if "SOURCE_CONFLICT" in contradictions or abort > max(valid, recalc, degraded):
  sigma\aggregation.py:103:        market_verdict = "ABORT_TRAJECTORY"
> sigma\aggregation.py:104:    elif "BROWNOUT" in risk_flags or "BROWNOUT_ACTIVE" in unknowns or 
"POWER_STATE_UNCERTAIN" in unknowns:
  sigma\aggregation.py:105:        market_verdict = "DEGRADED_NAVIGATION"
  sigma\aggregation.py:106:    elif (
> sigma\aggregation.py:107:        "TIME_SKEW" in risk_flags
  sigma\aggregation.py:108:        or "TIME_SKEW_ACTIVE" in unknowns
  sigma\aggregation.py:109:        or "TEMPORAL_ALIGNMENT_UNCERTAIN" in unknowns
  sigma\aggregation.py:110:        or any(u in unknowns for u in ["GPS_MISSING", "INERTIAL_MISSING", 
"RADIO_MISSING"])
  sigma\aggregation.py:111:        or mismatch_gap >= 0.22
  sigma\aggregation.py:112:    ):
  sigma\aggregation.py:113:        market_verdict = "RECALC_TRAJECTORY"
  sigma\aggregation.py:129:    return DomainAggregate(
  sigma\aggregation.py:130:        Domain.GPS_DEFENSE_AVIATION,
  sigma\aggregation.py:131:        market_verdict,
> sigma\aggregation.py:132:        confidence,
  sigma\aggregation.py:133:        contradictions,
  sigma\aggregation.py:134:        unknowns,
> sigma\aggregation.py:135:        risk_flags,
  sigma\aggregation.py:136:        evidence_refs,
  sigma\aggregation.py:137:        agent_votes=votes,
  sigma\aggregation.py:138:        extra_metrics=extra_metrics,
  sigma\aggregation.py:139:    )
  sigma\contracts.broken-ragnarok.py:10:    OBSERVATION = 1; INTERPRETATION = 2; CONTRADICTION = 3; PERIPHERAL 
= 4
  sigma\contracts.broken-ragnarok.py:11:    SIGMA = 5; KERNEL = 6; PROOF = 7; SCELLAGE = 8
  sigma\contracts.broken-ragnarok.py:12:
> sigma\contracts.broken-ragnarok.py:13:class Severity(IntEnum):
  sigma\contracts.broken-ragnarok.py:14:    S0 = 0; S1 = 1; S2 = 2; S3 = 3; S4 = 4
  sigma\contracts.broken-ragnarok.py:15:
  sigma\contracts.broken-ragnarok.py:16:class Domain(Enum):
  sigma\contracts.broken-ragnarok.py:17:    BANK = "bank"; TRADING = "trading"; ECOM = "ecom"
  sigma\contracts.broken-ragnarok.py:18:    GPS_DEFENSE_AVIATION = "gps_defense_aviation"; META = "meta"
  sigma\contracts.broken-ragnarok.py:19:
  sigma\contracts.broken-ragnarok.py:53:        return SmartAttribute(name)
  sigma\contracts.broken-ragnarok.py:54:
  sigma\contracts.broken-ragnarok.py:55:@dataclass
> sigma\contracts.broken-ragnarok.py:56:class DomainAggregate(UniversalBase):
  sigma\contracts.broken-ragnarok.py:57:    domain: str = "unknown"
  sigma\contracts.broken-ragnarok.py:58:    agent_votes: List[AgentVote] = field(default_factory=list)
> sigma\contracts.broken-ragnarok.py:59:    confidence: float = 0.0
  sigma\contracts.broken-ragnarok.py:60:    def __init__(self, **kwargs):
  sigma\contracts.broken-ragnarok.py:61:        v = kwargs.get("agent_votes", [])
  sigma\contracts.broken-ragnarok.py:62:        if isinstance(v, list):
  sigma\contracts.broken-ragnarok.py:63:            kwargs["agent_votes"] = [AgentVote(**item) if 
isinstance(item, dict) else item for item in v]
  sigma\contracts.broken-ragnarok.py:64:        # On appelle le constructeur de la dataclass (via object) puis 
la base
  sigma\contracts.broken-ragnarok.py:65:        for k, v in kwargs.items():
  sigma\contracts.broken-ragnarok.py:66:            setattr(self, k, v)
  sigma\contracts.broken-ragnarok.py:67:
  sigma\contracts.broken-ragnarok.py:68:@dataclass
> sigma\contracts.broken-ragnarok.py:69:class DomainAggregate(UniversalBase):
> sigma\contracts.broken-ragnarok.py:70:    domain: str = "unknown"; agent_votes: List[AgentVote] = 
field(default_factory=list); confidence: float = 0.0
  sigma\contracts.broken-ragnarok.py:71:    def __init__(self, *args, **kwargs):
  sigma\contracts.broken-ragnarok.py:72:        super().__init__(*args, **kwargs)
  sigma\contracts.broken-ragnarok.py:73:        v = getattr(self, "agent_votes", [])
  sigma\contracts.broken-ragnarok.py:74:        if isinstance(v, list):
  sigma\contracts.broken-ragnarok.py:75:            self.agent_votes = [AgentVote(**item) if isinstance(item, 
dict) else item for item in v]
  sigma\contracts.broken-ragnarok.py:76:
  sigma\contracts.broken-ragnarok.py:81:    inertial_available: bool = True
  sigma\contracts.broken-ragnarok.py:82:    radio_available: bool = True
  sigma\contracts.broken-ragnarok.py:83:    elapsed_s: float = 0.0
> sigma\contracts.broken-ragnarok.py:84:    position_confidence: float = 1.0
  sigma\contracts.broken-ragnarok.py:85:    # Champs de télémétrie requis pour le calcul du score de dérive
  sigma\contracts.broken-ragnarok.py:86:    trajectory_drift_score: float = 0.0
  sigma\contracts.broken-ragnarok.py:87:    source_conflict_score: float = 0.0
  sigma\contracts.broken-ragnarok.py:88:    environment_risk_score: float = 0.0
  sigma\contracts.broken-ragnarok.py:89:    attestation_ready: bool = True
  sigma\contracts.broken-ragnarok.py:90:
  sigma\contracts.broken-ragnarok.py:94:
  sigma\contracts.broken-ragnarok.py:95:
  sigma\contracts.broken-ragnarok.py:96:@dataclass
> sigma\contracts.broken-ragnarok.py:97:class CanonicalDecisionEnvelope(UniversalBase):
  sigma\contracts.broken-ragnarok.py:98:    x108_gate: str = "HOLD"
  sigma\contracts.broken-ragnarok.py:99:
  sigma\contracts.broken-ragnarok.py:100:@dataclass
  sigma\contracts.broken-ragnarok.py:101:class BankState(UniversalBase):
  sigma\contracts.broken-ragnarok.py:102:    amount: float = 0.0
  sigma\contracts.broken-ragnarok.py:103:    account_balance: float = 0.0
  sigma\contracts.py:10:    OBSERVATION = 1; INTERPRETATION = 2; CONTRADICTION = 3; PERIPHERAL = 4
  sigma\contracts.py:11:    SIGMA = 5; KERNEL = 6; PROOF = 7; SCELLAGE = 8
  sigma\contracts.py:12:
> sigma\contracts.py:13:class Severity(IntEnum):
  sigma\contracts.py:14:    S0 = 0; S1 = 1; S2 = 2; S3 = 3; S4 = 4
  sigma\contracts.py:15:    def __eq__(self, other):
  sigma\contracts.py:16:        if isinstance(other, str): return self.name == other
  sigma\contracts.py:17:        return super().__eq__(other)
  sigma\contracts.py:18:    def __str__(self): return self.name
  sigma\contracts.py:19:    def __repr__(self): return f'"{self.name}"'
  sigma\contracts.py:81:    agent_id: str = "A1_MEM"
  sigma\contracts.py:82:    vote: str = "HOLD"
  sigma\contracts.py:83:    proposed_verdict: str = "HOLD"
> sigma\contracts.py:84:    confidence: float = 0.0
  sigma\contracts.py:85:    domain: str = "unknown"
  sigma\contracts.py:86:    layer: int = 5
  sigma\contracts.py:87:    claim: str = "no_claim"
  sigma\contracts.py:88:    contradictions: List[str] = field(default_factory=list)
  sigma\contracts.py:89:    unknowns: List[str] = field(default_factory=list)
> sigma\contracts.py:90:    risk_flags: List[str] = field(default_factory=list)
  sigma\contracts.py:91:    evidence_refs: List[str] = field(default_factory=list)
> sigma\contracts.py:92:    severity_hint: Severity = field(default_factory=lambda: Severity.S0)
  sigma\contracts.py:93:
  sigma\contracts.py:94:    def __init__(self, *args, **kwargs):
  sigma\contracts.py:95:        if len(args) >= 2 and isinstance(args[1], (Domain, str)) and str(args[1]) in 
[d.value for d in Domain] + [d.name for d in Domain]:
> sigma\contracts.py:96:            field_order = ["agent_id", "domain", "layer", "claim", "confidence", 
"severity_hint"]
  sigma\contracts.py:97:            for i, value in enumerate(args):
  sigma\contracts.py:98:                if i < len(field_order): kwargs.setdefault(field_order[i], value)
  sigma\contracts.py:99:        else:
> sigma\contracts.py:100:            field_order = ["agent_id", "vote", "proposed_verdict", "confidence", 
"domain", "layer", "claim", "contradictions", "unknowns", "risk_flags", "evidence_refs", "severity_hint"]
  sigma\contracts.py:101:            for i, value in enumerate(args):
  sigma\contracts.py:102:                if i < len(field_order): kwargs.setdefault(field_order[i], value)
  sigma\contracts.py:103:
  sigma\contracts.py:104:        self.agent_id = kwargs.pop("agent_id", "A1_MEM")
  sigma\contracts.py:105:        self.domain = kwargs.pop("domain", "unknown")
  sigma\contracts.py:106:        self.layer = kwargs.pop("layer", 5)
  sigma\contracts.py:107:        self.claim = kwargs.pop("claim", "no_claim")
> sigma\contracts.py:108:        self.confidence = kwargs.pop("confidence", 0.0)
  sigma\contracts.py:109:        self.vote = kwargs.pop("vote", None)
  sigma\contracts.py:110:        self.proposed_verdict = kwargs.pop("proposed_verdict", None)
  sigma\contracts.py:111:        if not self.proposed_verdict: self.proposed_verdict = self.vote or "HOLD"
  sigma\contracts.py:112:        if not self.vote: self.vote = self.proposed_verdict or "HOLD"
  sigma\contracts.py:113:        self.contradictions = list(kwargs.pop("contradictions", []) or [])
  sigma\contracts.py:114:        self.unknowns = list(kwargs.pop("unknowns", []) or [])
> sigma\contracts.py:115:        self.risk_flags = list(kwargs.pop("risk_flags", []) or [])
  sigma\contracts.py:116:        self.evidence_refs = list(kwargs.pop("evidence_refs", []) or [])
  sigma\contracts.py:117:        
> sigma\contracts.py:118:        severity = kwargs.pop("severity_hint", Severity.S0)
> sigma\contracts.py:119:        try: self.severity_hint = severity if isinstance(severity, Severity) else 
Severity(severity)
> sigma\contracts.py:120:        except: self.severity_hint = Severity.S0
  sigma\contracts.py:121:
  sigma\contracts.py:122:        for k, v in kwargs.items(): setattr(self, k, v)
> sigma\contracts.py:123:        try: self.confidence = float(self.confidence)
> sigma\contracts.py:124:        except: self.confidence = 0.0
  sigma\contracts.py:125:
  sigma\contracts.py:126:@dataclass(init=False)
> sigma\contracts.py:127:class DomainAggregate(UniversalBase):
  sigma\contracts.py:128:    domain: str = "unknown"
  sigma\contracts.py:129:    market_verdict: str = "HOLD"
> sigma\contracts.py:130:    confidence: float = 0.0
  sigma\contracts.py:131:    contradictions: List[str] = field(default_factory=list)
  sigma\contracts.py:132:    unknowns: List[str] = field(default_factory=list)
> sigma\contracts.py:133:    risk_flags: List[str] = field(default_factory=list)
  sigma\contracts.py:134:    evidence_refs: List[str] = field(default_factory=list)
  sigma\contracts.py:135:    agent_votes: List[AgentVote] = field(default_factory=list)
  sigma\contracts.py:136:    extra_metrics: dict = field(default_factory=dict)
> sigma\contracts.py:137:    severity: Severity = field(default_factory=lambda: Severity.S0)
  sigma\contracts.py:138:
  sigma\contracts.py:139:    def __init__(self, *args, **kwargs):
> sigma\contracts.py:140:        self.domain = "unknown"; self.market_verdict = "HOLD"; self.confidence = 0.0
> sigma\contracts.py:141:        self.contradictions = []; self.unknowns = []; self.risk_flags = []
  sigma\contracts.py:142:        self.evidence_refs = []; self.agent_votes = []; self.extra_metrics = {}
> sigma\contracts.py:143:        self.severity = Severity.S0
  sigma\contracts.py:144:        super().__init__(*args, **kwargs)
  sigma\contracts.py:145:        v = getattr(self, "agent_votes", [])
  sigma\contracts.py:146:        if isinstance(v, list):
  sigma\contracts.py:147:            self.agent_votes = [AgentVote(**item) if isinstance(item, dict) else item 
for item in v]
  sigma\contracts.py:148:        for av in self.agent_votes:
  sigma\contracts.py:149:            self.contradictions.extend(list(getattr(av, "contradictions", []) or []))
  sigma\contracts.py:150:            self.unknowns.extend(list(getattr(av, "unknowns", []) or []))
> sigma\contracts.py:151:            self.risk_flags.extend(list(getattr(av, "risk_flags", []) or []))
  sigma\contracts.py:152:        
  sigma\contracts.py:153:        verdict = str(getattr(self, "market_verdict", "HOLD")).upper()
  sigma\contracts.py:154:        
  sigma\contracts.py:155:        if self.agent_votes:
  sigma\contracts.py:156:            # FIX SPECIAL REIMS : Restauration des scores de confiance élevés (0.85+)
  sigma\contracts.py:157:            if verdict in ("AUTHORIZE", "ALLOW", "TRAJECTORY_VALID", "PAY"):
> sigma\contracts.py:158:                if not self.contradictions and not self.unknowns and not 
self.risk_flags:
> sigma\contracts.py:159:                    self.confidence = 0.98; self.severity = Severity.S0
  sigma\contracts.py:160:                else:
> sigma\contracts.py:161:                    self.confidence = 0.85; self.severity = Severity.S1
  sigma\contracts.py:162:            elif verdict in ("BLOCK", "ABORT_TRAJECTORY", "REFUSE"):
> sigma\contracts.py:163:                self.confidence = 1.0; self.severity = Severity.S4
  sigma\contracts.py:164:            else:
  sigma\contracts.py:165:                # Fallback intelligent pour ANALYZE, REVIEW, RECALC_TRAJECTORY
> sigma\contracts.py:166:                self.confidence = 0.85; self.severity = Severity.S2
  sigma\contracts.py:167:        
> sigma\contracts.py:168:        obsidia_log(f"Sovereign Audit for {self.domain} | Verdict: {verdict} | Conf: 
{self.confidence} | Severity: {self.severity}")
  sigma\contracts.py:169:
  sigma\contracts.py:170:@dataclass
> sigma\contracts.py:171:class CanonicalDecisionEnvelope(UniversalBase):
  sigma\contracts.py:172:    domain: str = "unknown"
  sigma\contracts.py:173:    market_verdict: str = "HOLD"
> sigma\contracts.py:174:    confidence: float = 0.0
  sigma\contracts.py:175:    contradictions: List[str] = field(default_factory=list)
  sigma\contracts.py:176:    unknowns: List[str] = field(default_factory=list)
> sigma\contracts.py:177:    risk_flags: List[str] = field(default_factory=list)
  sigma\contracts.py:178:    x108_gate: str = "HOLD"
  sigma\contracts.py:179:    reason_code: str = "RAGNAROK_DEBUG"
> sigma\contracts.py:180:    severity: str = "S0"
  sigma\contracts.py:181:    decision_id: str = "debug-decision"
  sigma\contracts.py:182:    trace_id: str = "debug-trace"
  sigma\contracts.py:183:    ticket_required: bool = False
  sigma\contracts.py:184:    ticket_id: Optional[str] = None
  sigma\contracts.py:185:    attestation_ref: Optional[str] = None
  sigma\contracts.py:186:    source: str = "canonical_framework"
  sigma\contracts.py:189:    raw_engine: dict = field(default_factory=dict)
  sigma\contracts.py:190:
  sigma\contracts.py:191:    def __post_init__(self):
> sigma\contracts.py:192:        if hasattr(self, "severity"):
> sigma\contracts.py:193:            if isinstance(self.severity, int) and not isinstance(self.severity, str):
> sigma\contracts.py:194:                self.severity = f"S{self.severity}"
> sigma\contracts.py:195:            elif hasattr(self.severity, "name"):
> sigma\contracts.py:196:                self.severity = str(self.severity.name)
  sigma\contracts.py:197:
  sigma\contracts.py:198:@dataclass(init=False)
  sigma\contracts.py:199:class GpsDefenseAviationState(UniversalBase):
  sigma\contracts.py:200:    mission_id: str = "UNKNOWN"
  sigma\contracts.py:201:    flight_id: str = "UNKNOWN"
  sigma\contracts.py:202:    altitude: float = 0.0
  sigma\guard.py:4:import uuid
  sigma\guard.py:5:from dataclasses import dataclass
  sigma\guard.py:6:
> sigma\guard.py:7:from .contracts import CanonicalDecisionEnvelope, DomainAggregate, Severity, X108Gate, 
SourceTag
  sigma\guard.py:8:
  sigma\guard.py:9:
  sigma\guard.py:10:@dataclass
  sigma\guard.py:11:class GuardConfig:
> sigma\guard.py:12:    min_confidence_allow: float = 0.72
> sigma\guard.py:13:    hold_confidence_floor: float = 0.45
  sigma\guard.py:14:    max_unknowns_before_hold: int = 1
  sigma\guard.py:15:    max_contradictions_before_block: int = 2
  sigma\guard.py:16:
  sigma\guard.py:17:
  sigma\guard.py:18:class GuardX108:
  sigma\guard.py:19:    def __init__(self, config: GuardConfig | None = None) -> None:
  sigma\guard.py:22:    def decide(self, aggregate: DomainAggregate) -> CanonicalDecisionEnvelope:
  sigma\guard.py:23:        contradiction_count = len(aggregate.contradictions)
  sigma\guard.py:24:        unknown_count = len(aggregate.unknowns)
> sigma\guard.py:25:        risk_count = len(aggregate.risk_flags)
  sigma\guard.py:26:
> sigma\guard.py:27:        if contradiction_count >= self.config.max_contradictions_before_block or 
"FRAUD_PATTERN" in aggregate.risk_flags:
  sigma\guard.py:28:            gate = X108Gate.BLOCK
  sigma\guard.py:29:            reason = "CONTRADICTION_THRESHOLD_REACHED"
> sigma\guard.py:30:            severity = Severity.S4
> sigma\guard.py:31:        elif unknown_count > self.config.max_unknowns_before_hold or aggregate.confidence < 
self.config.hold_confidence_floor:
  sigma\guard.py:32:            gate = X108Gate.HOLD
> sigma\guard.py:33:            reason = "UNKNOWNS_OR_CONFIDENCE_LOW"
> sigma\guard.py:34:            severity = Severity.S2
> sigma\guard.py:35:        elif risk_count >= 2 and aggregate.confidence < self.config.min_confidence_allow:
  sigma\guard.py:36:            gate = X108Gate.HOLD
> sigma\guard.py:37:            reason = "RISK_FLAGS_REQUIRE_DELAY"
> sigma\guard.py:38:            severity = Severity.S2
  sigma\guard.py:39:        else:
  sigma\guard.py:40:            gate = X108Gate.ALLOW
  sigma\guard.py:41:            reason = "GUARD_ALLOW"
> sigma\guard.py:42:            severity = Severity.S0 if aggregate.confidence >= 
self.config.min_confidence_allow else Severity.S1
  sigma\guard.py:43:
  sigma\guard.py:44:        decision_id = f"{aggregate.domain.value}-{uuid.uuid4().hex[:12]}"
  sigma\guard.py:45:        trace_id = str(uuid.uuid4())
  sigma\guard.py:46:        ticket_required = gate == X108Gate.ALLOW
  sigma\guard.py:47:        ticket_id = uuid.uuid4().hex[:16] if ticket_required else None
  sigma\guard.py:48:        attestation_ref = 
hashlib.sha256("|".join(aggregate.evidence_refs).encode("utf-8")).hexdigest()[:24] if aggregate.evidence_refs 
else None
  sigma\guard.py:50:        return CanonicalDecisionEnvelope(
  sigma\guard.py:51:            domain=aggregate.domain.value,
  sigma\guard.py:52:            market_verdict=aggregate.market_verdict,
> sigma\guard.py:53:            confidence=aggregate.confidence,
  sigma\guard.py:54:            contradictions=aggregate.contradictions,
  sigma\guard.py:55:            unknowns=aggregate.unknowns,
> sigma\guard.py:56:            risk_flags=aggregate.risk_flags,
  sigma\guard.py:57:            x108_gate=gate.value,
  sigma\guard.py:58:            reason_code=reason,
> sigma\guard.py:59:            severity=severity.value,
  sigma\guard.py:60:            decision_id=decision_id,
  sigma\guard.py:61:            trace_id=trace_id,
  sigma\guard.py:62:            ticket_required=ticket_required,
  sigma\guard.py:63:            ticket_id=ticket_id,
  sigma\guard.py:64:            attestation_ref=attestation_ref,
  sigma\guard.py:65:            source=SourceTag.CANONICAL_FRAMEWORK.value,
  sigma\obsidia_sigma_v130.py:14:
  sigma\obsidia_sigma_v130.py:15:Usage :
  sigma\obsidia_sigma_v130.py:16:    monitor = ObsidiaSigmaMonitor()
> sigma\obsidia_sigma_v130.py:17:    monitor.evaluate_step(severity, risks, contras)
  sigma\obsidia_sigma_v130.py:18:    report = monitor.export_to_proofkit()
  sigma\obsidia_sigma_v130.py:19:"""
  sigma\obsidia_sigma_v130.py:20:
  sigma\obsidia_sigma_v130.py:21:import json
  sigma\obsidia_sigma_v130.py:22:import os
  sigma\obsidia_sigma_v130.py:23:import time
  sigma\obsidia_sigma_v130.py:26:from typing import List, Dict, Any, Optional
  sigma\obsidia_sigma_v130.py:27:
  sigma\obsidia_sigma_v130.py:28:
> sigma\obsidia_sigma_v130.py:29:SEVERITY_MAP = {"S0": 0.0, "S1": 0.25, "S2": 0.5, "S3": 0.75, "S4": 1.0}
  sigma\obsidia_sigma_v130.py:30:
  sigma\obsidia_sigma_v130.py:31:# Valeurs par defaut v1.4.0 (utilisees si sigma_config.json absent)
  sigma\obsidia_sigma_v130.py:32:_DEFAULT_TAU_MIN = 0.05
  sigma\obsidia_sigma_v130.py:33:_DEFAULT_TAU_MAX = 0.75
  sigma\obsidia_sigma_v130.py:34:_DEFAULT_ACCEL_LIMIT = 0.40
  sigma\obsidia_sigma_v130.py:35:
  sigma\obsidia_sigma_v130.py:103:    # Vecteur latent z_t
  sigma\obsidia_sigma_v130.py:104:    # ------------------------------------------------------------------
  sigma\obsidia_sigma_v130.py:105:
> sigma\obsidia_sigma_v130.py:106:    def _to_vector(self, severity: str, risk_count: int, contra_count: int) 
-> float:
> sigma\obsidia_sigma_v130.py:107:        base = SEVERITY_MAP.get(severity, 0.0)
  sigma\obsidia_sigma_v130.py:108:        return round(base + (risk_count * 0.05) + (contra_count * 0.1), 6)
  sigma\obsidia_sigma_v130.py:109:
  sigma\obsidia_sigma_v130.py:110:    # ------------------------------------------------------------------
  sigma\obsidia_sigma_v130.py:111:    # Evaluation d'un step
  sigma\obsidia_sigma_v130.py:112:    # ------------------------------------------------------------------
  sigma\obsidia_sigma_v130.py:113:
  sigma\obsidia_sigma_v130.py:114:    def evaluate_step(
  sigma\obsidia_sigma_v130.py:115:        self,
> sigma\obsidia_sigma_v130.py:116:        severity: str,
  sigma\obsidia_sigma_v130.py:117:        risks: List[Any],
  sigma\obsidia_sigma_v130.py:118:        contras: List[Any],
  sigma\obsidia_sigma_v130.py:119:        current_hash: Optional[str] = None,
  sigma\obsidia_sigma_v130.py:120:    ) -> Dict[str, Any]:
  sigma\obsidia_sigma_v130.py:121:        """
  sigma\obsidia_sigma_v130.py:122:        Evalue un step de decision et met a jour l'historique.
  sigma\obsidia_sigma_v130.py:123:        Retourne le rapport de stabilite du step.
  sigma\obsidia_sigma_v130.py:124:        """
> sigma\obsidia_sigma_v130.py:125:        z_t = self._to_vector(severity, len(risks), len(contras))
  sigma\obsidia_sigma_v130.py:126:        t_t = time.time()
  sigma\obsidia_sigma_v130.py:127:
  sigma\obsidia_sigma_v130.py:128:        step_report: Dict[str, Any] = {
  sigma\obsidia_sigma_v130.py:129:            "step": len(self.steps),
> sigma\obsidia_sigma_v130.py:130:            "severity": severity,
  sigma\obsidia_sigma_v130.py:131:            "z": z_t,
  sigma\obsidia_sigma_v130.py:132:            "z_t": z_t,
  sigma\obsidia_sigma_v130.py:133:            "velocity": 0.0,
  sigma\obsidia_sigma_v130.py:134:            "acceleration": 0.0,
  sigma\obsidia_sigma_v130.py:135:            "stability_status": "STABLE",
  sigma\obsidia_sigma_v130.py:136:            "violations": [],
  sigma\protocols.py:20:        meta_vote = meta_agent.evaluate(aggregate)
  sigma\protocols.py:21:        aggregate.contradictions.extend(meta_vote.contradictions)
  sigma\protocols.py:22:        aggregate.unknowns.extend(meta_vote.unknowns)
> sigma\protocols.py:23:        aggregate.risk_flags.extend(meta_vote.risk_flags)
  sigma\protocols.py:24:        aggregate.evidence_refs.append(f"meta:{meta_vote.agent_id}")
  sigma\protocols.py:25:    return aggregate
  sigma\protocols.py:26:
  sigma\protocols.py:27:
  sigma\protocols.py:28:def run_trading_pipeline(state: TradingState) -> CanonicalDecisionEnvelope:
  sigma\protocols.py:29:    aggregate = aggregate_trading([a.evaluate(state) for a in build_trading_agents()])
  sigma\run_pipeline.py:62:
  sigma\run_pipeline.py:63:def apply_sigma(result_dict: dict, sigma: ObsidiaSigmaMonitor) -> dict:
  sigma\run_pipeline.py:64:    step_report = sigma.evaluate_step(
> sigma\run_pipeline.py:65:        severity=result_dict.get("severity", "S0"),
> sigma\run_pipeline.py:66:        risks=result_dict.get("risk_flags", []),
  sigma\run_pipeline.py:67:        contras=result_dict.get("contradictions", []),
  sigma\run_pipeline.py:68:    )
  sigma\run_pipeline.py:69:    sigma_report = sigma.export_to_proofkit()
  sigma\run_pipeline.py:70:    stability = sigma_report["V18_9_sigma_stability"]["status"]
  sigma\run_pipeline.py:71:
  sigma\run_pipeline.py:72:    if stability == "FAIL":
  sigma\run_pipeline.py:73:        result_dict["market_verdict"] = "HOLD_STABILITY_ALERT"
> sigma\run_pipeline.py:74:        result_dict["severity"] = "S4"
  sigma\run_pipeline.py:75:        result_dict["sigma_override"] = True
  sigma\run_pipeline.py:76:    else:
  sigma\run_pipeline.py:77:        result_dict["sigma_override"] = False
  sigma\run_pipeline.py:78:
  sigma\run_pipeline.py:79:    result_dict["sigma_step"] = step_report
  sigma\run_pipeline.py:80:    result_dict["sigma_report"] = sigma_report["V18_9_sigma_stability"]
  sigma\domains\bank_agents.py:1:from __future__ import annotations
  sigma\domains\bank_agents.py:2:
  sigma\domains\bank_agents.py:3:from ..base import BaseAgent
> sigma\domains\bank_agents.py:4:from ..contracts import AgentVote, BankState, Domain, Layer, Severity
  sigma\domains\bank_agents.py:5:
  sigma\domains\bank_agents.py:6:
  sigma\domains\bank_agents.py:7:class TransactionContextAgent(BaseAgent):
  sigma\domains\bank_agents.py:8:    agent_id = "TransactionContextAgent"
  sigma\domains\bank_agents.py:9:    def evaluate(self, state: BankState) -> AgentVote:
  sigma\domains\bank_agents.py:10:        unknowns = ["UNKNOWN_CHANNEL"] if not state.channel else []
> sigma\domains\bank_agents.py:11:        return AgentVote(self.agent_id, Domain.BANK, Layer.OBSERVATION, 
f"type={state.transaction_type}, channel={state.channel}", 0.8, Severity.S1, proposed_verdict="ANALYZE", 
unknowns=unknowns)
  sigma\domains\bank_agents.py:12:
  sigma\domains\bank_agents.py:13:
  sigma\domains\bank_agents.py:14:class CounterpartyAgent(BaseAgent):
  sigma\domains\bank_agents.py:15:    agent_id = "CounterpartyAgent"
  sigma\domains\bank_agents.py:16:    def evaluate(self, state: BankState) -> AgentVote:
  sigma\domains\bank_agents.py:17:        verdict = "AUTHORIZE" if state.counterparty_known and 
state.counterparty_age_days > 30 else "ANALYZE"
> sigma\domains\bank_agents.py:18:        return AgentVote(self.agent_id, Domain.BANK, Layer.OBSERVATION, 
f"counterparty_known={state.counterparty_known}, age_days={state.counterparty_age_days}", 0.75 if 
verdict=="AUTHORIZE" else 0.55, Severity.S1, proposed_verdict=verdict)
  sigma\domains\bank_agents.py:19:
  sigma\domains\bank_agents.py:20:
  sigma\domains\bank_agents.py:21:class LiquidityExposureAgent(BaseAgent):
  sigma\domains\bank_agents.py:22:    agent_id = "LiquidityExposureAgent"
  sigma\domains\bank_agents.py:23:    def evaluate(self, state: BankState) -> AgentVote:
  sigma\domains\bank_agents.py:24:        pressure = 1.0 if state.account_balance <= 0 else state.amount / 
max(state.account_balance, 1e-9)
  sigma\domains\bank_agents.py:25:        verdict = "BLOCK" if pressure > 0.9 else "ANALYZE" if pressure > 0.5 
else "AUTHORIZE"
> sigma\domains\bank_agents.py:26:        sev = Severity.S3 if verdict=="BLOCK" else Severity.S2 if 
verdict=="ANALYZE" else Severity.S1
> sigma\domains\bank_agents.py:27:        return AgentVote(self.agent_id, Domain.BANK, Layer.OBSERVATION, 
f"liquidity_pressure={pressure:.2f}", min(1.0, pressure), sev, proposed_verdict=verdict, 
risk_flags=["CASH_PRESSURE"] if pressure > 0.5 else [])
  sigma\domains\bank_agents.py:28:
  sigma\domains\bank_agents.py:29:
  sigma\domains\bank_agents.py:30:class BehaviorShiftAgent(BaseAgent):
  sigma\domains\bank_agents.py:31:    agent_id = "BehaviorShiftAgent"
  sigma\domains\bank_agents.py:32:    def evaluate(self, state: BankState) -> AgentVote:
  sigma\domains\bank_agents.py:33:        verdict = "ANALYZE" if state.behavior_shift_score > 0.5 else 
"AUTHORIZE"
> sigma\domains\bank_agents.py:34:        return AgentVote(self.agent_id, Domain.BANK, Layer.OBSERVATION, 
f"behavior_shift={state.behavior_shift_score:.2f}", state.behavior_shift_score, Severity.S2 if 
verdict=="ANALYZE" else Severity.S1, proposed_verdict=verdict)
  sigma\domains\bank_agents.py:35:
  sigma\domains\bank_agents.py:36:
  sigma\domains\bank_agents.py:37:class FraudPatternAgent(BaseAgent):
  sigma\domains\bank_agents.py:38:    agent_id = "FraudPatternAgent"
  sigma\domains\bank_agents.py:39:    def evaluate(self, state: BankState) -> AgentVote:
  sigma\domains\bank_agents.py:40:        verdict = "BLOCK" if state.fraud_score > 0.75 else "ANALYZE" if 
state.fraud_score > 0.45 else "AUTHORIZE"
> sigma\domains\bank_agents.py:41:        sev = Severity.S4 if verdict=="BLOCK" else Severity.S2 if 
verdict=="ANALYZE" else Severity.S1
> sigma\domains\bank_agents.py:42:        return AgentVote(self.agent_id, Domain.BANK, Layer.INTERPRETATION, 
f"fraud_score={state.fraud_score:.2f}", state.fraud_score, sev, proposed_verdict=verdict, 
risk_flags=["FRAUD_PATTERN"] if verdict!="AUTHORIZE" else [])
  sigma\domains\bank_agents.py:43:
  sigma\domains\bank_agents.py:44:
  sigma\domains\bank_agents.py:45:class LimitPolicyAgent(BaseAgent):
  sigma\domains\bank_agents.py:46:    agent_id = "LimitPolicyAgent"
  sigma\domains\bank_agents.py:47:    def evaluate(self, state: BankState) -> AgentVote:
  sigma\domains\bank_agents.py:48:        ratio = state.amount / max(state.policy_limit, 1e-9)
  sigma\domains\bank_agents.py:49:        verdict = "BLOCK" if ratio > 1.0 else "ANALYZE" if ratio > 0.8 else 
"AUTHORIZE"
> sigma\domains\bank_agents.py:50:        sev = Severity.S3 if verdict=="BLOCK" else Severity.S2 if 
verdict=="ANALYZE" else Severity.S1
> sigma\domains\bank_agents.py:51:        return AgentVote(self.agent_id, Domain.BANK, Layer.INTERPRETATION, 
f"limit_ratio={ratio:.2f}", min(1.0, ratio), sev, proposed_verdict=verdict, risk_flags=["LIMIT_PRESSURE"] if 
ratio > 0.8 else [])
  sigma\domains\bank_agents.py:52:
  sigma\domains\bank_agents.py:53:
  sigma\domains\bank_agents.py:54:class AffordabilityAgent(BaseAgent):
  sigma\domains\bank_agents.py:55:    agent_id = "AffordabilityAgent"
  sigma\domains\bank_agents.py:56:    def evaluate(self, state: BankState) -> AgentVote:
  sigma\domains\bank_agents.py:57:        verdict = "AUTHORIZE" if state.affordability_score > 0.7 else 
"ANALYZE" if state.affordability_score > 0.4 else "BLOCK"
> sigma\domains\bank_agents.py:58:        sev = Severity.S3 if verdict=="BLOCK" else Severity.S2 if 
verdict=="ANALYZE" else Severity.S1
  sigma\domains\bank_agents.py:59:        return AgentVote(self.agent_id, Domain.BANK, Layer.INTERPRETATION, 
f"affordability={state.affordability_score:.2f}", state.affordability_score, sev, proposed_verdict=verdict)
  sigma\domains\bank_agents.py:60:
  sigma\domains\bank_agents.py:61:
  sigma\domains\bank_agents.py:62:class TemporalUrgencyAgent(BaseAgent):
  sigma\domains\bank_agents.py:63:    agent_id = "TemporalUrgencyAgent"
  sigma\domains\bank_agents.py:64:    def evaluate(self, state: BankState) -> AgentVote:
  sigma\domains\bank_agents.py:65:        verdict = "ANALYZE" if state.urgency_score > 0.75 else "AUTHORIZE"
> sigma\domains\bank_agents.py:66:        return AgentVote(self.agent_id, Domain.BANK, Layer.INTERPRETATION, 
f"urgency={state.urgency_score:.2f}", state.urgency_score, Severity.S2 if verdict=="ANALYZE" else Severity.S1, 
proposed_verdict=verdict, contradictions=["URGENT_BEHAVIOR"] if verdict=="ANALYZE" else [])
  sigma\domains\bank_agents.py:67:
  sigma\domains\bank_agents.py:68:
  sigma\domains\bank_agents.py:69:class IdentityMismatchAgent(BaseAgent):
  sigma\domains\bank_agents.py:70:    agent_id = "IdentityMismatchAgent"
  sigma\domains\bank_agents.py:71:    def evaluate(self, state: BankState) -> AgentVote:
  sigma\domains\bank_agents.py:72:        combined = max(state.identity_mismatch_score, 1 - 
state.device_trust_score)
  sigma\domains\bank_agents.py:73:        verdict = "BLOCK" if combined > 0.75 else "ANALYZE" if combined > 0.4 
else "AUTHORIZE"
> sigma\domains\bank_agents.py:74:        sev = Severity.S4 if verdict=="BLOCK" else Severity.S2 if 
verdict=="ANALYZE" else Severity.S1
  sigma\domains\bank_agents.py:75:        return AgentVote(self.agent_id, Domain.BANK, Layer.CONTRADICTION, 
f"identity_mismatch={combined:.2f}", combined, sev, proposed_verdict=verdict, 
contradictions=["IDENTITY_CONTEXT_MISMATCH"] if combined > 0.4 else [])
  sigma\domains\bank_agents.py:76:
  sigma\domains\bank_agents.py:77:
  sigma\domains\bank_agents.py:78:class NarrativeConflictAgent(BaseAgent):
  sigma\domains\bank_agents.py:79:    agent_id = "NarrativeConflictAgent"
  sigma\domains\bank_agents.py:80:    def evaluate(self, state: BankState) -> AgentVote:
  sigma\domains\bank_agents.py:81:        verdict = "ANALYZE" if state.narrative_conflict_score > 0.45 else 
"AUTHORIZE"
> sigma\domains\bank_agents.py:82:        return AgentVote(self.agent_id, Domain.BANK, Layer.CONTRADICTION, 
f"narrative_conflict={state.narrative_conflict_score:.2f}", state.narrative_conflict_score, Severity.S2 if 
verdict=="ANALYZE" else Severity.S1, proposed_verdict=verdict, contradictions=["NARRATIVE_CONFLICT"] if 
verdict=="ANALYZE" else [])
  sigma\domains\bank_agents.py:83:
  sigma\domains\bank_agents.py:84:
  sigma\domains\bank_agents.py:85:class RecoveryPathAgent(BaseAgent):
  sigma\domains\bank_agents.py:86:    agent_id = "RecoveryPathAgent"
  sigma\domains\bank_agents.py:87:    def evaluate(self, state: BankState) -> AgentVote:
  sigma\domains\bank_agents.py:88:        claim = "manual confirmation / delayed verification path available"
> sigma\domains\bank_agents.py:89:        return AgentVote(self.agent_id, Domain.BANK, Layer.PROOF, claim, 
0.85, Severity.S1, proposed_verdict="ANALYZE")
  sigma\domains\bank_agents.py:90:
  sigma\domains\bank_agents.py:91:
  sigma\domains\bank_agents.py:92:class BankProofAgent(BaseAgent):
  sigma\domains\bank_agents.py:93:    agent_id = "BankProofAgent"
  sigma\domains\bank_agents.py:94:    def evaluate(self, state: BankState) -> AgentVote:
  sigma\domains\bank_agents.py:95:        unknowns = []
  sigma\domains\bank_agents.py:98:        if state.recent_failed_attempts > 0:
  sigma\domains\bank_agents.py:99:            unknowns.append("RECENT_FAILED_ATTEMPTS")
  sigma\domains\bank_agents.py:100:        verdict = "ANALYZE" if unknowns else "AUTHORIZE"
> sigma\domains\bank_agents.py:101:        return AgentVote(self.agent_id, Domain.BANK, Layer.PROOF, "bank 
proof readiness", 0.9 if not unknowns else 0.45, Severity.S2 if unknowns else Severity.S0, 
proposed_verdict=verdict, unknowns=unknowns)
  sigma\domains\bank_agents.py:102:
  sigma\domains\bank_agents.py:103:
  sigma\domains\bank_agents.py:104:def build_bank_agents() -> list[BaseAgent]:
  sigma\domains\bank_agents.py:105:    return [
  sigma\domains\bank_agents.py:106:        TransactionContextAgent(),
  sigma\domains\bank_agents.py:107:        CounterpartyAgent(),
  sigma\domains\ecom_agents.py:1:from __future__ import annotations
  sigma\domains\ecom_agents.py:2:
  sigma\domains\ecom_agents.py:3:from ..base import BaseAgent
> sigma\domains\ecom_agents.py:4:from ..contracts import AgentVote, Domain, EcomState, Layer, Severity
  sigma\domains\ecom_agents.py:5:
  sigma\domains\ecom_agents.py:6:
  sigma\domains\ecom_agents.py:7:class TrafficQualityAgent(BaseAgent):
  sigma\domains\ecom_agents.py:8:    agent_id = "TrafficQualityAgent"
  sigma\domains\ecom_agents.py:9:    def evaluate(self, state: EcomState) -> AgentVote:
  sigma\domains\ecom_agents.py:10:        verdict = "PAY" if state.traffic_quality > 0.7 else "WAIT" if 
state.traffic_quality > 0.4 else "REFUSE"
> sigma\domains\ecom_agents.py:11:        sev = Severity.S2 if verdict=="REFUSE" else Severity.S1
  sigma\domains\ecom_agents.py:12:        return AgentVote(self.agent_id, Domain.ECOM, Layer.OBSERVATION, 
f"traffic_quality={state.traffic_quality:.2f}", state.traffic_quality, sev, proposed_verdict=verdict)
  sigma\domains\ecom_agents.py:13:
  sigma\domains\ecom_agents.py:14:
  sigma\domains\ecom_agents.py:15:class BasketIntentAgent(BaseAgent):
  sigma\domains\ecom_agents.py:16:    agent_id = "BasketIntentAgent"
  sigma\domains\ecom_agents.py:17:    def evaluate(self, state: EcomState) -> AgentVote:
  sigma\domains\ecom_agents.py:18:        verdict = "PAY" if state.basket_intent_score > 0.7 else "WAIT" if 
state.basket_intent_score > 0.4 else "REFUSE"
> sigma\domains\ecom_agents.py:19:        return AgentVote(self.agent_id, Domain.ECOM, Layer.OBSERVATION, 
f"basket_intent={state.basket_intent_score:.2f}", state.basket_intent_score, Severity.S1, 
proposed_verdict=verdict)
  sigma\domains\ecom_agents.py:20:
  sigma\domains\ecom_agents.py:21:
  sigma\domains\ecom_agents.py:22:class OfferHealthAgent(BaseAgent):
  sigma\domains\ecom_agents.py:23:    agent_id = "OfferHealthAgent"
  sigma\domains\ecom_agents.py:24:    def evaluate(self, state: EcomState) -> AgentVote:
  sigma\domains\ecom_agents.py:25:        verdict = "REFUSE" if not state.stock_ok or state.margin_rate < 0 
else "WAIT" if state.margin_rate < 0.1 else "PAY"
> sigma\domains\ecom_agents.py:26:        sev = Severity.S3 if verdict=="REFUSE" else Severity.S2 if 
verdict=="WAIT" else Severity.S1
  sigma\domains\ecom_agents.py:27:        return AgentVote(self.agent_id, Domain.ECOM, Layer.OBSERVATION, 
f"stock_ok={state.stock_ok}, margin={state.margin_rate:.2f}", 0.8, sev, proposed_verdict=verdict)
  sigma\domains\ecom_agents.py:28:
  sigma\domains\ecom_agents.py:29:
  sigma\domains\ecom_agents.py:30:class CustomerTrustAgent(BaseAgent):
  sigma\domains\ecom_agents.py:31:    agent_id = "CustomerTrustAgent"
  sigma\domains\ecom_agents.py:32:    def evaluate(self, state: EcomState) -> AgentVote:
  sigma\domains\ecom_agents.py:33:        verdict = "PAY" if state.customer_trust > 0.7 else "WAIT" if 
state.customer_trust > 0.4 else "REFUSE"
> sigma\domains\ecom_agents.py:34:        return AgentVote(self.agent_id, Domain.ECOM, Layer.OBSERVATION, 
f"customer_trust={state.customer_trust:.2f}", state.customer_trust, Severity.S1, proposed_verdict=verdict)
  sigma\domains\ecom_agents.py:35:
  sigma\domains\ecom_agents.py:36:
  sigma\domains\ecom_agents.py:37:class ConversionReadinessAgent(BaseAgent):
  sigma\domains\ecom_agents.py:38:    agent_id = "ConversionReadinessAgent"
  sigma\domains\ecom_agents.py:39:    def evaluate(self, state: EcomState) -> AgentVote:
  sigma\domains\ecom_agents.py:40:        verdict = "PAY" if state.conversion_readiness > 0.75 else "WAIT" if 
state.conversion_readiness > 0.45 else "REFUSE"
> sigma\domains\ecom_agents.py:41:        return AgentVote(self.agent_id, Domain.ECOM, Layer.INTERPRETATION, 
f"conversion_readiness={state.conversion_readiness:.2f}", state.conversion_readiness, Severity.S1, 
proposed_verdict=verdict)
  sigma\domains\ecom_agents.py:42:
  sigma\domains\ecom_agents.py:43:
  sigma\domains\ecom_agents.py:44:class MarginProtectionAgent(BaseAgent):
  sigma\domains\ecom_agents.py:45:    agent_id = "MarginProtectionAgent"
  sigma\domains\ecom_agents.py:46:    def evaluate(self, state: EcomState) -> AgentVote:
  sigma\domains\ecom_agents.py:47:        verdict = "REFUSE" if state.margin_rate < 0.05 else "WAIT" if 
state.margin_rate < 0.15 else "PAY"
> sigma\domains\ecom_agents.py:48:        sev = Severity.S3 if verdict=="REFUSE" else Severity.S2 if 
verdict=="WAIT" else Severity.S1
> sigma\domains\ecom_agents.py:49:        return AgentVote(self.agent_id, Domain.ECOM, Layer.INTERPRETATION, 
f"margin_rate={state.margin_rate:.2f}", min(1.0, max(0.0, 1-state.margin_rate)), sev, proposed_verdict=verdict, 
risk_flags=["LOW_MARGIN"] if verdict!="PAY" else [])
  sigma\domains\ecom_agents.py:50:
  sigma\domains\ecom_agents.py:51:
  sigma\domains\ecom_agents.py:52:class ROASRealityAgent(BaseAgent):
  sigma\domains\ecom_agents.py:53:    agent_id = "ROASRealityAgent"
  sigma\domains\ecom_agents.py:54:    def evaluate(self, state: EcomState) -> AgentVote:
  sigma\domains\ecom_agents.py:55:        verdict = "PAY" if state.roas > 2.0 else "WAIT" if state.roas > 1.0 
else "REFUSE"
> sigma\domains\ecom_agents.py:56:        sev = Severity.S2 if verdict=="REFUSE" else Severity.S1
> sigma\domains\ecom_agents.py:57:        return AgentVote(self.agent_id, Domain.ECOM, Layer.INTERPRETATION, 
f"roas={state.roas:.2f}", min(1.0, state.roas/4), sev, proposed_verdict=verdict, risk_flags=["LOW_ROAS"] if 
verdict=="REFUSE" else [])
  sigma\domains\ecom_agents.py:58:
  sigma\domains\ecom_agents.py:59:
  sigma\domains\ecom_agents.py:60:class FulfillmentRiskAgent(BaseAgent):
  sigma\domains\ecom_agents.py:61:    agent_id = "FulfillmentRiskAgent"
  sigma\domains\ecom_agents.py:62:    def evaluate(self, state: EcomState) -> AgentVote:
  sigma\domains\ecom_agents.py:63:        verdict = "REFUSE" if state.fulfillment_risk > 0.75 else "WAIT" if 
state.fulfillment_risk > 0.45 else "PAY"
> sigma\domains\ecom_agents.py:64:        sev = Severity.S3 if verdict=="REFUSE" else Severity.S2 if 
verdict=="WAIT" else Severity.S1
  sigma\domains\ecom_agents.py:65:        return AgentVote(self.agent_id, Domain.ECOM, Layer.INTERPRETATION, 
f"fulfillment_risk={state.fulfillment_risk:.2f}", state.fulfillment_risk, sev, proposed_verdict=verdict)
  sigma\domains\ecom_agents.py:66:
  sigma\domains\ecom_agents.py:67:
  sigma\domains\ecom_agents.py:68:class IntentConflictAgent(BaseAgent):
  sigma\domains\ecom_agents.py:69:    agent_id = "IntentConflictAgent"
  sigma\domains\ecom_agents.py:70:    def evaluate(self, state: EcomState) -> AgentVote:
  sigma\domains\ecom_agents.py:71:        verdict = "WAIT" if state.intent_conflict_score > 0.4 else "PAY"
> sigma\domains\ecom_agents.py:72:        sev = Severity.S2 if verdict=="WAIT" else Severity.S1
  sigma\domains\ecom_agents.py:73:        return AgentVote(self.agent_id, Domain.ECOM, Layer.CONTRADICTION, 
f"intent_conflict={state.intent_conflict_score:.2f}", state.intent_conflict_score, sev, 
proposed_verdict=verdict, contradictions=["INTENT_CONFLICT"] if verdict=="WAIT" else [])
  sigma\domains\ecom_agents.py:74:
  sigma\domains\ecom_agents.py:75:
  sigma\domains\ecom_agents.py:76:class CheckoutFrictionAgent(BaseAgent):
  sigma\domains\ecom_agents.py:77:    agent_id = "CheckoutFrictionAgent"
  sigma\domains\ecom_agents.py:78:    def evaluate(self, state: EcomState) -> AgentVote:
  sigma\domains\ecom_agents.py:79:        verdict = "WAIT" if state.checkout_friction_score > 0.45 else "PAY"
> sigma\domains\ecom_agents.py:80:        sev = Severity.S2 if verdict=="WAIT" else Severity.S1
  sigma\domains\ecom_agents.py:81:        return AgentVote(self.agent_id, Domain.ECOM, Layer.CONTRADICTION, 
f"checkout_friction={state.checkout_friction_score:.2f}", state.checkout_friction_score, sev, 
proposed_verdict=verdict, contradictions=["CHECKOUT_FRICTION"] if verdict=="WAIT" else [])
  sigma\domains\ecom_agents.py:82:
  sigma\domains\ecom_agents.py:83:
  sigma\domains\ecom_agents.py:84:class MerchantPolicyAgent(BaseAgent):
  sigma\domains\ecom_agents.py:85:    agent_id = "MerchantPolicyAgent"
  sigma\domains\ecom_agents.py:86:    def evaluate(self, state: EcomState) -> AgentVote:
  sigma\domains\ecom_agents.py:87:        verdict = "REFUSE" if state.merchant_policy_score < 0.2 else "WAIT" 
if state.merchant_policy_score < 0.5 else "PAY"
> sigma\domains\ecom_agents.py:88:        sev = Severity.S3 if verdict=="REFUSE" else Severity.S2 if 
verdict=="WAIT" else Severity.S1
> sigma\domains\ecom_agents.py:89:        return AgentVote(self.agent_id, Domain.ECOM, Layer.CONTRADICTION, 
f"merchant_policy={state.merchant_policy_score:.2f}", 1-state.merchant_policy_score, sev, 
proposed_verdict=verdict, risk_flags=["MERCHANT_POLICY_CONSTRAINT"] if verdict!="PAY" else [])
  sigma\domains\ecom_agents.py:90:
  sigma\domains\ecom_agents.py:91:
  sigma\domains\ecom_agents.py:92:class EcomProofAgent(BaseAgent):
  sigma\domains\ecom_agents.py:93:    agent_id = "EcomProofAgent"
  sigma\domains\ecom_agents.py:94:    def evaluate(self, state: EcomState) -> AgentVote:
  sigma\domains\ecom_agents.py:95:        unknowns = []
  sigma\domains\ecom_agents.py:98:        if state.order_value <= 0:
  sigma\domains\ecom_agents.py:99:            unknowns.append("NO_ORDER_VALUE")
  sigma\domains\ecom_agents.py:100:        verdict = "WAIT" if unknowns else "PAY"
> sigma\domains\ecom_agents.py:101:        return AgentVote(self.agent_id, Domain.ECOM, Layer.PROOF, "ecom 
proof readiness", 0.9 if not unknowns else 0.45, Severity.S2 if unknowns else Severity.S0, 
proposed_verdict=verdict, unknowns=unknowns)
  sigma\domains\ecom_agents.py:102:
  sigma\domains\ecom_agents.py:103:
  sigma\domains\ecom_agents.py:104:def build_ecom_agents() -> list[BaseAgent]:
  sigma\domains\ecom_agents.py:105:    return [
  sigma\domains\ecom_agents.py:106:        TrafficQualityAgent(),
  sigma\domains\ecom_agents.py:107:        BasketIntentAgent(),
  sigma\domains\gps_defense_aviation_agents.py:1:from __future__ import annotations
  sigma\domains\gps_defense_aviation_agents.py:2:
  sigma\domains\gps_defense_aviation_agents.py:3:from ..base import BaseAgent
> sigma\domains\gps_defense_aviation_agents.py:4:from ..contracts import AgentVote, Domain, Layer, Severity, 
GpsDefenseAviationState
  sigma\domains\gps_defense_aviation_agents.py:5:
  sigma\domains\gps_defense_aviation_agents.py:6:class SourceAvailabilityAgent(BaseAgent):
  sigma\domains\gps_defense_aviation_agents.py:7:    agent_id = "SourceAvailabilityAgent"
  sigma\domains\gps_defense_aviation_agents.py:8:    def evaluate(self, state: GpsDefenseAviationState) -> 
AgentVote:
  sigma\domains\gps_defense_aviation_agents.py:9:        missing = []
  sigma\domains\gps_defense_aviation_agents.py:10:        if not state.gps_available:
  sigma\domains\gps_defense_aviation_agents.py:18:            domain=Domain.GPS_DEFENSE_AVIATION,
  sigma\domains\gps_defense_aviation_agents.py:19:            layer=Layer.OBSERVATION,
  sigma\domains\gps_defense_aviation_agents.py:20:            claim="source availability",
> sigma\domains\gps_defense_aviation_agents.py:21:            confidence=0.95 if not missing else 0.35,
> sigma\domains\gps_defense_aviation_agents.py:22:            severity_hint=Severity.S0 if not missing else 
Severity.S3,
  sigma\domains\gps_defense_aviation_agents.py:23:            unknowns=missing,
  sigma\domains\gps_defense_aviation_agents.py:24:            proposed_verdict="RECALC_TRAJECTORY" if missing 
else "TRAJECTORY_VALID",
  sigma\domains\gps_defense_aviation_agents.py:25:        )
  sigma\domains\gps_defense_aviation_agents.py:26:
  sigma\domains\gps_defense_aviation_agents.py:27:class TrajectoryIntegrityAgent(BaseAgent):
  sigma\domains\gps_defense_aviation_agents.py:28:    agent_id = "TrajectoryIntegrityAgent"
  sigma\domains\gps_defense_aviation_agents.py:36:            Layer.INTERPRETATION,
  sigma\domains\gps_defense_aviation_agents.py:37:            "trajectory integrity",
  sigma\domains\gps_defense_aviation_agents.py:38:            max(0.0, 1.0 - drift),
> sigma\domains\gps_defense_aviation_agents.py:39:            Severity.S4 if drift >= 0.85 else Severity.S2 if 
drift >= 0.6 else Severity.S0,
> sigma\domains\gps_defense_aviation_agents.py:40:            risk_flags=risk,
  sigma\domains\gps_defense_aviation_agents.py:41:            proposed_verdict=verdict,
  sigma\domains\gps_defense_aviation_agents.py:42:        )
  sigma\domains\gps_defense_aviation_agents.py:43:
  sigma\domains\gps_defense_aviation_agents.py:44:class SourceConflictAgent(BaseAgent):
  sigma\domains\gps_defense_aviation_agents.py:45:    agent_id = "SourceConflictAgent"
  sigma\domains\gps_defense_aviation_agents.py:46:    def evaluate(self, state: GpsDefenseAviationState) -> 
AgentVote:
  sigma\domains\gps_defense_aviation_agents.py:53:            Layer.CONTRADICTION,
  sigma\domains\gps_defense_aviation_agents.py:54:            "source conflict",
  sigma\domains\gps_defense_aviation_agents.py:55:            max(0.0, 1.0 - conflict),
> sigma\domains\gps_defense_aviation_agents.py:56:            Severity.S4 if conflict >= 0.8 else Severity.S2 
if conflict >= 0.5 else Severity.S0,
  sigma\domains\gps_defense_aviation_agents.py:57:            contradictions=contradictions,
  sigma\domains\gps_defense_aviation_agents.py:58:            proposed_verdict=verdict,
  sigma\domains\gps_defense_aviation_agents.py:59:        )
  sigma\domains\gps_defense_aviation_agents.py:60:
  sigma\domains\gps_defense_aviation_agents.py:61:class TimeSkewAgent(BaseAgent):
  sigma\domains\gps_defense_aviation_agents.py:62:    agent_id = "TimeSkewAgent"
  sigma\domains\gps_defense_aviation_agents.py:71:            Layer.PROOF,
  sigma\domains\gps_defense_aviation_agents.py:72:            "time skew",
  sigma\domains\gps_defense_aviation_agents.py:73:            max(0.0, 1.0 - skew),
> sigma\domains\gps_defense_aviation_agents.py:74:            Severity.S4 if skew >= 0.9 else Severity.S3 if 
skew >= 0.8 else Severity.S2 if skew >= 0.5 else Severity.S0,
> sigma\domains\gps_defense_aviation_agents.py:75:            risk_flags=risk,
  sigma\domains\gps_defense_aviation_agents.py:76:            unknowns=severe_unknowns,
  sigma\domains\gps_defense_aviation_agents.py:77:            proposed_verdict=verdict,
  sigma\domains\gps_defense_aviation_agents.py:78:        )
  sigma\domains\gps_defense_aviation_agents.py:79:
  sigma\domains\gps_defense_aviation_agents.py:80:class BrownoutAgent(BaseAgent):
  sigma\domains\gps_defense_aviation_agents.py:81:    agent_id = "BrownoutAgent"
  sigma\domains\gps_defense_aviation_agents.py:90:            Layer.OBSERVATION,
  sigma\domains\gps_defense_aviation_agents.py:91:            "brownout",
  sigma\domains\gps_defense_aviation_agents.py:92:            max(0.0, 1.0 - b),
> sigma\domains\gps_defense_aviation_agents.py:93:            Severity.S4 if b >= 0.9 else Severity.S3 if b >= 
0.8 else Severity.S2 if b >= 0.5 else Severity.S0,
> sigma\domains\gps_defense_aviation_agents.py:94:            risk_flags=risk,
  sigma\domains\gps_defense_aviation_agents.py:95:            unknowns=severe_unknowns,
  sigma\domains\gps_defense_aviation_agents.py:96:            proposed_verdict=verdict,
  sigma\domains\gps_defense_aviation_agents.py:97:        )
  sigma\domains\gps_defense_aviation_agents.py:98:
  sigma\domains\gps_defense_aviation_agents.py:99:class AttestationReadinessAgent(BaseAgent):
  sigma\domains\gps_defense_aviation_agents.py:100:    agent_id = "GpsAttestationReadinessAgent"
  sigma\domains\gps_defense_aviation_agents.py:106:            Layer.PROOF,
  sigma\domains\gps_defense_aviation_agents.py:107:            "attestation readiness",
  sigma\domains\gps_defense_aviation_agents.py:108:            0.9 if ready else 0.4,
> sigma\domains\gps_defense_aviation_agents.py:109:            Severity.S0 if ready else Severity.S2,
  sigma\domains\gps_defense_aviation_agents.py:110:            unknowns=[] if ready else 
["ATTESTATION_NOT_READY"],
  sigma\domains\gps_defense_aviation_agents.py:111:            proposed_verdict="TRAJECTORY_VALID" if ready 
else "RECALC_TRAJECTORY",
  sigma\domains\gps_defense_aviation_agents.py:112:        )
  sigma\domains\gps_defense_aviation_agents.py:113:
  sigma\domains\gps_defense_aviation_agents.py:114:def build_gps_defense_aviation_agents():
  sigma\domains\gps_defense_aviation_agents.py:115:    return [
  sigma\domains\meta_agents.py:1:from __future__ import annotations
  sigma\domains\meta_agents.py:2:
  sigma\domains\meta_agents.py:3:from ..base import BaseAgent
> sigma\domains\meta_agents.py:4:from ..contracts import AgentVote, Domain, DomainAggregate, Layer, Severity
  sigma\domains\meta_agents.py:5:
  sigma\domains\meta_agents.py:6:
  sigma\domains\meta_agents.py:7:class BaseMetaAgent(BaseAgent):
  sigma\domains\meta_agents.py:8:    def evaluate(self, aggregate: DomainAggregate) -> AgentVote:
  sigma\domains\meta_agents.py:9:        raise NotImplementedError
  sigma\domains\meta_agents.py:10:
  sigma\domains\meta_agents.py:12:class UnknownsAgent(BaseMetaAgent):
  sigma\domains\meta_agents.py:13:    agent_id = "UnknownsAgent"
  sigma\domains\meta_agents.py:14:    def evaluate(self, aggregate: DomainAggregate) -> AgentVote:
> sigma\domains\meta_agents.py:15:        sev = Severity.S2 if aggregate.unknowns else Severity.S0
  sigma\domains\meta_agents.py:16:        return AgentVote(self.agent_id, Domain.META, Layer.CONTRADICTION, 
f"unknowns={len(aggregate.unknowns)}", 0.9 if aggregate.unknowns else 0.3, sev, proposed_verdict="HOLD" if 
aggregate.unknowns else aggregate.market_verdict, unknowns=list(aggregate.unknowns))
  sigma\domains\meta_agents.py:17:
  sigma\domains\meta_agents.py:18:
  sigma\domains\meta_agents.py:19:class ConflictResolutionAgent(BaseMetaAgent):
  sigma\domains\meta_agents.py:20:    agent_id = "ConflictResolutionAgent"
  sigma\domains\meta_agents.py:21:    def evaluate(self, aggregate: DomainAggregate) -> AgentVote:
> sigma\domains\meta_agents.py:22:        sev = Severity.S3 if aggregate.contradictions else Severity.S0
  sigma\domains\meta_agents.py:23:        return AgentVote(self.agent_id, Domain.META, Layer.CONTRADICTION, 
f"contradictions={len(aggregate.contradictions)}", 0.95 if aggregate.contradictions else 0.2, sev, 
proposed_verdict="HOLD" if aggregate.contradictions else aggregate.market_verdict, 
contradictions=list(aggregate.contradictions))
  sigma\domains\meta_agents.py:24:
  sigma\domains\meta_agents.py:25:
  sigma\domains\meta_agents.py:26:class PolicyScopeAgent(BaseMetaAgent):
  sigma\domains\meta_agents.py:27:    agent_id = "PolicyScopeAgent"
  sigma\domains\meta_agents.py:28:    def evaluate(self, aggregate: DomainAggregate) -> AgentVote:
> sigma\domains\meta_agents.py:29:        blocked = any(flag in {"LIMIT_PRESSURE", 
"MERCHANT_POLICY_CONSTRAINT"} for flag in aggregate.risk_flags)
> sigma\domains\meta_agents.py:30:        return AgentVote(self.agent_id, Domain.META, Layer.CONTRADICTION, 
"policy scope validation", 0.9 if blocked else 0.4, Severity.S3 if blocked else Severity.S1, 
proposed_verdict="BLOCK" if blocked else aggregate.market_verdict)
  sigma\domains\meta_agents.py:31:
  sigma\domains\meta_agents.py:32:
  sigma\domains\meta_agents.py:33:class TicketReadinessAgent(BaseMetaAgent):
  sigma\domains\meta_agents.py:34:    agent_id = "TicketReadinessAgent"
  sigma\domains\meta_agents.py:35:    def evaluate(self, aggregate: DomainAggregate) -> AgentVote:
  sigma\domains\meta_agents.py:36:        ready = not aggregate.unknowns and not aggregate.contradictions
> sigma\domains\meta_agents.py:37:        return AgentVote(self.agent_id, Domain.META, Layer.PROOF, "ticket 
readiness", 0.9 if ready else 0.35, Severity.S0 if ready else Severity.S2, 
proposed_verdict=aggregate.market_verdict, unknowns=[] if ready else ["TICKET_NOT_READY"])
  sigma\domains\meta_agents.py:38:
  sigma\domains\meta_agents.py:39:
  sigma\domains\meta_agents.py:40:class TraceIntegrityAgent(BaseMetaAgent):
  sigma\domains\meta_agents.py:41:    agent_id = "TraceIntegrityAgent"
  sigma\domains\meta_agents.py:42:    def evaluate(self, aggregate: DomainAggregate) -> AgentVote:
  sigma\domains\meta_agents.py:43:        ready = len(aggregate.agent_votes) >= 3 and 
len(aggregate.evidence_refs) >= 1
> sigma\domains\meta_agents.py:44:        return AgentVote(self.agent_id, Domain.META, Layer.PROOF, 
f"trace_evidence={len(aggregate.evidence_refs)}", 0.9 if ready else 0.4, Severity.S0 if ready else Severity.S2, 
proposed_verdict=aggregate.market_verdict, unknowns=[] if ready else ["TRACE_INCOMPLETE"])
  sigma\domains\meta_agents.py:45:
  sigma\domains\meta_agents.py:46:
  sigma\domains\meta_agents.py:47:class AttestationReadinessAgent(BaseMetaAgent):
  sigma\domains\meta_agents.py:48:    agent_id = "AttestationReadinessAgent"
  sigma\domains\meta_agents.py:49:    def evaluate(self, aggregate: DomainAggregate) -> AgentVote:
  sigma\domains\meta_agents.py:50:        ready = "proof_ready" in aggregate.extra_metrics
> sigma\domains\meta_agents.py:51:        return AgentVote(self.agent_id, Domain.META, Layer.PROOF, 
"attestation readiness", 0.85 if ready else 0.4, Severity.S0 if ready else Severity.S2, 
proposed_verdict=aggregate.market_verdict, unknowns=[] if ready else ["ATTESTATION_NOT_READY"])
  sigma\domains\meta_agents.py:52:
  sigma\domains\meta_agents.py:53:
  sigma\domains\meta_agents.py:54:class HumanOverrideEligibilityAgent(BaseMetaAgent):
  sigma\domains\meta_agents.py:55:    agent_id = "HumanOverrideEligibilityAgent"
  sigma\domains\meta_agents.py:56:    def evaluate(self, aggregate: DomainAggregate) -> AgentVote:
> sigma\domains\meta_agents.py:57:        eligible = aggregate.market_verdict in {"ANALYZE", "WAIT", "REVIEW", 
"HOLD"} or aggregate.confidence < 0.65
> sigma\domains\meta_agents.py:58:        return AgentVote(self.agent_id, Domain.META, Layer.PROOF, 
f"human_override={eligible}", 0.9 if eligible else 0.5, Severity.S1, proposed_verdict=aggregate.market_verdict)
  sigma\domains\meta_agents.py:59:
  sigma\domains\meta_agents.py:60:
> sigma\domains\meta_agents.py:61:class SeverityClassifierAgent(BaseMetaAgent):
> sigma\domains\meta_agents.py:62:    agent_id = "SeverityClassifierAgent"
  sigma\domains\meta_agents.py:63:    def evaluate(self, aggregate: DomainAggregate) -> AgentVote:
  sigma\domains\meta_agents.py:64:        score = 0
  sigma\domains\meta_agents.py:65:        score += len(aggregate.unknowns)
  sigma\domains\meta_agents.py:66:        score += len(aggregate.contradictions) * 2
> sigma\domains\meta_agents.py:67:        score += len(aggregate.risk_flags)
> sigma\domains\meta_agents.py:68:        severity = Severity.S4 if score >= 5 else Severity.S3 if score >= 3 
else Severity.S2 if score >= 1 else Severity.S0
> sigma\domains\meta_agents.py:69:        return AgentVote(self.agent_id, Domain.META, Layer.PROOF, 
f"severity_classified={severity.value}", min(1.0, 0.4 + score * 0.1), severity, 
proposed_verdict=aggregate.market_verdict)
  sigma\domains\meta_agents.py:70:
  sigma\domains\meta_agents.py:71:
  sigma\domains\meta_agents.py:72:class ReplayConsistencyAgent(BaseMetaAgent):
  sigma\domains\meta_agents.py:73:    agent_id = "ReplayConsistencyAgent"
  sigma\domains\meta_agents.py:74:    def evaluate(self, aggregate: DomainAggregate) -> AgentVote:
  sigma\domains\meta_agents.py:75:        deterministic = aggregate.extra_metrics.get("deterministic", True)
> sigma\domains\meta_agents.py:76:        return AgentVote(self.agent_id, Domain.META, Layer.PROOF, 
f"deterministic={deterministic}", 0.9 if deterministic else 0.4, Severity.S0 if deterministic else Severity.S2, 
proposed_verdict=aggregate.market_verdict)
  sigma\domains\meta_agents.py:77:
  sigma\domains\meta_agents.py:78:
  sigma\domains\meta_agents.py:79:class ProofConsistencyAgent(BaseMetaAgent):
  sigma\domains\meta_agents.py:80:    agent_id = "ProofConsistencyAgent"
  sigma\domains\meta_agents.py:81:    def evaluate(self, aggregate: DomainAggregate) -> AgentVote:
> sigma\domains\meta_agents.py:82:        coherent = bool(aggregate.market_verdict) and aggregate.confidence >= 
0.0
> sigma\domains\meta_agents.py:83:        return AgentVote(self.agent_id, Domain.META, Layer.PROOF, 
"payload/ticket/trace/severity coherence", 0.95 if coherent else 0.2, Severity.S0 if coherent else Severity.S3, 
proposed_verdict=aggregate.market_verdict)
  sigma\domains\meta_agents.py:84:
  sigma\domains\meta_agents.py:85:
  sigma\domains\meta_agents.py:86:def build_meta_agents() -> list[BaseMetaAgent]:
  sigma\domains\meta_agents.py:87:    return [
  sigma\domains\meta_agents.py:88:        UnknownsAgent(),
  sigma\domains\meta_agents.py:89:        ConflictResolutionAgent(),
  sigma\domains\meta_agents.py:92:        TraceIntegrityAgent(),
  sigma\domains\meta_agents.py:93:        AttestationReadinessAgent(),
  sigma\domains\meta_agents.py:94:        HumanOverrideEligibilityAgent(),
> sigma\domains\meta_agents.py:95:        SeverityClassifierAgent(),
  sigma\domains\meta_agents.py:96:        ReplayConsistencyAgent(),
  sigma\domains\meta_agents.py:97:        ProofConsistencyAgent(),
  sigma\domains\meta_agents.py:98:    ]
  sigma\domains\trading_agents.py:3:from typing import List
  sigma\domains\trading_agents.py:4:
  sigma\domains\trading_agents.py:5:from ..base import BaseAgent
> sigma\domains\trading_agents.py:6:from ..contracts import AgentVote, Domain, Layer, Severity, TradingState
  sigma\domains\trading_agents.py:7:from ..utils.indicators import rsi, zscore, bollinger, realized_volatility
  sigma\domains\trading_agents.py:8:
  sigma\domains\trading_agents.py:9:
  sigma\domains\trading_agents.py:10:def _ret(values: List[float], n: int = 1) -> float:
  sigma\domains\trading_agents.py:11:    if len(values) < n + 1 or values[-n - 1] == 0:
  sigma\domains\trading_agents.py:12:        return 0.0
  sigma\domains\trading_agents.py:18:    def evaluate(self, state: TradingState) -> AgentVote:
  sigma\domains\trading_agents.py:19:        change = _ret(state.prices, 1)
  sigma\domains\trading_agents.py:20:        verdict = "BUY" if change > 0.001 else "SELL" if change < -0.001 
else "HOLD"
> sigma\domains\trading_agents.py:21:        return AgentVote(self.agent_id, Domain.TRADING, Layer.OBSERVATION, 
f"1-step return={change:.4f}", min(1.0, abs(change)*25), Severity.S1, proposed_verdict=verdict)
  sigma\domains\trading_agents.py:22:
  sigma\domains\trading_agents.py:23:
  sigma\domains\trading_agents.py:24:class LiquidityAgent(BaseAgent):
  sigma\domains\trading_agents.py:25:    agent_id = "LiquidityAgent"
  sigma\domains\trading_agents.py:26:    def evaluate(self, state: TradingState) -> AgentVote:
  sigma\domains\trading_agents.py:27:        avg_vol = sum(state.volumes[-20:]) / max(1, 
min(len(state.volumes),20))
  sigma\domains\trading_agents.py:28:        spread = state.spreads_bps[-1] if state.spreads_bps else 0.0
  sigma\domains\trading_agents.py:29:        liquid = avg_vol > 0 and state.volumes[-1] >= avg_vol and spread < 
12
  sigma\domains\trading_agents.py:30:        verdict = "BUY" if liquid else "SELL" if spread > 25 else "HOLD"
> sigma\domains\trading_agents.py:31:        return AgentVote(self.agent_id, Domain.TRADING, Layer.OBSERVATION, 
f"spread_bps={spread:.2f}, avg_vol={avg_vol:.2f}", 0.7 if liquid else 0.5, Severity.S1, 
proposed_verdict=verdict)
  sigma\domains\trading_agents.py:32:
  sigma\domains\trading_agents.py:33:
  sigma\domains\trading_agents.py:34:class VolatilityAgent(BaseAgent):
  sigma\domains\trading_agents.py:35:    agent_id = "VolatilityAgent"
  sigma\domains\trading_agents.py:36:    def evaluate(self, state: TradingState) -> AgentVote:
  sigma\domains\trading_agents.py:37:        rv20 = realized_volatility(state.prices, 20) or 0.0
  sigma\domains\trading_agents.py:38:        rv60 = realized_volatility(state.prices, 60) or rv20 or 0.0001
  sigma\domains\trading_agents.py:39:        verdict = "SELL" if rv20 > rv60 * 1.3 else "BUY" if rv20 < rv60 * 
0.85 else "HOLD"
  sigma\domains\trading_agents.py:40:        conf = min(1.0, abs(rv20/rv60-1.0)*2) if rv60 else 0.2
> sigma\domains\trading_agents.py:41:        return AgentVote(self.agent_id, Domain.TRADING, Layer.OBSERVATION, 
f"rv20={rv20:.4f}, rv60={rv60:.4f}", conf, Severity.S2 if verdict=="SELL" else Severity.S1, 
proposed_verdict=verdict, risk_flags=["HIGH_VOLATILITY"] if verdict=="SELL" else [])
  sigma\domains\trading_agents.py:42:
  sigma\domains\trading_agents.py:43:
  sigma\domains\trading_agents.py:44:class MacroAgent(BaseAgent):
  sigma\domains\trading_agents.py:45:    agent_id = "MacroAgent"
  sigma\domains\trading_agents.py:46:    def evaluate(self, state: TradingState) -> AgentVote:
  sigma\domains\trading_agents.py:47:        risk = state.event_risk_scores[-1] if state.event_risk_scores else 
0.5
  sigma\domains\trading_agents.py:48:        verdict = "SELL" if risk > 0.7 else "BUY" if risk < 0.3 else "HOLD"
> sigma\domains\trading_agents.py:49:        return AgentVote(self.agent_id, Domain.TRADING, Layer.OBSERVATION, 
f"event_risk={risk:.2f}", min(1.0, abs(risk-0.5)*2), Severity.S2 if risk > 0.7 else Severity.S1, 
proposed_verdict=verdict)
  sigma\domains\trading_agents.py:50:
  sigma\domains\trading_agents.py:51:
  sigma\domains\trading_agents.py:52:class CorrelationAgent(BaseAgent):
  sigma\domains\trading_agents.py:53:    agent_id = "CorrelationAgent"
  sigma\domains\trading_agents.py:54:    def evaluate(self, state: TradingState) -> AgentVote:
  sigma\domains\trading_agents.py:55:        asset_ret = _ret(state.prices, 5)
  sigma\domains\trading_agents.py:56:        ref_ret = _ret(state.btc_reference_prices, 5)
  sigma\domains\trading_agents.py:57:        verdict = "BUY" if asset_ret > 0 and ref_ret > 0 else "SELL" if 
asset_ret < 0 and ref_ret < 0 else "HOLD"
  sigma\domains\trading_agents.py:58:        conf = min(1.0, abs(asset_ret - ref_ret) * 10)
> sigma\domains\trading_agents.py:59:        return AgentVote(self.agent_id, Domain.TRADING, Layer.OBSERVATION, 
f"asset_ret={asset_ret:.4f}, ref_ret={ref_ret:.4f}", conf, Severity.S1, proposed_verdict=verdict)
  sigma\domains\trading_agents.py:60:
  sigma\domains\trading_agents.py:61:
  sigma\domains\trading_agents.py:62:class EventAgent(BaseAgent):
  sigma\domains\trading_agents.py:63:    agent_id = "EventAgent"
  sigma\domains\trading_agents.py:64:    def evaluate(self, state: TradingState) -> AgentVote:
  sigma\domains\trading_agents.py:65:        risk = state.event_risk_scores[-1] if state.event_risk_scores else 
0.0
  sigma\domains\trading_agents.py:66:        verdict = "SELL" if risk > 0.65 else "BUY" if risk < 0.25 else 
"HOLD"
> sigma\domains\trading_agents.py:67:        return AgentVote(self.agent_id, Domain.TRADING, Layer.OBSERVATION, 
f"event_shock={risk:.2f}", min(1.0, abs(risk-0.45)*1.8), Severity.S2 if risk > 0.65 else Severity.S1, 
proposed_verdict=verdict)
  sigma\domains\trading_agents.py:68:
  sigma\domains\trading_agents.py:69:
  sigma\domains\trading_agents.py:70:class MomentumAgent(BaseAgent):
  sigma\domains\trading_agents.py:71:    agent_id = "MomentumAgent"
  sigma\domains\trading_agents.py:72:    def evaluate(self, state: TradingState) -> AgentVote:
  sigma\domains\trading_agents.py:73:        ret5 = _ret(state.prices, 5)
  sigma\domains\trading_agents.py:74:        r = rsi(state.prices, 14)
  sigma\domains\trading_agents.py:75:        verdict = "BUY" if ret5 > 0 and (r is None or r < 75) else "SELL" 
if ret5 < 0 and (r is None or r > 25) else "HOLD"
> sigma\domains\trading_agents.py:76:        return AgentVote(self.agent_id, Domain.TRADING, 
Layer.INTERPRETATION, f"ret5={ret5:.4f}, rsi14={r}", min(1.0, abs(ret5)*20), Severity.S1, 
proposed_verdict=verdict)
  sigma\domains\trading_agents.py:77:
  sigma\domains\trading_agents.py:78:
  sigma\domains\trading_agents.py:79:class MeanReversionAgent(BaseAgent):
  sigma\domains\trading_agents.py:80:    agent_id = "MeanReversionAgent"
  sigma\domains\trading_agents.py:81:    def evaluate(self, state: TradingState) -> AgentVote:
  sigma\domains\trading_agents.py:82:        z = zscore(state.prices, 20)
  sigma\domains\trading_agents.py:83:        lower, _, upper = bollinger(state.prices, 20, 2.0)
  sigma\domains\trading_agents.py:84:        if z is None or lower is None or upper is None:
> sigma\domains\trading_agents.py:85:            return AgentVote(self.agent_id, Domain.TRADING, 
Layer.INTERPRETATION, "need 20 prices", 0.2, Severity.S1)
  sigma\domains\trading_agents.py:86:        px = state.prices[-1]
  sigma\domains\trading_agents.py:87:        verdict = "BUY" if px < lower or z < -2.0 else "SELL" if px > 
upper or z > 2.0 else "HOLD"
> sigma\domains\trading_agents.py:88:        return AgentVote(self.agent_id, Domain.TRADING, 
Layer.INTERPRETATION, f"zscore20={z:.2f}", min(1.0, abs(z)/3), Severity.S1, proposed_verdict=verdict)
  sigma\domains\trading_agents.py:89:
  sigma\domains\trading_agents.py:90:
  sigma\domains\trading_agents.py:91:class BreakoutAgent(BaseAgent):
  sigma\domains\trading_agents.py:92:    agent_id = "BreakoutAgent"
  sigma\domains\trading_agents.py:93:    def evaluate(self, state: TradingState) -> AgentVote:
  sigma\domains\trading_agents.py:94:        if len(state.highs) < 20 or len(state.lows) < 20:
> sigma\domains\trading_agents.py:95:            return AgentVote(self.agent_id, Domain.TRADING, 
Layer.INTERPRETATION, "need 20 highs/lows", 0.2, Severity.S1)
  sigma\domains\trading_agents.py:96:        last = state.prices[-1]
  sigma\domains\trading_agents.py:97:        resistance = max(state.highs[-20:])
  sigma\domains\trading_agents.py:98:        support = min(state.lows[-20:])
  sigma\domains\trading_agents.py:99:        verdict = "BUY" if last > resistance else "SELL" if last < support 
else "HOLD"
  sigma\domains\trading_agents.py:100:        distance = max(abs(last - resistance), abs(last - support)) / 
max(last, 1e-9)
> sigma\domains\trading_agents.py:101:        return AgentVote(self.agent_id, Domain.TRADING, 
Layer.INTERPRETATION, f"support={support:.2f}, resistance={resistance:.2f}", min(1.0, distance*25), 
Severity.S1, proposed_verdict=verdict)
  sigma\domains\trading_agents.py:102:
  sigma\domains\trading_agents.py:103:
  sigma\domains\trading_agents.py:104:class PatternAgent(BaseAgent):
  sigma\domains\trading_agents.py:105:    agent_id = "PatternAgent"
  sigma\domains\trading_agents.py:106:    def evaluate(self, state: TradingState) -> AgentVote:
  sigma\domains\trading_agents.py:107:        seq = state.prices[-5:]
  sigma\domains\trading_agents.py:108:        if len(seq) < 5:
> sigma\domains\trading_agents.py:109:            return AgentVote(self.agent_id, Domain.TRADING, 
Layer.INTERPRETATION, "need 5 prices", 0.2, Severity.S1)
  sigma\domains\trading_agents.py:110:        rises = sum(1 for i in range(1, len(seq)) if seq[i] > seq[i-1])
  sigma\domains\trading_agents.py:111:        drops = sum(1 for i in range(1, len(seq)) if seq[i] < seq[i-1])
  sigma\domains\trading_agents.py:112:        verdict = "BUY" if rises >= 4 else "SELL" if drops >= 4 else 
"HOLD"
> sigma\domains\trading_agents.py:113:        return AgentVote(self.agent_id, Domain.TRADING, 
Layer.INTERPRETATION, f"up_moves={rises}, down_moves={drops}", min(1.0, max(rises,drops)/5), Severity.S1, 
proposed_verdict=verdict)
  sigma\domains\trading_agents.py:114:
  sigma\domains\trading_agents.py:115:
  sigma\domains\trading_agents.py:116:class SentimentAgent(BaseAgent):
  sigma\domains\trading_agents.py:117:    agent_id = "SentimentAgent"
  sigma\domains\trading_agents.py:118:    def evaluate(self, state: TradingState) -> AgentVote:
  sigma\domains\trading_agents.py:119:        score = state.sentiment_scores[-1] if state.sentiment_scores else 
0.0
  sigma\domains\trading_agents.py:120:        verdict = "BUY" if score > 0.2 else "SELL" if score < -0.2 else 
"HOLD"
> sigma\domains\trading_agents.py:121:        return AgentVote(self.agent_id, Domain.TRADING, 
Layer.INTERPRETATION, f"sentiment={score:.2f}", min(1.0, abs(score)), Severity.S1, proposed_verdict=verdict)
  sigma\domains\trading_agents.py:122:
  sigma\domains\trading_agents.py:123:
  sigma\domains\trading_agents.py:124:class PredictionAgent(BaseAgent):
  sigma\domains\trading_agents.py:125:    agent_id = "PredictionAgent"
  sigma\domains\trading_agents.py:126:    def evaluate(self, state: TradingState) -> AgentVote:
  sigma\domains\trading_agents.py:127:        rv20 = realized_volatility(state.prices, 20) or 0.0
  sigma\domains\trading_agents.py:129:        spread = state.spreads_bps[-1] if state.spreads_bps else 0.0
  sigma\domains\trading_agents.py:130:        composite = min(1.0, rv20*10 + risk*0.7 + spread/100)
  sigma\domains\trading_agents.py:131:        verdict = "SELL" if composite > 0.70 else "BUY" if composite < 
0.35 else "HOLD"
> sigma\domains\trading_agents.py:132:        return AgentVote(self.agent_id, Domain.TRADING, 
Layer.INTERPRETATION, f"composite_risk={composite:.2f}", min(1.0, abs(composite-0.5)*2), Severity.S2 if 
composite > 0.70 else Severity.S1, proposed_verdict=verdict)
  sigma\domains\trading_agents.py:133:
  sigma\domains\trading_agents.py:134:
  sigma\domains\trading_agents.py:135:class PortfolioAgent(BaseAgent):
  sigma\domains\trading_agents.py:136:    agent_id = "PortfolioAgent"
  sigma\domains\trading_agents.py:137:    def evaluate(self, state: TradingState) -> AgentVote:
  sigma\domains\trading_agents.py:138:        verdict = "SELL" if state.drawdown > 0.10 or state.exposure > 
0.80 else "BUY" if state.exposure < 0.30 and state.drawdown < 0.03 else "HOLD"
> sigma\domains\trading_agents.py:139:        return AgentVote(self.agent_id, Domain.TRADING, 
Layer.INTERPRETATION, f"exposure={state.exposure:.2f}, drawdown={state.drawdown:.2f}", min(1.0, 
max(state.drawdown, state.exposure)), Severity.S2 if state.drawdown > 0.10 else Severity.S1, 
proposed_verdict=verdict)
  sigma\domains\trading_agents.py:140:
  sigma\domains\trading_agents.py:141:
  sigma\domains\trading_agents.py:142:class ExecutionQualityAgent(BaseAgent):
  sigma\domains\trading_agents.py:143:    agent_id = "ExecutionQualityAgent"
  sigma\domains\trading_agents.py:144:    def evaluate(self, state: TradingState) -> AgentVote:
  sigma\domains\trading_agents.py:145:        cost_score = (state.spreads_bps[-1] if state.spreads_bps else 
0.0) / 100 + state.slippage_bps / 100
  sigma\domains\trading_agents.py:146:        verdict = "SELL" if cost_score > 0.25 else "BUY" if cost_score < 
0.08 else "HOLD"
> sigma\domains\trading_agents.py:147:        return AgentVote(self.agent_id, Domain.TRADING, 
Layer.CONTRADICTION, f"execution_cost_score={cost_score:.3f}", min(1.0, cost_score*3), Severity.S2 if 
verdict=="SELL" else Severity.S1, proposed_verdict=verdict, risk_flags=["POOR_EXECUTION"] if verdict=="SELL" 
else [])
  sigma\domains\trading_agents.py:148:
  sigma\domains\trading_agents.py:149:
  sigma\domains\trading_agents.py:150:class RegimeShiftAgent(BaseAgent):
  sigma\domains\trading_agents.py:151:    agent_id = "RegimeShiftAgent"
  sigma\domains\trading_agents.py:152:    def evaluate(self, state: TradingState) -> AgentVote:
  sigma\domains\trading_agents.py:153:        rv20 = realized_volatility(state.prices, 20) or 0.0
  sigma\domains\trading_agents.py:155:        verdict = "SELL" if rv5 > rv20 * 1.6 else "HOLD"
  sigma\domains\trading_agents.py:156:        contradictions = ["REGIME_SHIFT_DETECTED"] if verdict == "SELL" 
else []
  sigma\domains\trading_agents.py:157:        conf = min(1.0, abs((rv5/(rv20 or 0.0001))-1.0))
> sigma\domains\trading_agents.py:158:        return AgentVote(self.agent_id, Domain.TRADING, 
Layer.CONTRADICTION, f"rv5={rv5:.4f}, rv20={rv20:.4f}", conf, Severity.S3 if verdict=="SELL" else Severity.S1, 
proposed_verdict=verdict, contradictions=contradictions)
  sigma\domains\trading_agents.py:159:
  sigma\domains\trading_agents.py:160:
  sigma\domains\trading_agents.py:161:class PortfolioStressAgent(BaseAgent):
  sigma\domains\trading_agents.py:162:    agent_id = "PortfolioStressAgent"
  sigma\domains\trading_agents.py:163:    def evaluate(self, state: TradingState) -> AgentVote:
  sigma\domains\trading_agents.py:164:        stress = min(1.0, state.exposure * 0.8 + state.drawdown * 1.5 + 
max(0.0, state.order_book_imbalance) * 0.2)
  sigma\domains\trading_agents.py:165:        verdict = "SELL" if stress > 0.7 else "HOLD"
> sigma\domains\trading_agents.py:166:        return AgentVote(self.agent_id, Domain.TRADING, 
Layer.CONTRADICTION, f"portfolio_stress={stress:.2f}", stress, Severity.S3 if verdict=="SELL" else Severity.S1, 
proposed_verdict=verdict, risk_flags=["PORTFOLIO_STRESS"] if verdict=="SELL" else [])
  sigma\domains\trading_agents.py:167:
  sigma\domains\trading_agents.py:168:
  sigma\domains\trading_agents.py:169:class ProofConsistencyAgent(BaseAgent):
  sigma\domains\trading_agents.py:170:    agent_id = "ProofConsistencyAgent"
  sigma\domains\trading_agents.py:171:    def evaluate(self, state: TradingState) -> AgentVote:
  sigma\domains\trading_agents.py:172:        missing = []
  sigma\domains\trading_agents.py:175:        if len(state.prices) < 20:
  sigma\domains\trading_agents.py:176:            missing.append("SHORT_PRICE_HISTORY")
  sigma\domains\trading_agents.py:177:        verdict = "HOLD" if missing else "BUY"
> sigma\domains\trading_agents.py:178:        return AgentVote(self.agent_id, Domain.TRADING, Layer.PROOF, 
"proof consistency for trading payload", 0.9 if not missing else 0.4, Severity.S2 if missing else Severity.S0, 
proposed_verdict=verdict, unknowns=missing)
  sigma\domains\trading_agents.py:179:
  sigma\domains\trading_agents.py:180:
  sigma\domains\trading_agents.py:181:def build_trading_agents() -> list[BaseAgent]:
  sigma\domains\trading_agents.py:182:    return [
  sigma\domains\trading_agents.py:183:        MarketDataAgent(),
  sigma\domains\trading_agents.py:184:        LiquidityAgent(),



```
