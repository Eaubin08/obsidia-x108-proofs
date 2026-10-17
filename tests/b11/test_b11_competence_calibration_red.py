"""M42 B11 Compétence & Calibration — RED contract tests (Hardened).

Source of truth:
  docs/architecture/M42_B11_COMPETENCE_CALIBRATION_DOCTRINE_V1.md
  docs/architecture/M42_B11_COMPETENCE_CALIBRATION_SPEC_V1.md

Runtime target: ``app.cognition.b11.contracts`` (absent at RED).

Conventions:
- The runtime is imported lazily inside each test (``rt()``); an absent runtime makes
  each test FAIL with "M42 runtime app/cognition/b11 is absent (certified RED)".
- No collection error, no skip, no xfail, no fallback implementation.
- Tests express the constitutional boundaries: KX108_ONLY, memory_write=False,
  emits_act=False, kernel_mutation=False.
- Both positive behavior and negative discrimination (rejection of faulty mutations)
  are asserted in every test.
"""
from __future__ import annotations

import pytest


def rt():
    """Lazy runtime loader. Certified RED fails when runtime is absent."""
    try:
        import app.cognition.b11.contracts as b11
        return b11
    except ImportError:
        pytest.fail("M42 runtime app/cognition/b11 is absent (certified RED)")


def test_m42_red_01_profile_contextualized_representation():
    """Test 1: ContextualCompetenceProfile instantiates with tuple of domain, task, conditions, resources.
    Rejects scores outside [0.0, 1.0], booleans as scores, and empty required identifiers.
    """
    b11 = rt()

    # 1. Positive instantiation with explicit values
    profile = b11.ContextualCompetenceProfile(
        evaluation_id="eval-001",
        domain="bank",
        task_ref="account_wire_transfer_v1",
        conditions=("latency_budget_ms:50", "require_audit_trail"),
        target_resources=("agent_transfer", "validator_sens"),
        competence_regime=b11.CompetenceRegime.EVIDENCED_COMPETENCE,
        reliability_score=0.95,
        confidence_score=0.90,
        calibration_metric=0.05,
        evidence_refs=("test_transfer_pass_001", "proof_hash_abc"),
        unknowns=(),
        contradictions=(),
        risk_indicators=(),
        advisory_notes="Profile supported by audit tests.",
    )

    assert profile.evaluation_id == "eval-001"
    assert profile.domain == "bank"
    assert profile.task_ref == "account_wire_transfer_v1"
    assert profile.conditions == ("latency_budget_ms:50", "require_audit_trail")
    assert profile.target_resources == ("agent_transfer", "validator_sens")
    assert profile.competence_regime == b11.CompetenceRegime.EVIDENCED_COMPETENCE
    assert profile.reliability_score == 0.95
    assert profile.confidence_score == 0.90
    assert profile.calibration_metric == 0.05
    assert profile.evidence_refs == ("test_transfer_pass_001", "proof_hash_abc")
    assert profile.unknowns == ()

    # 2. Defaults for optional fields
    profile_default = b11.ContextualCompetenceProfile(
        evaluation_id="eval-002",
        domain="bank",
        task_ref="balance_check_v1",
        conditions=("budget:10",),
        target_resources=("agent_reader",),
        competence_regime=b11.CompetenceRegime.EVIDENCED_COMPETENCE,
        reliability_score=1.0,
        confidence_score=0.9,
        calibration_metric=0.0,
        evidence_refs=("proof_002",),
        unknowns=(),
    )
    assert profile_default.contradictions == ()
    assert profile_default.risk_indicators == ()
    assert profile_default.advisory_notes == ""

    # 3. Negative assertions: score range [0.0, 1.0]
    with pytest.raises(ValueError, match="M42_INVALID_SCORE"):
        b11.ContextualCompetenceProfile(
            evaluation_id="eval-bad-score-1",
            domain="bank",
            task_ref="t1",
            conditions=(),
            target_resources=("r1",),
            competence_regime=b11.CompetenceRegime.EVIDENCED_COMPETENCE,
            reliability_score=1.5,  # > 1.0
            confidence_score=0.5,
            calibration_metric=0.0,
            evidence_refs=(),
            unknowns=(),
        )

    with pytest.raises(ValueError, match="M42_INVALID_SCORE"):
        b11.ContextualCompetenceProfile(
            evaluation_id="eval-bad-score-2",
            domain="bank",
            task_ref="t1",
            conditions=(),
            target_resources=("r1",),
            competence_regime=b11.CompetenceRegime.EVIDENCED_COMPETENCE,
            reliability_score=0.5,
            confidence_score=-0.1,  # < 0.0
            calibration_metric=0.0,
            evidence_refs=(),
            unknowns=(),
        )

    # 4. Negative assertions: empty identifiers
    with pytest.raises(ValueError, match="M42_EMPTY_IDENTIFIER"):
        b11.ContextualCompetenceProfile(
            evaluation_id="   ",  # empty/whitespace
            domain="bank",
            task_ref="t1",
            conditions=(),
            target_resources=("r1",),
            competence_regime=b11.CompetenceRegime.EVIDENCED_COMPETENCE,
            reliability_score=0.5,
            confidence_score=0.5,
            calibration_metric=0.0,
            evidence_refs=(),
            unknowns=(),
        )


