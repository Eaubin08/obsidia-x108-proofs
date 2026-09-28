"""M8-D1: pure occurrence claim derivation + legacy shadow comparison.

OccurrenceClaim says what the current semantic level claims about the
realization of an event (never truth, evidence, verification or authority).
derive_occurrence is pure; the shadow adapter only reads parser / event output
and classifies each difference with the legacy OccurrenceStatus using the
M8-D0 vocabulary. Nothing here changes runtime behaviour.
"""
from __future__ import annotations

import pathlib
from dataclasses import replace
from itertools import product

import pytest

from app.semantic.lattice.complement_commitment import (
    ComplementCommitment,
    ConstructionType,
    ProjectionOperator,
    StatusDerivation,
    profile_for,
    resolve_commitment,
)
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.occurrence_derivation import (
    OccurrenceClaim,
    OccurrenceInput,
    derive_occurrence,
)
from app.semantic.lattice.occurrence_shadow import ShadowClass, shadow_frame

O = OccurrenceClaim
A = chr(39)
X = "Paul a lancé le test"


def _derive(**kw):
    return derive_occurrence(OccurrenceInput(source_object_ref="u1", **kw))


def _commit(family, construction=ConstructionType.QUE_PROPOSITION, *ops):
    return resolve_commitment(profile_for(family, construction), frozenset(ops), source_object_ref="u2")


def test_vocabulary_is_exactly_d0():
    assert [c.value for c in O] == ["ASSERTED_REALIZED", "ASSERTED_NOT_REALIZED", "PROJECTED_FUTURE", "CONTINGENT",
                                    "POSSIBLE", "NO_ASSERTION", "UNRESOLVED"]
    assert [c.value for c in ShadowClass] == ["SAME_SEMANTIC_MEANING", "EXPECTED_WEAKENING", "EXPECTED_DIMENSION_MOVE",
                                              "LEGACY_UNRESOLVED_NEW_MODEL_EXPLICIT", "NEW_MODEL_UNRESOLVED",
                                              "UNEXPECTED_DIFFERENCE"]


def test_every_result_reuses_status_derivation():
    for res in (_derive(), _derive(tense_aspect="PAST", realization_signal="PERFECTIVE"),
                _derive(commitment=_commit("BELIEF"))):
        assert isinstance(res.derivation, StatusDerivation)
        assert res.derivation.dimension == "occurrence" and res.derivation.value == res.claim.value
        assert res.derivation.rule and res.derivation.source_object_ref == "u1"


@pytest.mark.parametrize("family, construction, ops", [
    ("REPORT", ConstructionType.QUE_PROPOSITION, ()),
    ("REPORT", ConstructionType.QUE_PROPOSITION, (ProjectionOperator.NEGATION,)),
    ("BELIEF", ConstructionType.QUE_PROPOSITION, ()),
    ("BELIEF", ConstructionType.QUE_PROPOSITION, (ProjectionOperator.NEGATION,)),
    ("KNOW", ConstructionType.QUE_PROPOSITION, ()),
    ("KNOW", ConstructionType.QUE_PROPOSITION, (ProjectionOperator.NEGATION,)),
    ("KNOW", ConstructionType.QUE_PROPOSITION, (ProjectionOperator.QUESTION,)),
    ("LEARN", ConstructionType.QUE_PROPOSITION, ()),
    ("REMEMBER", ConstructionType.QUE_PROPOSITION, ()),
    ("PERCEPTION", ConstructionType.QUE_PROPOSITION, ()),
])
def test_non_assertive_commitments_make_no_assertion(family, construction, ops):
    # Even with a perfective past complement: the commitment decides, not the tense.
    res = _derive(commitment=_commit(family, construction, *ops), tense_aspect="PAST",
                  realization_signal="PERFECTIVE", polarity="negative")
    assert res.claim is O.NO_ASSERTION


def test_no_assertion_is_not_unresolved():
    assert _derive(commitment=resolve_commitment(None, frozenset())).claim is O.UNRESOLVED
    assert _derive(commitment=_commit("LEARN", ConstructionType.QUE_PROPOSITION, ProjectionOperator.MODAL)).claim \
        is O.UNRESOLVED
    assert _derive(unresolved_governance=True, tense_aspect="PAST", realization_signal="PERFECTIVE").claim \
        is O.UNRESOLVED
    assert _derive(tense_aspect="PRESENT").claim is O.UNRESOLVED
    assert _derive(directive=True).claim is O.NO_ASSERTION
    assert _derive(temporal_subordinate=True).claim is O.NO_ASSERTION


