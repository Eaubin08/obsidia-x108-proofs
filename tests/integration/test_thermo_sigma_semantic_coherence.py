"""
RED/GREEN integration tests for explicit semantic consumption of Thermo signals
by Sigma in the runtime path (`periphery/sigma_bridge.py` -> `sigma/domains/meta_agents.py` -> `GuardX108.decide()`).

Canonical constants, formulas, and risk flags reused (no invented thresholds, tolerances, or gate rules):
- periphery/constants.py: THETA_ENERGY (0.2), THETA_MISMATCH (0.35), THETA_THERMO_DEBT (1.0)
- periphery/energy_thermo.py: pin, pout, energy_efficiency = pout/pin, thermo_debt,
  truth_score, sigma_score, sigma_truth_mismatch = abs(sigma_score - truth_score)
  Canonical flags: ENERGY_INEFFICIENT, THERMO_DEBT_HIGH, SIGMA_TRUTH_MISMATCH, COLLAPSE_DISGUISED_HIGH_SIGMA
- sigma/aggregation.py: only GPS_DEFENSE_AVIATION defines canonical sigma_score = confidence and truth_score
  in aggregate.extra_metrics. Bank, Trading, and Ecom do not define domain sigma_score/truth_score and
  produce domain_comparison_status = "NOT_COMPARABLE".
- sigma/guard.py: GuardX108.decide(aggregate) produces x108_gate (ALLOW / HOLD / BLOCK); KX108 retains
  sovereign authority (decision_authority = "KX108_ONLY").
"""

from __future__ import annotations

from periphery.adapters.bank_adapter import build_bank_action, build_bank_state
from periphery.adapters.gps_adapter import build_gps_action, build_gps_state
from periphery.adapters.trading_adapter import build_trading_action, build_trading_state
from periphery.common import ActionCandidate, PeripheralSignalPacket
from periphery.control_plane import run_control_plane
from periphery.energy_thermo import run_energy_thermo
from periphery.sigma_bridge import (
    run_bank_with_periphery,
    run_ecom_with_periphery,
    run_gps_with_periphery,
    run_trading_with_periphery,
)
from sigma.contracts import EcomState


def _nominal_bank_state():
    return build_bank_state(
        {
            "action_id": "thermo_sigma_bank_01",
            "amount": 100.0,
            "policy_limit": 5000.0,
            "elapsed_s": 120.0,
        }
    )


def _nominal_ecom_state() -> EcomState:
    state = EcomState(session_id="thermo_sigma_ecom_01")
    for k, v in {
        "traffic_quality": 0.85,
        "basket_intent_score": 0.85,
        "stock_ok": True,
        "margin_rate": 0.30,
        "customer_trust": 0.85,
        "conversion_readiness": 0.85,
        "roas": 2.8,
        "fulfillment_risk": 0.15,
        "intent_conflict_score": 0.05,
        "checkout_friction_score": 0.05,
        "merchant_policy_score": 0.85,
        "x108_compliance_rate": 0.98,
        "order_value": 49.0,
    }.items():
        setattr(state, k, v)
    return state


def test_coherent_thermo_signal_semantically_evaluated_by_sigma():
    """A coherent Thermo signal is explicitly evaluated by Sigma and recorded in the envelope."""
    payload = {
        "action_id": "thermo_sigma_coh_01",
        "amount": 100.0,
        "policy_limit": 5000.0,
        "elapsed_s": 120.0,
    }
    action = build_bank_action(payload)
    state = build_bank_state(payload)
    packet = run_control_plane(action)

    envelope = run_bank_with_periphery(state, packet)

    assert envelope.x108_gate == "ALLOW"
    assert "meta:ThermoCoherenceAgent" in envelope.evidence_refs
    assert "thermo_sigma:COHERENT" in envelope.evidence_refs

    eval_report = envelope.metrics.get("sigma_thermo_evaluation")
    assert isinstance(eval_report, dict)
    assert eval_report["status"] == "COHERENT"
    assert eval_report["advisory_only"] is True
    assert eval_report["decision_authority"] == "KX108_ONLY"
    assert eval_report["emits_act"] is False
    assert eval_report["missing_keys"] == []
    assert eval_report["formula_status"] == "EXACT_MATCH"
    assert eval_report["formula_consistent"] is True
    assert eval_report["actual_sigma_truth_mismatch"] <= 0.35


