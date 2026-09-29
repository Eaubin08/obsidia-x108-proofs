"""A2: "Puis-je V ?" is the pouvoir operator (P1S), never the "puis" connective.

"puis" was only known to the segmenter ("puis-je" kept in its clause) and had
no lexical analysis, so "Puis-je lancer P et exécuter Q ?" built no modal
chain: "exécuter Q" became an injunctive REQUESTED infinitive with a gate.
"puis" followed by a hyphenated "je" is now read as pouvoir, present, first
person singular: an ability-permission question of the speaker, one QUESTION
operator over the coordination, no addressee request, no gate. The "puis"
connective ("Lance P puis exécute Q") is unchanged.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.projections import ProjectionAxis, project


def _gate(f):
    return {k: v["requires_gate"] for k, v in project(f, ProjectionAxis.AUTHORITY).items()}


def _assert_speaker_permission_question(u, gate):
    assert u.modality == "ABILITY_OR_PERMISSION"
    assert (u.subject, u.action_agent, u.request_target) == ("je", "SPEAKER", "NONE")
    assert u.pragmatic == "ASKED" and u.pragmatic not in {"REQUESTED", "INDIRECT_REQUEST"}
    assert not gate[u.id]


@pytest.mark.parametrize("text", [
    "Puis-je lancer le test ?",
    "Puis-je exécuter P ?",
    "Et puis-je lancer P ?",
])
def test_puis_je_is_the_pouvoir_modal(text):
    f = parse_utterance(text)
    gate = _gate(f)
    (u,) = f.units
    _assert_speaker_permission_question(u, gate)
    assert u.role == "PERMISSION_QUERY"


@pytest.mark.parametrize("text,n,kind", [
    ("Puis-je lancer P et exécuter Q ?", 2, "AND"),
    ("Puis-je lancer P, exécuter Q et arrêter R ?", 3, "AND"),
    ("Puis-je lancer P puis exécuter Q ?", 2, "AND"),
    ("Puis-je lancer P ou exécuter Q ?", 2, "OR"),
])
def test_puis_je_scopes_over_the_coordination(text, n, kind):
    f = parse_utterance(text)
    gate = _gate(f)
    assert len(f.units) == n
    for u in f.units:
        _assert_speaker_permission_question(u, gate)
    (coord,) = [c for c in f.coordinations if c.construction == "shared_modality"]
    assert (coord.kind, coord.members) == (kind, tuple(u.id for u in f.units))
    (op,) = f.operator_scopes
    assert (op.kind, op.source, op.scope, op.speech_act, op.target) == \
        ("ABILITY_OR_PERMISSION", "puis", coord.id, "QUESTION", "NONE")


@pytest.mark.parametrize("text", [
    "Lance P puis exécute Q.",
    "Lance P et puis exécute Q.",
    "Paul lance P, puis je lance Q.",
    "Et puis je lance Q.",
    "Puis lance P.",
])
def test_puis_connective_is_unchanged(text):
    f = parse_utterance(text)
    assert not f.operator_scopes
    assert all(u.modality is None for u in f.units)


def test_connective_puis_keeps_its_gated_requests():
    f = parse_utterance("Lance P puis exécute Q.")
    gate = _gate(f)
    assert [(u.pragmatic, gate[u.id]) for u in f.units] == [("REQUESTED", True), ("REQUESTED", True)]
    assert [(r.kind, r.evidence) for r in f.relations] == [("PRECEDES", "puis")]
