"""M42 B11 Compétence & Calibration — RED contract tests for Fail-Closed Evaluator.

Source of truth:
  docs/architecture/M42_B11_COMPETENCE_CALIBRATION_DOCTRINE_V1.md
  docs/architecture/M42_B11_COMPETENCE_CALIBRATION_SPEC_V1.md
  docs/architecture/M42_B11_FAIL_CLOSED_SPEC_V1.md

Runtime target: ``app.cognition.b11.evaluator.evaluate_contextual_competence`` (absent at RED).

Conventions:
- The evaluator runtime is imported lazily inside each test (``rt_evaluator()``).
- An absent evaluator makes each test FAIL with:
  "M42 B11 evaluator app/cognition/b11/evaluator.py is absent (certified RED)".
- No collection error, no skip, no xfail, no fallback implementation.
- Tests assert fail-closed behaviour when execution proofs lack independent verifiable anchors.
"""
from __future__ import annotations

import pytest
from app.cognition.b11.contracts import B11_EFFECTS, CompetenceRegime, ContextualCompetenceProfile


def rt_evaluator():
    """Lazy loader for the B11 contextual competence evaluator function."""
    try:
        from app.cognition.b11.evaluator import evaluate_contextual_competence
        return evaluate_contextual_competence
    except ImportError:
        pytest.fail("M42 B11 evaluator app/cognition/b11/evaluator.py is absent (certified RED)")


def test_m42_red_fc_01_fake_success_with_valid_hash_yields_unknown():
    """FC-01: A payload claiming SUCCESS with a valid self-hash but without independent anchor
    must NEVER yield EVIDENCED_COMPETENCE. It must fall back to UNKNOWN_COMPETENCE with EVIDENCE_UNANCHORED.
    """
    evaluate = rt_evaluator()

    unanchored_evidence = {
        "evidence_id": "fake-success-001",
        "target_resource": "agent_transfer",
        "task_ref": "account_wire_transfer_v1",
        "declared_outcome": "SUCCESS",
        "conditions": ("latency:50ms",),
        "payload_hash": "a1b2c3d4e5f60000111122223333444455556666777788889999aaaabbbbcccc",
        "anchor_ref": None,  # No independent anchor
    }

    profile: ContextualCompetenceProfile = evaluate(
        evaluation_id="eval-fc-001",
        domain="bank",
        task_ref="account_wire_transfer_v1",
        target_resources=("agent_transfer",),
        conditions=("latency:50ms",),
        evidence_records=(unanchored_evidence,),
    )

    assert profile.competence_regime == CompetenceRegime.UNKNOWN_COMPETENCE
    assert profile.confidence_score == 0.0
    assert profile.reliability_score is None
    assert "EVIDENCE_UNANCHORED" in profile.unknowns


def test_m42_red_fc_02_caller_self_attestation_rejected():
    """FC-02: Caller self-attestation flags (is_verified=True, is_authenticated=True)
    cannot create trust. The evidence is rejected, leaving the profile in UNKNOWN_COMPETENCE
    with risk indicator SELF_ATTESTATION_REJECTED.
    """
    evaluate = rt_evaluator()

    self_attested_evidence = {
        "evidence_id": "self-attested-001",
        "target_resource": "agent_trader",
        "task_ref": "arbitrage_v1",
        "declared_outcome": "SUCCESS",
        "is_verified": True,        # Caller self-attestation
        "is_authenticated": True,   # Caller self-attestation
        "anchor_ref": None,
    }

    profile: ContextualCompetenceProfile = evaluate(
        evaluation_id="eval-fc-002",
        domain="trading",
        task_ref="arbitrage_v1",
        target_resources=("agent_trader",),
        conditions=(),
        evidence_records=(self_attested_evidence,),
    )

    assert profile.competence_regime == CompetenceRegime.UNKNOWN_COMPETENCE
    assert profile.confidence_score == 0.0
    assert profile.reliability_score is None
    assert "SELF_ATTESTATION_REJECTED" in profile.risk_indicators