def test_entailed_inherits_parent_and_never_promotes_without_it():
    entailed = _commit("PERCEPTION", ConstructionType.DIRECT_INFINITIVE_PERCEPTION)
    assert _derive(commitment=entailed).claim is O.UNRESOLVED
    for parent in O:
        res = _derive(commitment=entailed, parent_claim=parent)
        expected = O.NO_ASSERTION if parent is O.ASSERTED_NOT_REALIZED else parent
        assert res.claim is expected
    conditional = _commit("PERCEPTION", ConstructionType.DIRECT_INFINITIVE_PERCEPTION, ProjectionOperator.CONDITION)
    assert _derive(commitment=conditional).claim is O.CONTINGENT


@pytest.mark.parametrize("kw, claim", [
    ({"tense_aspect": "PAST", "realization_signal": "PERFECTIVE"}, O.ASSERTED_REALIZED),
    ({"tense_aspect": "PAST", "polarity": "negative"}, O.ASSERTED_NOT_REALIZED),
    ({"tense_aspect": "FUTURE"}, O.PROJECTED_FUTURE),
    ({"tense_aspect": "NEAR_FUTURE"}, O.PROJECTED_FUTURE),
    ({"tense_aspect": "FUTURE", "polarity": "negative"}, O.PROJECTED_FUTURE),
    ({"tense_aspect": "AVERTED"}, O.ASSERTED_NOT_REALIZED),
    ({"conditional_role": "target", "tense_aspect": "FUTURE"}, O.CONTINGENT),
    ({"hypothetical": True, "polarity": "negative"}, O.CONTINGENT),
    ({"modality": "ABILITY_OR_PERMISSION"}, O.POSSIBLE),
    ({"modality": "OBLIGATION"}, O.UNRESOLVED),
    ({"modality": "DESIRE"}, O.NO_ASSERTION),
    ({"modality": "KNOW_HOW"}, O.NO_ASSERTION),
    ({"modality": "ABILITY_OR_PERMISSION", "polarity": "negative"}, O.UNRESOLVED),
    ({"modality": "ABILITY_OR_PERMISSION", "tense_aspect": "FUTURE"}, O.UNRESOLVED),
    ({"directive": True, "polarity": "negative"}, O.NO_ASSERTION),
    ({"question": True, "tense_aspect": "PAST", "realization_signal": "PERFECTIVE"}, O.NO_ASSERTION),
    ({"attribution_boundary": True, "tense_aspect": "PAST", "realization_signal": "PERFECTIVE"}, O.NO_ASSERTION),
    ({"tense_aspect": "CONDITIONAL"}, O.UNRESOLVED),
    ({"malformed_ancestry": True, "tense_aspect": "PAST", "realization_signal": "PERFECTIVE"}, O.UNRESOLVED),
])
def test_local_signal_rules(kw, claim):
    assert _derive(**kw).claim is claim


