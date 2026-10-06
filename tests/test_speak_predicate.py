"""SPEAK: a canonical non-reporting predicate, recognised by construction.

"parler" is SPEAK (class "other"): never embedding_say, so never REPORTS (SPEAK != SAY).
Its unsupported complements stay explicit and open: "à Marie" is an UNRESOLVED
ObliqueArgumentRef; "de KX108" is not an object (no TOPIC role yet) but reported content
(speak_complement_of); "du fait que P" / "de ce que P" use the known-governor contract (P
EMBEDDED under SPEAK, unresolved_complement_governance, never a relative nor an asserted
occurrence). SAY / REPORTS are unchanged.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary

ASSERTIVE = {"ASSERTED_REALIZED", "ASSERTED_NOT_REALIZED", "PROJECTED_FUTURE", "POSSIBLE"}


def _speak(f):
    (u,) = [u for u in f.units if u.predicate == "SPEAK"]
    return u


def test_bare_speak_closes():
    f = parse_utterance("Paul parle.")
    u = _speak(f)
    assert (u.subject, u.predicate_class, u.objects) == ("paul", "other", ()) and f.closure
    assert not f.relations and governable_summary(f)["requested_world_actions"] == []


def test_speak_a_marie_is_an_unresolved_oblique():
    f = parse_utterance("Paul parle à Marie.")
    assert [(o.role, o.marker, o.argument.text) for o in f.oblique_arguments] == [("UNRESOLVED", "à", "marie")]
    assert not f.closure


def test_speak_de_complement_is_kept_not_an_object():
    f = parse_utterance("Paul parle de KX108.")
    u = _speak(f)
    assert u.objects == () and not f.closure
    (m,) = [m for m in f.missing if m.endswith(f":speak_complement_of={u.id}")]
    a, b = map(int, m.split(":")[1].split("-"))
    assert f.raw[a:b] == "de KX108"


@pytest.mark.parametrize("text", ["Marie parle du fait que Paul a lancé le test.",
                                  "Marie parle de ce que Paul a lancé."])
def test_speak_complement_is_embedded_never_asserted_nor_reported(text):
    f = parse_utterance(text)
    s, x = _speak(f), next(u for u in f.units if u.predicate == "EXECUTE")
    assert (x.embedded_under, x.pragmatic) == (s.id, "EMBEDDED")
    assert not any(r.kind == "REPORTS" for r in f.relations)
    assert f"unresolved_complement_governance:{x.id}" in f.ambiguities and not f.closure
    claims = {c.predicate_ref: c.occurrence_claim.value for c in build_frame_event_index(f).events()}
    assert claims.get(x.id) not in ASSERTIVE


def test_say_reports_unchanged():
    f = parse_utterance("Marie dit que Paul a lancé le test.")
    assert ("REPORTS", "u1", "u2") in [(r.kind, r.source, r.target) for r in f.relations]
    assert f.units[1].pragmatic == "REPORTED" and f.closure


def test_reported_speak_is_reported_by_say_not_by_speak():
    f = parse_utterance("Paul dit que Marie parle.")
    assert [(r.kind, r.source, r.target) for r in f.relations] == [("REPORTS", "u1", "u2")]
    assert f.units[1].predicate == "SPEAK"