def test_not_comparable_domain_sigma_score_in_bank_trading_ecom():
    """
    Bank, Trading, and Ecom aggregators do not define domain sigma_score or truth_score;
    aggregate.confidence is not substituted for domain_sigma_score.
    Even with low Thermo truth_score (0.10), Sigma produces domain_comparison_status='NOT_COMPARABLE'
    and does not trigger any synthetic HOLD on this comparison.
    """
    # 1. Bank
    bank_action = ActionCandidate(
        action_id="thermo_sigma_not_comp_bank",
        domain="bank",
        actor_id="tester",
        intent="transfer",
        action_type="transfer",
        irreversible=False,
        timestamp_plan="2026-10-17T00:00:00Z",
        payload={"truth_score": 0.10},
    )
    bank_packet = run_energy_thermo(bank_action)
    assert bank_packet.recommended_gate == "NONE"
    bank_env = run_bank_with_periphery(_nominal_bank_state(), bank_packet)
    bank_eval = bank_env.metrics["sigma_thermo_evaluation"]
    assert bank_eval["domain_comparison_status"] == "NOT_COMPARABLE"
    assert bank_eval["domain_sigma_score"] is None
    assert bank_eval["domain_truth_score"] is None
    assert bank_eval["status"] == "COHERENT"
    assert "SIGMA_TRUTH_MISMATCH" not in bank_env.risk_flags
    assert bank_env.x108_gate == "ALLOW"

    # 2. Trading
    trading_action = build_trading_action({"action_id": "thermo_sigma_not_comp_trading", "truth_score": 0.10})
    trading_packet = run_energy_thermo(trading_action)
    trading_state = build_trading_state({"action_id": "thermo_sigma_not_comp_trading"})
    trading_env = run_trading_with_periphery(trading_state, trading_packet)
    trading_eval = trading_env.metrics["sigma_thermo_evaluation"]
    assert trading_eval["domain_comparison_status"] == "NOT_COMPARABLE"
    assert trading_eval["domain_sigma_score"] is None
    assert trading_eval["domain_truth_score"] is None
    assert trading_eval["status"] == "COHERENT"
    assert "SIGMA_TRUTH_MISMATCH" not in trading_env.risk_flags

    # 3. Ecom
    ecom_action = ActionCandidate(
        action_id="thermo_sigma_not_comp_ecom",
        domain="ecom",
        actor_id="tester",
        intent="checkout",
        action_type="pay",
        irreversible=False,
        timestamp_plan="2026-10-17T00:00:00Z",
        payload={"truth_score": 0.10},
    )
    ecom_packet = run_energy_thermo(ecom_action)
    ecom_env = run_ecom_with_periphery(_nominal_ecom_state(), ecom_packet)
    ecom_eval = ecom_env.metrics["sigma_thermo_evaluation"]
    assert ecom_eval["domain_comparison_status"] == "NOT_COMPARABLE"
    assert ecom_eval["domain_sigma_score"] is None
    assert ecom_eval["domain_truth_score"] is None
    assert ecom_eval["status"] == "COHERENT"
    assert "SIGMA_TRUTH_MISMATCH" not in ecom_env.risk_flags