def test_m42_red_fc_03_b9_path_id_does_not_prove_execution_outcome():
    """FC-03: CognitivePath.path_id from B9 hashes only (subject, goal, steps), not status.
    A B9 path reference without external execution receipt cannot prove operational success.
    Yields UNKNOWN_COMPETENCE with B9_PATH_STATUS_UNSEALED.
    """
    evaluate = rt_evaluator()

    b9_unsealed_status_evidence = {
        "evidence_id": "b9-path-ref-001",
        "target_resource": "agent_planner",
        "task_ref": "multi_step_plan_v1",
        "provenance": "app.cognition.b9",
        "b9_path_id": "b9_path_hash_12345",
        "declared_status": "SUCCEEDED",  # Mutable status not part of path_id
        "external_execution_receipt": None,
    }

    profile: ContextualCompetenceProfile = evaluate(
        evaluation_id="eval-fc-003",
        domain="meta",
        task_ref="multi_step_plan_v1",
        target_resources=("agent_planner",),
        conditions=(),
        evidence_records=(b9_unsealed_status_evidence,),
    )

    assert profile.competence_regime == CompetenceRegime.UNKNOWN_COMPETENCE
    assert profile.confidence_score == 0.0
    assert profile.reliability_score is None
    assert "B9_PATH_STATUS_UNSEALED" in profile.unknowns


def test_m42_red_fc_04_b7_reject_distinguished_from_technical_incompetence():
    """FC-04: A B7 syntax/role rejection (validate_candidate -> REJECT) is a cognitive
    context non-conformance, not a definitive technical incapacity. Must not produce
    EVIDENCED_INCOMPETENCE. Traces B7_ROLE_NON_CONFORMANCE in contradictions.
    """
    evaluate = rt_evaluator()

    b7_rejection_record = {
        "evidence_id": "b7-rej-001",
        "target_resource": "agent_resolver",
        "task_ref": "resolve_coreference_v1",
        "provenance": "app.cognition.b7.validation",
        "b7_verdict": "REJECT",
        "b7_reason": "STRUCTURED_REFERENT_ONLY: phrase not in structured referents",
    }

    profile: ContextualCompetenceProfile = evaluate(
        evaluation_id="eval-fc-004",
        domain="linguistics",
        task_ref="resolve_coreference_v1",
        target_resources=("agent_resolver",),
        conditions=(),
        evidence_records=(b7_rejection_record,),
    )

    # Must NOT conclude EVIDENCED_INCOMPETENCE
    assert profile.competence_regime != CompetenceRegime.EVIDENCED_INCOMPETENCE
    assert profile.competence_regime == CompetenceRegime.UNKNOWN_COMPETENCE
    assert "B7_ROLE_NON_CONFORMANCE" in profile.contradictions
    assert not getattr(profile, "is_permanently_incapacitated", False)


def test_m42_red_fc_05_guard_x108_block_distinguished_from_technical_incompetence():
    """FC-05: A GuardX108 BLOCK is an access/security gate decision (COMPETENCE != AUTHORITY).
    It must not be converted into an empirical failure of the organ itself.
    Traces ACCESS_GATE_BLOCKED in risk_indicators.
    """
    evaluate = rt_evaluator()

    guard_block_record = {
        "evidence_id": "guard-block-001",
        "target_resource": "drone_controller",
        "task_ref": "fly_waypoint_v1",
        "provenance": "sigma.guard.GuardX108",
        "x108_gate": "BLOCK",
        "reason_code": "TICKET_NOT_READY",
    }

    profile: ContextualCompetenceProfile = evaluate(
        evaluation_id="eval-fc-005",
        domain="gps_defense_aviation",
        task_ref="fly_waypoint_v1",
        target_resources=("drone_controller",),
        conditions=(),
        evidence_records=(guard_block_record,),
    )

    # Must NOT conclude EVIDENCED_INCOMPETENCE
    assert profile.competence_regime != CompetenceRegime.EVIDENCED_INCOMPETENCE
    assert profile.competence_regime == CompetenceRegime.UNKNOWN_COMPETENCE
    assert "ACCESS_GATE_BLOCKED" in profile.risk_indicators
    assert not getattr(profile, "is_permanently_incapacitated", False)


def test_m42_red_fc_06_total_absence_of_evidence_yields_unknown_without_incapacity():
    """FC-06: Total absence of evidence yields UNKNOWN_COMPETENCE with confidence=0.0
    and reliability=None (M32: UNKNOWN != FALSE, UNKNOWN != INCAPACITY).
    Traces NO_HISTORICAL_EVIDENCE in unknowns.
    """
    evaluate = rt_evaluator()

    profile: ContextualCompetenceProfile = evaluate(
        evaluation_id="eval-fc-006",
        domain="bank",
        task_ref="unprecedented_task_v0",
        target_resources=("agent_new",),
        conditions=(),
        evidence_records=(),  # Total absence
    )

    assert profile.competence_regime == CompetenceRegime.UNKNOWN_COMPETENCE
    assert profile.confidence_score == 0.0
    assert profile.reliability_score is None
    assert "NO_HISTORICAL_EVIDENCE" in profile.unknowns
    assert profile.competence_regime != CompetenceRegime.EVIDENCED_INCOMPETENCE


