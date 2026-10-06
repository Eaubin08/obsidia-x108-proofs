"""D7 option B: purpose clauses are embedded under their unique structural host.

"pour + INF" and "pour que / afin que P": role PURPOSE, EMBEDS(host -> purpose) with
evidence "pour" / "pour_que", only when the host is structurally unique (the one main unit
of an uncoordinated clause, or the adjacent main clause of a preposed purpose with no
coordinated member). Otherwise the attachment is named (coordination_attachment_ambiguous),
never chosen by proximity. Never a cause, condition, temporal order or authority; the
purpose content is neither asserted nor requested (no occurrence); the host keeps its gate.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary

_CAUSAL = {"CAUSES", "CONDITIONS", "PREVENTS", "PRECEDES", "TEMPORAL_ANCHOR", "OVERLAPS", "EXCEPTS"}


@pytest.mark.parametrize("text,host,purpose,evidence,requested", [
    ("Paul lance P pour tester Q.", "u1", "u2", "pour", []),
    ("Lance P pour tester Q.", "u1", "u2", "pour", ["lance"]),
    ("Pour tester Q, lance P.", "u2", "u1", "pour", ["lance"]),
    ("Paul lance P pour que Marie teste Q.", "u1", "u2", "pour_que", []),
    ("Lance P afin que Marie teste Q.", "u1", "u2", "pour_que", ["lance"]),
    ("Pour que Marie teste Q, lance P.", "u2", "u1", "pour_que", ["lance"]),
])
def test_purpose_embedded_under_unique_host(text, host, purpose, evidence, requested):
    f = parse_utterance(text)
    p = f.unit(purpose)
    assert (p.role, p.pragmatic, p.embedded_under) == ("PURPOSE", "EMBEDDED", host)
    assert [(r.kind, r.source, r.target, r.evidence) for r in f.relations] == [("EMBEDS", host, purpose, evidence)]
    assert not any(r.kind in _CAUSAL for r in f.relations)
    occ = {e.predicate_ref: e.occurrence_claim.value for e in build_frame_event_index(f).events()}
    assert occ.get(purpose) in {None, "NO_ASSERTION", "UNRESOLVED"}
    assert governable_summary(f)["requested_action_surfaces"] == requested and f.closure


@pytest.mark.parametrize("text,purpose", [("Paul lance P et exécute Q pour tester R.", "u3"),
                                          ("Pour tester Q, lance P et exécute R.", "u1"),
                                          ("Lance P et exécute R pour que Marie teste Q.", "u3")])
def test_purpose_over_coordination_stays_open(text, purpose):
    f = parse_utterance(text)
    assert f.unit(purpose).role == "PURPOSE"
    assert not any(r.kind == "EMBEDS" and r.target == purpose for r in f.relations)
    assert f"coordination_attachment_ambiguous:{purpose}" in f.ambiguities and not f.closure


def test_serve_for_unchanged():
    f = parse_utterance("Le script sert à tester Q.")
    assert [(r.kind, r.evidence) for r in f.relations] == [("EMBEDS", "servir_a")] and f.closure
