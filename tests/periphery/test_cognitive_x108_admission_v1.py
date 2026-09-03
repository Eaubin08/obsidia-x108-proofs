"""
W2 — Tests substantifs: admit_cognitive_context -> DecisionTicketDryRun.
"""
from __future__ import annotations
import pytest
from unittest.mock import patch
from periphery.context.context_packet_builder_v2 import build_context_packet_v2
from periphery.context.context_packet_validator import ContextPacketValidationResult
from periphery.x108_ingress.x108_context_boundary import BoundaryCheckResult
from periphery.context.cognitive_x108_admission import admit_cognitive_context
from runtime_wiring.packet_types import DecisionTicketDryRun

_VALID_DECISIONS = frozenset({"BLOCK", "HOLD", "ALLOW_CONTEXT_ONLY"})


def _v2(contradictions=None):
    return build_context_packet_v2(
        query="test cognitif W2",
        language="fr",
        dominant_trees=[1, 7],
        risk_flags=["RISK_LOW"],
        unknowns=["u1"],
        contradictions=[] if contradictions is None else contradictions,
    )


def _bad_validation(proj):
    return ContextPacketValidationResult(
        packet_id="x",
        valid=False,
        violations=["INVARIANT_VIOLATED:readonly==False expected True"],
    )


def _bad_boundary(proj):
    return BoundaryCheckResult(
        packet_id="x",
        passed=False,
        violations=["BOUNDARY_VIOLATION:readonly==False required True"],
    )

# 1. valide + critical=False -> ALLOW_CONTEXT_ONLY
def test_valid_non_critical_allow():
    result = admit_cognitive_context(_v2(), "sig-w2-allow", critical_action_requested=False)
    assert result.decision == "ALLOW_CONTEXT_ONLY"
    assert result.x108_gate_status == "X108_EVALUATED_DRY_RUN"

# 2. valide + critical=True -> HOLD
def test_valid_critical_hold():
    result = admit_cognitive_context(_v2(), "sig-w2-hold", critical_action_requested=True)
    assert result.decision == "HOLD"
    assert result.x108_gate_status == "X108_EVALUATED_DRY_RUN"

# 3. pregate fail -> BLOCK + X108_FAIL_CLOSED + evaluate_dry_run non appele
def test_pregate_block_no_evaluate(monkeypatch):
    _TARGET = "periphery.context.cognitive_x108_admission.validate_context_packet"
    called = []
    def _fake_evaluate(*a, **kw):
        called.append(True)
        raise AssertionError("evaluate_dry_run should not be called on pregate fail")
    monkeypatch.setattr(_TARGET, _bad_validation)
    monkeypatch.setattr(
        "periphery.context.cognitive_x108_admission.evaluate_dry_run",
        _fake_evaluate,
    )
    result = admit_cognitive_context(_v2(), "sig-w2-pregate")
    assert result.decision == "BLOCK"
    assert result.x108_gate_status == "X108_FAIL_CLOSED"
    assert "PREGATE_FAIL_CLOSED" in result.reason_codes
    assert called == []

# 4. violation + critical=True -> BLOCK, jamais HOLD
def test_violation_beats_critical(monkeypatch):
    monkeypatch.setattr(
        "periphery.context.cognitive_x108_admission.validate_context_packet",
        _bad_validation,
    )
    result = admit_cognitive_context(_v2(), "sig-w2-beat", critical_action_requested=True)
    assert result.decision == "BLOCK"
    assert result.x108_gate_status == "X108_FAIL_CLOSED"

# 5. retour toujours DecisionTicketDryRun
def test_return_type_allow():
    assert isinstance(admit_cognitive_context(_v2(), "sig-w2-type-a"), DecisionTicketDryRun)

def test_return_type_hold():
    assert isinstance(admit_cognitive_context(_v2(), "sig-w2-type-h", critical_action_requested=True), DecisionTicketDryRun)

def test_return_type_pregate(monkeypatch):
    monkeypatch.setattr(
        "periphery.context.cognitive_x108_admission.validate_context_packet",
        _bad_validation,
    )
    assert isinstance(admit_cognitive_context(_v2(), "sig-w2-type-b"), DecisionTicketDryRun)

# 6. decision toujours dans le set valide
def test_decision_in_valid_set_allow():
    assert admit_cognitive_context(_v2(), "sig-w2-set-a").decision in _VALID_DECISIONS

def test_decision_in_valid_set_hold():
    assert admit_cognitive_context(_v2(), "sig-w2-set-h", critical_action_requested=True).decision in _VALID_DECISIONS

# 7. context_refs / ticket_id / reason_codes coherents
def test_context_refs_present_on_allow():
    result = admit_cognitive_context(_v2(), "sig-w2-refs")
    assert len(result.context_packet_refs) == 1
    assert result.context_packet_refs[0].startswith("cp-cognitive-")

def test_ticket_id_not_empty():
    result = admit_cognitive_context(_v2(), "sig-w2-tid")
    assert result.ticket_id

def test_reason_codes_not_empty_allow():
    result = admit_cognitive_context(_v2(), "sig-w2-rc")
    assert len(result.reason_codes) > 0

def test_pregate_ticket_id_format(monkeypatch):
    monkeypatch.setattr(
        "periphery.context.cognitive_x108_admission.validate_context_packet",
        _bad_validation,
    )
    result = admit_cognitive_context(_v2(), "sig-w2-tid-fmt")
    assert result.ticket_id.startswith("dt-cogn-pregate-")

def test_pregate_reason_has_pregate_constant(monkeypatch):
    monkeypatch.setattr(
        "periphery.context.cognitive_x108_admission.validate_context_packet",
        _bad_validation,
    )
    result = admit_cognitive_context(_v2(), "sig-w2-rc-const")
    assert "PREGATE_FAIL_CLOSED" in result.reason_codes
    assert any("readonly" in r for r in result.reason_codes)

# 8. non-souverainete intacte sur le resultat
def test_emits_act_false():
    assert admit_cognitive_context(_v2(), "sig-w2-ns-act").emits_act is False

def test_decision_authority_kx108():
    assert admit_cognitive_context(_v2(), "sig-w2-ns-da").decision_authority == "KX108_ONLY"

def test_dry_run_true():
    assert admit_cognitive_context(_v2(), "sig-w2-ns-dr").dry_run is True

def test_validate_invariants_allow():
    admit_cognitive_context(_v2(), "sig-w2-inv").validate_invariants()

def test_validate_invariants_hold():
    admit_cognitive_context(_v2(), "sig-w2-inv-h", critical_action_requested=True).validate_invariants()

def test_validate_invariants_pregate(monkeypatch):
    monkeypatch.setattr(
        "periphery.context.cognitive_x108_admission.validate_context_packet",
        _bad_validation,
    )
    admit_cognitive_context(_v2(), "sig-w2-inv-b").validate_invariants()

# 9. aucun AgentResult / AgentLayer importe dans le module
def test_no_agent_symbols_in_module():
    import periphery.context.cognitive_x108_admission as mod
    assert "AgentResult" not in mod.__dict__
    assert "AgentLayer" not in mod.__dict__