def test_m42_red_fc_07_evaluator_preserves_constitutional_boundaries():
    """FC-07: The evaluator is a pure function. It produces a profile that maintains
    emits_act=False, memory_write=False, kernel_mutation=False, b12_selection=False,
    and decision_authority=KX108_ONLY as defined in B11_EFFECTS.
    """
    evaluate = rt_evaluator()

    profile: ContextualCompetenceProfile = evaluate(
        evaluation_id="eval-fc-007",
        domain="trading",
        task_ref="check_position_v1",
        target_resources=("agent_trader",),
        conditions=(),
        evidence_records=(),
    )

    assert isinstance(profile, ContextualCompetenceProfile)
    assert not hasattr(profile, "authorize")
    assert not hasattr(profile, "execute")
    assert not hasattr(profile, "emit_act")
    assert not hasattr(profile, "mutate_kernel")
    assert not hasattr(profile, "write_durable_memory")
    assert not hasattr(profile, "select_organ")
    assert not hasattr(profile, "admissibility_status")

    # Invariants B11_EFFECTS canoniques vérifiés formellement
    assert B11_EFFECTS["emits_act"] is False
    assert B11_EFFECTS["memory_write"] is False
    assert B11_EFFECTS["kernel_mutation"] is False
    assert B11_EFFECTS["decision_authority"] == "KX108_ONLY"
    assert B11_EFFECTS["advisory_only"] is True
    assert B11_EFFECTS["b12_selection"] is False


def test_m42_red_fc_08_hostile_dynamic_property_descriptor_zero_effects():
    """Anti-Descriptor Gate: An arbitrary object with dynamic @property descriptors
    attempting to execute side-effects upon attribute lookup must be rejected
    without invoking any getter. Side effect counter must remain strictly 0.
    """
    evaluate = rt_evaluator()

    class HostileObjectWithSideEffects:
        counter: int = 0

        @property
        def is_verified(self):
            HostileObjectWithSideEffects.counter += 1
            return True

        @property
        def declared_outcome(self):
            HostileObjectWithSideEffects.counter += 1
            return "SUCCESS"

        def __getattr__(self, name):
            HostileObjectWithSideEffects.counter += 1
            return None

    hostile_record = HostileObjectWithSideEffects()

    profile: ContextualCompetenceProfile = evaluate(
        evaluation_id="eval-fc-008",
        domain="security",
        task_ref="sandbox_execution_v1",
        target_resources=("agent_sandbox",),
        conditions=(),
        evidence_records=(hostile_record,),
    )

    # Counter MUST remain strictly 0: no getattr, no property invocation
    assert HostileObjectWithSideEffects.counter == 0
    assert profile.competence_regime == CompetenceRegime.UNKNOWN_COMPETENCE
    assert profile.confidence_score == 0.0
    assert profile.reliability_score is None
    assert "INVALID_RECORD_STRUCTURE_REJECTED" in profile.risk_indicators


def test_m42_red_fc_09_hostile_custom_mapping_subclass_zero_effects():
    """Anti-Descriptor Gate: A custom mapping subclass overriding .get() or __getitem__
    with side-effect counters must be rejected as non-native.
    Counter must remain strictly 0.
    """
    evaluate = rt_evaluator()

    class HostileMappingSubclass(dict):
        counter: int = 0

        def get(self, k, default=None):
            HostileMappingSubclass.counter += 1
            return super().get(k, default)

        def __getitem__(self, k):
            HostileMappingSubclass.counter += 1
            return super().__getitem__(k)

    hostile_mapping = HostileMappingSubclass({
        "evidence_id": "hostile-001",
        "declared_outcome": "SUCCESS",
        "is_verified": True,
    })

    profile: ContextualCompetenceProfile = evaluate(
        evaluation_id="eval-fc-009",
        domain="security",
        task_ref="sandbox_execution_v1",
        target_resources=("agent_sandbox",),
        conditions=(),
        evidence_records=(hostile_mapping,),
    )

    # Counter MUST remain strictly 0: custom mapping subclass rejected
    assert HostileMappingSubclass.counter == 0
    assert profile.competence_regime == CompetenceRegime.UNKNOWN_COMPETENCE
    assert profile.confidence_score == 0.0
    assert profile.reliability_score is None
    assert "INVALID_RECORD_STRUCTURE_REJECTED" in profile.risk_indicators


