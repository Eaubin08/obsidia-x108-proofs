"""M4: EventReferenceRelation.status says where a relation comes from, never
that its source occurred or its target is true.

Closed vocabulary: "structural" (parser / embedding-derived) and
"nominal_reference" (explicit nominal reference adapter). Occurrence stays on
the events; epistemic meaning stays in its own layer.
"""
from __future__ import annotations

from itertools import product

import pytest

from app.semantic.lattice.event_extraction import extract_event_candidates
from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.events import EventReferenceRelation, EventRelationKind, RELATION_STATUSES
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.knowledge_event_extraction import extract_knowledge_event_targets
from app.semantic.lattice.meta_event_relations import (
    extract_belief_event_relations,
    extract_nominal_reference_relations,
    extract_report_event_relations,
)
from app.semantic.lattice.observation_event_extraction import extract_observation_event_targets
from app.semantic.lattice.review_join import build_review_envelope


def _structural(frame):
    index = build_frame_event_index(frame)
    base = extract_event_candidates(frame)
    return index, [
        *extract_observation_event_targets(frame, base).relations,
        *extract_knowledge_event_targets(frame, base).relations,
        *extract_report_event_relations(frame, index).relations,
        *extract_belief_event_relations(frame, index).relations,
    ]


@pytest.mark.parametrize("text, kind, source_occurrence", [
    ("Paul croit que Marie a lancé le test.", "BELIEVES_ABOUT", "ASSERTED_OCCURRED"),
    ("Paul dit que Marie a lancé le test.", "REPORTS_ABOUT", "ASSERTED_OCCURRED"),
    ("Paul n'a pas dit que Marie a lancé le test.", "REPORTS_ABOUT", "NEGATED"),
    ("Paul aurait dit que Marie a lancé le test.", "REPORTS_ABOUT", "UNKNOWN"),
    ("Paul dira que Marie a lancé le test.", "REPORTS_ABOUT", "FUTURE"),
    ("Paul pourrait dire que Marie a lancé le test.", "REPORTS_ABOUT", "UNCERTAIN"),
    ("J'ai vu Marie lancer le test.", "OBSERVES", "ASSERTED_OCCURRED"),
    ("J'ai appris que Marie a lancé le test.", "LEARNS_ABOUT", "ASSERTED_OCCURRED"),
    ("Je n'ai pas appris que Marie a lancé le test.", "LEARNS_ABOUT", "NEGATED"),
])
def test_structural_relation_status_is_origin_not_truth(text, kind, source_occurrence):
    index, relations = _structural(parse_utterance(text))
    relation = next(r for r in relations if r.relation_kind.value == kind)

    assert relation.status == "structural"
    # The relation exists structurally; the source keeps its own occurrence.
    assert index.by_event_id(relation.source_event).occurrence_status.value == source_occurrence


def test_nested_structural_relations_do_not_carry_source_occurrence():
    index, relations = _structural(parse_utterance("Luc dit que Paul croit que Marie a lancé le test."))
    believes = next(r for r in relations if r.relation_kind is EventRelationKind.BELIEVES_ABOUT)

    assert {r.status for r in relations} == {"structural"}
    assert index.by_event_id(believes.source_event).occurrence_status.value == "REPORTED"


def test_nominal_reference_status_is_preserved():
    frame = parse_utterance("Paul a lancé le test. J'ai observé ce lancement. Marie a mentionné ce lancement.")
    index = build_frame_event_index(frame)
    nominal = extract_nominal_reference_relations(frame, index).relations

    assert [r.status for r in nominal] == ["nominal_reference", "nominal_reference"]
    assert all(r.provenance["target_rule"] == "explicit_nominal_reference" for r in nominal)


def test_vocabulary_is_closed_and_default_is_structural():
    assert RELATION_STATUSES == frozenset({"structural", "nominal_reference"})
    assert EventReferenceRelation(EventRelationKind.ABOUT, "e1", "e2").status == "structural"
    for bad in ("asserted", "true", "verified", "occurred", ""):
        with pytest.raises(ValueError):
            EventReferenceRelation(EventRelationKind.ABOUT, "e1", "e2", status=bad)


