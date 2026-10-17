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


def test_c2_thermo_recommended_gate_hold_remains_advisory_without_artificial_unknown():
    """
    Phase A (C2): Trace energy_thermo.py::recommended_gate='HOLD' -> DomainAggregate ->
    ThermoSigmaEvaluation -> GuardX108 -> CanonicalDecisionEnvelope.
    Verifies on nominal, high thermo_debt (> 1.0), and incomplete Thermo packets that:
    - Canonical Thermo metrics and risk_flags (THERMO_DEBT_HIGH, ENERGY_INEFFICIENT, SIGMA_TRUTH_MISMATCH)
      are preserved as signals;
    - Thermo's recommended_gate='HOLD' is NOT converted into an artificial unknown
      ('PERIPHERY_RECOMMENDS_HOLD') in DomainAggregate.unknowns (nor cascaded into 'TICKET_NOT_READY');
    - Sigma exposes its advisory recommendation (proposed_verdict='HOLD', advisory_only=True);
    - GuardX108 computes x108_gate strictly from canonical DomainAggregate contracts.
    """
    base_payload = {
        "action_id": "thermo_c2_nominal_01",
        "amount": 100.0,
        "policy_limit": 5000.0,
        "elapsed_s": 120.0,
    }
    state = build_bank_state(base_payload)

    # 1. Nominal case via run_control_plane:
    nominal_action = build_bank_action(base_payload)
    nominal_packet = run_control_plane(nominal_action)
    assert nominal_packet.recommended_gate == "NONE"
    env_nominal = run_bank_with_periphery(state, nominal_packet)
    assert env_nominal.x108_gate == "ALLOW"
    assert env_nominal.unknowns == []

    # 2. High thermo_debt case (energy_cost=2.5 -> thermo_debt=2.5 > THETA_THERMO_DEBT=1.0)
    # tested both via direct run_energy_thermo and via full run_control_plane:
    high_debt_payload = {
        **base_payload,
        "action_id": "thermo_c2_high_debt_01",
        "energy_cost": 2.5,
    }
    high_debt_action = build_bank_action(high_debt_payload)
    thermo_only_packet = run_energy_thermo(high_debt_action)
    assert thermo_only_packet.extra_metrics["thermo_debt"] == 2.5
    assert "THERMO_DEBT_HIGH" in thermo_only_packet.risk_flags
    assert thermo_only_packet.unknowns == []
    assert thermo_only_packet.recommended_gate == "HOLD"

    control_plane_packet = run_control_plane(high_debt_action)
    assert control_plane_packet.extra_metrics["thermo_debt"] == 2.5
    assert "THERMO_DEBT_HIGH" in control_plane_packet.risk_flags
    assert control_plane_packet.unknowns == []
    assert control_plane_packet.recommended_gate == "HOLD"

    for packet in (thermo_only_packet, control_plane_packet):
        env_high_debt = run_bank_with_periphery(state, packet)
        eval_high_debt = env_high_debt.metrics["sigma_thermo_evaluation"]

        # Canonical Thermo metrics and risk flag preserved:
        assert env_high_debt.metrics["thermo_debt"] == 2.5
        assert "THERMO_DEBT_HIGH" in env_high_debt.risk_flags
        assert eval_high_debt["status"] == "INCOHERENT"
        assert "THERMO_DEBT_HIGH" in eval_high_debt["risk_flags"]
        assert eval_high_debt["proposed_verdict"] == "HOLD"
        assert eval_high_debt["advisory_only"] is True
        assert eval_high_debt["decision_authority"] == "KX108_ONLY"
        assert eval_high_debt["emits_act"] is False

        # Thermo's recommended_gate='HOLD' is NOT turned into an artificial unknown:
        assert "PERIPHERY_RECOMMENDS_HOLD" not in env_high_debt.unknowns
        assert "TICKET_NOT_READY" not in env_high_debt.unknowns
        assert env_high_debt.unknowns == env_nominal.unknowns

        # GuardX108 computes the gate from canonical contracts (1 risk flag with high confidence -> ALLOW):
        assert env_high_debt.x108_gate == "ALLOW"
        assert env_high_debt.reason_code == "GUARD_ALLOW"

    # 3. Incomplete Thermo packet with recommended_gate="HOLD":
    incomplete_hold_packet = PeripheralSignalPacket(
        action_id="thermo_c2_incomplete_hold_01",
        domain="bank",
        extra_metrics={"thermo_debt": 2.5, "pin": 1.0},
        risk_flags=["THERMO_DEBT_HIGH"],
        recommended_gate="HOLD",
    )
    env_inc_hold = run_bank_with_periphery(state, incomplete_hold_packet)
    eval_inc_hold = env_inc_hold.metrics["sigma_thermo_evaluation"]
    assert eval_inc_hold["status"] == "INCOMPLETE"
    assert eval_inc_hold["unknowns"] == ["THERMO_SIGNAL_INCOMPLETE"]
    assert eval_inc_hold["proposed_verdict"] == "HOLD"
    assert "PERIPHERY_RECOMMENDS_HOLD" not in env_inc_hold.unknowns
    assert "THERMO_SIGNAL_INCOMPLETE" not in env_inc_hold.unknowns
    assert env_inc_hold.unknowns == env_nominal.unknowns
    assert env_inc_hold.x108_gate == "ALLOW"