def test_m42_red_fc_10_evidence_id_hostile_str_dunder_zero_effects():
    """FC-10: An evidence_id containing a non-str object with dynamic __str__ side-effects
    must NOT have its __str__ invoked. Counter must remain strictly 0.
    """
    evaluate = rt_evaluator()

    class HostileStrId:
        counter: int = 0

        def __str__(self):
            HostileStrId.counter += 1
            return "hostile-id"

    hostile_id = HostileStrId()
    record = {
        "evidence_id": hostile_id,
        "declared_outcome": "SUCCESS",
    }

    profile: ContextualCompetenceProfile = evaluate(
        evaluation_id="eval-fc-010",
        domain="security",
        task_ref="sandbox_execution_v1",
        target_resources=("agent_sandbox",),
        conditions=(),
        evidence_records=(record,),
    )

    assert HostileStrId.counter == 0
    assert profile.competence_regime == CompetenceRegime.UNKNOWN_COMPETENCE
    assert profile.confidence_score == 0.0
    assert profile.reliability_score is None
    assert "INVALID_EVIDENCE_ID_REJECTED" in profile.risk_indicators


def test_m42_red_fc_11_evidence_records_hostile_iter_zero_effects():
    """FC-11: An evidence_records container that is not a native tuple/list (e.g. generator
    or custom iterable with hostile __iter__/__next__) must be rejected BEFORE iteration.
    Counter must remain strictly 0.
    """
    evaluate = rt_evaluator()

    class HostileRecordsIterable:
        counter: int = 0

        def __iter__(self):
            HostileRecordsIterable.counter += 1
            yield {"evidence_id": "fake"}

        def __next__(self):
            HostileRecordsIterable.counter += 1
            raise StopIteration

    hostile_iterable = HostileRecordsIterable()

    profile: ContextualCompetenceProfile = evaluate(
        evaluation_id="eval-fc-011",
        domain="security",
        task_ref="sandbox_execution_v1",
        target_resources=("agent_sandbox",),
        conditions=(),
        evidence_records=hostile_iterable,
    )

    assert HostileRecordsIterable.counter == 0
    assert profile.competence_regime == CompetenceRegime.UNKNOWN_COMPETENCE
    assert profile.confidence_score == 0.0
    assert profile.reliability_score is None
    assert "INVALID_CONTAINER_STRUCTURE_REJECTED" in profile.risk_indicators


def test_m42_red_fc_12_record_value_hostile_eq_zero_effects():
    """FC-12: A record value with a hostile __eq__ comparison operator must NOT
    have its __eq__ invoked against string literals. Counter must remain strictly 0.
    """
    evaluate = rt_evaluator()

    class HostileEqOutcome:
        counter: int = 0

        def __eq__(self, other):
            HostileEqOutcome.counter += 1
            return True

    hostile_outcome = HostileEqOutcome()
    record = {
        "evidence_id": "valid-id-012",
        "declared_outcome": hostile_outcome,
        "provenance": HostileEqOutcome(),
    }

    profile: ContextualCompetenceProfile = evaluate(
        evaluation_id="eval-fc-012",
        domain="security",
        task_ref="sandbox_execution_v1",
        target_resources=("agent_sandbox",),
        conditions=(),
        evidence_records=(record,),
    )

    assert HostileEqOutcome.counter == 0
    assert profile.competence_regime == CompetenceRegime.UNKNOWN_COMPETENCE
    assert profile.confidence_score == 0.0
    assert profile.reliability_score is None


def test_m42_red_fc_13_resources_and_conditions_hostile_str_zero_effects():
    """FC-13: target_resources or conditions containing non-str objects with hostile __str__
    must NOT have their __str__ invoked. Counter must remain strictly 0.
    """
    evaluate = rt_evaluator()

    class HostileResourceStr:
        counter: int = 0

        def __str__(self):
            HostileResourceStr.counter += 1
            return "hostile_res"

    hostile_resource = HostileResourceStr()
    hostile_condition = HostileResourceStr()

    profile: ContextualCompetenceProfile = evaluate(
        evaluation_id="eval-fc-013",
        domain="security",
        task_ref="sandbox_execution_v1",
        target_resources=(hostile_resource,),
        conditions=(hostile_condition,),
        evidence_records=(),
    )

    assert HostileResourceStr.counter == 0
    assert profile.competence_regime == CompetenceRegime.UNKNOWN_COMPETENCE
    assert profile.confidence_score == 0.0
    assert profile.reliability_score is None
    assert "INVALID_RESOURCE_STRUCTURE_REJECTED" in profile.risk_indicators
    assert "INVALID_CONDITION_STRUCTURE_REJECTED" in profile.risk_indicators