KNOWN_CASES = [
    ("Paul lance le test.", "EXECUTE", "UNKNOWN", O.UNRESOLVED, ShadowClass.SAME_SEMANTIC_MEANING),
    ("Paul va lancer le test.", "EXECUTE", "UNKNOWN", O.PROJECTED_FUTURE, ShadowClass.LEGACY_UNRESOLVED_NEW_MODEL_EXPLICIT),
    ("Paul peut lancer le test.", "EXECUTE", "UNCERTAIN", O.POSSIBLE, ShadowClass.SAME_SEMANTIC_MEANING),
    ("Paul doit lancer le test.", "EXECUTE", "UNCERTAIN", O.UNRESOLVED, ShadowClass.NEW_MODEL_UNRESOLVED),
    ("Paul veut lancer le test.", "EXECUTE", "UNCERTAIN", O.NO_ASSERTION, ShadowClass.EXPECTED_DIMENSION_MOVE),
    (f"Marie dit que {X}.", "EXECUTE", "REPORTED", O.NO_ASSERTION, ShadowClass.EXPECTED_DIMENSION_MOVE),
    (f"Marie n{A}a pas dit que {X}.", "EXECUTE", "REPORTED", O.NO_ASSERTION, ShadowClass.EXPECTED_DIMENSION_MOVE),
    (f"Marie croit que {X}.", "EXECUTE", "UNKNOWN", O.NO_ASSERTION, ShadowClass.SAME_SEMANTIC_MEANING),
    (f"Marie ne croit pas que {X}.", "EXECUTE", "UNKNOWN", O.NO_ASSERTION, ShadowClass.SAME_SEMANTIC_MEANING),
    (f"Marie sait que {X}.", "EXECUTE", "UNKNOWN", O.NO_ASSERTION, ShadowClass.SAME_SEMANTIC_MEANING),
    (f"Marie ne sait pas que {X}.", "EXECUTE", "UNKNOWN", O.NO_ASSERTION, ShadowClass.SAME_SEMANTIC_MEANING),
    (f"Marie a appris que {X}.", "EXECUTE", "ASSERTED_OCCURRED", O.NO_ASSERTION, ShadowClass.EXPECTED_WEAKENING),
    (f"Marie doit apprendre que {X}.", "EXECUTE", "ASSERTED_OCCURRED", O.UNRESOLVED, ShadowClass.NEW_MODEL_UNRESOLVED),
    (f"Marie voit que {X}.", "EXECUTE", "ASSERTED_OCCURRED", O.NO_ASSERTION, ShadowClass.EXPECTED_WEAKENING),
    ("Marie voit Paul lancer le test.", "EXECUTE", "UNKNOWN", O.ASSERTED_REALIZED,
     ShadowClass.LEGACY_UNRESOLVED_NEW_MODEL_EXPLICIT),
    ("Marie ne voit pas Paul lancer le test.", "EXECUTE", "UNKNOWN", O.NO_ASSERTION, ShadowClass.SAME_SEMANTIC_MEANING),
    ("Paul a lancé le test avant que Marie relance le build.", "EXECUTE#2", "HYPOTHETICAL", O.NO_ASSERTION,
     ShadowClass.EXPECTED_DIMENSION_MOVE),
    ("Paul a failli lancer le test.", "EXECUTE", "UNKNOWN", O.ASSERTED_NOT_REALIZED,
     ShadowClass.LEGACY_UNRESOLVED_NEW_MODEL_EXPLICIT),
    ("Paul aurait lancé le test.", "EXECUTE", "UNKNOWN", O.UNRESOLVED, ShadowClass.SAME_SEMANTIC_MEANING),
    (X + ".", "EXECUTE", "ASSERTED_OCCURRED", O.ASSERTED_REALIZED, ShadowClass.SAME_SEMANTIC_MEANING),
    ("Ne lance pas le test.", "EXECUTE", "NEGATED", O.NO_ASSERTION, ShadowClass.EXPECTED_DIMENSION_MOVE),
    ("Si Marie lance le lot, Paul ne relance pas le build.", "EXECUTE#2", "NEGATED", O.CONTINGENT,
     ShadowClass.EXPECTED_WEAKENING),
    (f"Marie découvre que {X}.", "EXECUTE", "UNKNOWN", O.UNRESOLVED, ShadowClass.SAME_SEMANTIC_MEANING),
]


def _record(text, which):
    predicate, _, nth = which.partition("#")
    records = [r for r in shadow_frame(parse_utterance(text)) if r.predicate == predicate]
    return records[int(nth or 1) - 1]


@pytest.mark.parametrize("text, which, legacy, claim, klass", KNOWN_CASES)
def test_known_shadow_cases(text, which, legacy, claim, klass):
    rec = _record(text, which)
    assert (rec.legacy_occurrence, rec.new_occurrence_claim, rec.classification) == (legacy, claim, klass), rec
    assert rec.derivation_rule and rec.notes


@pytest.mark.parametrize("governor, claim", [
    ("Marie voit Paul lancer le test.", O.ASSERTED_REALIZED),
    ("Marie a vu Paul lancer le test.", O.ASSERTED_REALIZED),
    ("Marie ne voit pas Paul lancer le test.", O.NO_ASSERTION),
    ("Est-ce que Marie voit Paul lancer le test ?", O.NO_ASSERTION),
    ("Marie verra Paul lancer le test.", O.PROJECTED_FUTURE),
    ("Si Marie voit Paul lancer le test, Luc attend.", O.CONTINGENT),
])
def test_direct_perception_never_bypasses_parent_scope(governor, claim):
    assert _record(governor, "EXECUTE").new_occurrence_claim is claim


def test_modules_are_shadow_only():
    root = pathlib.Path(__file__).resolve().parents[1] / "app"
    for path in root.rglob("*.py"):
        if path.name in {"occurrence_derivation.py", "occurrence_shadow.py"}:
            continue
        text = path.read_text(encoding="utf-8")
        assert "occurrence_derivation" not in text and "occurrence_shadow" not in text, path
    core = (root / "semantic" / "lattice" / "occurrence_derivation.py").read_text(encoding="utf-8")
    imports = [l for l in core.splitlines() if l.startswith(("import ", "from "))]
    assert all("french_grammar" not in l and "event_" not in l and "review_join" not in l for l in imports)