def test_gps_domain_truth_and_sigma_scores_comparable_and_evaluated():
    """
    In GPS_DEFENSE_AVIATION, aggregate_gps_defense_aviation canonically defines
    sigma_score = confidence and truth_score in extra_metrics.
    Sigma preserves domain_truth_score and domain_sigma_score, reports COMPARABLE,
    and evaluates coherence against Thermo truth_score.
    """
    payload = {"action_id": "thermo_sigma_gps_01"}
    action = build_gps_action(payload)
    state = build_gps_state(payload)
    packet = run_control_plane(action)

    envelope = run_gps_with_periphery(state, packet)

    assert "domain_truth_score" in envelope.metrics
    assert "domain_sigma_score" in envelope.metrics
    eval_report = envelope.metrics.get("sigma_thermo_evaluation")
    assert isinstance(eval_report, dict)
    assert eval_report["domain_comparison_status"] == "COMPARABLE"
    assert eval_report["domain_truth_score"] == envelope.metrics["domain_truth_score"]
    assert eval_report["domain_sigma_score"] == envelope.metrics["domain_sigma_score"]

    # When Thermo reports truth_score=0.10 while GPS domain_sigma_score is ~0.98,
    # Sigma detects SIGMA_TRUTH_MISMATCH (> 0.35) in its advisory evaluation.
    gps_mismatch_action = ActionCandidate(
        action_id="thermo_sigma_gps_mismatch_01",
        domain="gps",
        actor_id="tester",
        intent="nav",
        action_type="navigate",
        irreversible=False,
        timestamp_plan="2026-10-17T00:00:00Z",
        payload={"truth_score": 0.10},
    )
    gps_mismatch_packet = run_energy_thermo(gps_mismatch_action)
    env_gps_mismatch = run_gps_with_periphery(state, gps_mismatch_packet)
    eval_gps_mismatch = env_gps_mismatch.metrics["sigma_thermo_evaluation"]
    assert eval_gps_mismatch["domain_comparison_status"] == "COMPARABLE"
    assert eval_gps_mismatch["status"] == "INCOHERENT"
    assert eval_gps_mismatch["actual_sigma_truth_mismatch"] > 0.35
    assert "SIGMA_TRUTH_MISMATCH" in eval_gps_mismatch["risk_flags"]
    assert "SIGMA_TRUTH_MISMATCH" in env_gps_mismatch.risk_flags
    assert eval_gps_mismatch["proposed_verdict"] == "HOLD"
    assert eval_gps_mismatch["advisory_only"] is True


def test_canonical_thermo_thresholds_and_uncontracted_formula_discrepancy_Remain_advisory():
    """
    Sigma evaluates canonical Thermo thresholds (ENERGY_INEFFICIENT, THERMO_DEBT_HIGH,
    SIGMA_TRUTH_MISMATCH) and reports uncontracted numerical formula discrepancies as
    NOT_EVALUATED_NO_CANONICAL_TOLERANCE without inventing new HOLD/BLOCK gate rules.
    """
    state = _nominal_bank_state()

    # Case 1: Low energy_efficiency (< THETA_ENERGY = 0.2) and high thermo_debt (> 1.0)
    # with recommended_gate='NONE': Sigma explicitly records ENERGY_INEFFICIENT and THERMO_DEBT_HIGH
    # in its advisory evaluation without inventing a synthetic unknown or overriding GuardX108.
    packet_thresholds = PeripheralSignalPacket(
        action_id="thermo_sigma_advisory_thresholds_01",
        domain="bank",
        extra_metrics={
            "pin": 10.0,
            "pout": 1.0,
            "energy_efficiency": 0.10,
            "thermo_debt": 2.5,
            "truth_score": 0.20,
            "sigma_score": 0.90,
            "sigma_truth_mismatch": 0.70,
        },
        recommended_gate="NONE",
    )
    env_thresh = run_bank_with_periphery(state, packet_thresholds)
    eval_thresh = env_thresh.metrics["sigma_thermo_evaluation"]
    assert eval_thresh["status"] == "INCOHERENT"
    assert "ENERGY_INEFFICIENT" in eval_thresh["risk_flags"]
    assert "THERMO_DEBT_HIGH" in eval_thresh["risk_flags"]
    assert "SIGMA_TRUTH_MISMATCH" in eval_thresh["risk_flags"]
    assert "LOW_ENERGY_EFFICIENCY" not in eval_thresh["risk_flags"]
    assert eval_thresh["contradictions"] == []
    assert eval_thresh["proposed_verdict"] == "HOLD"
    assert eval_thresh["advisory_only"] is True
    assert eval_thresh["decision_authority"] == "KX108_ONLY"
    # Even with both thermo_debt > 1.0 and mismatch > 0.35, no synthetic BLOCK is invented:
    assert env_thresh.x108_gate != "BLOCK"

    # Case 2: Numerical discrepancy in energy_efficiency (0.90 vs pout/pin = 0.10)
    # Not covered by any canonical tolerance contract -> reported as NOT_EVALUATED_NO_CANONICAL_TOLERANCE,
    # never transformed into a contradiction or BLOCK.
    packet_discrepancy = PeripheralSignalPacket(
        action_id="thermo_sigma_formula_not_evaluated_01",
        domain="bank",
        extra_metrics={
            "pin": 10.0,
            "pout": 1.0,
            "energy_efficiency": 0.90,
            "thermo_debt": 0.0,
            "truth_score": 0.95,
            "sigma_score": 0.95,
            "sigma_truth_mismatch": 0.0,
        },
        recommended_gate="NONE",
    )
    env_disc = run_bank_with_periphery(state, packet_discrepancy)
    eval_disc = env_disc.metrics["sigma_thermo_evaluation"]
    assert eval_disc["formula_status"] == "NOT_EVALUATED_NO_CANONICAL_TOLERANCE"
    assert eval_disc["formula_consistent"] is None
    assert eval_disc["contradictions"] == []
    assert "THERMO_FORMULA_CONTRADICTION" not in env_disc.contradictions
    assert env_disc.x108_gate == "ALLOW"