def test_review_join_exposes_status_verbatim_without_truth():
    frame = parse_utterance("Paul n'a pas dit que Marie a lancé le test. J'ai observé ce lancement.")
    index = build_frame_event_index(frame)
    run = next(u for u in frame.units if u.predicate == "EXECUTE")
    env = build_review_envelope(frame, index.event_for(run.id).event_ref.event_id, index)

    assert sorted((r.relation_kind.value, r.status) for r in env.relations) == [
        ("OBSERVES", "nominal_reference"), ("REPORTS_ABOUT", "structural")]
    statuses = {c["relation_status"] for c in env.epistemic_contributions if c["origin"] == "event_relation"}
    assert statuses == {"structural", "nominal_reference"}
    assert env.metadata["truth"] is None
    assert all(c["state"] is None for c in env.epistemic_contributions if c["origin"] == "event_relation")


def test_relation_status_adversarial_matrix():
    subjects = ("Paul", "Nadia", "Le directeur", "Omar", "Léa")
    report = ("dit que", "n'a pas dit que", "aurait dit que", "dira que", "pourrait dire que", "a dit que")
    belief = ("croit que", "ne croit pas que", "croira que", "supposait que")
    templates = (
        "{s} {v} Marie a relancé {x}.",
        "Luc dit que {s} {v} Marie a relancé {x}.",
        "{s} {v} Marie a vu Tom relancer {x}.",
        "{s} {v} Marie a appris que Tom a relancé {x}.",
    )
    extra = ("J'ai vu {s} relancer {x}.", "Je n'ai pas vu {s} relancer {x}.", "J'ai appris que {s} a relancé {x}.",
             "{s} a relancé {x}. J'ai observé ce lancement. Marie a mentionné ce lancement. Luc croit ce lancement.")
    metrics = dict.fromkeys(("RELATIONS", "STRUCTURAL_RELATION_ASSERTED_STATUS", "NOMINAL_STATUS_CHANGED",
                             "OUT_OF_VOCABULARY", "PROVENANCE_LOST", "NEW_TRUTH_SCALAR", "NEW_EPISTEMIC_STATE"), 0)
    source_statuses: set[str] = set()
    texts = [t.format(s=s, v=v, x=x) for t, s, v, x in product(templates, subjects, report + belief, ("le script", "la suite", "le job", "le build", "le test"))]
    texts += [t.format(s=s, x=x) for t, s, x in product(extra, subjects, ("le script", "la suite", "le job", "le build"))]
    for text in texts:
        frame = parse_utterance(text)
        index, structural = _structural(frame)
        nominal = extract_nominal_reference_relations(frame, index, structural_relations=structural).relations
        for relation in (*structural, *nominal):
            metrics["RELATIONS"] += 1
            source_statuses.add(index.by_event_id(relation.source_event).occurrence_status.value)
            if relation.status not in RELATION_STATUSES:
                metrics["OUT_OF_VOCABULARY"] += 1
            if relation in structural and relation.status != "structural":
                metrics["STRUCTURAL_RELATION_ASSERTED_STATUS"] += 1
            if relation in nominal and relation.status != "nominal_reference":
                metrics["NOMINAL_STATUS_CHANGED"] += 1
            if not relation.provenance.get("source") and not relation.provenance.get("resolution_rule"):
                metrics["PROVENANCE_LOST"] += 1
        for candidate in index.events():
            env = build_review_envelope(frame, candidate.event_ref.event_id, index)
            if env.metadata["truth"] is not None:
                metrics["NEW_TRUTH_SCALAR"] += 1
            metrics["NEW_EPISTEMIC_STATE"] += sum(
                c["state"] is not None for c in env.epistemic_contributions if c["origin"] == "event_relation")
    assert metrics["RELATIONS"] >= 1500
    assert {"ASSERTED_OCCURRED", "NEGATED", "UNKNOWN", "FUTURE", "UNCERTAIN", "REPORTED"} <= source_statuses
    for key, value in metrics.items():
        if key != "RELATIONS":
            assert value == 0, (key, metrics)