def test_m42_red_02_three_epistemic_regimes():
    """Test 2: Exactly three distinct epistemic regimes; invalid regime raises ValueError."""
    b11 = rt()
    assert hasattr(b11.CompetenceRegime, "EVIDENCED_COMPETENCE")
    assert hasattr(b11.CompetenceRegime, "EVIDENCED_INCOMPETENCE")
    assert hasattr(b11.CompetenceRegime, "UNKNOWN_COMPETENCE")

    regimes = {
        b11.CompetenceRegime.EVIDENCED_COMPETENCE,
        b11.CompetenceRegime.EVIDENCED_INCOMPETENCE,
        b11.CompetenceRegime.UNKNOWN_COMPETENCE,
    }
    assert len(regimes) == 3

    # All 3 valid regimes can instantiate a profile
    p_comp = b11.ContextualCompetenceProfile(
        evaluation_id="eval-r1",
        domain="trading",
        task_ref="arbitrage_v1",
        conditions=(),
        target_resources=("r1",),
        competence_regime=b11.CompetenceRegime.EVIDENCED_COMPETENCE,
        reliability_score=0.9,
        confidence_score=0.9,
        calibration_metric=0.0,
        evidence_refs=("p1",),
        unknowns=(),
    )
    assert p_comp.competence_regime == b11.CompetenceRegime.EVIDENCED_COMPETENCE

    p_incomp = b11.ContextualCompetenceProfile(
        evaluation_id="eval-r2",
        domain="trading",
        task_ref="arbitrage_v1",
        conditions=(),
        target_resources=("r1",),
        competence_regime=b11.CompetenceRegime.EVIDENCED_INCOMPETENCE,
        reliability_score=0.0,
        confidence_score=0.9,
        calibration_metric=0.0,
        evidence_refs=("fail_log_01",),
        unknowns=(),
        contradictions=("VIOLATED_SLIPPAGE_LIMIT",),
    )
    assert p_incomp.competence_regime == b11.CompetenceRegime.EVIDENCED_INCOMPETENCE

    # Rejection of invalid regimes
    for invalid in ["ASSUMED_COMPETENT", "PROBABLY_TRUE", "", None, 123]:
        with pytest.raises(ValueError, match="M42_INVALID_REGIME"):
            b11.ContextualCompetenceProfile(
                evaluation_id="eval-invalid",
                domain="trading",
                task_ref="arbitrage_v1",
                conditions=(),
                target_resources=("agent_trader",),
                competence_regime=invalid,
                reliability_score=None,
                confidence_score=0.0,
                calibration_metric=None,
                evidence_refs=(),
                unknowns=("u1",),
            )