def test_c1_runtime_compute_cost_counted_once_in_control_plane_debt_breakdown():
    """
    Phase B (C1): Trace compute_cost -> thermo_debt -> energy_debt -> total_debt in the
    canonical runtime pipeline (ActionCandidate -> run_control_plane -> compute_debt).
    Proves that:
    1. In the standard runtime flow, payload['compute_cost'] is folded into extra_metrics['thermo_debt']
       by run_energy_thermo, while extra_metrics['computational_debt'] is 0.0 (not populated by
       run_control_plane), and DebtBreakdown.total_debt counts energy_debt (= thermo_debt) once
       without adding DebtBreakdown.thermo_debt a second time.
    2. Only if an external caller manually injects extra_metrics['computational_debt'] alongside
       payload['compute_cost'] do both terms add in total_debt; because no canonical contract
       defines unit/semantic equivalence between payload['compute_cost'] and
       extra_metrics['computational_debt'] (delta_C in governed_state.py), no uncontracted
       subtraction is invented.
    """
    from periphery.gencoin_debt_model import compute_debt

    action = build_bank_action(
        {
            "action_id": "thermo_c1_debt_trace_01",
            "amount": 100.0,
            "policy_limit": 5000.0,
            "elapsed_s": 120.0,
            "gross_value": 100.0,
            "compute_cost": 3.0,
        }
    )
    packet = run_control_plane(action)
    assert packet.extra_metrics["thermo_debt"] == 3.0
    assert "computational_debt" not in packet.extra_metrics

    debt = compute_debt(action, packet)
    assert debt.thermo_debt == 3.0
    assert debt.energy_debt == 3.0
    assert debt.computational_debt == 0.0
    # compute_cost=3.0 is counted once in total_debt (not doubled by energy_debt + thermo_debt):
    assert debt.total_debt == 3.0
    assert debt.net_value == 97.0