def test_occurrence_property_matrix():
    metrics = dict.fromkeys((
        "CASES", "OCCURRENCE_WITHOUT_DERIVATION", "PRESUPPOSITION_TO_ASSERTED_OCCURRENCE",
        "ATTRIBUTED_TO_ASSERTED_OCCURRENCE", "MENTIONED_TO_ASSERTED_OCCURRENCE", "QUESTIONED_TO_ASSERTED_OCCURRENCE",
        "UNRESOLVED_TO_ASSERTED_OCCURRENCE", "ENTAILED_WITHOUT_PARENT_PROMOTION", "NEGATED_DIRECTIVE_TO_NOT_REALIZED",
        "MULTIOPERATOR_UNSAFE_RESOLUTION", "CRASH",
    ), 0)
    counts = dict.fromkeys(O, 0)
    asserted = {O.ASSERTED_REALIZED, O.ASSERTED_NOT_REALIZED}
    commitments = [None, *[resolve_commitment(profile_for(f, c), frozenset(ops)) for f, c, ops in [
        ("REPORT", "QUE_PROPOSITION", ()), ("REPORT", "QUE_PROPOSITION", (ProjectionOperator.NEGATION,)),
        ("KNOW", "QUE_PROPOSITION", ()), ("KNOW", "QUE_PROPOSITION", (ProjectionOperator.QUESTION,)),
        ("LEARN", "QUE_PROPOSITION", (ProjectionOperator.MODAL,)),
        ("PERCEPTION", "DIRECT_INFINITIVE_PERCEPTION", ()),
        ("PERCEPTION", "DIRECT_INFINITIVE_PERCEPTION", (ProjectionOperator.CONDITION,)),
        ("NONE", "QUE_PROPOSITION", ())]]]
    for (commitment, polarity, tense, modality, directive, question, role, boundary, unresolved, parent) in product(
            commitments, ("positive", "negative"), ("PAST", "PRESENT", "FUTURE", "NEAR_FUTURE", "AVERTED", "CONDITIONAL"),
            (None, "ABILITY_OR_PERMISSION", "OBLIGATION", "DESIRE"), (False, True), (False, True),
            (None, "target", "temporal"), (False, True), (False, True), (None, O.ASSERTED_REALIZED)):
        metrics["CASES"] += 1
        inp = OccurrenceInput(
            source_object_ref="u1", polarity=polarity, tense_aspect=tense, modality=modality, directive=directive,
            question=question, conditional_role=role if role == "target" else None,
            temporal_subordinate=role == "temporal", attribution_boundary=boundary, unresolved_governance=unresolved,
            realization_signal="PERFECTIVE" if tense == "PAST" else None, commitment=commitment, parent_claim=parent)
        try:
            res = derive_occurrence(inp)
        except Exception:
            metrics["CRASH"] += 1
            continue
        counts[res.claim] += 1
        if res.derivation is None or res.derivation.dimension != "occurrence" or not res.derivation.rule:
            metrics["OCCURRENCE_WITHOUT_DERIVATION"] += 1
        c = commitment.commitment if commitment is not None else None
        if res.claim in asserted:
            metrics["PRESUPPOSITION_TO_ASSERTED_OCCURRENCE"] += c is ComplementCommitment.PRESUPPOSED
            metrics["ATTRIBUTED_TO_ASSERTED_OCCURRENCE"] += c is ComplementCommitment.ATTRIBUTED
            metrics["MENTIONED_TO_ASSERTED_OCCURRENCE"] += c is ComplementCommitment.MENTIONED
            metrics["QUESTIONED_TO_ASSERTED_OCCURRENCE"] += c is ComplementCommitment.QUESTIONED
            metrics["UNRESOLVED_TO_ASSERTED_OCCURRENCE"] += c is ComplementCommitment.UNRESOLVED or unresolved
            metrics["ENTAILED_WITHOUT_PARENT_PROMOTION"] += c is ComplementCommitment.ENTAILED and parent is None
        if directive and polarity == "negative" and res.claim is O.ASSERTED_NOT_REALIZED:
            metrics["NEGATED_DIRECTIVE_TO_NOT_REALIZED"] += 1
        if c is None and modality and (polarity == "negative" or tense in {"FUTURE", "NEAR_FUTURE", "AVERTED"}) \
                and not (directive or question or boundary or unresolved or role) and res.claim is not O.UNRESOLVED:
            metrics["MULTIOPERATOR_UNSAFE_RESOLUTION"] += 1

    assert metrics["CASES"] >= 8000, metrics
    assert all(counts[c] > 0 for c in O), counts
    for key, value in metrics.items():
        if key != "CASES":
            assert value == 0, (key, metrics)