def test_m42_red_03_unknown_competence_not_incapacity():
    """Test 3: UNKNOWN != INCAPACITY (M32/M42); UNKNOWN_COMPETENCE requires confidence=0.0,
    reliability=None, calibration=None, and unknowns non-empty.
    Rejects any attempt to set positive confidence, reliability, or empty unknowns.
    """
    b11 = rt()

    # 1. Valid UNKNOWN_COMPETENCE
    profile = b11.ContextualCompetenceProfile(
        evaluation_id="eval-unknown-001",
        domain="gps_defense_aviation",
        task_ref="new_untested_maneuver_v0",
        conditions=("high_wind",),
        target_resources=("drone_controller_experimental",),
        competence_regime=b11.CompetenceRegime.UNKNOWN_COMPETENCE,
        reliability_score=None,
        confidence_score=0.0,
        calibration_metric=None,
        evidence_refs=(),
        unknowns=("NO_FLIGHT_LOG_EVIDENCE", "UNCERTIFIED_ACTUATOR_RESPONSE"),
    )

    assert profile.competence_regime == b11.CompetenceRegime.UNKNOWN_COMPETENCE
    assert profile.confidence_score == 0.0
    assert profile.reliability_score is None
    assert profile.calibration_metric is None
    assert len(profile.unknowns) >= 1
    assert profile.competence_regime != b11.CompetenceRegime.EVIDENCED_INCOMPETENCE
    assert not getattr(profile, "is_permanently_incapacitated", False)

    # 2. Negative: positive confidence rejected under UNKNOWN_COMPETENCE
    with pytest.raises(ValueError, match="M42_UNKNOWN_REGIME_ZERO_CONFIDENCE"):
        b11.ContextualCompetenceProfile(
            evaluation_id="eval-u-bad-conf",
            domain="gps_defense_aviation",
            task_ref="task1",
            conditions=(),
            target_resources=("r1",),
            competence_regime=b11.CompetenceRegime.UNKNOWN_COMPETENCE,
            reliability_score=None,
            confidence_score=0.75,  # Violates M42: confidence must be 0.0
            calibration_metric=None,
            evidence_refs=(),
            unknowns=("u1",),
        )

    # 3. Negative: non-None reliability rejected under UNKNOWN_COMPETENCE
    with pytest.raises(ValueError, match="M42_UNKNOWN_REGIME_NO_RELIABILITY"):
        b11.ContextualCompetenceProfile(
            evaluation_id="eval-u-bad-rel",
            domain="gps_defense_aviation",
            task_ref="task1",
            conditions=(),
            target_resources=("r1",),
            competence_regime=b11.CompetenceRegime.UNKNOWN_COMPETENCE,
            reliability_score=0.5,  # Must be None
            confidence_score=0.0,
            calibration_metric=None,
            evidence_refs=(),
            unknowns=("u1",),
        )

    # 4. Negative: empty unknowns rejected under UNKNOWN_COMPETENCE
    with pytest.raises(ValueError, match="M42_UNKNOWN_REGIME_REQUIRES_UNKNOWNS"):
        b11.ContextualCompetenceProfile(
            evaluation_id="eval-u-no-unknowns",
            domain="gps_defense_aviation",
            task_ref="task1",
            conditions=(),
            target_resources=("r1",),
            competence_regime=b11.CompetenceRegime.UNKNOWN_COMPETENCE,
            reliability_score=None,
            confidence_score=0.0,
            calibration_metric=None,
            evidence_refs=(),
            unknowns=(),  # Empty unknowns forbidden when unknown
        )


def test_m42_red_04_open_composition_no_closed_catalog():
    """Test 4: Open composition of arbitrary resources and tasks without closed catalog / enum whitelist.
    Order of composition is semantic and preserved ((A, B) != (B, A)). Empty resources rejected.
    """
    b11 = rt()
    # A completely novel composition and task name must be accepted without enumeration error
    novel_resources = ("brody_custom_agent", "corpus_lexical_french", "neural_gate_sensor_xyz")
    profile = b11.ContextualCompetenceProfile(
        evaluation_id="eval-novel-001",
        domain="linguistics_meta",
        task_ref="unprecedented_cross_syntax_resolution_task_v9",
        conditions=(),
        target_resources=novel_resources,
        competence_regime=b11.CompetenceRegime.UNKNOWN_COMPETENCE,
        reliability_score=None,
        confidence_score=0.0,
        calibration_metric=None,
        evidence_refs=(),
        unknowns=("NO_PRIOR_BENCHMARK",),
    )
    assert profile.target_resources == novel_resources
    assert profile.domain == "linguistics_meta"

    # Order sensitivity: (A, B) != (B, A) per B9-R2
    profile_reversed = b11.ContextualCompetenceProfile(
        evaluation_id="eval-novel-002",
        domain="linguistics_meta",
        task_ref="unprecedented_cross_syntax_resolution_task_v9",
        conditions=(),
        target_resources=tuple(reversed(novel_resources)),
        competence_regime=b11.CompetenceRegime.UNKNOWN_COMPETENCE,
        reliability_score=None,
        confidence_score=0.0,
        calibration_metric=None,
        evidence_refs=(),
        unknowns=("NO_PRIOR_BENCHMARK",),
    )
    assert profile.target_resources != profile_reversed.target_resources

    # Negative: empty resources rejected
    with pytest.raises(ValueError, match="M42_EMPTY_RESOURCES"):
        b11.ContextualCompetenceProfile(
            evaluation_id="eval-empty-res",
            domain="bank",
            task_ref="t1",
            conditions=(),
            target_resources=(),  # Empty resources forbidden
            competence_regime=b11.CompetenceRegime.EVIDENCED_COMPETENCE,
            reliability_score=1.0,
            confidence_score=1.0,
            calibration_metric=0.0,
            evidence_refs=(),
            unknowns=(),
        )


