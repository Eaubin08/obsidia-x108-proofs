"""G5: "R si P et Q" never attaches Q by proximity.

After a postposed protasis ("Lance R si Paul veut lancer P et exécuter Q"), Q
may continue the protasis or the main clause (held doctrine, H11). The
conditional host was taken as the NEXT main head, so the protasis conditioned
Q (CONDITIONS P -> Q) instead of R, Q became an independent gated request
coordinated with R, and closure was True.

Fail-closed: the member after a postposed protasis is kept, named
(coordination_attachment_ambiguous), never semantically REQUESTED, never
related by proximity (no CONDITIONS to it, no COORDINATES with R), its
occurrence stays unresolved, and the protasis conditions its own host R.
G5-R: its main-clause request reading is still exposed at runtime as a
possible request (EMBEDDED + role REQUEST); a member whose morphology leaves
only the main imperative reading is a request (test_postposed_protasis_request). Forms whose structure
fixes the attachment are unchanged: the preposed conjunctive protasis ("Si P
et Q, R") and a member coordinated before the protasis ("R et Q si P").
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary
from app.semantic.lattice.projections import ProjectionAxis, project

_REQ = {"REQUESTED", "INDIRECT_REQUEST", "FORBIDDEN"}


def _gate(f):
    return {k: v["requires_gate"] for k, v in project(f, ProjectionAxis.AUTHORITY).items()}


def _rels(f):
    return {(r.kind, r.source, r.target) for r in f.relations}


@pytest.mark.parametrize("text", [
    "Lance R si Paul veut lancer P et exécuter Q.",
    "Lance R si Paul peut lancer P et exécuter Q.",
    "Lance R si Paul doit lancer P et exécuter Q.",
    "Lance R si Paul va lancer P et exécuter Q.",
    "Lance R si Paul lance P et exécute Q.",
    "Lance R si Paul lance P et exécuter Q.",
    "Lance R si Paul veut lancer P, exécuter Q.",
    "Lance R si Paul veut lancer P ou exécuter Q.",
    "Paul lance R si Paul veut lancer P et exécuter Q.",
])
def test_member_after_postposed_protasis_is_named_not_attached(text):
    f = parse_utterance(text)
    r, p = f.units[0], f.units[1]
    (q,) = [u for u in f.units if u.lemma == "exécuter"]
    assert [a.head for a in q.objects] == ["q"]                                  # Q kept
    assert q.pragmatic == "EMBEDDED" and q.pragmatic not in _REQ and not _gate(f)[q.id]
    assert f"coordination_attachment_ambiguous:{q.id}" in f.ambiguities
    assert not any(q.id in (x.source, x.target) and x.kind in {"CONDITIONS", "COORDINATES", "ALTERNATIVE"}
                   for x in f.relations)                                         # no proximity relation
    assert ("CONDITIONS", p.id, r.id) in _rels(f)                                # the protasis conditions R
    events = {c.predicate_ref: c for c in build_frame_event_index(f).events()}
    assert events[q.id].occurrence_claim.value == "UNRESOLVED"
    assert q.role == "REQUEST" and q.surface in governable_summary(f)["requested_action_surfaces"]  # possible
    assert not f.closure


def test_main_directive_keeps_its_gate():
    f = parse_utterance("Lance R si Paul veut lancer P et exécuter Q.")
    assert (f.units[0].pragmatic, _gate(f)["u1"]) == ("REQUESTED", True)


def test_preposed_conjunctive_protasis_is_unchanged():
    f = parse_utterance("Si Paul veut lancer P et exécuter Q, lance R.")
    assert not any(a.startswith("coordination_attachment_ambiguous") for a in f.ambiguities)
    r = next(u for u in f.units if u.lemma == "lancer" and u.span[0] > 30)
    assert r.pragmatic == "REQUESTED" and any(x.kind == "CONDITIONS" and x.target == r.id for x in f.relations)


def test_member_before_the_protasis_is_unchanged():
    f = parse_utterance("Lance R et exécute Q si Paul veut lancer P.")
    gate = _gate(f)
    r, q = f.units[0], f.units[1]
    assert (r.pragmatic, q.pragmatic, gate[r.id], gate[q.id]) == ("REQUESTED", "REQUESTED", True, True)
    assert ("COORDINATES", r.id, q.id) in _rels(f)
    assert not any(a.startswith("coordination_attachment_ambiguous") for a in f.ambiguities)


def test_simple_postposed_protasis_is_unchanged():
    f = parse_utterance("Lance R si Paul veut lancer P.")
    assert ("CONDITIONS", "u2", "u1") in _rels(f) and f.closure


@pytest.mark.parametrize("text", ["Lance R si Paul lance P et n'exécute pas Q.",
                                  "Lance R si Paul veut lancer P et ne pas exécuter Q."])
def test_possible_main_clause_prohibition_is_kept_but_named(text):
    # one reading is a prohibition of the main clause: in doubt it is kept (never relaxes execution)
    f = parse_utterance(text)
    q = f.units[-1]
    assert (q.lemma, q.pragmatic) == ("exécuter", "FORBIDDEN") and "NO_EXECUTE(q)" in f.constraints
    assert f"coordination_attachment_ambiguous:{q.id}" in f.ambiguities and not f.closure
    assert not any(q.id in (x.source, x.target) for x in f.relations if x.kind == "CONDITIONS")
