"""Governance projection of the utterance frame onto the existing pipeline.

Checks the "gov" expectations of the frozen matrix against build_ir /
gates / decide, plus explicit regressions of the 5E-2B-R prototype.
"""
from __future__ import annotations

import pytest

import app.ir.unified_ir as unified_ir
from app.gates.gates import evaluate
from app.ir.unified_ir import build_ir
from app.router.decision import decide
from tests.semantic_grammar_matrix import PROBES

# Pre-existing gap (already present before the prototype, commit 0b348ab):
# infinitive / indirect execution requests never reached HOLD.
TIGHTENING_PENDING: set[str] = {
    "modal_tu_peux_question",
    "modal_inversion",
    "modal_conditional_politeness",
    "modal_obligation_devoir",
    "modal_obligation_falloir",
    "modal_vouloir_que",
    "modal_vouloir_que_politeness",
    "sequence_avant_de",
}

GOV_PROBES = [p for p in PROBES if "gov" in p]


def _params():
    for p in GOV_PROBES:
        marks = []
        if p["id"] in TIGHTENING_PENDING:
            marks.append(pytest.mark.xfail(strict=True, reason="infinitive/indirect HOLD gap"))
        yield pytest.param(p, id=p["id"], marks=marks)


@pytest.mark.parametrize("probe", list(_params()))
def test_matrix_governance(probe):
    gov = probe["gov"]
    decision = decide(probe["text"], memory_index={})
    verdict = decision["gate"]["verdict"]
    if "verdict" in gov:
        if gov["verdict"] == "!HOLD":
            assert verdict != "HOLD", decision["gate"]
        else:
            assert verdict == gov["verdict"], decision["gate"]
    if "route" in gov:
        assert decision["route"] == gov["route"], decision["reason"]
    if "matched" in gov:
        assert decision["gate"]["matched"] == gov["matched"]


@pytest.mark.parametrize("prompt", [
    "sans attendre, lance le script",
    "sans hésiter, execute le script",
    "ne t'inquiète pas, lance le script, pas besoin de confirmer",
])
def test_prototype_scope_regression_is_fixed(prompt):
    ir = build_ir(prompt)
    assert "no_execute" not in ir["constraints"]
    assert ir["intent_type"] == "world_action"
    assert evaluate(ir)["verdict"] == "HOLD"
    assert decide(prompt, memory_index={})["route"] == "hold_commands_only"


@pytest.mark.parametrize("prompt", [
    "prépare le sans rien lancer",
    "prépare le script mais ne l'exécute pas",
    "prepare the script but do not execute it",
])
def test_prepare_no_execute_needs_referent_not_remote_model(prompt):
    ir = build_ir(prompt)
    assert ir["action_type"] == "prepare"
    assert "no_execute" in ir["constraints"]
    assert "referent" in ir["missing"]
    decision = decide(prompt, memory_index={})
    assert decision["gate"]["verdict"] == "CLARIFY"
    assert decision["route"] == "clarification_needed"
    assert decision["model"] is None


def test_relaxation_never_hides_a_later_positive_same_verb():
    prompt = "prépare le script, ne l'exécute pas, puis exécute-le"
    ir = build_ir(prompt)
    assert ir["semantics"]["execution_hold_relaxable"] is False
    assert ir["semantics"]["contradictions"]
    assert evaluate(ir)["verdict"] == "HOLD"


def test_oral_negation_never_relaxes():
    ir = build_ir("prepare le script mais l execute pas")
    assert ir["semantics"]["confirmed_no_execute"] is False
    assert "no_execute" not in ir["constraints"]
    assert evaluate(ir)["verdict"] == "HOLD"


def test_gate_telemetry_reports_positive_verb():
    gate = evaluate(build_ir("prepare the script, do not execute it, then run it"))
    assert gate["verdict"] == "HOLD"
    assert gate["matched"] == "run"


def test_parser_failure_relaxes_nothing(monkeypatch):
    def boom(_raw):
        raise RuntimeError("parser down")

    monkeypatch.setattr(unified_ir, "parse_utterance", boom)
    ir = build_ir("prépare le script mais ne l'exécute pas")
    assert ir["semantics"]["closure_blockers"] == ["parser_error"]
    assert "no_execute" not in ir["constraints"]
    assert evaluate(ir)["verdict"] == "HOLD"


def test_ir_semantics_is_descriptive_and_bounded():
    ir = build_ir("on m'a dit qu'il avait lancé le script")
    sem = ir["semantics"]
    assert sem["boundary"]["decision_authority"] == "KX108_ONLY"
    assert sem["boundary"]["emits_act"] is False
    assert sem["requested_world_actions"] == []
    # descriptive non-request, but governance stays fail-closed
    assert evaluate(ir)["verdict"] == "HOLD"


@pytest.mark.parametrize("prompt", ["maman est là ?", "est-ce qu'il pleut dehors ?"])
def test_current_world_evidence_preserved(prompt):
    decision = decide(prompt, memory_index={})
    assert decision["route"] == "evidence_required"
    assert decision["ir"]["semantics"]["evidence_needs"]