def test_c2_merged_packet_with_unlisted_non_thermo_hold_risk_is_not_classified_as_thermo_only():
    """
    Robustness check on C2:
    On the real merge path (merge_packets), a packet containing Thermo metrics,
    recommended_gate='HOLD', and a new non-Thermo risk flag (not in any static non-Thermo list)
    must NOT be misclassified as a Thermo-only HOLD.
    Also verifies:
    - A pure Thermo HOLD remains advisory (no 'PERIPHERY_RECOMMENDS_HOLD');
    - A known non-Thermo HOLD (e.g. TRAJECTORY_DIVERGENCE via run_control_plane) preserves its
      prior behavior ('PERIPHERY_RECOMMENDS_HOLD' in unknowns -> x108_gate == 'HOLD').
    """
    from periphery.merge import merge_packets

    base_payload = {
        "action_id": "thermo_c2_merge_robustness_01",
        "amount": 100.0,
        "policy_limit": 5000.0,
        "elapsed_s": 120.0,
        "energy_cost": 2.5,
    }
    state = build_bank_state(base_payload)
    action = build_bank_action(base_payload)

    # 1. Pure Thermo HOLD remains advisory:
    pure_thermo_packet = run_control_plane(action)
    assert pure_thermo_packet.recommended_gate == "HOLD"
    assert pure_thermo_packet.risk_flags == ["THERMO_DEBT_HIGH"]
    env_pure_thermo = run_bank_with_periphery(state, pure_thermo_packet)
    assert "PERIPHERY_RECOMMENDS_HOLD" not in env_pure_thermo.unknowns
    assert env_pure_thermo.metrics["sigma_thermo_evaluation"]["proposed_verdict"] == "HOLD"
    assert env_pure_thermo.x108_gate == "ALLOW"

    # 2a. Real merge path: high-debt Thermo packet merged with a peripheral packet carrying
    # recommended_gate='HOLD' and a new non-Thermo risk flag ('NEW_UNLISTED_PERIPHERAL_RISK'):
    unlisted_non_thermo_packet = PeripheralSignalPacket(
        action_id=action.action_id,
        domain=action.domain,
        risk_flags=["NEW_UNLISTED_PERIPHERAL_RISK"],
        recommended_gate="HOLD",
    )
    merged_with_unlisted_risk = merge_packets(pure_thermo_packet, unlisted_non_thermo_packet)
    assert merged_with_unlisted_risk.recommended_gate == "HOLD"
    assert "THERMO_DEBT_HIGH" in merged_with_unlisted_risk.risk_flags
    assert "NEW_UNLISTED_PERIPHERAL_RISK" in merged_with_unlisted_risk.risk_flags

    env_unlisted = run_bank_with_periphery(state, merged_with_unlisted_risk)
    assert "PERIPHERY_RECOMMENDS_HOLD" in env_unlisted.unknowns
    assert env_unlisted.x108_gate == "HOLD"

    # 2b. Real merge path: nominal Thermo packet (all 7 Thermo metrics, risk_flags=[], gate='NONE')
    # merged with a peripheral packet carrying recommended_gate='HOLD' and 'NEW_UNLISTED_PERIPHERAL_RISK'
    # (only 1 risk flag in total, so x108_gate='HOLD' is driven by 'PERIPHERY_RECOMMENDS_HOLD'):
    nominal_thermo_action = build_bank_action({**base_payload, "energy_cost": 0.0})
    nominal_thermo_packet = run_energy_thermo(nominal_thermo_action)
    assert nominal_thermo_packet.recommended_gate == "NONE"
    assert nominal_thermo_packet.risk_flags == []
    merged_nominal_plus_unlisted = merge_packets(nominal_thermo_packet, unlisted_non_thermo_packet)
    assert merged_nominal_plus_unlisted.recommended_gate == "HOLD"
    assert merged_nominal_plus_unlisted.risk_flags == ["NEW_UNLISTED_PERIPHERAL_RISK"]

    env_nominal_plus_unlisted = run_bank_with_periphery(state, merged_nominal_plus_unlisted)
    assert "PERIPHERY_RECOMMENDS_HOLD" in env_nominal_plus_unlisted.unknowns
    assert env_nominal_plus_unlisted.x108_gate == "HOLD"
    assert env_nominal_plus_unlisted.reason_code == "UNKNOWNS_OR_CONFIDENCE_LOW"

    # 3. Known non-Thermo HOLD via run_control_plane (e.g. TRAJECTORY_DIVERGENCE) preserves prior behavior:
    non_thermo_hold_action = build_bank_action(
        {
            **base_payload,
            "action_id": "thermo_c2_non_thermo_hold_01",
            "energy_cost": 0.0,
            "trajectory_divergence": 0.8,
        }
    )
    non_thermo_hold_packet = run_control_plane(non_thermo_hold_action)
    assert non_thermo_hold_packet.recommended_gate == "HOLD"
    assert "TRAJECTORY_DIVERGENCE" in non_thermo_hold_packet.risk_flags
    env_non_thermo = run_bank_with_periphery(state, non_thermo_hold_packet)
    assert "PERIPHERY_RECOMMENDS_HOLD" in env_non_thermo.unknowns
    assert env_non_thermo.x108_gate == "HOLD"


