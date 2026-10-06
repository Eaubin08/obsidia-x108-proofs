"""N7: a verb coordinated inside a subject "qui" relative is never a root request.

"Le script qui lance P et exécute Q est prêt": "exécute Q" became a definitive REQUESTED and
"est prêt" was dropped while the frame closed. A verb coordinated right after a subject
relative on the sentence-initial NP continues that relative (attachment open, named, no
request, no gate); what follows its objects is the antecedent's main predicate, reported.
A subject relative whose main predicate is found nowhere keeps the frame open
(main_predicate_unresolved). A main imperative before the relative is unchanged.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary


@pytest.mark.parametrize("text", ["Le script qui lance P et exécute Q est prêt.",
                                  "Le script qui lance P ou exécute Q est prêt."])
def test_relative_member_never_requested(text):
    f = parse_utterance(text)
    m = f.unit("u2")
    # N7b (requalified): same status as the relative's own predicate, never a request
    assert (m.lemma, [a.text for a in m.objects]) == ("exécuter", ["q"])
    assert m.pragmatic == f.unit("u1").pragmatic and m.pragmatic not in {"REQUESTED", "INDIRECT_REQUEST"}
    # N7b (requalified, formerly only named ambiguous): coordinated inside the relative
    assert any(r.kind in {"COORDINATES", "ALTERNATIVE"} and (r.source, r.target) == ("u1", "u2") for r in f.relations)
    assert any(x.endswith(":main_predicate_after_relative_of=u2") for x in f.missing)
    assert governable_summary(f)["requested_world_actions"] == [] and not f.closure


def test_unresolved_main_predicate_keeps_frame_open():
    f = parse_utterance("Le système qui teste P et analyse Q fonctionne.")
    assert any(x.endswith(":main_predicate_unresolved") for x in f.missing) and not f.closure
    assert governable_summary(f)["requested_world_actions"] == []


@pytest.mark.parametrize("text,subject", [("Le script qui lance P lance Q.", "script"), ("Paul qui lance P lance Q.", "paul")])
def test_found_main_predicate_unchanged(text, subject):
    f = parse_utterance(text)
    assert f.unit("u2").subject == subject and f.closure


def test_main_imperative_before_relative_unchanged():
    f = parse_utterance("Lance le script qui teste P et exécute Q.")
    assert f.units[0].pragmatic == "REQUESTED"
