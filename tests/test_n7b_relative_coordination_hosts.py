"""N7b: predicates coordinated after a subject "qui" relative are attached by morphology
(H11 option C), never by proximity, and never become definitive root requests.

- only the relative can host the member (relative on the sentence-initial NP; an imperative
  or infinitive host that cannot coordinate a 3rd-person finite form): it is coordinated with
  the relative's predicate (COORDINATES / ALTERNATIVE), same antecedent / parent, no request;
- imperative-only form ("et exécutez Q"): the host's directive (unchanged);
- 3sg / imperative homograph under an imperative host ("Lance le script qui teste P et
  exécute Q"): attachment open and named, possible request exposed fail-closed (H11 C);
  under a finite declarative host: open and named, no request.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary


def _rels(f):
    return [(r.kind, r.source, r.target) for r in f.relations]


@pytest.mark.parametrize("text,link", [
    ("Peux-tu lancer le script qui teste P et exécute Q ?", "COORDINATES"),
    ("Lance le script qui teste P et a exécuté Q.", "COORDINATES"),
])
def test_member_inside_relative(text, link):
    f = parse_utterance(text)
    assert (link, "u2", "u3") in _rels(f) and ("EMBEDS", "u1", "u3") in _rels(f)
    assert f.unit("u3").pragmatic not in {"REQUESTED", "INDIRECT_REQUEST"}
    assert "exécute" not in governable_summary(f)["requested_action_surfaces"]


@pytest.mark.parametrize("text,link", [("Le script qui lance P et exécute Q est prêt.", "COORDINATES"),
                                       ("Le script qui lance P ou exécute Q est prêt.", "ALTERNATIVE")])
def test_subject_relative_coordination_represented(text, link):
    f = parse_utterance(text)
    assert _rels(f) == [(link, "u1", "u2")]
    assert governable_summary(f)["requested_world_actions"] == [] and not f.closure


@pytest.mark.parametrize("text", ["Lance le script qui teste P et exécute Q.", "Lance le script qui teste P ou exécute Q."])
def test_imperative_host_homograph_open_with_possible_request(text):
    f = parse_utterance(text)
    m = f.unit("u3")
    assert m.pragmatic == "EMBEDDED" and m.pragmatic != "REQUESTED"
    assert "coordination_attachment_ambiguous:u3" in f.ambiguities and not f.closure
    assert f.unit("u1").pragmatic == "REQUESTED"


def test_declarative_host_homograph_open_no_request():
    f = parse_utterance("Paul lance le script qui teste P et exécute Q.")
    assert "coordination_attachment_ambiguous:u3" in f.ambiguities and not f.closure
    assert governable_summary(f)["requested_world_actions"] == []


def test_controls():
    f = parse_utterance("Lance le script qui teste P et exécutez Q.")
    assert [u.pragmatic for u in f.units] == ["REQUESTED", "ASSERTED", "REQUESTED"]
    assert [u.pragmatic for u in parse_utterance("Lance P et exécute Q.").units] == ["REQUESTED", "REQUESTED"]
    assert governable_summary(parse_utterance("Lance le script qui teste P."))["requested_action_surfaces"] == ["lance"]