def test_c2_merged_thermo_hold_with_flagless_non_thermo_hold_preserves_periphery_recommends_hold():
    """
    Edge case C2 on explicit HOLD provenance in merge_packets:
    1. When Thermo emits recommended_gate='HOLD' with a canonical Thermo risk_flag ('THERMO_DEBT_HIGH')
       AND another peripheral packet emits recommended_gate='HOLD' without any risk_flag, unknown, or
       contradiction, merge_packets(thermo_packet, flagless_hold_packet) must NOT be classified as
       Thermo-only HOLD: 'PERIPHERY_RECOMMENDS_HOLD' must be preserved in DomainAggregate.unknowns.
    2. Inverse case: when Thermo alone emits recommended_gate='HOLD' (either directly or merged with
       NONE packets in run_control_plane), it remains advisory ('PERIPHERY_RECOMMENDS_HOLD' not added).
    """
    from periphery.merge import merge_packets

    payload = {
        "action_id": "thermo_c2_flagless_hold_merge_01",
        "amount": 100.0,
        "policy_limit": 5000.0,
        "elapsed_s": 120.0,
        "energy_cost": 2.5,
    }
    state = build_bank_state(payload)
    action = build_bank_action(payload)

    thermo_hold_packet = run_energy_thermo(action)
    assert thermo_hold_packet.recommended_gate == "HOLD"
    assert thermo_hold_packet.risk_flags == ["THERMO_DEBT_HIGH"]

    flagless_non_thermo_hold_packet = PeripheralSignalPacket(
        action_id=action.action_id,
        domain=action.domain,
        recommended_gate="HOLD",
    )
    assert flagless_non_thermo_hold_packet.risk_flags == []
    assert flagless_non_thermo_hold_packet.unknowns == []
    assert flagless_non_thermo_hold_packet.contradictions == []

    # 1. Merged Thermo HOLD + flagless non-Thermo HOLD -> NOT Thermo-only:
    merged_both_hold = merge_packets(thermo_hold_packet, flagless_non_thermo_hold_packet)
    assert merged_both_hold.recommended_gate == "HOLD"
    assert merged_both_hold.risk_flags == ["THERMO_DEBT_HIGH"]
    assert merged_both_hold.hold_origins == ["non_thermo", "thermo"]

    env_both_hold = run_bank_with_periphery(state, merged_both_hold)
    assert env_both_hold.metrics["periphery_hold_origins"] == ["non_thermo", "thermo"]
    assert "PERIPHERY_RECOMMENDS_HOLD" in env_both_hold.unknowns
    assert env_both_hold.x108_gate == "HOLD"
    assert env_both_hold.reason_code == "UNKNOWNS_OR_CONFIDENCE_LOW"

    # 2. Inverse case: Thermo HOLD alone (direct and via run_control_plane) remains advisory:
    for pure_packet in (thermo_hold_packet, run_control_plane(action)):
        env_thermo_alone = run_bank_with_periphery(state, pure_packet)
        assert env_thermo_alone.metrics["periphery_hold_origins"] == ["thermo"]
        assert "PERIPHERY_RECOMMENDS_HOLD" not in env_thermo_alone.unknowns
        assert env_thermo_alone.metrics["sigma_thermo_evaluation"]["proposed_verdict"] == "HOLD"
        assert env_thermo_alone.x108_gate == "ALLOW"