def test_incomplete_thermo_signal_explicitly_reported_as_advisory():
    """
    An incomplete Thermo signal (partial Thermo keys in extra_metrics) is explicitly evaluated
    as status='INCOMPLETE' with missing_keys, unknowns=['THERMO_SIGNAL_INCOMPLETE'], and
    proposed_verdict='HOLD' in the advisory report sigma_thermo_evaluation, without incrementing
    DomainAggregate.unknowns or overriding GuardX108's gate calculation.
    """
    state = _nominal_bank_state()
    baseline_packet = PeripheralSignalPacket(
        action_id="thermo_sigma_baseline_no_thermo_01",
        domain="bank",
        extra_metrics={},
        recommended_gate="NONE",
    )
    env_baseline = run_bank_with_periphery(state, baseline_packet)

    incomplete_packet = PeripheralSignalPacket(
        action_id="thermo_sigma_incomplete_01",
        domain="bank",
        extra_metrics={
            "thermo_debt": 0.2,
            "pin": 1.0,
            # missing pout, energy_efficiency, truth_score, sigma_score, sigma_truth_mismatch
        },
        recommended_gate="NONE",
    )

    env_incomplete = run_bank_with_periphery(state, incomplete_packet)
    eval_report = env_incomplete.metrics.get("sigma_thermo_evaluation")
    assert isinstance(eval_report, dict)

    # 1. Advisory report explicitly contains the INCOMPLETE marker and proposed HOLD:
    assert eval_report["status"] == "INCOMPLETE"
    assert "pout" in eval_report["missing_keys"]
    assert "energy_efficiency" in eval_report["missing_keys"]
    assert eval_report["unknowns"] == ["THERMO_SIGNAL_INCOMPLETE"]
    assert eval_report["proposed_verdict"] == "HOLD"
    assert "thermo_sigma:INCOMPLETE" in env_incomplete.evidence_refs

    # 2. DomainAggregate.unknowns (exposed on envelope.unknowns) is NOT incremented by this marker:
    assert "THERMO_SIGNAL_INCOMPLETE" not in env_incomplete.unknowns
    assert env_incomplete.unknowns == env_baseline.unknowns
    assert len(env_incomplete.unknowns) == len(env_baseline.unknowns)

    # 3. Final x108_gate is computed by GuardX108 from the existing aggregate (not forced to HOLD):
    assert env_incomplete.x108_gate == env_baseline.x108_gate == "ALLOW"
    assert env_incomplete.reason_code == env_baseline.reason_code == "GUARD_ALLOW"

    # 4. No Sigma/Thermo component emits ACT and KX108_ONLY authority remains intact:
    assert eval_report["advisory_only"] is True
    assert eval_report["decision_authority"] == "KX108_ONLY"
    assert eval_report["emits_act"] is False
    assert env_incomplete.metrics.get("periphery_can_emit_act") is False
    assert env_incomplete.raw_engine["consensus"]["does_not_authorize_action"] is True
    assert env_incomplete.raw_engine["consensus"]["does_not_override_x108_gate"] is True

