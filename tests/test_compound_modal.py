"""NF2 (safety only): a compound-tense modal governs its infinitive, never a request.

"Paul a voulu lancer P": the HAVE branch built "voulu" as an ordinary
participle and "lancer P" became an injunctive REQUESTED infinitive with a
gate, even without coordination. AUX + participle of vouloir / pouvoir /
devoir / savoir / falloir + infinitive is now one modal chain (modality,
compound tense, subject of the auxiliary), shared by coordinated bare
infinitives like the simple chain. A past modal is never a directive
(no REQUESTED / INDIRECT_REQUEST). Its occurrence is NOT decided: the
claim is UNRESOLVED (rule modal_past_open, marker
modal_past_occurrence_open), never realized / possible / asserted, and the
legacy realized flag stays unset. "a pu" / "a dû" / "a voulu" semantics
remain a held doctrine.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.projections import ProjectionAxis, project

REQUESTS = {"REQUESTED", "INDIRECT_REQUEST", "FORBIDDEN"}


def _view(text):
    f = parse_utterance(text)
    gate = {k: v["requires_gate"] for k, v in project(f, ProjectionAxis.AUTHORITY).items()}
    events = {c.predicate_ref: c for c in build_frame_event_index(f).events()}
    return f, gate, events


@pytest.mark.parametrize("text,modality", [
    ("Paul a voulu lancer P.", "DESIRE"),
    ("Paul a pu lancer P.", "ABILITY_OR_PERMISSION"),
    ("Paul a dû lancer P.", "OBLIGATION"),
    ("Paul avait voulu lancer P.", "DESIRE"),
    ("Paul n'a pas voulu lancer P.", "DESIRE"),
    ("Paul n'a pas pu lancer P.", "ABILITY_OR_PERMISSION"),
    ("Paul a su lancer P.", "KNOW_HOW"),
    ("Tu as dû lancer P.", "OBLIGATION"),
    ("As-tu pu lancer P ?", "ABILITY_OR_PERMISSION"),
    ("Il a fallu lancer P.", "OBLIGATION"),
])
def test_compound_modal_governs_its_infinitive(text, modality):
    f, gate, events = _view(text)
    (u,) = [x for x in f.units if x.lemma == "lancer"]
    assert u.modality == modality
    assert u.pragmatic not in REQUESTS and not gate[u.id] and u.request_target == "NONE"
    assert u.realized is None
    if u.id in events:
        assert (events[u.id].occurrence_claim.value, events[u.id].occurrence_derivation.rule) == \
            ("UNRESOLVED", "modal_past_open")
    assert f"modal_past_occurrence_open:{u.id}" in f.ambiguities
    assert not any(x.lemma in {"vouloir", "pouvoir", "devoir", "savoir", "falloir"} for x in f.units)


@pytest.mark.parametrize("text", [
    "Paul a voulu lancer P et exécuter Q.",
    "Paul a pu lancer P, exécuter Q.",
    "Paul a dû lancer P puis exécuter Q.",
    "Paul avait voulu lancer P ou exécuter Q.",
])
def test_coordinated_infinitives_share_the_compound_modal(text):
    f, gate, events = _view(text)
    assert len(f.units) == 2
    for u in f.units:
        assert u.modality is not None and u.pragmatic not in REQUESTS and not gate[u.id]
        assert u.realized is None
        if u.id in events:
            assert events[u.id].occurrence_claim.value == "UNRESOLVED"
    assert any(c.construction == "shared_modality" for c in f.coordinations)


def test_negated_compound_desire_member_stays_open():
    f, gate, _ = _view("Paul n'a pas voulu lancer P et exécuter Q.")
    q = f.units[-1]
    assert q.pragmatic == "EMBEDDED" and not gate[q.id]
    assert f"negated_scope_open:{q.id}" in f.ambiguities


@pytest.mark.parametrize("text,claim", [
    ("Paul a lancé P.", "ASSERTED_REALIZED"),
    ("Paul pouvait lancer P.", "POSSIBLE"),
    ("Paul voulait lancer P.", "NO_ASSERTION"),
    ("Paul peut lancer P.", "POSSIBLE"),
])
def test_other_tenses_unchanged(text, claim):
    f, _, events = _view(text)
    assert events[f.units[0].id].occurrence_claim.value == claim
    assert not any(a.startswith("modal_past_occurrence_open") for a in f.ambiguities)


@pytest.mark.parametrize("text", ["Paul a voulu que Nadia lance P.", "Paul a pu.", "Paul a fait lancer P."])
def test_no_chain_without_a_bare_infinitive(text):
    f = parse_utterance(text)
    assert not any(a.startswith("modal_past_occurrence_open") for a in f.ambiguities)