def test_c2_thermo_recommended_gate_hold_remains_advisory_without_artificial_unknown():
    """
    Phase A (C2): Trace energy_thermo.py::recommended_gate='HOLD' -> DomainAggregate ->
    ThermoSigmaEvaluation -> GuardX108 -> CanonicalDecisionEnvelope.
    Verifies on nominal, high thermo_debt (> 1.0), and incomplete Thermo packets that:
    - Canonical Thermo metrics and risk_flags (THERMO_DEBT_HIGH, ENERGY_INEFFICIENT, SIGMA_TRUTH_MISMATCH)
      are preserved as signals;
    - Thermo's recommended_gate='HOLD' is NOT converted into an artificial unknown
      ('PERIPHERY_RECOMMENDS_HOLD') in DomainAggregate.unknowns (nor cascaded into 'TICKET_NOT_READY');
    - Sigma exposes its advisory recommendation (proposed_verdict='HOLD', advisory_only=True);
    - GuardX108 computes x108_gate strictly from canonical DomainAggregate contracts.
    """
    base_payload = {
        "action_id": "thermo_c2_nominal_01",
        "amount": 100.0,
        "policy_limit": 5000.0,
        "elapsed_s": 120.0,
    }
    state = build_bank_state(base_payload)

    # 1. Nominal case via run_control_plane:
    nominal_action = build_bank_action(base_payload)
    nominal_packet = run_control_plane(nominal_action)
    assert nominal_packet.recommended_gate == "NONE"
    env_nominal = run_bank_with_periphery(state, nominal_packet)
    assert env_nominal.x108_gate == "ALLOW"
    assert env_nominal.unknowns == []

    # 2. High thermo_debt case (energy_cost=2.5 -> thermo_debt=2.5 > THETA_THERMO_DEBT=1.0)
    # tested both via direct run_energy_thermo and via full run_control_plane:
    high_debt_payload = {
        **base_payload,
        "action_id": "thermo_c2_high_debt_01",
        "energy_cost": 2.5,
    }
    high_debt_action = build_bank_action(high_debt_payload)
    thermo_only_packet = run_energy_thermo(high_debt_action)
    assert thermo_only_packet.extra_metrics["thermo_debt"] == 2.5
    assert "THERMO_DEBT_HIGH" in thermo_only_packet.risk_flags
    assert thermo_only_packet.unknowns == []
    assert thermo_only_packet.recommended_gate == "HOLD"

    control_plane_packet = run_control_plane(high_debt_action)
    assert control_plane_packet.extra_metrics["thermo_debt"] == 2.5
    assert "THERMO_DEBT_HIGH" in control_plane_packet.risk_flags
    assert control_plane_packet.unknowns == []
    assert control_plane_packet.recommended_gate == "HOLD"

    for packet in (thermo_only_packet, control_plane_packet):
        env_high_debt = run_bank_with_periphery(state, packet)
        eval_high_debt = env_high_debt.metrics["sigma_thermo_evaluation"]

        # Canonical Thermo metrics and risk flag preserved:
        assert env_high_debt.metrics["thermo_debt"] == 2.5
        assert "THERMO_DEBT_HIGH" in env_high_debt.risk_flags
        assert eval_high_debt["status"] == "INCOHERENT"
        assert "THERMO_DEBT_HIGH" in eval_high_debt["risk_flags"]
        assert eval_high_debt["proposed_verdict"] == "HOLD"
        assert eval_high_debt["advisory_only"] is True
        assert eval_high_debt["decision_authority"] == "KX108_ONLY"
        assert eval_high_debt["emits_act"] is False

        # Thermo's recommended_gate='HOLD' is NOT turned into an artificial unknown:
        assert "PERIPHERY_RECOMMENDS_HOLD" not in env_high_debt.unknowns
        assert "TICKET_NOT_READY" not in env_high_debt.unknowns
        assert env_high_debt.unknowns == env_nominal.unknowns

        # GuardX108 computes the gate from canonical contracts (1 risk flag with high confidence -> ALLOW):
        assert env_high_debt.x108_gate == "ALLOW"
        assert env_high_debt.reason_code == "GUARD_ALLOW"

    # 3. Incomplete Thermo packet with recommended_gate="HOLD":
    incomplete_hold_packet = PeripheralSignalPacket(
        action_id="thermo_c2_incomplete_hold_01",
        domain="bank",
        extra_metrics={"thermo_debt": 2.5, "pin": 1.0},
        risk_flags=["THERMO_DEBT_HIGH"],
        recommended_gate="HOLD",
    )
    env_inc_hold = run_bank_with_periphery(state, incomplete_hold_packet)
    eval_inc_hold = env_inc_hold.metrics["sigma_thermo_evaluation"]
    assert eval_inc_hold["status"] == "INCOMPLETE"
    assert eval_inc_hold["unknowns"] == ["THERMO_SIGNAL_INCOMPLETE"]
    assert eval_inc_hold["proposed_verdict"] == "HOLD"
    assert "PERIPHERY_RECOMMENDS_HOLD" not in env_inc_hold.unknowns
    assert "THERMO_SIGNAL_INCOMPLETE" not in env_inc_hold.unknowns
    assert env_inc_hold.unknowns == env_nominal.unknowns
    assert env_inc_hold.x108_gate == "ALLOW"


def test_c1_runtime_compute_cost_counted_once_in_control_plane_debt_breakdown():
    """
    Phase B (C1): Trace compute_cost -> thermo_debt -> energy_debt -> total_debt in the
    canonical runtime pipeline (ActionCandidate -> run_control_plane -> compute_debt).
    Proves that:
    1. In the standard runtime flow, payload['compute_cost'] is folded into extra_metrics['thermo_debt']
       by run_energy_thermo, while extra_metrics['computational_debt'] is 0.0 (not populated by
       run_control_plane), and DebtBreakdown.total_debt counts energy_debt (= thermo_debt) once
       without adding DebtBreakdown.thermo_debt a second time.
    2. Only if an external caller manually injects extra_metrics['computational_debt'] alongside
       payload['compute_cost'] do both terms add in total_debt; because no canonical contract
       defines unit/semantic equivalence between payload['compute_cost'] and
       extra_metrics['computational_debt'] (delta_C in governed_state.py), no uncontracted
       subtraction is invented.
    """
    from periphery.gencoin_debt_model import compute_debt

    action = build_bank_action(
        {
            "action_id": "thermo_c1_debt_trace_01",
            "amount": 100.0,
            "policy_limit": 5000.0,
            "elapsed_s": 120.0,
            "gross_value": 100.0,
            "compute_cost": 3.0,
        }
    )
    packet = run_control_plane(action)
    assert packet.extra_metrics["thermo_debt"] == 3.0
    assert "computational_debt" not in packet.extra_metrics

    debt = compute_debt(action, packet)
    assert debt.thermo_debt == 3.0
    assert debt.energy_debt == 3.0
    assert debt.computational_debt == 0.0
    # compute_cost=3.0 is counted once in total_debt (not doubled by energy_debt + thermo_debt):
    assert debt.total_debt == 3.0
    assert debt.net_value == 97.0