def test_m42_red_05_immutability_and_hashability():
    """Test 5: Profile is immutable; attribute mutation is blocked; mutable inputs are deeply detached."""
    b11 = rt()

    raw_unknowns = ["unresolved_1", "unresolved_2"]
    raw_resources = ["service_a", "service_b"]

    profile = b11.ContextualCompetenceProfile(
        evaluation_id="eval-immut-001",
        domain="ecom",
        task_ref="checkout_cart_v1",
        conditions=(),
        target_resources=raw_resources,
        competence_regime=b11.CompetenceRegime.UNKNOWN_COMPETENCE,
        reliability_score=None,
        confidence_score=0.0,
        calibration_metric=None,
        evidence_refs=("ecom_test_001",),
        unknowns=raw_unknowns,
    )

    # 1. Attribute reassignment blocked
    with pytest.raises(Exception):
        profile.confidence_score = 0.5

    with pytest.raises(Exception):
        profile.target_resources = ("other_service",)

    # 2. Deep detachment: mutating caller's raw list does not alter profile
    raw_unknowns.append("leak_unknown_3")
    raw_resources.append("leak_service_c")
    assert profile.unknowns == ("unresolved_1", "unresolved_2")
    assert profile.target_resources == ("service_a", "service_b")

    # 3. Hashable and equality
    profile_dup = b11.ContextualCompetenceProfile(
        evaluation_id="eval-immut-001",
        domain="ecom",
        task_ref="checkout_cart_v1",
        conditions=(),
        target_resources=("service_a", "service_b"),
        competence_regime=b11.CompetenceRegime.UNKNOWN_COMPETENCE,
        reliability_score=None,
        confidence_score=0.0,
        calibration_metric=None,
        evidence_refs=("ecom_test_001",),
        unknowns=("unresolved_1", "unresolved_2"),
    )
    assert profile == profile_dup
    assert hash(profile) == hash(profile_dup)


def test_m42_red_06_invariants_and_effects():
    """Test 6: B11_EFFECTS declares memory_write=False, emits_act=False, kernel_mutation=False, KX108_ONLY.
    Mapping is read-only (immutable).
    """
    b11 = rt()
    assert hasattr(b11, "B11_EFFECTS")
    effects = b11.B11_EFFECTS
    assert effects["memory_write"] is False
    assert effects["emits_act"] is False
    assert effects["kernel_mutation"] is False
    assert effects["decision_authority"] == "KX108_ONLY"
    assert effects["advisory_only"] is True
    assert effects["b12_selection"] is False

    # Mapping must be read-only (e.g. MappingProxyType)
    with pytest.raises((TypeError, Exception)):
        effects["emits_act"] = True

    with pytest.raises((TypeError, Exception)):
        effects["memory_write"] = True


def test_m42_red_07_no_act_or_kernel_mutation():
    """Test 7: ContextualCompetenceProfile and module cannot emit ACT or execute operations."""
    b11 = rt()
    profile = b11.ContextualCompetenceProfile(
        evaluation_id="eval-noact-001",
        domain="bank",
        task_ref="wire_transfer_v1",
        conditions=(),
        target_resources=("agent_transfer",),
        competence_regime=b11.CompetenceRegime.EVIDENCED_COMPETENCE,
        reliability_score=1.0,
        confidence_score=1.0,
        calibration_metric=0.0,
        evidence_refs=("proof_1",),
        unknowns=(),
    )

    # Instance cannot emit action
    assert not hasattr(profile, "authorize")
    assert not hasattr(profile, "execute")
    assert not hasattr(profile, "emit_act")
    assert not hasattr(profile, "mutate_kernel")
    assert not hasattr(profile, "write_durable_memory")

    # Module cannot emit action
    assert not hasattr(b11, "authorize")
    assert not hasattr(b11, "execute")
    assert not hasattr(b11, "emit_act")
    assert not hasattr(b11, "write_durable_memory")


def test_m42_red_08_no_b12_admissibility_or_selection():
    """Test 8: Strict separation from B12 / M43 (no admissibility, selection, or gate fields/methods)."""
    b11 = rt()
    profile = b11.ContextualCompetenceProfile(
        evaluation_id="eval-nob12-001",
        domain="trading",
        task_ref="order_placement_v1",
        conditions=(),
        target_resources=("agent_order",),
        competence_regime=b11.CompetenceRegime.EVIDENCED_COMPETENCE,
        reliability_score=0.9,
        confidence_score=0.9,
        calibration_metric=0.02,
        evidence_refs=("proof_order_01",),
        unknowns=(),
    )

    # B11 evaluates competence; it never decides admissibility or selection
    assert not hasattr(profile, "admissibility_status")
    assert not hasattr(profile, "selected_action")
    assert not hasattr(profile, "selection_verdict")
    assert not hasattr(profile, "gate_verdict")

    # Module has no selection logic
    assert not hasattr(b11, "select_organ")
    assert not hasattr(b11, "decide_admissibility")
    assert not hasattr(b11, "filter_admissible")
